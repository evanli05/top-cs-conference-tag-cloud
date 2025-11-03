"""
Utility functions for CS Conference Tag Cloud
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List


def log(message: str, level: str = 'INFO'):
    """
    Print log message with timestamp

    Args:
        message (str): Message to log
        level (str): Log level (INFO, WARNING, ERROR)
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] [{level}] {message}")


def save_json(data: Any, filepath: str, pretty: bool = True):
    """
    Save data to JSON file

    Args:
        data: Data to save (must be JSON serializable)
        filepath (str): Path to output file
        pretty (bool): Whether to pretty-print JSON
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        log(f"Saved data to {filepath}")
    except Exception as e:
        log(f"Error saving JSON to {filepath}: {e}", 'ERROR')
        raise


def load_json(filepath: str) -> Any:
    """
    Load data from JSON file

    Args:
        filepath (str): Path to JSON file

    Returns:
        Loaded data
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        log(f"Loaded data from {filepath}")
        return data
    except FileNotFoundError:
        log(f"File not found: {filepath}", 'WARNING')
        return None
    except Exception as e:
        log(f"Error loading JSON from {filepath}: {e}", 'ERROR')
        raise


def clean_text(text: str) -> str:
    """
    Clean and normalize text

    Args:
        text (str): Text to clean

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove extra whitespace
    text = ' '.join(text.split())

    return text


def progress_bar(current: int, total: int, prefix: str = '', suffix: str = '', length: int = 50):
    """
    Display progress bar in console

    Args:
        current (int): Current iteration
        total (int): Total iterations
        prefix (str): Prefix string
        suffix (str): Suffix string
        length (int): Character length of bar
    """
    if total == 0:
        return

    percent = current / total
    filled_length = int(length * percent)
    bar = '█' * filled_length + '-' * (length - filled_length)

    print(f'\r{prefix} |{bar}| {percent:.1%} {suffix}', end='', flush=True)

    # Print newline on completion
    if current == total:
        print()


def rate_limit(last_request_time: float, min_delay: float = 1.0) -> float:
    """
    Enforce rate limiting between API requests

    Args:
        last_request_time (float): Timestamp of last request
        min_delay (float): Minimum delay between requests (seconds)

    Returns:
        float: Current timestamp after delay
    """
    if last_request_time > 0:
        elapsed = time.time() - last_request_time
        if elapsed < min_delay:
            time.sleep(min_delay - elapsed)

    return time.time()


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format

    Returns:
        str: Formatted timestamp (YYYY-MM-DD)
    """
    return datetime.now().strftime('%Y-%m-%d')


def validate_papers(papers: List[Dict]) -> tuple:
    """
    Validate paper data quality

    Args:
        papers (List[Dict]): List of paper dictionaries

    Returns:
        tuple: (is_valid, error_message, stats)
    """
    if not papers:
        return False, "No papers found", {}

    # Count papers with required fields
    valid_count = 0
    missing_title = 0
    missing_year = 0
    total = len(papers)

    years = []

    for paper in papers:
        has_title = 'title' in paper and paper['title']
        has_year = 'year' in paper and paper['year']

        if has_title and has_year:
            valid_count += 1
            years.append(paper['year'])
        else:
            if not has_title:
                missing_title += 1
            if not has_year:
                missing_year += 1

    stats = {
        'total': total,
        'valid': valid_count,
        'invalid': total - valid_count,
        'missing_title': missing_title,
        'missing_year': missing_year,
        'years': sorted(set(years)) if years else []
    }

    if valid_count == 0:
        return False, "No valid papers found", stats

    if valid_count < total * 0.9:  # More than 10% invalid
        return False, f"Too many invalid papers: {total - valid_count}/{total}", stats

    return True, "Validation passed", stats


def summarize_data(papers: List[Dict], years: List[int] = None):
    """
    Print summary statistics about paper data

    Args:
        papers (List[Dict]): List of paper dictionaries
        years (List[int]): Expected years
    """
    if not papers:
        log("No papers to summarize", 'WARNING')
        return

    total = len(papers)
    log(f"\n{'='*50}")
    log(f"Data Summary")
    log(f"{'='*50}")
    log(f"Total papers: {total}")

    # Count by year
    year_counts = {}
    for paper in papers:
        year = paper.get('year')
        if year:
            year_counts[year] = year_counts.get(year, 0) + 1

    log(f"\nPapers by year:")
    for year in sorted(year_counts.keys()):
        count = year_counts[year]
        log(f"  {year}: {count} papers")

    # Check for expected years
    if years:
        missing_years = set(years) - set(year_counts.keys())
        if missing_years:
            log(f"\nWarning: Missing data for years: {sorted(missing_years)}", 'WARNING')

    # Sample paper titles
    log(f"\nSample titles (first 3):")
    for i, paper in enumerate(papers[:3], 1):
        title = paper.get('title', 'N/A')
        year = paper.get('year', 'N/A')
        log(f"  {i}. [{year}] {title[:80]}...")

    log(f"{'='*50}\n")


if __name__ == '__main__':
    # Test utilities
    print("Testing utility functions...")

    # Test logging
    log("This is an info message", 'INFO')
    log("This is a warning", 'WARNING')
    log("This is an error", 'ERROR')

    # Test text cleaning
    test_text = "  MACHINE Learning:  A Novel  Approach  "
    cleaned = clean_text(test_text)
    print(f"\nCleaned text: '{cleaned}'")

    # Test progress bar
    print("\nProgress bar test:")
    for i in range(101):
        progress_bar(i, 100, prefix='Processing:', suffix='Complete')
        time.sleep(0.01)

    # Test timestamp
    print(f"\nCurrent timestamp: {get_current_timestamp()}")

    print("\nUtility tests complete!")
