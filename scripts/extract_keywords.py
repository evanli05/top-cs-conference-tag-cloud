"""
Extract keywords from paper titles for word cloud generation
"""

import re
from collections import Counter
from typing import List, Dict, Set
import sys

# Import local modules
import config
import utils


class KeywordExtractor:
    """Extract and process keywords from paper titles"""

    def __init__(self, conference_key: str = None):
        """
        Initialize keyword extractor

        Args:
            conference_key (str): Conference key (e.g., 'kdd')
        """
        self.conference_key = conference_key or config.DEFAULT_CONFERENCE
        self.conf_config = config.get_conference_config(self.conference_key)
        self.stopwords = config.STOPWORDS

        utils.log(f"Initialized Keyword Extractor for {self.conf_config['name']}")

    def extract_keywords_from_papers(self, papers: List[Dict]) -> Dict:
        """
        Extract keywords from all papers

        Args:
            papers (List[Dict]): List of paper dictionaries

        Returns:
            Dict: Keyword statistics with overall and per-year frequencies
        """
        utils.log(f"\nExtracting keywords from {len(papers)} papers...")

        # Initialize counters
        overall_counter = Counter()
        year_counters = {}

        # Process each paper
        for i, paper in enumerate(papers, 1):
            if i % 100 == 0:
                utils.progress_bar(
                    i, len(papers),
                    prefix='Progress:',
                    suffix=f'Processing paper {i}/{len(papers)}'
                )

            title = paper.get('title', '')
            year = paper.get('year')

            if not title or not year:
                continue

            # Extract keywords from title
            keywords = self._extract_keywords_from_title(title)

            # Update counters
            overall_counter.update(keywords)

            # Update year-specific counter
            if year not in year_counters:
                year_counters[year] = Counter()
            year_counters[year].update(keywords)

        utils.progress_bar(len(papers), len(papers), prefix='Progress:', suffix='Complete!')

        # Compile results
        results = {
            'overall': dict(overall_counter),
            'by_year': {year: dict(counter) for year, counter in year_counters.items()},
            'total_papers': len(papers),
            'total_unique_keywords': len(overall_counter)
        }

        utils.log(f"\nExtracted {len(overall_counter)} unique keywords")

        return results

    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """
        Extract keywords from a single paper title

        Args:
            title (str): Paper title

        Returns:
            List[str]: List of extracted keywords
        """
        keywords = []

        # Clean and normalize title
        title = title.lower()
        # Remove special characters but keep spaces and hyphens
        title = re.sub(r'[^\w\s\-]', ' ', title)
        # Normalize whitespace
        title = ' '.join(title.split())

        # Split into words
        words = title.split()

        # Extract unigrams (single words)
        if 1 in config.NGRAM_SIZES:
            for word in words:
                # Clean word (remove trailing hyphens, etc.)
                word = word.strip('-')

                # Apply filters
                if self._is_valid_keyword(word):
                    keywords.append(word)

        # Extract bigrams (two-word phrases)
        if 2 in config.NGRAM_SIZES:
            for i in range(len(words) - 1):
                word1 = words[i].strip('-')
                word2 = words[i + 1].strip('-')

                # Both words must be valid
                if self._is_valid_keyword(word1) and self._is_valid_keyword(word2):
                    bigram = f"{word1} {word2}"
                    keywords.append(bigram)

        # Extract trigrams (three-word phrases) if configured
        if 3 in config.NGRAM_SIZES:
            for i in range(len(words) - 2):
                word1 = words[i].strip('-')
                word2 = words[i + 1].strip('-')
                word3 = words[i + 2].strip('-')

                # All words must be valid
                if (self._is_valid_keyword(word1) and
                    self._is_valid_keyword(word2) and
                    self._is_valid_keyword(word3)):
                    trigram = f"{word1} {word2} {word3}"
                    keywords.append(trigram)

        return keywords

    def _is_valid_keyword(self, word: str) -> bool:
        """
        Check if a word is a valid keyword

        Args:
            word (str): Word to check

        Returns:
            bool: True if valid, False otherwise
        """
        # Check minimum length
        if len(word) < config.MIN_WORD_LENGTH:
            return False

        # Check maximum length
        if len(word) > config.MAX_WORD_LENGTH:
            return False

        # Check if it's a stopword
        if word in self.stopwords:
            return False

        # Must contain at least one letter
        if not re.search(r'[a-z]', word):
            return False

        # Reject words that are all numbers
        if word.isdigit():
            return False

        return True

    def filter_keywords(self, keyword_stats: Dict, min_frequency: int = None) -> Dict:
        """
        Filter keywords by minimum frequency

        Args:
            keyword_stats (Dict): Keyword statistics
            min_frequency (int): Minimum frequency threshold

        Returns:
            Dict: Filtered keyword statistics
        """
        if min_frequency is None:
            min_frequency = config.MIN_KEYWORD_FREQUENCY

        utils.log(f"\nFiltering keywords (min frequency: {min_frequency})...")

        overall = keyword_stats['overall']
        by_year = keyword_stats['by_year']

        # Filter overall keywords
        filtered_overall = {
            keyword: count
            for keyword, count in overall.items()
            if count >= min_frequency
        }

        # Filter year-specific keywords (keep only if in filtered_overall)
        filtered_by_year = {}
        for year, counter in by_year.items():
            filtered_by_year[year] = {
                keyword: count
                for keyword, count in counter.items()
                if keyword in filtered_overall
            }

        utils.log(f"Kept {len(filtered_overall)} keywords (removed {len(overall) - len(filtered_overall)})")

        return {
            'overall': filtered_overall,
            'by_year': filtered_by_year,
            'total_papers': keyword_stats['total_papers'],
            'total_unique_keywords': len(filtered_overall),
            'min_frequency': min_frequency
        }

    def get_top_keywords(self, keyword_stats: Dict, max_keywords: int = None) -> Dict:
        """
        Get top N most frequent keywords

        Args:
            keyword_stats (Dict): Keyword statistics
            max_keywords (int): Maximum number of keywords to return

        Returns:
            Dict: Top keywords with statistics
        """
        if max_keywords is None:
            max_keywords = config.MAX_KEYWORDS

        utils.log(f"\nSelecting top {max_keywords} keywords...")

        overall = keyword_stats['overall']
        by_year = keyword_stats['by_year']

        # Sort by frequency and get top N
        top_keywords = dict(
            sorted(overall.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        )

        # Filter year-specific data to only include top keywords
        filtered_by_year = {}
        for year, counter in by_year.items():
            filtered_by_year[year] = {
                keyword: count
                for keyword, count in counter.items()
                if keyword in top_keywords
            }

        utils.log(f"Selected {len(top_keywords)} top keywords")

        return {
            'overall': top_keywords,
            'by_year': filtered_by_year,
            'total_papers': keyword_stats['total_papers'],
            'total_unique_keywords': len(top_keywords),
            'min_frequency': keyword_stats.get('min_frequency', config.MIN_KEYWORD_FREQUENCY)
        }

    def save_keywords(self, keyword_stats: Dict, filepath: str = None):
        """
        Save keyword statistics to JSON file

        Args:
            keyword_stats (Dict): Keyword statistics
            filepath (str): Output file path
        """
        if filepath is None:
            filepath = config.PROCESSED_KEYWORDS_FILE

        # Add metadata
        data = {
            'metadata': {
                'conference': self.conf_config['name'],
                'full_name': self.conf_config['full_name'],
                'categories': self.conf_config['categories'],
                'years': self.conf_config['years'],
                'total_papers': keyword_stats['total_papers'],
                'total_unique_keywords': keyword_stats['total_unique_keywords'],
                'min_frequency': keyword_stats.get('min_frequency', config.MIN_KEYWORD_FREQUENCY),
                'max_keywords': config.MAX_KEYWORDS,
                'ngram_sizes': config.NGRAM_SIZES,
                'generated_at': utils.get_current_timestamp(),
            },
            'keywords': {
                'overall': keyword_stats['overall'],
                'by_year': keyword_stats['by_year']
            }
        }

        utils.save_json(data, filepath)
        utils.log(f"Saved keyword statistics to {filepath}")


def main():
    """Main execution function"""
    utils.log("CS Conference Tag Cloud - Keyword Extractor")
    utils.log("=" * 50)

    # Load papers from Step 2
    papers_data = utils.load_json(config.RAW_PAPERS_FILE)

    if not papers_data:
        utils.log(f"Failed to load papers from {config.RAW_PAPERS_FILE}", 'ERROR')
        utils.log("Please run fetch_papers.py first (Step 2)", 'ERROR')
        sys.exit(1)

    papers = papers_data.get('papers', [])

    if not papers:
        utils.log("No papers found in data file", 'ERROR')
        sys.exit(1)

    utils.log(f"Loaded {len(papers)} papers from {config.RAW_PAPERS_FILE}")

    # Initialize extractor
    extractor = KeywordExtractor(config.DEFAULT_CONFERENCE)

    # Extract keywords
    keyword_stats = extractor.extract_keywords_from_papers(papers)

    # Filter by minimum frequency
    keyword_stats = extractor.filter_keywords(keyword_stats)

    # Get top keywords
    keyword_stats = extractor.get_top_keywords(keyword_stats)

    # Save results
    extractor.save_keywords(keyword_stats)

    # Print summary
    utils.log(f"\n{'='*50}")
    utils.log(f"Keyword Extraction Summary")
    utils.log(f"{'='*50}")
    utils.log(f"Total papers processed: {keyword_stats['total_papers']}")
    utils.log(f"Total unique keywords: {keyword_stats['total_unique_keywords']}")
    utils.log(f"Min frequency threshold: {keyword_stats['min_frequency']}")
    utils.log(f"\nTop 10 keywords:")

    for i, (keyword, count) in enumerate(
        sorted(keyword_stats['overall'].items(), key=lambda x: x[1], reverse=True)[:10],
        1
    ):
        utils.log(f"  {i}. '{keyword}': {count} occurrences")

    utils.log(f"\n{'='*50}")
    utils.log("✓ Keyword extraction complete!")
    utils.log(f"Output: {config.PROCESSED_KEYWORDS_FILE}")


if __name__ == '__main__':
    main()