# Top CS Conference Tag Cloud

An interactive word cloud visualization showing research trends from top-tier computer science conferences based on paper title keywords.

## Overview

This project helps CS researchers understand trending topics and research areas by visualizing keywords from accepted papers at top conferences like KDD, IJCAI, NeurIPS, and more. The goal is to provide insights into hot research areas and emerging trends in computer science.

## Features

- **Interactive Word Cloud**: Keywords sized by frequency, providing visual insight into research trends
- **Year Filtering**: View trends across different years (2020-2024)
- **Conference Filtering**: Focus on specific conferences (starting with KDD)
- **Category Filtering**: Filter by conference category (Data Mining, AI, Machine Learning, etc.)
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern Academic Design**: Clean, professional interface suitable for research contexts

## Current Status

**Pilot Conference**: KDD (Knowledge Discovery and Data Mining)
**Years Covered**: 2020-2024
**Status**: In Development

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
├── index.html              # Main webpage
├── .gitignore
└── README.md
```

## Getting Started

### Prerequisites

- **Python 3.8+** for data processing
- **Modern web browser** (Chrome, Firefox, Safari)
- **Git** for version control
- **Internet connection** for fetching data from DBLP API

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

3. **You're ready to go!**

## Usage

### Fetch Latest Conference Data

To update the conference paper data and regenerate the word cloud:

```bash
python scripts/run_pipeline.py
```

This pipeline will:
1. Fetch papers from DBLP API for KDD (2020-2024)
2. Extract keywords from paper titles
3. Remove stopwords and common academic terms
4. Calculate keyword frequencies per year
5. Generate `data/processed/wordcloud_data.json`

### View the Website Locally

**Option 1: Direct file open**
```bash
open index.html
# or double-click index.html in your file browser
```

**Option 2: Local server (recommended)**
```bash
# Python 3
python -m http.server 8000

# Then visit: http://localhost:8000
```

**Option 3: Live Server (VS Code extension)**
- Install "Live Server" extension in VS Code
- Right-click `index.html` and select "Open with Live Server"

### Using the Website

1. **View the word cloud**: Keywords are sized by frequency
2. **Hover over words**: See exact frequency counts
3. **Filter by year**: Use the year selector to view specific years or ranges
4. **Filter by category**: Select conference categories (for future multi-conference support)
5. **Responsive**: Resize browser or view on mobile - layout adapts automatically

## Data Format

The word cloud data is stored in JSON format at `data/processed/wordcloud_data.json`:

```json
{
  "metadata": {
    "conference": "KDD",
    "years": [2020, 2021, 2022, 2023, 2024],
    "total_papers": 1247,
    "total_keywords": 156,
    "last_updated": "2024-01-15",
    "categories": ["Data Mining"]
  },
  "words": [
    {
      "text": "machine learning",
      "value": 45,
      "years": {
        "2020": 8,
        "2021": 9,
        "2022": 10,
        "2023": 9,
        "2024": 9
      }
    },
    {
      "text": "neural network",
      "value": 38,
      "years": {
        "2020": 5,
        "2021": 7,
        "2022": 9,
        "2023": 8,
        "2024": 9
      }
    }
  ]
}
```

### Field Descriptions

**Metadata:**
- `conference`: Conference name (e.g., "KDD")
- `years`: Array of years included in the dataset
- `total_papers`: Total number of papers analyzed
- `total_keywords`: Number of unique keywords extracted
- `last_updated`: Date when data was last generated
- `categories`: Conference-level categories (e.g., "Data Mining", "AI")

**Word Objects:**
- `text`: The keyword or phrase (string)
- `value`: Total frequency across all years (number) - determines word size
- `years`: Object mapping year to frequency count for that year

## Conferences

### Current (V1)
- **KDD** (ACM SIGKDD Conference on Knowledge Discovery and Data Mining)

### Planned (Future Versions)

**Data Mining:**
- KDD, ICDM, SDM, WSDM

**Artificial Intelligence:**
- IJCAI, AAAI

**Machine Learning:**
- NeurIPS, ICML, ICLR

**Computer Vision:**
- CVPR, ICCV, ECCV

**Natural Language Processing:**
- ACL, EMNLP, NAACL

**Information Retrieval:**
- SIGIR, WWW

## Technology Stack

**Frontend:**
- HTML5, CSS3, JavaScript (ES6+)
- D3.js v7 with d3-cloud for word cloud visualization
- Vanilla JavaScript (no framework dependencies)
- Responsive design with CSS Grid and Flexbox

**Backend/Data Processing:**
- Python 3.8+
- `requests` library for DBLP API calls
- Native Python for text processing and keyword extraction
- JSON for data storage

**Data Source:**
- [DBLP Computer Science Bibliography](https://dblp.org/) API

**Hosting:**
- GitHub Pages (static site hosting)

## Development

### Development Roadmap

**Phase 1: Foundation (Current)**
- ✅ Project setup and planning
- 🔄 Minimal frontend with sample data
- ⏳ DBLP data fetching for KDD
- ⏳ Keyword extraction pipeline
- ⏳ Data generation and integration

**Phase 2: Enhancement**
- Multi-year comparison view
- Trending topics (words increasing over time)
- Click on keywords to see paper list
- Export word cloud as image

**Phase 3: Expansion**
- Add more conferences (IJCAI, NeurIPS, etc.)
- Cross-conference comparison
- Topic clustering and categorization
- Historical trend analysis

### Step-by-Step Implementation

**Step 1: Minimal Frontend with Sample Data**
- Create sample JSON with realistic KDD keywords
- Build HTML structure
- Style with modern academic design
- Implement D3.js word cloud
- Add year and category filters
- Test responsiveness and interactivity

**Step 2: DBLP Data Fetching**
- Configure DBLP API endpoints
- Implement paper fetching for KDD 2020-2024
- Handle API rate limiting and errors
- Store raw paper data
- Validate data quality (~1000-1500 papers expected)

**Step 3: Keyword Extraction**
- Process paper titles
- Remove stopwords (common words like "the", "and", "using")
- Remove generic academic terms ("paper", "study", "approach")
- Extract unigrams and bigrams
- Calculate frequency per year
- Quality check for relevance

**Step 4: JSON Data Generator**
- Transform extracted keywords to frontend format
- Generate metadata
- Create production `wordcloud_data.json`
- Integrate with frontend
- End-to-end testing

### Testing Strategy

Each implementation step includes comprehensive testing:

**Functional Testing:**
- Word cloud renders correctly
- Filters work as expected
- Data loads without errors
- Interactive features respond properly

**Data Quality Testing:**
- Keywords are relevant and meaningful
- No stopwords or generic terms
- Frequency counts are accurate
- Year breakdowns sum correctly

**Cross-browser Testing:**
- Chrome, Firefox, Safari
- Mobile browsers (iOS Safari, Chrome Mobile)

**Performance Testing:**
- Page load time < 2 seconds
- Filter updates < 500ms
- Smooth animations and transitions

## Manual Data Update Process

Since the project uses manual data updates, here's the recommended workflow:

1. **Annual Update** (after conference proceedings published):
   ```bash
   python scripts/run_pipeline.py
   ```

2. **Review Generated Data**:
   - Check `data/processed/wordcloud_data.json`
   - Verify keyword quality
   - Ensure year counts are correct

3. **Test Locally**:
   - Open `index.html` in browser
   - Test all filters
   - Verify visual appearance

4. **Commit and Deploy**:
   ```bash
   git add data/processed/wordcloud_data.json
   git commit -m "Update KDD data for 2024"
   git push origin main
   ```

5. **GitHub Pages** automatically deploys the update

## Contributing

Contributions are welcome! Here's how you can help:

- **Add new conferences**: Implement data fetching for additional conferences
- **Improve keyword extraction**: Enhance the NLP pipeline for better keyword quality
- **UI/UX improvements**: Suggest or implement design enhancements
- **Bug fixes**: Report or fix issues
- **Documentation**: Improve or expand documentation

### Contribution Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Data Source**: [DBLP Computer Science Bibliography](https://dblp.org/) - Comprehensive computer science bibliography maintained by Schloss Dagstuhl
- **Visualization**: [D3.js](https://d3js.org/) - Data-Driven Documents by Mike Bostock
- **Word Cloud Layout**: [d3-cloud](https://github.com/jasondavies/d3-cloud) by Jason Davies
- **Inspiration**: Academic research community and conference organizers

## Contact

For questions, suggestions, or collaboration:
- Open an issue on GitHub
- Email: [your-email@example.com]
- Twitter: [@yourhandle]

## Citation

If you use this tool in your research or find it helpful, please consider citing:

```bibtex
@misc{cs_conference_tagcloud,
  title={Top CS Conference Tag Cloud: Visualizing Research Trends},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/top-cs-conference-tag-cloud}
}
```

---

**Made with ❤️ for the CS research community**
