"""
Extract keywords from paper titles using LLM (Local Ollama or Gemini API)
"""

import re
import json
import time
import requests
from collections import Counter
from typing import List, Dict
import sys

# Import local modules
import config
import utils


class KeywordExtractor:
    """Extract and process keywords from paper titles using LLM"""

    def __init__(self, conference_key: str = None):
        """
        Initialize keyword extractor with LLM backend

        Args:
            conference_key (str): Conference key (e.g., 'kdd')
        """
        self.conference_key = conference_key or config.DEFAULT_CONFERENCE
        self.conf_config = config.get_conference_config(self.conference_key)
        self.backend = config.LLM_BACKEND

        utils.log(f"Initialized Keyword Extractor for {self.conf_config['name']}")
        utils.log(f"LLM Backend: {self.backend}")

        # Initialize backend
        if self.backend == 'local':
            self._init_local_llm()
        elif self.backend == 'gemini':
            self._init_gemini()
        else:
            self._handle_fatal_error(
                ValueError(f"Unknown backend: {self.backend}"),
                "Invalid LLM_BACKEND configuration"
            )

    def _init_local_llm(self):
        """Initialize local Ollama LLM"""
        self.ollama_url = f"{config.OLLAMA_BASE_URL}/api/generate"
        self.model_name = config.OLLAMA_MODEL

        # Test connection
        try:
            response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])

            # Check if model is available
            model_names = [m.get('name', '') for m in models]
            if not any(config.OLLAMA_MODEL in name for name in model_names):
                utils.log(f"⚠️  Model '{config.OLLAMA_MODEL}' not found in Ollama", 'WARNING')
                utils.log(f"Available models: {model_names}", 'WARNING')
                utils.log(f"\nPlease run: ollama pull {config.OLLAMA_MODEL}", 'ERROR')
                sys.exit(1)

            utils.log(f"✓ Connected to Ollama at {config.OLLAMA_BASE_URL}")
            utils.log(f"✓ Using model: {config.OLLAMA_MODEL}")
        except requests.exceptions.RequestException as e:
            self._handle_fatal_error(
                e,
                f"Failed to connect to Ollama at {config.OLLAMA_BASE_URL}. Make sure Ollama is running."
            )

    def _init_gemini(self):
        """Initialize Gemini API"""
        try:
            import google.generativeai as genai

            genai.configure(api_key=config.GEMINI_API_KEY)
            self.genai = genai
            self.model = genai.GenerativeModel(
                config.GEMINI_MODEL,
                generation_config={
                    "temperature": config.LLM_TEMPERATURE,
                    "response_mime_type": "application/json",
                }
            )
            utils.log(f"✓ Gemini API initialized successfully")
            utils.log(f"✓ Using model: {config.GEMINI_MODEL}")
        except Exception as e:
            self._handle_fatal_error(e, "Failed to initialize Gemini API")

    def extract_keywords_from_papers(self, papers: List[Dict]) -> Dict:
        """
        Extract keywords from all papers using LLM

        Args:
            papers (List[Dict]): List of paper dictionaries

        Returns:
            Dict: Keyword statistics with overall and per-year frequencies
        """
        utils.log(f"\nExtracting keywords from {len(papers)} papers using {self.backend.upper()} LLM...")

        return self._extract_keywords_llm(papers)

    def _extract_keywords_llm(self, papers: List[Dict]) -> Dict:
        """
        Extract keywords using LLM with batch processing

        Args:
            papers (List[Dict]): List of paper dictionaries

        Returns:
            Dict: Keyword statistics with overall and per-year frequencies
        """
        # Initialize counters
        overall_counter = Counter()
        year_counters = {}

        # Create batches
        batch_size = config.LLM_BATCH_SIZE
        total_batches = (len(papers) + batch_size - 1) // batch_size

        utils.log(f"Processing in {total_batches} batches ({batch_size} papers/batch)")
        if self.backend == 'local':
            utils.log(f"Estimated time: ~{int(total_batches * 2.2)} minutes (1.5-2 hours total)")

        start_time = time.time()

        # Process papers in batches
        for batch_idx in range(total_batches):
            start_idx = batch_idx * batch_size
            end_idx = min(start_idx + batch_size, len(papers))
            batch = papers[start_idx:end_idx]

            # Show progress
            utils.progress_bar(
                batch_idx, total_batches,
                prefix='Progress:',
                suffix=f'Batch {batch_idx + 1}/{total_batches} ({start_idx}-{end_idx})'
            )

            # Extract keywords for this batch
            try:
                batch_start = time.time()
                batch_results = self._extract_batch(batch)
                batch_time = time.time() - batch_start

                # Rate limiting for Gemini API (15 RPM = 4 seconds between requests)
                if self.backend == 'gemini' and batch_idx < total_batches - 1:
                    time.sleep(4.0)

                # Update counters
                for i, paper_keywords in enumerate(batch_results):
                    paper = batch[i]
                    year = paper.get('year')

                    # Update overall counter
                    overall_counter.update(paper_keywords)

                    # Update year-specific counter
                    if year not in year_counters:
                        year_counters[year] = Counter()
                    year_counters[year].update(paper_keywords)

                # Show timing info every 10 batches
                if (batch_idx + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / (batch_idx + 1)
                    remaining = (total_batches - batch_idx - 1) * avg_time
                    utils.log(f"\n  Batch {batch_idx + 1} took {batch_time:.1f}s | Avg: {avg_time:.1f}s/batch | ETA: {int(remaining/60)}m {int(remaining%60)}s")

            except Exception as e:
                utils.log(f"\n  Error processing batch {batch_idx + 1}: {e}", 'WARNING')
                utils.log(f"  Retrying batch...", 'WARNING')

                # Retry logic
                for retry in range(config.LLM_MAX_RETRIES):
                    try:
                        delay = config.LLM_RETRY_DELAY * (2 ** retry)
                        utils.log(f"  Retry {retry + 1}/{config.LLM_MAX_RETRIES} after {delay}s...", 'WARNING')
                        time.sleep(delay)

                        batch_results = self._extract_batch(batch)

                        # Update counters
                        for i, paper_keywords in enumerate(batch_results):
                            paper = batch[i]
                            year = paper.get('year')
                            overall_counter.update(paper_keywords)
                            if year not in year_counters:
                                year_counters[year] = Counter()
                            year_counters[year].update(paper_keywords)

                        utils.log(f"  ✓ Retry successful", 'WARNING')
                        break

                    except Exception as retry_error:
                        if retry == config.LLM_MAX_RETRIES - 1:
                            self._handle_fatal_error(
                                retry_error,
                                f"Failed to process batch {batch_idx + 1} after {config.LLM_MAX_RETRIES} retries"
                            )

        utils.progress_bar(total_batches, total_batches, prefix='Progress:', suffix='Complete!')

        total_time = time.time() - start_time
        utils.log(f"\n✓ Total processing time: {int(total_time/60)}m {int(total_time%60)}s")

        # Compile results
        results = {
            'overall': dict(overall_counter),
            'by_year': {year: dict(counter) for year, counter in year_counters.items()},
            'total_papers': len(papers),
            'total_unique_keywords': len(overall_counter)
        }

        utils.log(f"✓ Extracted {len(overall_counter)} unique keywords")

        return results

    def _extract_batch(self, papers: List[Dict]) -> List[List[str]]:
        """
        Extract keywords from a batch of papers using LLM

        Args:
            papers (List[Dict]): Batch of papers

        Returns:
            List[List[str]]: List of keyword lists for each paper
        """
        if self.backend == 'local':
            return self._extract_batch_ollama(papers)
        elif self.backend == 'gemini':
            return self._extract_batch_gemini(papers)

    def _extract_batch_ollama(self, papers: List[Dict]) -> List[List[str]]:
        """Extract keywords using local Ollama"""
        prompt = self._create_batch_prompt(papers)

        try:
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": config.LLM_TEMPERATURE,
                    }
                },
                timeout=config.LLM_REQUEST_TIMEOUT
            )
            response.raise_for_status()

            result = response.json()
            response_text = result.get('response', '')

            # Parse response
            batch_results = self._parse_llm_response(response_text, len(papers))
            return batch_results

        except Exception as e:
            raise Exception(f"Ollama API error: {str(e)}")

    def _extract_batch_gemini(self, papers: List[Dict]) -> List[List[str]]:
        """Extract keywords using Gemini API"""
        prompt = self._create_batch_prompt(papers)

        try:
            response = self.model.generate_content(prompt)
            batch_results = self._parse_llm_response(response.text, len(papers))
            return batch_results

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def _create_batch_prompt(self, papers: List[Dict]) -> str:
        """
        Create prompt for batch keyword extraction

        Args:
            papers (List[Dict]): Batch of papers

        Returns:
            str: Formatted prompt
        """
        # Build title list
        titles_json = []
        for i, paper in enumerate(papers):
            titles_json.append({
                "index": i,
                "title": paper.get('title', '')
            })

        prompt = f"""You are a keyword extraction expert for computer science research papers.

Task: Extract EXACTLY 3 specific technical keywords from each paper title below.

CRITICAL REQUIREMENTS:
1. You MUST provide exactly 3 keywords for each title (no more, no less)
2. Each result MUST include the "index" field matching the input
3. Prefer multi-word technical phrases over single words (e.g., "graph neural networks" not just "graph")
4. Avoid generic terms like "learning", "data", "model", "system", "network" when used alone
5. Focus on specific research methods, algorithms, application domains, or technical concepts
6. Output lowercase, normalize spaces (no extra whitespace)
7. Each keyword should be meaningful and specific to researchers in the field
8. If a title mentions specific techniques, prioritize those over general categories

Examples:
Title: "Deep Graph Neural Networks with Shallow Subgraph Samplers"
Keywords: ["graph neural networks", "subgraph sampling", "deep learning"]

Title: "Federated Learning with Differential Privacy Guarantees"
Keywords: ["federated learning", "differential privacy", "privacy preserving"]

Title: "Attention-based Recommendation Systems for E-commerce Applications"
Keywords: ["attention mechanism", "recommendation systems", "e-commerce"]

Title: "Contrastive Learning for Time Series Anomaly Detection"
Keywords: ["contrastive learning", "time series", "anomaly detection"]

Now extract keywords from these titles:

{json.dumps(titles_json, indent=2)}

Return a JSON object with this exact format:
{{
  "results": [
    {{"index": 0, "keywords": ["keyword1", "keyword2", "keyword3"]}},
    {{"index": 1, "keywords": ["keyword1", "keyword2", "keyword3"]}},
    ...
  ]
}}

Important: Return ONLY the JSON object, no additional text."""

        return prompt

    def _parse_llm_response(self, response_text: str, expected_count: int) -> List[List[str]]:
        """
        Parse JSON response from LLM with robust clipping

        Args:
            response_text (str): JSON response from API
            expected_count (int): Expected number of results (batch size)

        Returns:
            List[List[str]]: Parsed keyword lists (exactly expected_count items)
        """
        try:
            # Parse JSON
            data = json.loads(response_text)

            # Extract results
            if 'results' not in data:
                raise ValueError("Response missing 'results' key")

            results = data['results']

            # Log mismatch but continue processing
            if len(results) != expected_count:
                utils.log(f"  Warning: Expected {expected_count} results, got {len(results)}. Clipping to expected size.", 'WARNING')

            # Create index-to-result mapping
            result_map = {}
            for item in results:
                idx = item.get('index', -1)
                # Only accept valid indices
                if 0 <= idx < expected_count:
                    result_map[idx] = item.get('keywords', [])
                else:
                    utils.log(f"  Warning: Ignoring result with invalid index {idx}", 'WARNING')

            # Build final results array with exactly expected_count items
            batch_results = []
            for i in range(expected_count):
                if i in result_map:
                    keywords = result_map[i]
                else:
                    # Missing result - use empty list
                    utils.log(f"  Warning: Missing result for index {i}, using empty keywords", 'WARNING')
                    keywords = []

                # Normalize and clip to exactly 3 keywords
                normalized = []
                for kw in keywords[:3]:  # Take at most 3 keywords
                    # Clean and normalize
                    kw = str(kw).lower().strip()
                    # Normalize whitespace
                    kw = ' '.join(kw.split())
                    # Remove extra punctuation
                    kw = re.sub(r'[^\w\s-]', '', kw)

                    # Validate
                    if len(kw) >= config.MIN_WORD_LENGTH and len(kw) <= config.MAX_WORD_LENGTH:
                        normalized.append(kw)

                batch_results.append(normalized)

            # Verify we have exactly the expected count
            if len(batch_results) != expected_count:
                raise ValueError(f"Internal error: Got {len(batch_results)} results after clipping, expected {expected_count}")

            return batch_results

        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {response_text[:200]}...")
        except Exception as e:
            raise ValueError(f"Failed to process response: {e}")

    def _handle_fatal_error(self, error: Exception, context: str):
        """
        Handle fatal error and exit

        Args:
            error (Exception): The error that occurred
            context (str): Context description
        """
        utils.log("\n" + "=" * 70, 'ERROR')
        utils.log("⚠️  CAUTION: LLM Keyword Extraction Failed", 'ERROR')
        utils.log("=" * 70, 'ERROR')
        utils.log(f"\nError: {str(error)}", 'ERROR')
        utils.log(f"Context: {context}", 'ERROR')
        utils.log("\nPossible causes:", 'ERROR')
        if self.backend == 'local':
            utils.log("  1. Ollama not running (start with: ollama serve)", 'ERROR')
            utils.log(f"  2. Model not downloaded (run: ollama pull {config.OLLAMA_MODEL})", 'ERROR')
            utils.log("  3. Connection refused (check http://localhost:11434)", 'ERROR')
        else:
            utils.log("  1. Invalid or expired API key", 'ERROR')
            utils.log("  2. Rate limit exceeded", 'ERROR')
            utils.log("  3. Network connection issue", 'ERROR')
        utils.log("\nPlease check the error and try again.", 'ERROR')
        utils.log("=" * 70, 'ERROR')
        sys.exit(1)

    def filter_keywords(self, keyword_stats: Dict, min_frequency: int = None) -> Dict:
        """Filter keywords by minimum frequency"""
        if min_frequency is None:
            min_frequency = config.MIN_KEYWORD_FREQUENCY

        utils.log(f"\nFiltering keywords (min frequency: {min_frequency})...")

        overall = keyword_stats['overall']
        by_year = keyword_stats['by_year']

        filtered_overall = {
            keyword: count
            for keyword, count in overall.items()
            if count >= min_frequency
        }

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
        """Get top N most frequent keywords"""
        if max_keywords is None:
            max_keywords = config.MAX_KEYWORDS

        utils.log(f"\nSelecting top {max_keywords} keywords...")

        overall = keyword_stats['overall']
        by_year = keyword_stats['by_year']

        top_keywords = dict(
            sorted(overall.items(), key=lambda x: x[1], reverse=True)[:max_keywords]
        )

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
        """Save keyword statistics to JSON file"""
        if filepath is None:
            filepath = config.PROCESSED_KEYWORDS_FILE

        backend_info = f"{self.backend.upper()} LLM"
        if self.backend == 'local':
            backend_info += f" ({config.OLLAMA_MODEL})"
        else:
            backend_info += f" ({config.GEMINI_MODEL})"

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
                'extraction_method': backend_info,
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
    utils.log(f"CS Conference Tag Cloud - Keyword Extractor ({config.LLM_BACKEND.upper()} LLM)")
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
