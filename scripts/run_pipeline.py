"""
Master pipeline script to run all data processing steps
"""

import sys
import time

# Import local modules
import config
import utils
from fetch_papers import DBLPFetcher
from extract_keywords import KeywordExtractor
from generate_data import DataGenerator


def run_pipeline(conference_key: str = None):
    """
    Run the complete data processing pipeline

    Steps:
    1. Fetch papers from DBLP API
    2. Extract keywords from paper titles
    3. Generate frontend-ready JSON data

    Args:
        conference_key (str): Conference key (default: from config)
    """
    start_time = time.time()

    if conference_key is None:
        conference_key = config.DEFAULT_CONFERENCE

    conf_config = config.get_conference_config(conference_key)

    utils.log("=" * 70)
    utils.log("CS CONFERENCE TAG CLOUD - FULL PIPELINE")
    utils.log("=" * 70)
    utils.log(f"Conference: {conf_config['name']} ({conf_config['full_name']})")
    utils.log(f"Years: {conf_config['years']}")
    utils.log(f"Categories: {conf_config['categories']}")
    utils.log("=" * 70)
    utils.log("")

    # Ensure directories exist
    config.ensure_directories()

    # ==================================================================
    # STEP 1: FETCH PAPERS FROM DBLP
    # ==================================================================
    utils.log("\n" + "=" * 70)
    utils.log("STEP 1: FETCHING PAPERS FROM DBLP API")
    utils.log("=" * 70)

    fetcher = DBLPFetcher(conference_key)
    papers = fetcher.fetch_all_years()

    # Validate papers
    is_valid, message, stats = utils.validate_papers(papers)
    if not is_valid:
        utils.log(f"Paper validation failed: {message}", 'ERROR')
        utils.log(f"Stats: {stats}", 'ERROR')
        sys.exit(1)

    utils.log(f"\n✓ Step 1 Complete: {message}")

    # Save papers
    fetcher.save_papers(papers)

    # Print summary
    utils.summarize_data(papers, conf_config['years'])

    # ==================================================================
    # STEP 2: EXTRACT KEYWORDS FROM TITLES
    # ==================================================================
    utils.log("\n" + "=" * 70)
    utils.log("STEP 2: EXTRACTING KEYWORDS FROM PAPER TITLES")
    utils.log("=" * 70)

    extractor = KeywordExtractor(conference_key)

    # Extract keywords
    keyword_stats = extractor.extract_keywords_from_papers(papers)

    # Filter by minimum frequency
    keyword_stats = extractor.filter_keywords(keyword_stats)

    # Get top keywords
    keyword_stats = extractor.get_top_keywords(keyword_stats)

    # Save intermediate results
    extractor.save_keywords(keyword_stats)

    utils.log(f"\n✓ Step 2 Complete: Extracted {keyword_stats['total_unique_keywords']} keywords")

    # ==================================================================
    # STEP 3: GENERATE FRONTEND DATA
    # ==================================================================
    utils.log("\n" + "=" * 70)
    utils.log("STEP 3: GENERATING FRONTEND-READY DATA")
    utils.log("=" * 70)

    generator = DataGenerator(conference_key)

    # Transform to frontend format
    frontend_data = generator.transform_to_frontend_format(keyword_stats)

    # Validate
    is_valid, message, stats = generator.validate_frontend_data(frontend_data)
    if not is_valid:
        utils.log(f"Frontend data validation failed: {message}", 'ERROR')
        sys.exit(1)

    # Save
    generator.save_frontend_data(frontend_data)

    utils.log(f"\n✓ Step 3 Complete: Generated frontend data with {stats['total_words']} keywords")

    # ==================================================================
    # PIPELINE COMPLETE
    # ==================================================================
    elapsed_time = time.time() - start_time

    utils.log("\n" + "=" * 70)
    utils.log("PIPELINE COMPLETE!")
    utils.log("=" * 70)
    utils.log(f"\nPipeline Summary:")
    utils.log(f"  - Conference: {conf_config['name']}")
    utils.log(f"  - Years: {conf_config['years']}")
    utils.log(f"  - Total papers: {len(papers)}")
    utils.log(f"  - Total keywords: {stats['total_words']}")
    utils.log(f"  - Top keyword: '{stats['top_keyword']}' ({stats['top_keyword_count']} occurrences)")
    utils.log(f"  - Execution time: {elapsed_time:.2f} seconds")
    utils.log(f"\nOutput Files:")
    utils.log(f"  - Raw papers: {config.get_raw_papers_file(config.DEFAULT_CONFERENCE)}")
    utils.log(f"  - Keywords (intermediate): {config.PROCESSED_KEYWORDS_FILE}")
    utils.log(f"  - Word cloud data (final): {config.FINAL_DATA_FILE}")
    utils.log(f"\nNext Steps:")
    utils.log(f"  1. Start local server: python3 -m http.server 8000")
    utils.log(f"  2. Open browser: http://localhost:8000")
    utils.log(f"  3. View the word cloud and test filters!")
    utils.log("=" * 70)


def main():
    """Main execution function"""
    # Parse command-line arguments (optional: specify conference)
    conference_key = None
    if len(sys.argv) > 1:
        conference_key = sys.argv[1]
        utils.log(f"Using conference from command line: {conference_key}")

    try:
        run_pipeline(conference_key)
    except KeyboardInterrupt:
        utils.log("\n\nPipeline interrupted by user", 'WARNING')
        sys.exit(1)
    except Exception as e:
        utils.log(f"\n\nPipeline failed with error: {e}", 'ERROR')
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()