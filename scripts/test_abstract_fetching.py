"""
Test abstract fetching on a small sample of papers
"""

import json
import sys

# Import local modules
import config
import utils
from fetch_papers import DBLPFetcher

def main():
    """Test abstract fetching on 5 papers"""
    utils.log("Testing Abstract Fetching")
    utils.log("=" * 50)

    # Load existing papers
    with open(config.RAW_PAPERS_FILE, 'r') as f:
        data = json.load(f)
        all_papers = data['papers']

    utils.log(f"Loaded {len(all_papers)} papers from {config.RAW_PAPERS_FILE}")

    # Select 5 test papers (include some from 2025 and some from older years)
    test_papers = [
        all_papers[0],   # 2020 paper
        all_papers[500], # Mid-range
        all_papers[1000], # Mid-range
        all_papers[2500], # Probably 2025
        all_papers[-1],   # Last paper (definitely 2025)
    ]

    utils.log(f"\nSelected {len(test_papers)} test papers:")
    for i, paper in enumerate(test_papers, 1):
        utils.log(f"  {i}. {paper['year']}: {paper['title'][:60]}...")

    # Initialize fetcher
    fetcher = DBLPFetcher(config.DEFAULT_CONFERENCE)

    # Enrich test papers with abstracts
    enriched_papers = fetcher.enrich_papers_with_abstracts(test_papers)

    # Display results
    utils.log("\n" + "=" * 50)
    utils.log("Test Results:")
    utils.log("=" * 50)

    for i, paper in enumerate(enriched_papers, 1):
        utils.log(f"\nPaper {i}:")
        utils.log(f"  Title: {paper['title']}")
        utils.log(f"  Year: {paper['year']}")
        utils.log(f"  DOI: {paper.get('doi', 'N/A')}")
        utils.log(f"  Abstract Source: {paper.get('abstract_source', 'None')}")
        utils.log(f"  Citation Count: {paper.get('citation_count', 'N/A')}")

        if paper.get('abstract'):
            abstract_preview = paper['abstract'][:200] + "..." if len(paper['abstract']) > 200 else paper['abstract']
            utils.log(f"  Abstract: {abstract_preview}")
        else:
            utils.log(f"  Abstract: NOT FOUND")

    utils.log("\n✓ Test complete!")

if __name__ == '__main__':
    main()
