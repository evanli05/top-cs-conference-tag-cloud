# Development Guide

This guide contains technical information for developers working on the Top CS Conference Tag Cloud project.

## Table of Contents

- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Local Development Setup](#local-development-setup)
- [Debugging & Troubleshooting](#debugging--troubleshooting)
- [Testing](#testing)
- [Development Roadmap](#development-roadmap)
- [Architecture Notes](#architecture-notes)

## Project Structure

```
top-cs-conference-tag-cloud/
├── data/
│   ├── sample/              # Sample data for frontend testing
│   │   └── wordcloud_sample.json
│   ├── raw/                 # Raw paper data from DBLP API
│   │   └── kdd_papers.json
│   └── processed/           # Generated word cloud data for frontend
│       └── wordcloud_data.json
├── scripts/                 # Python data collection and processing
│   ├── config.py           # Configuration settings
│   ├── fetch_papers.py     # Fetch papers from DBLP API
│   ├── extract_keywords.py # Extract keywords from paper titles
│   ├── generate_data.py    # Generate JSON for frontend consumption
│   ├── run_pipeline.py     # Master script to run full pipeline
│   ├── utils.py            # Shared utility functions
│   └── requirements.txt    # Python dependencies
├── css/
│   └── style.css           # Website styling
├── js/
│   ├── app.js              # Main application logic
│   └── wordcloud.js        # D3.js word cloud rendering
├── docs/
│   ├── DEVELOPMENT.md      # This file
│   └── CONTRIBUTING.md     # Contribution guidelines
├── index.html              # Main webpage
├── .gitignore
└── README.md
```

### Key Files

- **index.html**: Main entry point, contains HTML structure
- **js/app.js**: Application logic, data loading, filtering
- **js/wordcloud.js**: D3.js word cloud visualization implementation
- **css/style.css**: All styling using CSS custom properties for theming
- **scripts/run_pipeline.py**: Master script to run entire data pipeline
- **data/processed/wordcloud_data.json**: Production data consumed by frontend

## Technology Stack

### Frontend

- **HTML5, CSS3, JavaScript (ES6+)**
- **D3.js v7** with d3-cloud for word cloud visualization
- **Vanilla JavaScript** (no framework dependencies)
- **Responsive design** with CSS Grid and Flexbox
- **Modern CSS** with custom properties (variables) for theming

### Backend/Data Processing

- **Python 3.8+**
- **requests** library for DBLP API calls
- **beautifulsoup4** for HTML parsing
- **google-generativeai** for LLM-based keyword extraction
- **Native Python** for text processing
- **JSON** for data storage

### Data Source

- [DBLP Computer Science Bibliography](https://dblp.org/) - Computer science bibliography database
- Web scraping from DBLP HTML pages (no official API endpoint)

### Hosting

- **GitHub Pages** (static site hosting)

## Local Development Setup

### Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Safari)
- Git for version control
- Internet connection for fetching data from DBLP

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/top-cs-conference-tag-cloud.git
   cd top-cs-conference-tag-cloud
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r scripts/requirements.txt
   ```

3. **Set up Gemini API key (for keyword extraction):**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

### Running the Development Server

**Important**: You MUST use a local web server to avoid CORS (Cross-Origin Resource Sharing) errors when loading JSON data files.

**Why is this needed?**
- Browsers block `fetch()` requests from `file://` URLs for security reasons
- When you open `index.html` directly (double-click or `open index.html`), the browser uses the `file://` protocol
- This causes the error: "Failed to load data" in the word cloud section

**Start a local web server:**

```bash
# Navigate to project directory
cd top-cs-conference-tag-cloud

# Start Python's built-in HTTP server on port 8000
python3 -m http.server 8000

# Server output:
# Serving HTTP on :: port 8000 (http://[::]:8000/) ...

# Open browser and visit:
# http://localhost:8000
```

**To stop the server:**
```bash
# Press Ctrl+C in the terminal
```

**Alternative servers:**
```bash
# PHP (if installed)
php -S localhost:8000

# Node.js (if installed)
npx http-server -p 8000

# VS Code Live Server extension
# Right-click index.html → "Open with Live Server"
```

### Data Pipeline

To fetch and process conference data:

```bash
# Run the complete pipeline
python scripts/run_pipeline.py
```

This will:
1. Fetch papers from DBLP for KDD (2020-2025)
2. Extract keywords from paper titles using Gemini LLM
3. Calculate keyword frequencies per year
4. Generate `data/processed/wordcloud_data.json`

**Individual steps:**

```bash
# Step 1: Fetch raw papers from DBLP
python scripts/fetch_papers.py

# Step 2: Extract keywords using LLM
python scripts/extract_keywords.py

# Step 3: Generate final JSON for frontend
python scripts/generate_data.py
```

## Debugging & Troubleshooting

### Common Issues and Solutions

**Issue 1: "Failed to load data" or "Failed to fetch"**
- **Cause**: Opening HTML file directly without a web server
- **Solution**: Use `python3 -m http.server 8000` and visit `http://localhost:8000`

**Issue 2: Word cloud doesn't update when changing JSON file**
- **Cause**: Browser cache
- **Solution**: Hard refresh (Ctrl+Shift+R on Windows/Linux, Cmd+Shift+R on Mac)

**Issue 3: Port 8000 already in use**
- **Cause**: Another server is using port 8000
- **Solution**: Use a different port: `python3 -m http.server 8001`

**Issue 4: Console shows "d3 is not defined"**
- **Cause**: D3.js CDN failed to load (network issue)
- **Solution**: Check internet connection and refresh page

**Issue 5: "Cannot set properties of null"**
- **Cause**: JavaScript trying to access DOM elements that don't exist
- **Solution**: Check browser console for specific element IDs, ensure HTML structure matches JS expectations

**Issue 6: Gemini API rate limit errors**
- **Cause**: Exceeding 15 requests per minute for gemini-2.5-flash-lite
- **Solution**: Script automatically rate-limits (4 seconds between requests), wait for it to complete

### Browser Developer Tools

Open Developer Tools to debug:
- **Chrome/Edge**: F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
- **Firefox**: F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)
- **Safari**: Cmd+Option+I (must enable Developer menu first)

**Useful console commands:**
```javascript
// Check if data loaded
console.log(window.app.data);

// Check current filters
console.log(window.app.filters);

// Manually apply filters
window.app.applyFilters();

// Check word cloud instance
console.log(window.wordCloudInstance);

// Reload word cloud
window.wordCloudInstance.resize();
```

### Inspecting Network Requests

1. Open Developer Tools → Network tab
2. Refresh page
3. Look for `wordcloud_data.json` request
4. Check:
   - Status code (should be 200)
   - Response preview (should show valid JSON)
   - Headers (content-type should be application/json)

## Testing

### Testing Checklist for Local Development

- [ ] Start local server: `python3 -m http.server 8000`
- [ ] Open browser to `http://localhost:8000`
- [ ] Check browser console for errors (should be none)
- [ ] Verify word cloud renders with sample data
- [ ] Test year filter (select different years)
- [ ] Test category filter (Data Mining, ML, AI, etc.)
- [ ] Test conference filter (KDD, future conferences)
- [ ] Test reset filters button
- [ ] Test hover tooltips on words (should show frequency breakdown)
- [ ] Test responsive design (resize browser window)
- [ ] Test on mobile device or browser emulation
- [ ] Verify tooltip positioning at screen edges

### Functional Testing

**Word Cloud Rendering:**
- [ ] Words appear sized by frequency
- [ ] Color scheme is visually appealing
- [ ] Layout is balanced (no overlap)
- [ ] Animation is smooth

**Filters:**
- [ ] Year filter updates word cloud correctly
- [ ] Category filter works (when multiple conferences added)
- [ ] Conference filter works
- [ ] Reset button clears all filters
- [ ] Multiple filters work together

**Interactive Features:**
- [ ] Hover shows tooltip with accurate data
- [ ] Tooltip follows mouse intelligently
- [ ] Tooltip stays on screen (edge detection works)
- [ ] Click on word logs to console (future: show papers)

### Data Quality Testing

- [ ] Keywords are relevant and meaningful
- [ ] No stopwords or generic terms (the, and, using, etc.)
- [ ] Frequency counts are accurate
- [ ] Year breakdowns sum to total value
- [ ] No duplicate keywords
- [ ] Keywords are lowercase and normalized

### Cross-browser Testing

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

### Performance Testing

- [ ] Page load time < 2 seconds
- [ ] Filter updates < 500ms
- [ ] Smooth animations (60fps)
- [ ] No memory leaks (check in long sessions)
- [ ] JSON file size < 500KB

## Development Roadmap

### Phase 1: Foundation ✅ COMPLETE

- [x] Project setup and planning
- [x] Minimal frontend with sample data
- [x] DBLP data fetching for KDD
- [x] LLM-based keyword extraction pipeline
- [x] Data generation and integration
- [x] Responsive design implementation
- [x] Tooltip positioning improvements

### Phase 2: Enhancement (In Progress)

- [ ] Dark mode support
- [ ] Multi-year comparison view
- [ ] Trending topics (words increasing over time)
- [ ] Click on keywords to see paper list
- [ ] Export word cloud as image
- [ ] Search functionality for keywords
- [ ] Animated transitions between filter states

### Phase 3: Expansion

- [ ] Add more conferences (IJCAI, NeurIPS, ICLR, etc.)
- [ ] Cross-conference comparison view
- [ ] Topic clustering and categorization
- [ ] Historical trend analysis (2015-2025)
- [ ] Author network visualization
- [ ] Research area recommendations

### Phase 4: Advanced Features

- [ ] Real-time data updates (webhooks)
- [ ] User accounts and favorites
- [ ] Custom word cloud creation
- [ ] API for programmatic access
- [ ] Integration with paper databases (arXiv, ACM DL)

## Architecture Notes

### Data Flow

```
DBLP Website
    ↓
fetch_papers.py (web scraping)
    ↓
data/raw/kdd_papers.json
    ↓
extract_keywords.py (LLM extraction)
    ↓
data/processed/keywords_intermediate.json
    ↓
generate_data.py (aggregation)
    ↓
data/processed/wordcloud_data.json
    ↓
Frontend (D3.js visualization)
```

### Frontend Architecture

**app.js** (Application Logic):
- Loads data from JSON
- Manages filter state
- Handles user interactions
- Updates word cloud visualization

**wordcloud.js** (Visualization):
- Creates D3.js word cloud layout
- Renders SVG elements
- Handles tooltips
- Manages responsiveness

**CSS Variables System**:
```css
:root {
  --color-primary: #2563eb;
  --color-bg: #ffffff;
  --spacing-md: 1.5rem;
  /* ... more variables */
}
```
This makes theming and dark mode implementation straightforward.

### Backend Architecture

**config.py**:
- Centralized configuration
- API settings (Gemini, DBLP)
- Stopwords and filtering rules
- Conference definitions

**fetch_papers.py**:
- Multi-part conference support
- Rate limiting (1 second between requests)
- HTML parsing with BeautifulSoup
- Error handling and retries

**extract_keywords.py**:
- Batch processing (50 papers per request)
- LLM-based extraction (Gemini 2.5 Flash Lite)
- Rate limiting (4 seconds = 15 RPM)
- Robust error handling with clipping

**generate_data.py**:
- Keyword frequency aggregation
- Year-wise breakdown
- Top N selection (200 keywords)
- Metadata generation

### LLM Integration

**Why LLM-based extraction?**
- Traditional NLP (TF-IDF, KeyBERT) extracts too many generic terms
- LLM understands semantic meaning and research context
- Can identify multi-word phrases (e.g., "graph neural networks")
- Filters out stopwords intelligently

**Gemini 2.5 Flash Lite Settings:**
- Model: `gemini-2.5-flash-lite`
- Rate limits: 15 RPM, 250K TPM, 1K RPD
- Batch size: 50 papers per request
- Temperature: 0.0 (deterministic)
- Keywords per title: exactly 3

**Prompt Engineering:**
- Explicit JSON schema in prompt
- Index-based result mapping (prevents misalignment)
- Clear examples for few-shot learning
- Emphasis on multi-word phrases

### Performance Optimizations

**Frontend:**
- Limit to top 100 words in visualization
- Debounced resize handling (250ms)
- CSS animations (GPU-accelerated)
- Lazy loading for future features

**Backend:**
- Batch API requests
- Rate limiting to avoid API errors
- Caching with JSON files
- Incremental updates (only new years)

### Abstract Fetching System

**Overview:**
The project uses a multi-tier approach (4 tiers) to enrich paper data with abstracts, supporting DOI-based papers, OpenReview-based conferences, and conference-specific proceedings websites. The system automatically detects the paper source and uses the appropriate API or fetcher.

**Why Abstracts?**
- Improves keyword extraction quality
- Provides richer context for research trends
- Enables future features (semantic search, clustering)
- Adds citation counts for impact analysis

#### Architecture

**Tier 0: OpenReview ID Search (For OpenReview-based Conferences)**
- **Purpose**: Find OpenReview forum IDs by paper title search
- **Use Case**: Papers with OpenReview URLs but missing forum IDs
- **Coverage**: Supplements Tier 1 for OpenReview conferences
- **Speed**: ~1 second per paper (rate limited)
- **API**: OpenReview search API

**Tier 1: OpenReview API (For OpenReview-based Conferences)**
- **Purpose**: Fetch abstracts for conferences using OpenReview platform (ICLR, ICML)
- **Detection**: Automatic detection based on OpenReview URL in DBLP HTML
- **Coverage**: ~100% for OpenReview-hosted conferences
- **Speed**: ~1 second per paper (rate limited)
- **Rate Limit**: 1 request per second (polite rate limiting)
- **API Versions**:
  - API v1 for conferences 2023 and earlier
  - API v2 for conferences 2024 and later
- **Data Format**: Plain text abstracts and TL;DR summaries

**Tier 2: OpenAlex API (Primary for DOI-based Papers)**
- **Purpose**: Batch fetching for high-speed processing
- **Coverage**: ~92% of papers (lower for recent publications)
- **Speed**: ~5 minutes for 3,000 papers
- **Batch Size**: 100 DOIs per request
- **Rate Limit**: 10 requests/second (polite pool with mailto parameter)
- **Data Format**: Inverted index (word → positions)

**Tier 3: Semantic Scholar API (Fallback for DOI-based Papers)**
- **Purpose**: Fill gaps from OpenAlex
- **Coverage**: ~90%+ of missing papers
- **Speed**: ~3 seconds per paper
- **Rate Limit**: 1 request per 3 seconds (free tier)
- **Data Format**: Plain text abstracts

**Tier 4: NeurIPS Proceedings (Custom Fetcher for NeurIPS 2020-2024)**
- **Purpose**: Direct HTML parsing from proceedings.neurips.cc
- **Use Case**: NeurIPS 2020-2024 papers (before OpenReview migration)
- **Coverage**: ~60-70% (only papers with proceedings URLs)
- **Speed**: ~1-2 seconds per paper (rate limited)
- **Rate Limit**: 1 request per second (polite rate limiting)
- **Data Format**: Plain text abstracts extracted from HTML
- **Hash Extraction**: Extracts 32-character hexadecimal hashes from DBLP proceedings URLs
- **Tracks Supported**: "Conference" and "Datasets_and_Benchmarks"

**Combined Coverage**: 95-99% of all papers

#### Implementation Details

**File**: `scripts/fetch_papers.py`

**Key Methods**:

1. **`enrich_papers_with_abstracts(papers)`**
   - Main orchestration method for multi-tier approach
   - Tier 0: Searches OpenReview by title for papers with OpenReview URLs but missing forum IDs
   - Tier 1: Fetches from OpenReview for papers with `openreview_id`
   - Tier 2: Calls OpenAlex for bulk DOI-based fetching
   - Tier 3: Falls back to Semantic Scholar for missing DOI abstracts
   - Tier 4: Fetches from NeurIPS Proceedings for NeurIPS 2020-2024 papers with proceedings URLs
   - Returns papers with abstract fields added

2. **`_extract_openreview_id(url)`**
   - Extracts OpenReview forum ID from URL
   - Parses URL parameter: `openreview.net/forum?id=XXXXX`
   - Returns forum ID or None

3. **`fetch_abstract_openreview(forum_id, year, venue)`**
   - Single OpenReview paper lookup
   - Automatically selects API version based on year:
     - API v1 for years ≤ 2023
     - API v2 for years ≥ 2024
   - Extracts abstract or TL;DR from response
   - Rate-limited with 1-second delay
   - Returns (abstract, citation_count, forum_id) tuple

4. **`fetch_abstracts_openalex(papers)`**
   - Extracts DOIs from papers
   - Batches into groups of 100
   - Queries OpenAlex with pipe-separated DOI filter
   - Converts inverted index to plain text
   - Returns DOI → (abstract, citation_count, source_id) mapping

5. **`fetch_abstract_semantic_scholar(doi)`**
   - Single DOI lookup
   - Rate-limited with 3-second delay
   - Returns (abstract, citation_count, s2_paper_id) tuple
   - Handles 404 gracefully (paper not found)

6. **`reconstruct_abstract_from_inverted_index(inv_index)`**
   - Converts OpenAlex inverted index to plain text
   - Maps positions to words
   - Sorts by position and joins

7. **`_extract_hash_from_proceedings_url(url)`**
   - Extracts 32-character hexadecimal hash and track type from DBLP proceedings URLs
   - Parses URL pattern: `papers.nips.cc/paper_files/paper/{year}/hash/{hash}-Abstract-{track}.html`
   - Tracks supported: "Conference", "Datasets_and_Benchmarks"
   - Returns (hash, track_type) tuple or (None, None) if not found

8. **`fetch_neurips_proceedings_abstract(year, paper_hash, track)`**
   - Fetches abstract directly from proceedings.neurips.cc
   - Constructs URL from year, hash, and track type
   - Parses HTML to extract title, authors, abstract, PDF URL
   - Rate-limited with 1-second delay
   - Returns dict with abstract, source='neurips_proceedings', and metadata

#### Data Structure

**Paper Object (after enrichment)**:
```python
{
    'title': str,
    'year': int,
    'authors': [str],
    'venue': str,
    'url': str,                           # DBLP record URL
    'doi': str,                           # DOI URL (for DOI-based papers)
    'openreview_url': str,                # OpenReview URL (for OpenReview papers)
    'openreview_id': str or None,         # OpenReview forum ID
    'neurips_proceedings_url': str or None,  # NeurIPS proceedings URL (for NeurIPS 2020-2024)
    # ENRICHED FIELDS:
    'abstract': str or None,              # Plain text abstract
    'abstract_source': str or None,       # 'openreview', 'openalex', 'semantic_scholar', 'neurips_proceedings', or None
    'citation_count': int or None,        # Citation count from API (None for OpenReview/NeurIPS)
    'source_id': str or None              # Forum ID, OpenAlex ID, S2 paper ID, or None
}
```

#### API Endpoints

**OpenReview API v1** (for conferences 2023 and earlier):
```
GET https://api.openreview.net/notes?id={forum_id}
Response: { "notes": [{ "content": { "abstract": "...", "TL;DR": "..." } }] }
```

**OpenReview API v2** (for conferences 2024 and later):
```
GET https://api2.openreview.net/notes/{forum_id}
Response: { "content": { "abstract": "...", "TL;DR": "..." } }
```

**OpenAlex**:
```
GET https://api.openalex.org/works
Parameters:
  - filter: "doi:DOI1|DOI2|...|DOI100"
  - per-page: 100
  - mailto: yli05@yahoo.com (for polite pool)
```

**Semantic Scholar**:
```
GET https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}
Parameters:
  - fields: "abstract,citationCount"
```

**NeurIPS Proceedings**:
```
GET https://proceedings.neurips.cc/paper_files/paper/{year}/hash/{hash}-Abstract-{track}.html
Example: https://proceedings.neurips.cc/paper_files/paper/2022/hash/002262941c9edfd472a79298b2ac5e17-Abstract-Conference.html
Tracks: "Conference", "Datasets_and_Benchmarks"
Method: HTML parsing with BeautifulSoup
  - Meta tags: citation_title, citation_author, citation_pdf_url
  - Abstract: <h4>Abstract</h4> followed by <p><p>text</p></p>
```

#### Configuration

**File**: `scripts/config.py`

```python
# OpenReview API Configuration
OPENREVIEW_API_V1_URL = "https://api.openreview.net"
OPENREVIEW_API_V2_URL = "https://api2.openreview.net"
OPENREVIEW_RATE_LIMIT = 1.0  # 1 request per second
OPENREVIEW_TIMEOUT = 10
OPENREVIEW_API_V2_YEAR_THRESHOLD = 2024  # Conferences from 2024+ use API v2

# Map conferences to OpenReview venue IDs
# Note: NeurIPS 2020-2024 use custom Tier 4 fetcher (proceedings.neurips.cc)
# NeurIPS 2025+ may use OpenReview (to be determined)
OPENREVIEW_VENUES = {
    'iclr': 'ICLR.cc',
    'icml': 'ICML.cc',
}

# NeurIPS Proceedings Configuration (Tier 4)
NEURIPS_PROCEEDINGS_BASE_URL = "https://proceedings.neurips.cc"
NEURIPS_PROCEEDINGS_RATE_LIMIT = 1.0  # 1 request per second
NEURIPS_PROCEEDINGS_TIMEOUT = 10

# OpenAlex API Configuration
OPENALEX_API_URL = "https://api.openalex.org/works"
OPENALEX_BATCH_SIZE = 100
OPENALEX_RATE_LIMIT = 10  # requests per second
OPENALEX_EMAIL = "yli05@yahoo.com"

# Semantic Scholar API Configuration
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper"
SEMANTIC_SCHOLAR_RATE_LIMIT = 0.33  # 1 request per 3 seconds
SEMANTIC_SCHOLAR_FIELDS = "abstract,citationCount"
SEMANTIC_SCHOLAR_TIMEOUT = 10
```

#### Usage

**Automatic (via pipeline)**:
```bash
python scripts/fetch_papers.py
```
This automatically enriches papers with abstracts after fetching from DBLP.

**Manual (standalone)**:
```python
from fetch_papers import DBLPFetcher

fetcher = DBLPFetcher('kdd')
papers = [...] # Your paper list
enriched_papers = fetcher.enrich_papers_with_abstracts(papers)
```

#### Performance Metrics

**For 3,016 papers**:
- OpenAlex: ~5 minutes (31 batches × 0.1s)
- Semantic Scholar: ~12-15 minutes (~240 papers × 3s)
- **Total Time**: ~20 minutes
- **Total Cost**: $0 (completely free)

#### Error Handling

**OpenAlex Errors**:
- Retry logic with exponential backoff
- Batch-level error handling (continues on failure)
- Graceful degradation (nulls for failed batches)

**Semantic Scholar Errors**:
- HTTP 404: Paper not found (expected, not logged as error)
- Timeout: Logged as warning, returns None
- Rate limit exceeded: 3-second delay prevents this

#### Limitations

1. **Recent Papers**: OpenAlex coverage is lower for papers published in the last 3-6 months
2. **Non-ACM Papers**: Some conference papers may not be in either API
3. **API Availability**: Dependent on external services (99.9% uptime)
4. **Rate Limits**: Free tiers have modest limits (sufficient for current needs)

#### Future Improvements

- **Request Semantic Scholar API key** for faster processing (1-100 req/sec)
- **Implement caching** to avoid re-fetching on pipeline reruns
- **Add arXiv API** as third fallback tier
- **Parallelize Semantic Scholar** requests with API key
- **Track abstract quality** metrics (length, completeness)

#### Monitoring

**Statistics Logged**:
- Total papers processed
- Abstracts from OpenAlex (count + %)
- Abstracts from Semantic Scholar (count + %)
- Papers without abstracts (count + %)
- Processing time per tier

**Example Output**:
```
==================================================
Abstract Fetching Summary:
==================================================
Total papers: 3,016
Papers with abstracts: 2,965 (98.3%)
  - From OpenAlex: 2,775 (92.0%)
  - From Semantic Scholar: 190 (6.3%)
Papers without abstracts: 51 (1.7%)
```

#### Testing

**Test File**: `scripts/test_abstract_fetching.py`

```bash
python scripts/test_abstract_fetching.py
```

Tests abstract fetching on 5 sample papers (covering different years) to verify both API tiers work correctly.

---

### Security Considerations

- No user authentication required (static site)
- API keys stored in environment variables
- No server-side code execution
- CORS handled by GitHub Pages
- XSS prevention (D3.js escapes text)

---

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

For user documentation, see [README.md](../README.md).
