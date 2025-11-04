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

### Security Considerations

- No user authentication required (static site)
- API keys stored in environment variables
- No server-side code execution
- CORS handled by GitHub Pages
- XSS prevention (D3.js escapes text)

---

For contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

For user documentation, see [README.md](../README.md).
