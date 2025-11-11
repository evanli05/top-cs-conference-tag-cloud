"""
Fetch paper data from DBLP API for CS conferences
TODO:
    1. Edge case of keynotes/invited talks that is not started with "Keynote" is not elimited from the fetch results. Therefore
        the fetched results still have a little noise. Need to update this later.
    2. Test the commit on VSCODE.

"""

import requests
import time
from typing import List, Dict
import sys
from bs4 import BeautifulSoup
import re
import argparse
import json
import os

# Import local modules
import config
import utils


class DBLPFetcher:
    """Fetch paper data from DBLP API"""

    def __init__(self, conference_key: str = None):
        """
        Initialize DBLP fetcher

        Args:
            conference_key (str): Conference key (e.g., 'kdd')
        """
        self.conference_key = conference_key or config.DEFAULT_CONFERENCE
        self.conf_config = config.get_conference_config(self.conference_key)
        self.last_request_time = 0

        utils.log(f"Initialized DBLP Fetcher for {self.conf_config['name']}")

    def fetch_papers_for_year(self, year: int) -> List[Dict]:
        """
        Fetch papers for a specific conference and year by crawling DBLP pages

        Args:
            year (int): Year to fetch

        Returns:
            List[Dict]: List of paper dictionaries
        """
        venue = self.conf_config['dblp_venue']
        conference_name = self.conf_config['name']

        utils.log(f"Fetching {conference_name} {year} papers from DBLP...")

        # Check if this conference year has multiple parts
        multi_part_key = (venue, year)
        if multi_part_key in config.DBLP_MULTI_PART_CONFERENCES:
            suffixes = config.DBLP_MULTI_PART_CONFERENCES[multi_part_key]
        else:
            suffixes = ['']  # Single page

        all_papers = []

        for suffix in suffixes:
            # Build URL for DBLP conference page
            # Format: https://dblp.org/db/conf/kdd/kdd2020.html
            # Special case: NeurIPS uses /conf/nips/ directory but neurips{year}.html filenames
            dblp_dir = self.conf_config.get('dblp_dir', venue)
            url = f"{config.DBLP_BASE_URL}/db/conf/{dblp_dir}/{venue}{year}{suffix}.html"

            utils.log(f"  Crawling {url}...")

            try:
                # Rate limiting
                self.last_request_time = utils.rate_limit(
                    self.last_request_time,
                    config.REQUEST_DELAY
                )

                # Fetch the page
                response = requests.get(
                    url,
                    headers={'User-Agent': config.USER_AGENT},
                    timeout=config.REQUEST_TIMEOUT
                )

                response.raise_for_status()

                # Parse HTML and extract papers
                papers = self._parse_dblp_html(response.text, year)
                all_papers.extend(papers)

                utils.log(f"  Found {len(papers)} papers")

            except requests.exceptions.RequestException as e:
                utils.log(f"  Error fetching {url}: {e}", 'WARNING')
            except Exception as e:
                utils.log(f"  Unexpected error for {url}: {e}", 'ERROR')

        utils.log(f"Fetched {len(all_papers)} papers for {conference_name} {year}")
        return all_papers

    def _parse_dblp_html(self, html_content: str, year: int) -> List[Dict]:
        """
        Parse DBLP HTML page and extract paper information

        Args:
            html_content (str): HTML content from DBLP page
            year (int): Expected year

        Returns:
            List[Dict]: List of paper dictionaries
        """
        papers = []
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all publication entries (class="entry")
        # DBLP structure: <li class="entry">...</li>
        entries = soup.find_all('li', class_='entry')

        for i, entry in enumerate(entries, 1):
            try:
                # Extract title - usually in <span class="title"> or <cite>
                title_elem = entry.find('span', class_='title')
                if not title_elem:
                    # Try alternate structure
                    title_elem = entry.find('cite', itemprop='headline')

                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)

                # Remove trailing period if present
                if title.endswith('.'):
                    title = title[:-1]

                # Basic filtering for non-papers (proceedings pages are already clean)
                # Only filter out obvious non-research entries
                title_lower = title.lower()
                conf_name_lower = self.conf_config['name'].lower()

                # Skip proceedings metadata and non-research entries
                if (title_lower.startswith(f"{conf_name_lower} '") or  # "KDD '20:"
                    title_lower.startswith('proceedings of') or
                    title_lower.startswith('keynote') or
                    'keynote speaker:' in title_lower or  # "Keynote Speaker: Name"
                    title_lower.startswith('invited talk')):
                    continue

                # Extract authors - usually in <span itemprop="author">
                author_elems = entry.find_all('span', itemprop='author')
                if not author_elems:
                    # Try alternate: <span class="this-person"> or just find all author spans
                    author_elems = entry.find_all('span', class_='this-person')

                authors = []
                for author_elem in author_elems:
                    # Get author name from various possible elements
                    author_name = None
                    author_span = author_elem.find('span', itemprop='name')
                    if author_span:
                        author_name = author_span.get_text(strip=True)
                    else:
                        # Try direct text
                        author_name = author_elem.get_text(strip=True)

                    if author_name:
                        # Clean author name: remove DBLP disambiguation IDs
                        author_name = re.sub(r'\s+\d{4}$', '', author_name).strip()
                        authors.append(author_name)

                # Extract URL to paper details page
                url_elem = entry.find('nav', class_='publ')
                paper_url = ''
                doi = ''
                openreview_url = ''
                openreview_id = None
                neurips_proceedings_url = ''

                if url_elem:
                    # Look for OpenReview link (check this first for conferences using OpenReview)
                    openreview_link = url_elem.find('a', href=re.compile(r'openreview\.net'))
                    if openreview_link:
                        openreview_url = openreview_link.get('href', '')
                        openreview_id = self._extract_openreview_id(openreview_url)

                    # Look for DOI link
                    doi_link = url_elem.find('a', href=re.compile(r'doi\.org'))
                    if doi_link:
                        doi = doi_link.get('href', '')

                    # Look for DBLP record URL
                    dblp_link = url_elem.find('a', href=re.compile(r'dblp\.org/rec'))
                    if dblp_link:
                        paper_url = dblp_link.get('href', '')

                    # Look for NeurIPS proceedings link (for NeurIPS conferences 2020-2024)
                    # These URLs contain hashes for direct abstract access
                    neurips_link = url_elem.find('a', href=re.compile(r'(proceedings\.neurips\.cc|papers\.nips\.cc)'))
                    if neurips_link:
                        neurips_proceedings_url = neurips_link.get('href', '')

                # Create paper dictionary
                paper = {
                    'title': title,
                    'year': year,
                    'authors': authors,
                    'venue': self.conf_config['name'],
                    'url': paper_url,
                    'doi': doi,
                    'openreview_url': openreview_url,
                    'openreview_id': openreview_id,
                    'neurips_proceedings_url': neurips_proceedings_url
                }

                papers.append(paper)

                # Progress logging for large conference years (every 1000 papers)
                if config.DBLP_PROGRESS_LOG_INTERVAL > 0 and len(papers) % config.DBLP_PROGRESS_LOG_INTERVAL == 0:
                    self._save_progress_log(f"DBLP {year}: {len(papers)} papers parsed (entry {i}/{len(entries)})")

            except Exception as e:
                utils.log(f"    Error parsing entry: {e}", 'WARNING')
                continue

        return papers

    def fetch_all_years(self, years: List[int] = None) -> List[Dict]:
        """
        Fetch papers for all specified years

        Args:
            years (List[int]): Years to fetch (default: from config)

        Returns:
            List[Dict]: Combined list of all papers
        """
        if years is None:
            years = self.conf_config['years']

        all_papers = []
        conference_name = self.conf_config['name']

        utils.log(f"\nFetching {conference_name} papers for years: {years}")
        utils.log(f"{'='*50}")

        for i, year in enumerate(years, 1):
            utils.progress_bar(
                i - 1, len(years),
                prefix=f'Progress:',
                suffix=f'Fetching {year}...'
            )

            papers = self.fetch_papers_for_year(year)
            all_papers.extend(papers)

            time.sleep(0.5)  # Small delay between years

        utils.progress_bar(len(years), len(years), prefix='Progress:', suffix='Complete!')

        utils.log(f"\nTotal papers fetched: {len(all_papers)}")

        return all_papers

    def save_papers(self, papers: List[Dict], filepath: str = None):
        """
        Save papers to JSON file

        Args:
            papers (List[Dict]): Papers to save
            filepath (str): Output file path (default: conference-specific from config)
        """
        if filepath is None:
            filepath = config.get_raw_papers_file(self.conference_key)

        # Add metadata
        data = {
            'metadata': {
                'conference': self.conf_config['name'],
                'full_name': self.conf_config['full_name'],
                'categories': self.conf_config['categories'],
                'years': self.conf_config['years'],
                'total_papers': len(papers),
                'fetched_at': utils.get_current_timestamp(),
                'source': 'DBLP'
            },
            'papers': papers
        }

        utils.save_json(data, filepath)
        utils.log(f"Saved {len(papers)} papers to {filepath}")

    def _save_progress_log(self, message: str):
        """
        Append progress message to log file

        Args:
            message (str): Progress message to log
        """
        log_file = config.get_raw_papers_file(self.conference_key).replace('.json', '_progress.log')
        timestamp = utils.get_current_timestamp()

        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            utils.log(f"Warning: Could not write to progress log: {e}", 'WARNING')

    def reconstruct_abstract_from_inverted_index(self, inv_index: Dict[str, List[int]]) -> str:
        """
        Convert OpenAlex inverted index to plain text abstract

        Args:
            inv_index (Dict): Inverted index mapping word -> list of positions

        Returns:
            str: Reconstructed abstract text
        """
        if not inv_index:
            return None

        # Create list of (position, word) tuples
        word_positions = []
        for word, positions in inv_index.items():
            for pos in positions:
                word_positions.append((pos, word))

        # Sort by position
        word_positions.sort(key=lambda x: x[0])

        # Join words to form abstract
        abstract = " ".join([word for _, word in word_positions])
        return abstract

    def _extract_openreview_id(self, url: str) -> str:
        """
        Extract OpenReview forum ID from URL

        Args:
            url (str): OpenReview URL (e.g., https://openreview.net/forum?id=XXXXX)

        Returns:
            str: Forum ID or None if not found
        """
        if not url or 'openreview.net' not in url:
            return None

        # Extract forum ID from URL parameter
        # Format: https://openreview.net/forum?id=XXXXX
        match = re.search(r'[?&]id=([^&]+)', url)
        if match:
            return match.group(1)

        return None

    def search_openreview_by_title(self, title: str, year: int, venue: str) -> str:
        """
        Search OpenReview for a paper by title to find its forum ID

        Args:
            title (str): Paper title to search for
            year (int): Paper year (determines API version and venue)
            venue (str): Conference venue key (e.g., 'iclr')

        Returns:
            str: Forum ID if found, None otherwise
        """
        if not config.OPENREVIEW_SEARCH_ENABLED or not title or venue not in config.OPENREVIEW_VENUES:
            return None

        try:
            # Rate limiting
            time.sleep(1.0 / config.OPENREVIEW_RATE_LIMIT)

            # Select API version based on year
            if year >= config.OPENREVIEW_API_V2_YEAR_THRESHOLD:
                base_url = config.OPENREVIEW_API_V2_URL
            else:
                base_url = config.OPENREVIEW_API_V1_URL

            # Construct venue string for search (e.g., "ICLR.cc/2024/Conference")
            venue_name = config.OPENREVIEW_VENUES[venue]
            search_venue = f"{venue_name}/{year}/Conference"

            # Search for papers by title in this venue
            url = f"{base_url}/notes"
            params = {
                'content.title': title,
                'invitation': f"{search_venue}/-/Blind_Submission",
                'limit': 1
            }

            response = requests.get(url, params=params, timeout=config.OPENREVIEW_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # Extract forum ID from search results
            notes = data.get('notes', [])
            if notes and len(notes) > 0:
                forum_id = notes[0].get('id') or notes[0].get('forum')
                if forum_id:
                    return forum_id

            return None

        except Exception as e:
            utils.log(f"    Error searching OpenReview for '{title[:50]}...': {e}", 'WARNING')
            return None

    def fetch_abstract_openreview(self, forum_id: str, year: int, venue: str) -> tuple:
        """
        Fetch abstract from OpenReview API for a single paper

        Args:
            forum_id (str): OpenReview forum ID
            year (int): Paper year (determines API version)
            venue (str): Conference venue key (e.g., 'iclr')

        Returns:
            tuple: (abstract, citation_count, openreview_id) or (None, None, None)
        """
        if not forum_id:
            return (None, None, None)

        try:
            # Rate limiting
            time.sleep(1.0 / config.OPENREVIEW_RATE_LIMIT)

            # Select API version based on year
            if year >= config.OPENREVIEW_API_V2_YEAR_THRESHOLD:
                # Use API v2 for 2024+
                base_url = config.OPENREVIEW_API_V2_URL
            else:
                # Use API v1 for 2023 and earlier
                base_url = config.OPENREVIEW_API_V1_URL

            # Both API versions use the same endpoint format
            url = f"{base_url}/notes?id={forum_id}"

            response = requests.get(url, timeout=config.OPENREVIEW_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            # Extract abstract - both API versions return list of notes
            abstract = None
            citation_count = None  # OpenReview doesn't provide citation counts

            notes = data.get('notes', [])
            if notes:
                content = notes[0].get('content', {})
                # Abstract may be in 'abstract', 'TLDR', or other fields
                abstract = content.get('abstract') or content.get('TL;DR') or content.get('tldr')

                # Some OpenReview abstracts are dictionaries with 'value' key
                if isinstance(abstract, dict) and 'value' in abstract:
                    abstract = abstract['value']

            return (abstract, citation_count, forum_id)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Paper not found in OpenReview
                return (None, None, None)
            utils.log(f"    HTTP error for OpenReview ID {forum_id}: {e}", 'WARNING')
            return (None, None, None)
        except Exception as e:
            utils.log(f"    Error fetching OpenReview ID {forum_id}: {e}", 'WARNING')
            return (None, None, None)

    def fetch_abstracts_openalex(self, papers: List[Dict]) -> Dict[str, tuple]:
        """
        Fetch abstracts from OpenAlex API in batches

        Args:
            papers (List[Dict]): List of papers with DOI field

        Returns:
            Dict[str, tuple]: Mapping of DOI -> (abstract, citation_count, semantic_scholar_id)
        """
        utils.log("\nFetching abstracts from OpenAlex...")

        # Extract DOIs from papers
        dois = []
        for paper in papers:
            doi = paper.get('doi', '').replace('https://doi.org/', '').strip().lower()
            if doi:
                dois.append(doi)

        if not dois:
            utils.log("  No DOIs found in papers", 'WARNING')
            return {}

        utils.log(f"  Found {len(dois)} papers with DOIs")

        abstracts = {}
        batch_size = config.OPENALEX_BATCH_SIZE
        total_batches = (len(dois) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min(start_idx + batch_size, len(dois))
            batch_dois = dois[start_idx:end_idx]

            # Create filter parameter for batch query
            doi_filter = "|".join(batch_dois)

            try:
                # Rate limiting
                if batch_num > 0:
                    time.sleep(1.0 / config.OPENALEX_RATE_LIMIT)

                # Query OpenAlex API
                url = config.OPENALEX_API_URL
                params = {
                    "filter": f"doi:{doi_filter}",
                    "per-page": batch_size,
                    "mailto": config.OPENALEX_EMAIL
                }

                response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
                response.raise_for_status()
                data = response.json()

                # Process results
                for work in data.get("results", []):
                    doi = work.get("doi", "").replace("https://doi.org/", "").lower()
                    inv_index = work.get("abstract_inverted_index")
                    citation_count = work.get("cited_by_count", 0)
                    openalex_id = work.get("id", "").replace("https://openalex.org/", "")

                    if inv_index:
                        abstract = self.reconstruct_abstract_from_inverted_index(inv_index)
                        abstracts[doi] = (abstract, citation_count, openalex_id)
                    else:
                        abstracts[doi] = (None, citation_count, openalex_id)

                utils.log(f"  Batch {batch_num + 1}/{total_batches}: Retrieved {len([a for a in abstracts.values() if a[0] is not None])} abstracts")

            except Exception as e:
                utils.log(f"  Error fetching batch {batch_num + 1}: {e}", 'WARNING')

        abstract_count = len([a for a in abstracts.values() if a[0] is not None])
        utils.log(f"  OpenAlex: {abstract_count}/{len(dois)} abstracts ({abstract_count * 100 / len(dois):.1f}%)")

        return abstracts

    def fetch_abstract_semantic_scholar(self, doi: str) -> tuple:
        """
        Fetch abstract from Semantic Scholar API for a single paper

        Args:
            doi (str): DOI of the paper (without https://doi.org/ prefix)

        Returns:
            tuple: (abstract, citation_count, s2_paper_id) or (None, None, None)
        """
        if not doi:
            return (None, None, None)

        try:
            # Rate limiting
            time.sleep(1.0 / config.SEMANTIC_SCHOLAR_RATE_LIMIT)

            # Query Semantic Scholar API
            url = f"{config.SEMANTIC_SCHOLAR_API_URL}/DOI:{doi}"
            params = {"fields": config.SEMANTIC_SCHOLAR_FIELDS}

            response = requests.get(url, params=params, timeout=config.SEMANTIC_SCHOLAR_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            abstract = data.get("abstract")
            citation_count = data.get("citationCount", 0)
            s2_paper_id = data.get("paperId")

            return (abstract, citation_count, s2_paper_id)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Paper not found in Semantic Scholar
                return (None, None, None)
            utils.log(f"    HTTP error for DOI {doi}: {e}", 'WARNING')
            return (None, None, None)
        except Exception as e:
            utils.log(f"    Error fetching DOI {doi}: {e}", 'WARNING')
            return (None, None, None)

    def fetch_abstract_openalex_by_title(self, title: str) -> tuple:
        """
        Fetch abstract from OpenAlex by searching for paper title

        This is a fallback for papers where DOI-based lookup failed (e.g., IEEE papers).
        OpenAlex DOI indexing for IEEE papers is incomplete, but title search works.

        Args:
            title (str): Paper title to search for

        Returns:
            tuple: (abstract, citation_count, openalex_id) or (None, None, None)
        """
        if not title or len(title) < 10:  # Skip very short titles
            return (None, None, None)

        try:
            # Rate limiting (same as OpenAlex batch)
            time.sleep(1.0 / config.OPENALEX_RATE_LIMIT)

            # Query OpenAlex API by title
            url = config.OPENALEX_API_URL
            params = {
                "filter": f"title.search:{title}",
                "per-page": 1,
                "mailto": config.OPENALEX_EMAIL
            }

            response = requests.get(url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            if not results:
                return (None, None, None)

            # Get first result (best match)
            work = results[0]
            inv_index = work.get("abstract_inverted_index")
            citation_count = work.get("cited_by_count", 0)
            openalex_id = work.get("id", "").replace("https://openalex.org/", "")

            if inv_index:
                abstract = self.reconstruct_abstract_from_inverted_index(inv_index)
                return (abstract, citation_count, openalex_id)
            else:
                return (None, citation_count, openalex_id)

        except Exception as e:
            utils.log(f"    Error fetching by title '{title[:50]}...': {e}", 'WARNING')
            return (None, None, None)

    def _extract_hash_from_proceedings_url(self, url: str) -> tuple:
        """
        Extract hash and track type from NeurIPS proceedings URL

        Args:
            url (str): Proceedings URL from DBLP

        Returns:
            tuple: (hash, track_type) or (None, None) if not found

        Examples:
            Input: "http://papers.nips.cc/paper_files/paper/2022/hash/002262941c9edfd472a79298b2ac5e17-Abstract-Conference.html"
            Output: ("002262941c9edfd472a79298b2ac5e17", "Conference")

            Input: "https://proceedings.neurips.cc/paper/2020/hash/0004d0b59e19461ff126e3a08a814c33-Abstract.html"
            Output: ("0004d0b59e19461ff126e3a08a814c33", "Conference")  # Default to Conference
        """
        # Try to match with explicit track type first
        match = re.search(
            r'/hash/([a-f0-9]{32})-Abstract-(Conference|Datasets_and_Benchmarks)',
            url
        )
        if match:
            return match.group(1), match.group(2)

        # Fall back to matching without track type (default to Conference)
        match = re.search(
            r'/hash/([a-f0-9]{32})-Abstract',
            url
        )
        if match:
            return match.group(1), "Conference"

        return None, None

    def fetch_neurips_proceedings_abstract(self, year: int, paper_hash: str, track: str = None) -> tuple:
        """
        Fetch abstract and metadata from NeurIPS proceedings website

        Args:
            year (int): Conference year (e.g., 2022)
            paper_hash (str): 32-character hexadecimal hash
            track (str): Deprecated parameter (kept for backward compatibility, not used)

        Returns:
            tuple: (abstract, None, proceedings_url) or (None, None, None) if fetch fails
            Note: citation_count is None because proceedings doesn't provide it
        """
        if not paper_hash:
            return (None, None, None)

        try:
            # Rate limiting for proceedings site
            time.sleep(1.0 / config.NEURIPS_PROCEEDINGS_RATE_LIMIT)

            # Build URL (correct format for proceedings.neurips.cc)
            # Note: URLs don't include track type suffix, just -Abstract.html
            url = f"{config.NEURIPS_PROCEEDINGS_BASE_URL}/paper/{year}/hash/{paper_hash}-Abstract.html"

            response = requests.get(url, timeout=config.NEURIPS_PROCEEDINGS_TIMEOUT)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract abstract from HTML (nested <p> tags after <h4>Abstract</h4>)
            abstract = None
            abstract_h4 = soup.find('h4', string='Abstract')
            if abstract_h4:
                abstract_p = abstract_h4.find_next('p')
                if abstract_p:
                    # Abstract may be in nested <p> tags or directly in the <p>
                    inner_p = abstract_p.find('p')
                    if inner_p:
                        abstract = inner_p.get_text().strip()
                    else:
                        # Fallback: use direct text if no nested <p>
                        abstract = abstract_p.get_text().strip()

            if abstract:
                return (abstract, None, url)  # citation_count is None
            return (None, None, None)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Paper not found on proceedings site
                return (None, None, None)
            utils.log(f"    HTTP error for hash {paper_hash}: {e}", 'WARNING')
            return (None, None, None)
        except Exception as e:
            utils.log(f"    Error fetching hash {paper_hash}: {e}", 'WARNING')
            return (None, None, None)

    def enrich_papers_with_abstracts(self, papers: List[Dict]) -> List[Dict]:
        """
        Enrich papers with abstracts using three-tier approach:
        0. Search OpenReview by title for missing forum IDs (OpenReview-based conferences only)
        1. Fetch from OpenReview (for papers with OpenReview URLs)
        2. Fetch from OpenAlex (fast, batch processing for DOI papers)
        3. Fall back to Semantic Scholar for missing DOI abstracts

        Includes progress logging and incremental saves for monitoring and recovery.

        Args:
            papers (List[Dict]): Papers to enrich

        Returns:
            List[Dict]: Papers with added abstract fields
        """
        utils.log("\n" + "=" * 50)
        utils.log("Enriching papers with abstracts...")
        utils.log("=" * 50)

        # Initialize all papers with None values (if not already present)
        for paper in papers:
            if 'abstract' not in paper:
                paper['abstract'] = None
            if 'citation_count' not in paper:
                paper['citation_count'] = None
            if 'abstract_source' not in paper:
                paper['abstract_source'] = None
            if 'source_id' not in paper:
                paper['source_id'] = None

        # Recovery mode: Check how many papers already have abstracts
        existing_abstracts = len([p for p in papers if p.get('abstract')])
        if config.ENABLE_RECOVERY_MODE and existing_abstracts > 0:
            utils.log(f"\n[RECOVERY MODE] Found {existing_abstracts} papers with existing abstracts")
            utils.log(f"[RECOVERY MODE] Will skip these and continue from where we left off")
            self._save_progress_log(f"Recovery mode: {existing_abstracts} papers already have abstracts")

        # Tier 0: For OpenReview-based conferences, search for missing forum IDs by title
        venue = self.conf_config.get('dblp_venue')
        if venue in config.OPENREVIEW_VENUES:
            # Find papers that don't have openreview_id but should (no abstract yet)
            papers_needing_id = [p for p in papers if not p.get('openreview_id') and not p.get('abstract')]

            if papers_needing_id:
                utils.log(f"\n[OpenReview ID Search] Searching for missing forum IDs by title...")
                utils.log(f"  Papers to search: {len(papers_needing_id)}")
                self._save_progress_log(f"Starting OpenReview ID search for {len(papers_needing_id)} papers")

                found_count = 0
                for i, paper in enumerate(papers_needing_id, 1):
                    if i % 100 == 0 or i == len(papers_needing_id):
                        utils.log(f"  Search progress: {i}/{len(papers_needing_id)} (found {found_count} IDs)")

                    title = paper.get('title')
                    year = paper.get('year')

                    forum_id = self.search_openreview_by_title(title, year, venue)
                    if forum_id:
                        paper['openreview_id'] = forum_id
                        found_count += 1

                utils.log(f"  Found {found_count}/{len(papers_needing_id)} forum IDs by title search")
                self._save_progress_log(f"OpenReview ID search complete: {found_count}/{len(papers_needing_id)} found")

        # Tier 1: Fetch from OpenReview for papers with OpenReview URLs
        openreview_papers = [p for p in papers if p.get('openreview_id') and not p.get('abstract')]

        if openreview_papers:
            utils.log(f"\nFetching abstracts from OpenReview...")
            utils.log(f"  Papers to fetch: {len(openreview_papers)}")
            self._save_progress_log(f"Starting OpenReview abstract fetch for {len(openreview_papers)} papers")

            abstracts_fetched = 0
            for i, paper in enumerate(openreview_papers, 1):
                if i % 10 == 0 or i == len(openreview_papers):
                    utils.log(f"  Progress: {i}/{len(openreview_papers)}")

                openreview_id = paper.get('openreview_id')
                year = paper.get('year')
                venue = self.conf_config.get('dblp_venue')

                abstract, citation_count, forum_id = self.fetch_abstract_openreview(
                    openreview_id, year, venue
                )

                if abstract:
                    paper['abstract'] = abstract
                    paper['citation_count'] = citation_count
                    paper['abstract_source'] = 'openreview'
                    paper['source_id'] = forum_id
                    abstracts_fetched += 1

                # Progress logging and incremental saves
                if config.ABSTRACT_PROGRESS_LOG_INTERVAL > 0 and abstracts_fetched > 0 and abstracts_fetched % config.ABSTRACT_PROGRESS_LOG_INTERVAL == 0:
                    self._save_progress_log(f"OpenReview: {abstracts_fetched} abstracts fetched (progress: {i}/{len(openreview_papers)})")

                    if config.ENABLE_INCREMENTAL_SAVES and abstracts_fetched % config.INCREMENTAL_SAVE_INTERVAL == 0:
                        utils.log(f"  [INCREMENTAL SAVE] Saving progress... ({abstracts_fetched} abstracts)")
                        self.save_papers(papers)

            openreview_count = len([p for p in openreview_papers if p.get('abstract')])
            utils.log(f"  OpenReview: {openreview_count}/{len(openreview_papers)} abstracts ({openreview_count * 100 / len(openreview_papers):.1f}%)")
            self._save_progress_log(f"OpenReview complete: {openreview_count}/{len(openreview_papers)} abstracts")

        # Tier 2: Fetch from OpenAlex (batch) for papers with DOIs
        doi_papers = [p for p in papers if p.get('doi') and not p.get('abstract')]

        if doi_papers:
            utils.log(f"\nFetching abstracts from OpenAlex (batch processing)...")
            utils.log(f"  Papers to fetch: {len(doi_papers)}")
            self._save_progress_log(f"Starting OpenAlex batch fetch for {len(doi_papers)} papers")

            openalex_abstracts = self.fetch_abstracts_openalex(doi_papers)

            # Add abstracts from OpenAlex to papers
            abstracts_added = 0
            for paper in doi_papers:
                doi = paper.get('doi', '').replace('https://doi.org/', '').strip().lower()
                if doi in openalex_abstracts:
                    abstract, citation_count, source_id = openalex_abstracts[doi]
                    if abstract:
                        paper['abstract'] = abstract
                        paper['citation_count'] = citation_count
                        paper['abstract_source'] = 'openalex'
                        paper['source_id'] = source_id
                        abstracts_added += 1

            utils.log(f"  OpenAlex: {abstracts_added}/{len(doi_papers)} abstracts ({abstracts_added * 100 / len(doi_papers):.1f}%)")
            self._save_progress_log(f"OpenAlex complete: {abstracts_added}/{len(doi_papers)} abstracts")

            # Incremental save after OpenAlex batch
            if config.ENABLE_INCREMENTAL_SAVES and abstracts_added > 0:
                utils.log(f"  [INCREMENTAL SAVE] Saving progress after OpenAlex batch...")
                self.save_papers(papers)

        # Tier 3: OpenAlex title-based search for papers still missing abstracts
        # This is a fallback for papers where DOI lookup failed (e.g., IEEE CVPR papers)
        # Grouped with Tier 2 (OpenAlex DOI) for logical API grouping
        title_search_papers = [p for p in papers if p['abstract'] is None and p.get('title')]

        if title_search_papers:
            utils.log(f"\nFetching missing abstracts from OpenAlex (title search)...")
            utils.log(f"  Papers to fetch: {len(title_search_papers)}")
            utils.log(f"  Note: This is a fallback for papers where DOI lookup failed (e.g., IEEE papers)")
            self._save_progress_log(f"Starting OpenAlex title search for {len(title_search_papers)} papers")

            abstracts_fetched = 0
            for i, paper in enumerate(title_search_papers, 1):
                title = paper.get('title', '')

                if i % 50 == 0 or i == len(title_search_papers):
                    utils.log(f"  Progress: {i}/{len(title_search_papers)} | Fetched: {abstracts_fetched}")

                abstract, citation_count, openalex_id = self.fetch_abstract_openalex_by_title(title)

                if abstract:
                    paper['abstract'] = abstract
                    paper['citation_count'] = citation_count
                    paper['abstract_source'] = 'openalex_title'
                    paper['source_id'] = openalex_id
                    abstracts_fetched += 1

                # Progress logging and incremental saves
                if config.ABSTRACT_PROGRESS_LOG_INTERVAL > 0 and abstracts_fetched > 0 and abstracts_fetched % config.ABSTRACT_PROGRESS_LOG_INTERVAL == 0:
                    self._save_progress_log(f"OpenAlex title search: {abstracts_fetched} abstracts fetched (progress: {i}/{len(title_search_papers)})")

                    if config.ENABLE_INCREMENTAL_SAVES and abstracts_fetched % config.INCREMENTAL_SAVE_INTERVAL == 0:
                        utils.log(f"  [INCREMENTAL SAVE] Saving progress... ({abstracts_fetched} abstracts)")
                        self.save_papers(papers)

            utils.log(f"  OpenAlex (title search): {abstracts_fetched}/{len(title_search_papers)} abstracts ({abstracts_fetched * 100 / len(title_search_papers):.1f}%)")
            self._save_progress_log(f"OpenAlex title search complete: {abstracts_fetched}/{len(title_search_papers)} abstracts")

        # Tier 4: Fetch missing abstracts from Semantic Scholar
        # Slower API (1 req per 3 seconds), runs after exhausting both OpenAlex methods
        missing_papers = [p for p in papers if p['abstract'] is None and p.get('doi')]

        if missing_papers:
            utils.log(f"\nFetching missing abstracts from Semantic Scholar...")
            utils.log(f"  Papers to fetch: {len(missing_papers)}")
            self._save_progress_log(f"Starting Semantic Scholar fetch for {len(missing_papers)} papers")

            abstracts_fetched = 0
            for i, paper in enumerate(missing_papers, 1):
                doi = paper.get('doi', '').replace('https://doi.org/', '').strip()

                if i % 10 == 0 or i == len(missing_papers):
                    utils.log(f"  Progress: {i}/{len(missing_papers)}")

                abstract, citation_count, s2_paper_id = self.fetch_abstract_semantic_scholar(doi)

                if abstract:
                    paper['abstract'] = abstract
                    paper['citation_count'] = citation_count
                    paper['abstract_source'] = 'semantic_scholar'
                    paper['source_id'] = s2_paper_id
                    abstracts_fetched += 1

                # Progress logging and incremental saves
                if config.ABSTRACT_PROGRESS_LOG_INTERVAL > 0 and abstracts_fetched > 0 and abstracts_fetched % config.ABSTRACT_PROGRESS_LOG_INTERVAL == 0:
                    self._save_progress_log(f"Semantic Scholar: {abstracts_fetched} abstracts fetched (progress: {i}/{len(missing_papers)})")

                    if config.ENABLE_INCREMENTAL_SAVES and abstracts_fetched % config.INCREMENTAL_SAVE_INTERVAL == 0:
                        utils.log(f"  [INCREMENTAL SAVE] Saving progress... ({abstracts_fetched} abstracts)")
                        self.save_papers(papers)

            utils.log(f"  Semantic Scholar: {abstracts_fetched}/{len(missing_papers)} abstracts ({abstracts_fetched * 100 / len(missing_papers):.1f}%)")
            self._save_progress_log(f"Semantic Scholar complete: {abstracts_fetched}/{len(missing_papers)} abstracts")

        # Tier 5: Fetch from NeurIPS proceedings for papers without abstracts (NeurIPS 2020-2024 only)
        venue = self.conf_config.get('dblp_venue')
        if venue == 'neurips':
            neurips_proceedings_papers = [p for p in papers if p['abstract'] is None and p.get('neurips_proceedings_url')]

            if neurips_proceedings_papers:
                utils.log(f"\nFetching missing abstracts from NeurIPS Proceedings...")
                utils.log(f"  Papers to fetch: {len(neurips_proceedings_papers)}")
                utils.log(f"  Rate limit: {config.NEURIPS_PROCEEDINGS_RATE_LIMIT} requests/second ({1.0 / config.NEURIPS_PROCEEDINGS_RATE_LIMIT:.2f}s delay between requests)")
                utils.log(f"  Estimated time: ~{len(neurips_proceedings_papers) / config.NEURIPS_PROCEEDINGS_RATE_LIMIT / 60:.1f} minutes")
                self._save_progress_log(f"Starting NeurIPS Proceedings fetch for {len(neurips_proceedings_papers)} papers")

                abstracts_fetched = 0
                failed_count = 0
                start_time = time.time()

                for i, paper in enumerate(neurips_proceedings_papers, 1):
                    # Log progress every 10 papers
                    if i % 10 == 0 or i == len(neurips_proceedings_papers):
                        elapsed = time.time() - start_time
                        avg_time_per_paper = elapsed / i if i > 0 else 0
                        remaining_papers = len(neurips_proceedings_papers) - i
                        estimated_remaining_time = avg_time_per_paper * remaining_papers / 60  # in minutes
                        utils.log(f"  Progress: {i}/{len(neurips_proceedings_papers)} | "
                                 f"Success: {abstracts_fetched} | Failed: {failed_count} | "
                                 f"Elapsed: {elapsed/60:.1f}m | ETA: ~{estimated_remaining_time:.1f}m")

                    proceedings_url = paper.get('neurips_proceedings_url', '')
                    year = paper.get('year')
                    title = paper.get('title', 'Unknown')

                    # Extract hash and track from proceedings URL
                    paper_hash, track = self._extract_hash_from_proceedings_url(proceedings_url)

                    if paper_hash and track:
                        # Log the URL being fetched (for debugging)
                        if config.VERBOSE and i <= 5:  # Log first 5 URLs for debugging
                            utils.log(f"    Fetching: {proceedings_url[:80]}...")

                        abstract, citation_count, source_url = self.fetch_neurips_proceedings_abstract(
                            year, paper_hash, track
                        )

                        if abstract:
                            paper['abstract'] = abstract
                            paper['citation_count'] = citation_count  # Will be None
                            paper['abstract_source'] = 'neurips_proceedings'
                            paper['source_id'] = source_url
                            abstracts_fetched += 1

                            # Log successful fetches for first few papers
                            if config.VERBOSE and abstracts_fetched <= 3:
                                utils.log(f"    ✓ Successfully fetched abstract for: {title[:60]}...")
                        else:
                            failed_count += 1
                            # Log failures (helpful for debugging)
                            if config.VERBOSE and failed_count <= 5:
                                utils.log(f"    ✗ Failed to fetch abstract for: {title[:60]}...", 'WARNING')
                    else:
                        failed_count += 1
                        if config.VERBOSE and failed_count <= 5:
                            utils.log(f"    ✗ Could not extract hash from URL for: {title[:60]}...", 'WARNING')

                    # Progress logging and incremental saves
                    if config.ABSTRACT_PROGRESS_LOG_INTERVAL > 0 and abstracts_fetched > 0 and abstracts_fetched % config.ABSTRACT_PROGRESS_LOG_INTERVAL == 0:
                        self._save_progress_log(f"NeurIPS Proceedings: {abstracts_fetched} abstracts fetched (progress: {i}/{len(neurips_proceedings_papers)})")

                        if config.ENABLE_INCREMENTAL_SAVES and abstracts_fetched % config.INCREMENTAL_SAVE_INTERVAL == 0:
                            utils.log(f"  [INCREMENTAL SAVE] Saving progress... ({abstracts_fetched} abstracts)")
                            self.save_papers(papers)

                # Final statistics
                total_time = time.time() - start_time
                success_rate = abstracts_fetched / len(neurips_proceedings_papers) * 100 if len(neurips_proceedings_papers) > 0 else 0
                utils.log(f"\n  NeurIPS Proceedings Fetch Complete:")
                utils.log(f"    Total attempted: {len(neurips_proceedings_papers)}")
                utils.log(f"    Successfully fetched: {abstracts_fetched} ({success_rate:.1f}%)")
                utils.log(f"    Failed: {failed_count} ({failed_count * 100 / len(neurips_proceedings_papers):.1f}%)")
                utils.log(f"    Total time: {total_time / 60:.1f} minutes")
                utils.log(f"    Average time per paper: {total_time / len(neurips_proceedings_papers):.2f} seconds")
                self._save_progress_log(f"NeurIPS Proceedings complete: {abstracts_fetched}/{len(neurips_proceedings_papers)} abstracts ({success_rate:.1f}%)")

        # Calculate final statistics
        total_papers = len(papers)
        papers_with_abstracts = len([p for p in papers if p.get('abstract')])
        openreview_count = len([p for p in papers if p.get('abstract_source') == 'openreview'])
        openalex_count = len([p for p in papers if p.get('abstract_source') == 'openalex'])
        openalex_title_count = len([p for p in papers if p.get('abstract_source') == 'openalex_title'])
        semantic_scholar_count = len([p for p in papers if p.get('abstract_source') == 'semantic_scholar'])
        neurips_proceedings_count = len([p for p in papers if p.get('abstract_source') == 'neurips_proceedings'])

        utils.log("\n" + "=" * 50)
        utils.log("Abstract Fetching Summary:")
        utils.log("=" * 50)
        utils.log(f"Total papers: {total_papers}")
        utils.log(f"Papers with abstracts: {papers_with_abstracts} ({papers_with_abstracts * 100 / total_papers:.1f}%)")
        utils.log(f"  - From OpenReview: {openreview_count} ({openreview_count * 100 / total_papers:.1f}%)")
        utils.log(f"  - From OpenAlex (DOI): {openalex_count} ({openalex_count * 100 / total_papers:.1f}%)")
        if openalex_title_count > 0:
            utils.log(f"  - From OpenAlex (title): {openalex_title_count} ({openalex_title_count * 100 / total_papers:.1f}%)")
        utils.log(f"  - From Semantic Scholar: {semantic_scholar_count} ({semantic_scholar_count * 100 / total_papers:.1f}%)")
        if neurips_proceedings_count > 0:
            utils.log(f"  - From NeurIPS Proceedings: {neurips_proceedings_count} ({neurips_proceedings_count * 100 / total_papers:.1f}%)")
        utils.log(f"Papers without abstracts: {total_papers - papers_with_abstracts} ({(total_papers - papers_with_abstracts) * 100 / total_papers:.1f}%)")

        self._save_progress_log(f"Abstract enrichment complete: {papers_with_abstracts}/{total_papers} papers ({papers_with_abstracts * 100 / total_papers:.1f}%)")

        return papers

    def load_papers(self) -> List[Dict]:
        """
        Load papers from existing JSON file

        Returns:
            List[Dict]: List of papers loaded from JSON
        """
        json_file = config.get_raw_papers_file(self.conference_key)

        if not os.path.exists(json_file):
            utils.log(f"Error: File not found: {json_file}", 'ERROR')
            sys.exit(1)

        utils.log(f"Loading papers from: {json_file}")

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        papers = data.get('papers', [])
        utils.log(f"Loaded {len(papers)} papers from JSON file")

        return papers


def main():
    """Main execution function"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Fetch paper data from DBLP and enrich with abstracts'
    )
    parser.add_argument(
        '--refetch-abstracts',
        action='store_true',
        help='Load existing papers from JSON and only re-fetch missing abstracts (skip DBLP fetching)'
    )
    parser.add_argument(
        '--conference',
        type=str,
        default=None,
        help='Specify conference to fetch (e.g., neurips, cvpr, kdd). If not specified, uses DEFAULT_CONFERENCE from config'
    )
    args = parser.parse_args()

    utils.log("CS Conference Tag Cloud - Data Fetcher")
    utils.log("=" * 50)

    # Ensure directories exist
    config.ensure_directories()

    # Determine which conference to use
    conference_key = args.conference if args.conference else config.DEFAULT_CONFERENCE
    utils.log(f"Conference: {conference_key.upper()}")

    # Initialize fetcher
    fetcher = DBLPFetcher(conference_key)

    if args.refetch_abstracts:
        # Refetch abstracts mode: Load existing papers from JSON
        utils.log("\n[REFETCH MODE] Loading existing papers from JSON...")
        utils.log("Skipping DBLP fetching - will only re-fetch missing abstracts")
        utils.log("=" * 50)
        papers = fetcher.load_papers()

        # Log current state
        papers_with_abstracts = len([p for p in papers if p.get('abstract')])
        papers_without_abstracts = len(papers) - papers_with_abstracts
        utils.log(f"\nCurrent state:")
        utils.log(f"  Total papers: {len(papers)}")
        utils.log(f"  Papers with abstracts: {papers_with_abstracts} ({papers_with_abstracts * 100 / len(papers):.1f}%)")
        utils.log(f"  Papers missing abstracts: {papers_without_abstracts} ({papers_without_abstracts * 100 / len(papers):.1f}%)")
        utils.log(f"  Rate limit: {config.NEURIPS_PROCEEDINGS_RATE_LIMIT} requests/second")

    else:
        # Normal mode: Fetch papers from DBLP
        utils.log("\n[NORMAL MODE] Fetching papers from DBLP...")
        utils.log("=" * 50)

        # Fetch papers
        papers = fetcher.fetch_all_years()

        # Validate papers
        is_valid, message, stats = utils.validate_papers(papers)

        if not is_valid:
            utils.log(f"Validation failed: {message}", 'ERROR')
            utils.log(f"Stats: {stats}", 'ERROR')
            sys.exit(1)

        utils.log(f"Validation passed: {message}")

        # Save papers after DBLP phase (for recovery if abstract fetching fails)
        if config.ENABLE_INCREMENTAL_SAVES:
            utils.log("\n[INCREMENTAL SAVE] Saving papers after DBLP phase...")
            fetcher.save_papers(papers)
            fetcher._save_progress_log(f"DBLP phase complete: {len(papers)} papers saved")

    # Enrich papers with abstracts
    papers = fetcher.enrich_papers_with_abstracts(papers)

    # Save papers (final save)
    fetcher.save_papers(papers)

    # Print summary
    utils.summarize_data(papers, fetcher.conf_config['years'])

    utils.log("✓ Data fetching complete!")
    utils.log(f"Output: {config.get_raw_papers_file(config.DEFAULT_CONFERENCE)}")


if __name__ == '__main__':
    main()
