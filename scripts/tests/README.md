# Tests and Analysis Scripts

This folder (`scripts/tests/`) contains test scripts and analysis tools for the project.

## Analysis Scripts

### analyze_coverage.py

Analyzes paper and abstract coverage statistics for all conferences.

**Usage:**
```bash
python3 scripts/tests/analyze_coverage.py
```

**Output:**
- Prints detailed coverage statistics for each conference
- Generates year-by-year breakdown
- Saves results to `data/raw/coverage_stats.json`

**Example Output:**
```
Conference: KDD
Total Papers: 3,016
Papers with Abstracts: 3,010
Abstract Coverage: 99.8%
```

## Test Scripts

### test_abstract_fetching.py

Tests the abstract fetching system for a specific conference.

**Usage:**
```bash
python3 scripts/tests/test_abstract_fetching.py
```

**Purpose:**
- Tests multi-tier abstract fetching
- Validates API connections
- Checks rate limiting

### test_neurips_proceedings.py

Tests the NeurIPS proceedings scraper.

**Usage:**
```bash
python3 scripts/tests/test_neurips_proceedings.py
```

**Purpose:**
- Tests NeurIPS HTML parsing
- Validates hash extraction
- Checks abstract retrieval

### test_step2.sh

Tests Step 2 of the data pipeline (keyword extraction).

**Usage:**
```bash
bash scripts/tests/test_step2.sh
```

**Purpose:**
- Tests keyword extraction from paper titles
- Validates LLM API integration
- Checks output format

### test_step4.sh

Tests Step 4 of the data pipeline (data aggregation).

**Usage:**
```bash
bash scripts/tests/test_step4.sh
```

**Purpose:**
- Tests final data aggregation
- Validates output JSON structure
- Checks filtering logic

## Running All Tests

To run all tests sequentially:

```bash
# Analysis
python3 scripts/tests/analyze_coverage.py

# Abstract fetching tests
python3 scripts/tests/test_abstract_fetching.py
python3 scripts/tests/test_neurips_proceedings.py

# Pipeline tests
bash scripts/tests/test_step2.sh
bash scripts/tests/test_step4.sh
```

## Test Data

Test scripts use data from:
- `data/raw/` - Conference paper data
- `data/processed/` - Processed keyword data

## Adding New Tests

When adding new test scripts:
1. Place them in this `scripts/tests/` folder
2. Use descriptive names (e.g., `test_<feature>.py`)
3. Update this README with usage instructions
4. Ensure tests can run independently

## Notes

- All test scripts should be run from the project root directory
- Some tests require API keys (set in `.env` file)
- Tests may take several minutes depending on API rate limits
