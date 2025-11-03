"""
Generate final word cloud data JSON for frontend consumption
"""

import sys
from typing import Dict, List

# Import local modules
import config
import utils


class DataGenerator:
    """Generate frontend-ready word cloud data"""

    def __init__(self, conference_key: str = None):
        """
        Initialize data generator

        Args:
            conference_key (str): Conference key (e.g., 'kdd')
        """
        self.conference_key = conference_key or config.DEFAULT_CONFERENCE
        self.conf_config = config.get_conference_config(self.conference_key)

        utils.log(f"Initialized Data Generator for {self.conf_config['name']}")

    def transform_to_frontend_format(self, keyword_data: Dict) -> Dict:
        """
        Transform intermediate keyword data to frontend format

        Args:
            keyword_data (Dict): Intermediate keyword statistics

        Returns:
            Dict: Frontend-ready word cloud data
        """
        utils.log("\nTransforming data to frontend format...")

        metadata = keyword_data['metadata']
        overall = keyword_data['keywords']['overall']
        by_year = keyword_data['keywords']['by_year']

        # Create words array for frontend
        words = []

        for keyword, total_count in overall.items():
            # Build year breakdown
            years_dict = {}
            for year in metadata['years']:
                year_str = str(year)
                # Get count for this year (0 if not present)
                # Try both integer and string keys
                year_data = by_year.get(year, by_year.get(str(year), {}))
                count = year_data.get(keyword, 0)
                if count > 0:  # Only include years with non-zero counts
                    years_dict[year_str] = count

            # Create word object
            word_obj = {
                'text': keyword,
                'value': total_count,
                'years': years_dict
            }

            words.append(word_obj)

        # Sort words by value (descending)
        words.sort(key=lambda x: x['value'], reverse=True)

        # Create final data structure
        frontend_data = {
            'metadata': {
                'conference': metadata['conference'],
                'full_name': metadata['full_name'],
                'categories': metadata['categories'],
                'years': metadata['years'],
                'total_papers': metadata['total_papers'],
                'total_keywords': len(words),
                'last_updated': metadata['generated_at']
            },
            'words': words
        }

        utils.log(f"Generated {len(words)} word objects for frontend")

        return frontend_data

    def validate_frontend_data(self, data: Dict) -> tuple:
        """
        Validate frontend data structure

        Args:
            data (Dict): Frontend data to validate

        Returns:
            tuple: (is_valid, error_message, stats)
        """
        utils.log("\nValidating frontend data...")

        # Check top-level structure
        if 'metadata' not in data or 'words' not in data:
            return False, "Missing 'metadata' or 'words' key", {}

        metadata = data['metadata']
        words = data['words']

        # Check metadata fields
        required_metadata = ['conference', 'years', 'total_papers', 'total_keywords', 'categories']
        for field in required_metadata:
            if field not in metadata:
                return False, f"Missing metadata field: {field}", {}

        # Check words structure
        if not isinstance(words, list):
            return False, "Words must be a list", {}

        if len(words) == 0:
            return False, "No words found", {}

        # Validate word objects
        invalid_words = []
        for i, word in enumerate(words):
            if not isinstance(word, dict):
                invalid_words.append(f"Word {i} is not a dict")
                continue

            # Check required fields
            if 'text' not in word or 'value' not in word or 'years' not in word:
                invalid_words.append(f"Word {i} missing required fields")
                continue

            # Check types
            if not isinstance(word['text'], str):
                invalid_words.append(f"Word {i} text is not string")
            if not isinstance(word['value'], int):
                invalid_words.append(f"Word {i} value is not int")
            if not isinstance(word['years'], dict):
                invalid_words.append(f"Word {i} years is not dict")

        if invalid_words:
            return False, f"Invalid word objects: {'; '.join(invalid_words[:5])}", {}

        # Calculate statistics
        total_occurrences = sum(word['value'] for word in words)
        avg_occurrences = total_occurrences / len(words) if words else 0

        stats = {
            'total_words': len(words),
            'total_occurrences': total_occurrences,
            'avg_occurrences': round(avg_occurrences, 2),
            'top_keyword': words[0]['text'] if words else None,
            'top_keyword_count': words[0]['value'] if words else 0
        }

        utils.log("Validation passed!")
        return True, "Valid", stats

    def save_frontend_data(self, data: Dict, filepath: str = None):
        """
        Save frontend data to JSON file

        Args:
            data (Dict): Frontend data
            filepath (str): Output file path
        """
        if filepath is None:
            filepath = config.FINAL_DATA_FILE

        utils.save_json(data, filepath)
        utils.log(f"Saved frontend data to {filepath}")


def main():
    """Main execution function"""
    utils.log("CS Conference Tag Cloud - Data Generator")
    utils.log("=" * 50)

    # Load intermediate keyword data from Step 3
    keyword_data = utils.load_json(config.PROCESSED_KEYWORDS_FILE)

    if not keyword_data:
        utils.log(f"Failed to load keywords from {config.PROCESSED_KEYWORDS_FILE}", 'ERROR')
        utils.log("Please run extract_keywords.py first (Step 3)", 'ERROR')
        sys.exit(1)

    utils.log(f"Loaded keyword data from {config.PROCESSED_KEYWORDS_FILE}")

    # Initialize generator
    generator = DataGenerator(config.DEFAULT_CONFERENCE)

    # Transform to frontend format
    frontend_data = generator.transform_to_frontend_format(keyword_data)

    # Validate data
    is_valid, message, stats = generator.validate_frontend_data(frontend_data)

    if not is_valid:
        utils.log(f"Validation failed: {message}", 'ERROR')
        sys.exit(1)

    # Save frontend data
    generator.save_frontend_data(frontend_data)

    # Print summary
    utils.log(f"\n{'='*50}")
    utils.log(f"Data Generation Summary")
    utils.log(f"{'='*50}")
    utils.log(f"Conference: {frontend_data['metadata']['conference']}")
    utils.log(f"Years: {frontend_data['metadata']['years']}")
    utils.log(f"Total papers: {frontend_data['metadata']['total_papers']}")
    utils.log(f"Total keywords: {frontend_data['metadata']['total_keywords']}")
    utils.log(f"Total occurrences: {stats['total_occurrences']}")
    utils.log(f"Average occurrences per keyword: {stats['avg_occurrences']}")
    utils.log(f"\nTop keyword: '{stats['top_keyword']}' ({stats['top_keyword_count']} occurrences)")

    utils.log(f"\n{'='*50}")
    utils.log("✓ Data generation complete!")
    utils.log(f"Output: {config.FINAL_DATA_FILE}")
    utils.log("\nYou can now open index.html in a browser to see the word cloud!")
    utils.log("Remember to start a local server: python3 -m http.server 8000")


if __name__ == '__main__':
    main()