"""
Fetch paper data from DBLP API for CS conferences
TODO:
    1. Edge case of keynotes/invited talks that is not started with "Keynote" is not elimited from the fetch results. Therefore
        the fetched results still have a little noise. Need to update this later.

"""

import requests
import time
from typing import List, Dict
import sys
from bs4 import BeautifulSoup
import re

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
            url = f"{config.DBLP_BASE_URL}/db/conf/{venue}/{venue}{year}{suffix}.html"

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

        for entry in entries:
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

                if url_elem:
                    # Look for DOI link
                    doi_link = url_elem.find('a', href=re.compile(r'doi\.org'))
                    if doi_link:
                        doi = doi_link.get('href', '')

                    # Look for DBLP record URL
                    dblp_link = url_elem.find('a', href=re.compile(r'dblp\.org/rec'))
                    if dblp_link:
                        paper_url = dblp_link.get('href', '')

                # Create paper dictionary
                paper = {
                    'title': title,
                    'year': year,
                    'authors': authors,
                    'venue': self.conf_config['name'],
                    'url': paper_url,
                    'doi': doi
                }

                papers.append(paper)

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
            filepath (str): Output file path (default: from config)
        """
        if filepath is None:
            filepath = config.RAW_PAPERS_FILE

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


def main():
    """Main execution function"""
    utils.log("CS Conference Tag Cloud - Data Fetcher")
    utils.log("=" * 50)

    # Ensure directories exist
    config.ensure_directories()

    # Initialize fetcher
    fetcher = DBLPFetcher(config.DEFAULT_CONFERENCE)

    # Fetch papers
    papers = fetcher.fetch_all_years()

    # Validate papers
    is_valid, message, stats = utils.validate_papers(papers)

    if not is_valid:
        utils.log(f"Validation failed: {message}", 'ERROR')
        utils.log(f"Stats: {stats}", 'ERROR')
        sys.exit(1)

    utils.log(f"Validation passed: {message}")

    # Save papers
    fetcher.save_papers(papers)

    # Print summary
    utils.summarize_data(papers, fetcher.conf_config['years'])

    utils.log("✓ Data fetching complete!")
    utils.log(f"Output: {config.RAW_PAPERS_FILE}")


if __name__ == '__main__':
    main()
