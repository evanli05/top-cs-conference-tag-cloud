#!/usr/bin/env python3
"""
Test script for NeurIPS proceedings hybrid abstract fetcher
This script tests the new approach: DBLP for metadata + proceedings.nips.cc for abstracts
"""

import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional, Tuple

# Test configurations
NEURIPS_PROCEEDINGS_BASE_URL = "https://proceedings.nips.cc"
TEST_DBLP_URL = "https://dblp.org/db/conf/nips/neurips2022.html"


def extract_hash_from_proceedings_url(url: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract hash and track type from DBLP proceedings URL

    Args:
        url: DBLP proceedings URL

    Returns:
        Tuple of (hash, track_type) or (None, None) if not found

    Example:
        Input: "http://papers.nips.cc/paper_files/paper/2022/hash/002262941c9edfd472a79298b2ac5e17-Abstract-Conference.html"
        Output: ("002262941c9edfd472a79298b2ac5e17", "Conference")
    """
    match = re.search(
        r'/hash/([a-f0-9]{32})-Abstract-(Conference|Datasets_and_Benchmarks)',
        url
    )
    if match:
        return match.group(1), match.group(2)
    return None, None


def fetch_neurips_abstract_from_proceedings(
    year: int,
    paper_hash: str,
    track: str = "Conference"
) -> Optional[Dict[str, str]]:
    """
    Fetch abstract and metadata from NeurIPS proceedings website

    Args:
        year: Conference year (e.g., 2022)
        paper_hash: 32-character hexadecimal hash
        track: "Conference" or "Datasets_and_Benchmarks"

    Returns:
        Dict with keys: title, authors (list), abstract, pdf_url, source
        or None if fetch fails
    """
    # Build URL
    url = f"{NEURIPS_PROCEEDINGS_BASE_URL}/paper_files/paper/{year}/hash/{paper_hash}-Abstract-{track}.html"

    print(f"  Fetching: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract from meta tags (most reliable)
        title_tag = soup.find('meta', {'name': 'citation_title'})
        title = title_tag['content'] if title_tag else None

        author_tags = soup.find_all('meta', {'name': 'citation_author'})
        authors = [tag['content'] for tag in author_tags]

        pdf_tag = soup.find('meta', {'name': 'citation_pdf_url'})
        pdf_url = pdf_tag['content'] if pdf_tag else None

        # Extract abstract from HTML (no meta tag available)
        abstract = None
        abstract_h4 = soup.find('h4', string='Abstract')
        if abstract_h4:
            abstract_p = abstract_h4.find_next('p')
            if abstract_p:
                # Abstract is in nested <p> tags
                inner_p = abstract_p.find('p')
                if inner_p:
                    abstract = inner_p.get_text().strip()

        return {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'pdf_url': pdf_url,
            'source': 'neurips_proceedings'
        }

    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return None


def test_dblp_extraction():
    """Test extracting proceedings URLs from DBLP"""
    print("\n" + "="*60)
    print("TEST 1: Extract Proceedings URLs from DBLP")
    print("="*60)

    try:
        response = requests.get(TEST_DBLP_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        entries = soup.find_all('li', class_='entry')

        print(f"Found {len(entries)} papers on DBLP page")

        # Test first 5 papers
        test_papers = []
        for i, entry in enumerate(entries[:5], 1):
            title_elem = entry.find('span', class_='title')
            title = title_elem.text.strip() if title_elem else 'Unknown'

            # Find proceedings URL
            nav_elem = entry.find('nav', class_='publ')
            proceedings_url = None

            if nav_elem:
                links = nav_elem.find_all('a', href=True)
                for link in links:
                    href = link.get('href', '')
                    if 'proceedings.neurips.cc' in href or 'papers.nips.cc' in href:
                        proceedings_url = href
                        break

            print(f"\n  Paper {i}:")
            print(f"    Title: {title[:60]}...")

            if proceedings_url:
                paper_hash, track = extract_hash_from_proceedings_url(proceedings_url)
                print(f"    Proceedings URL: {proceedings_url[:80]}...")
                print(f"    Hash: {paper_hash}")
                print(f"    Track: {track}")

                if paper_hash and track:
                    test_papers.append({
                        'title': title,
                        'year': 2022,
                        'hash': paper_hash,
                        'track': track
                    })
            else:
                print(f"    No proceedings URL found!")

        return test_papers

    except Exception as e:
        print(f"Error: {e}")
        return []


def test_proceedings_fetch(test_papers):
    """Test fetching abstracts from proceedings"""
    print("\n" + "="*60)
    print("TEST 2: Fetch Abstracts from Proceedings")
    print("="*60)

    if not test_papers:
        print("No test papers available!")
        return

    for i, paper in enumerate(test_papers[:3], 1):  # Test first 3 papers
        print(f"\n  Test {i}: {paper['title'][:60]}...")

        result = fetch_neurips_abstract_from_proceedings(
            paper['year'],
            paper['hash'],
            paper['track']
        )

        if result:
            print(f"    ✓ Success!")
            print(f"    Title: {result['title']}")
            print(f"    Authors: {', '.join(result['authors'][:3])}{'...' if len(result['authors']) > 3 else ''}")
            print(f"    Abstract length: {len(result['abstract']) if result['abstract'] else 0} chars")
            if result['abstract']:
                print(f"    Abstract preview: {result['abstract'][:100]}...")
        else:
            print(f"    ✗ Failed to fetch")


if __name__ == "__main__":
    print("NeurIPS Proceedings Hybrid Fetcher Test")
    print("=" * 60)

    # Test 1: Extract proceedings URLs from DBLP
    test_papers = test_dblp_extraction()

    # Test 2: Fetch abstracts from proceedings
    test_proceedings_fetch(test_papers)

    print("\n" + "="*60)
    print("Test completed!")
    print("="*60)
