"""
Fetch paper data from DBLP API for CS conferences
"""

import requests
import time
from typing import List, Dict
import sys

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
        Fetch papers for a specific conference and year

        Args:
            year (int): Year to fetch

        Returns:
            List[Dict]: List of paper dictionaries
        """
        venue = self.conf_config['dblp_venue']
        conference_name = self.conf_config['name']

        utils.log(f"Fetching {conference_name} {year} papers from DBLP...")

        # Build query parameters
        # DBLP search query: search for papers in this venue and year
        query = f"{venue} {year}"

        params = {
            'q': query,
            'format': 'json',
            'h': config.MAX_RESULTS_PER_REQUEST  # Maximum results
        }

        headers = {
            'User-Agent': config.USER_AGENT
        }

        try:
            # Rate limiting
            self.last_request_time = utils.rate_limit(
                self.last_request_time,
                config.REQUEST_DELAY
            )

            # Make API request
            response = requests.get(
                config.DBLP_API_BASE_URL,
                params=params,
                headers=headers,
                timeout=config.REQUEST_TIMEOUT
            )

            response.raise_for_status()

            # Parse response
            data = response.json()

            # Extract papers from response
            papers = self._parse_dblp_response(data, year)

            utils.log(f"Fetched {len(papers)} papers for {conference_name} {year}")

            return papers

        except requests.exceptions.RequestException as e:
            utils.log(f"Error fetching data for {year}: {e}", 'ERROR')
            return []
        except Exception as e:
            utils.log(f"Unexpected error for {year}: {e}", 'ERROR')
            return []

    def _parse_dblp_response(self, data: Dict, year: int) -> List[Dict]:
        """
        Parse DBLP API response and extract paper information

        Args:
            data (Dict): DBLP API response
            year (int): Expected year for filtering

        Returns:
            List[Dict]: List of paper dictionaries
        """
        papers = []

        # DBLP response structure: result -> hits -> hit[]
        result = data.get('result', {})
        hits = result.get('hits', {})
        hit_list = hits.get('hit', [])

        if not hit_list:
            utils.log(f"No hits found in DBLP response", 'WARNING')
            return papers

        # Process each hit
        for hit in hit_list:
            info = hit.get('info', {})

            # Extract paper information
            title = info.get('title', '')
            paper_year = info.get('year', '')
            venue = info.get('venue', '')
            authors = info.get('authors', {})
            url = info.get('url', '')
            doi = info.get('doi', '')

            # Clean title (remove HTML tags if any)
            if isinstance(title, str):
                # DBLP sometimes wraps titles in HTML tags
                import re
                title = re.sub(r'<[^>]+>', '', title)
                title = title.strip()

            # Filter out conference proceedings metadata entries and workshops/tutorials
            # These are NOT actual papers, but metadata about the conference itself
            title_lower = title.lower() if title else ''
            if title_lower:
                # Patterns indicating proceedings/metadata/workshops (not actual research papers)
                is_non_paper = any([
                    # Conference proceedings metadata
                    title_lower.startswith('kdd \'') or title_lower.startswith('kdd\''),  # "KDD '20:"
                    title_lower.startswith('proceedings of'),  # "Proceedings of..."
                    'virtual event' in title_lower and ',' in title,  # Has location/event info
                    # Check for date patterns (August 23-27, 2020)
                    re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d', title_lower),

                    # Workshop/tutorial/special day titles
                    'workshop on' in title_lower,  # "Workshop on..."
                    'workshop:' in title_lower,  # "Workshop: ..."
                    'workshop.' in title_lower,  # "...Workshop."
                    ' workshop' in title_lower and ('kdd' in title_lower or 'acm' in title_lower or 'international' in title_lower),
                    'international workshop' in title_lower,
                    title_lower.startswith('tutorial'),  # "Tutorial on..."
                    'tutorial:' in title_lower,  # "...Tutorial: ..."
                    'tutorial on' in title_lower,  # "Tutorial on..."
                    ' tutorial to' in title_lower,  # "A Tutorial to..."
                    ' tutorial.' in title_lower or title_lower.endswith(' tutorial'),  # "...Tutorial."
                    'a tutorial' in title_lower,  # "A Tutorial..."
                    'hands-on tutorial' in title_lower,
                    'kdd 20' in title_lower and 'tutorial' in title_lower,  # "KDD 2021 Tutorial..."
                    ' day:' in title_lower or title_lower.startswith('day '),  # "Health Day:", "Special Day"
                    'special day' in title_lower,
                    'kdd workshop' in title_lower,
                    'kdd tutorial' in title_lower,
                    'acm kdd' in title_lower and 'workshop' in title_lower,
                    'panel discussion' in title_lower,
                    'invited talk' in title_lower,
                    'dshealth' in title_lower,  # Specific workshop name
                    # Specific workshop names
                    'document intelligence workshop' in title_lower,
                    'aiot workshop' in title_lower,
                    'artificial intelligence of things' in title_lower and 'workshop' in title_lower,
                ])

                if is_non_paper:
                    continue

            # Parse year
            try:
                paper_year = int(paper_year)
            except (ValueError, TypeError):
                paper_year = None

            # Filter by year (must match exactly)
            if paper_year != year:
                continue

            # Filter by venue (should contain conference name)
            venue_lower = str(venue).lower()
            conf_name_lower = self.conf_config['name'].lower()

            # DBLP venue format is often "KDD" or "SIGKDD"
            if conf_name_lower not in venue_lower and \
               self.conf_config['dblp_venue'] not in venue_lower:
                continue

            # IMPORTANT: Filter out workshop papers and non-conference publications
            # Workshop venues have @ symbol (e.g., "DaSH@KDD", "AdKDD@KDD")
            # We only want main conference papers (venue == "KDD")
            if isinstance(venue, str) and '@' in venue:
                continue
            # Also filter if venue is a list (indicates workshop proceedings)
            if isinstance(venue, list):
                continue
            # Filter out SIGKDD Explorations (newsletter/magazine, not conference)
            if isinstance(venue, str) and 'Explor' in venue:
                continue

            # Parse authors
            author_list = []
            if isinstance(authors, dict):
                author_data = authors.get('author', [])
                if isinstance(author_data, list):
                    author_list = [
                        a.get('text', a) if isinstance(a, dict) else str(a)
                        for a in author_data
                    ]
                elif isinstance(author_data, str):
                    author_list = [author_data]
            elif isinstance(authors, list):
                author_list = [str(a) for a in authors]

            # Clean author names: remove DBLP disambiguation IDs (e.g., "John Doe 0001" -> "John Doe")
            author_list = [re.sub(r'\s+\d{4}$', '', author).strip() for author in author_list]

            # Create paper dictionary
            paper = {
                'title': title,
                'year': paper_year,
                'authors': author_list,
                'venue': venue,
                'url': url if url else '',
                'doi': doi if doi else ''
            }

            # Only add if has title
            if title:
                papers.append(paper)

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
