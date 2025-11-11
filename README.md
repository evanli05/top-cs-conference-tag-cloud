# Top CS Conference Tag Cloud

An interactive word cloud visualization showing research trends from top-tier computer science conferences based on paper title keywords.

## Overview

This project helps CS researchers understand trending topics and research areas by visualizing keywords from accepted papers at top conferences. Discover hot research areas and emerging trends in computer science through an intuitive, interactive interface.

## Features

- **Interactive Word Cloud**: Keywords sized by frequency, providing visual insight into research trends
- **Year Filtering**: View trends across different years (2020-2025)
- **Conference Filtering**: Focus on specific conferences or categories
- **Category Filtering**: Filter by conference category (Data Mining, AI, Machine Learning, CV, NLP)
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern Design**: Clean, professional interface suitable for academic contexts

## Current Status

- **Conferences Covered**: 6 (KDD, ICLR, AAAI, NeurIPS, CVPR, IJCAI)
- **Years**: 2020-2025
- **Total Papers**: 60,814 papers from top-tier CS conferences
- **Abstract Coverage**: 98.5% (59,884 papers with abstracts)
- **Data Quality**: Multi-tier fetching system ensuring high-quality abstracts

## Quick Start

### View Online

🚀 **Live Demo**: https://evanli05.github.io/top-cs-conference-tag-cloud/

### Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/top-cs-conference-tag-cloud.git
   cd top-cs-conference-tag-cloud
   ```

2. **Start local web server:**
   ```bash
   python3 -m http.server 8000
   ```

3. **Open in browser:**
   ```
   http://localhost:8000
   ```

That's it! The word cloud should load with KDD conference data.

## Usage

### Exploring the Word Cloud

- **Word Size**: Larger words appear more frequently in paper titles
- **Hover**: See exact frequency counts and year-by-year breakdown
- **Filters**: Use year, category, and conference filters to narrow down trends
- **Reset**: Click "Reset Filters" to return to the full dataset

### Updating Conference Data

To fetch the latest conference data:

```bash
# 1. Install dependencies
pip install -r scripts/requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env file and add your Gemini API key

# 3. Run data pipeline
python scripts/run_pipeline.py
```

This will:
1. Fetch papers from DBLP
2. Extract keywords using LLM
3. Generate updated visualization data

## Conferences

### Currently Supported

| Conference | Full Name | Category | Years | Papers |
|------------|-----------|----------|-------|--------|
| **KDD** | ACM SIGKDD Conference on Knowledge Discovery and Data Mining | Machine Learning | 2020-2025 | 3,016 |
| **ICLR** | International Conference on Learning Representations | Machine Learning | 2020-2025 | 10,184 |
| **AAAI** | AAAI Conference on Artificial Intelligence | Artificial Intelligence | 2020-2025 | 13,828 |
| **NeurIPS** | Conference on Neural Information Processing Systems | Machine Learning | 2020-2024 | 15,105 |
| **CVPR** | IEEE/CVF Conference on Computer Vision and Pattern Recognition | Computer Vision | 2020-2025 | 13,145 |
| **IJCAI** | International Joint Conference on Artificial Intelligence | Artificial Intelligence | 2020-2025 | 5,536 |

### Planned

**Machine Learning**: ICML
**Computer Vision**: ICCV, ECCV
**Natural Language Processing**: ACL, EMNLP, NAACL
**Data Mining**: ICDM, SDM, WSDM

## Data Coverage & Quality

### Abstract Coverage by Conference

Our multi-tier abstract fetching system achieves excellent coverage across all conferences:

| Conference | Total Papers | With Abstracts | Coverage | Notes |
|------------|--------------|----------------|----------|-------|
| **NeurIPS** | 15,105 | 15,099 | **100.0%** | Custom proceedings fetcher + OpenAlex |
| **ICLR** | 10,184 | 10,177 | **99.9%** | OpenReview API (primary source) |
| **AAAI** | 13,828 | 13,803 | **99.8%** | OpenAlex + Semantic Scholar |
| **KDD** | 3,016 | 3,010 | **99.8%** | OpenAlex batch fetching |
| **CVPR** | 13,145 | 12,692 | **96.6%** | OpenAlex + title-based search + Semantic Scholar (known issue: For the missing abstract papers, OpenAlex API returns abstract field as "Null", and Semantic Scholar blocked me to fetch some CVPR paper abstract due to copyright policy) |
| **IJCAI** | 5,536 | 5,103 | **92.2%** | OpenAlex + Semantic Scholar (known issue: some IJCAI 2024 papers don't have DOI, leading to failures of fetching abstracts from OpenAlex and Semantic Scholar) |
| **Overall** | **60,814** | **59,884** | **98.5%** | Across all 6 conferences |

### Year-by-Year Coverage Highlights

**Best Coverage (100.0%)**:
- NeurIPS 2021, 2023, 2024
- CVPR 2022, 2023
- AAAI 2023
- IJCAI 2023, 2025
- KDD 2020, 2021, 2022, 2024

**Coverage Challenges**:
- IJCAI 2024: 59.1% (429 papers missing abstracts - ongoing fetch)
- CVPR 2024: 84.1% (433 papers missing abstracts)

### Abstract Fetching Architecture

We use a sophisticated **6-tier fallback system** to maximize abstract coverage:

1. **Tier 0**: OpenReview ID search (for papers with OpenReview URLs)
2. **Tier 1**: OpenReview API (ICLR, ICML) - ~100% coverage
3. **Tier 2**: OpenAlex batch API (DOI-based) - ~95% coverage
4. **Tier 3**: OpenAlex title search (fallback) - ~50% additional recovery
5. **Tier 4**: Semantic Scholar DOI lookup - ~90% coverage
6. **Tier 4.5**: Semantic Scholar title search - for papers without DOIs
7. **Tier 5**: NeurIPS Proceedings (custom HTML parser) - ~60-70% for NeurIPS 2020-2024

**Rate Limiting & API Management**:
- OpenAlex: 10 req/sec (polite pool)
- Semantic Scholar: 1 req/sec
- OpenReview: 1 req/sec
- NeurIPS Proceedings: 2 req/sec

**Recovery Mode**: Intelligent incremental fetching that skips papers already having abstracts, enabling efficient re-runs.

## Documentation

- **[Development Guide](docs/DEVELOPMENT.md)** - Technical details, architecture, debugging
- **[Contributing Guidelines](docs/CONTRIBUTING.md)** - How to contribute, code style, PR process

## Technology

**Frontend**: HTML5, CSS3, JavaScript (ES6+), D3.js
**Backend**: Python 3.8+, Gemini LLM API
**Data Source**: [DBLP Computer Science Bibliography](https://dblp.org/)
**Hosting**: GitHub Pages

## Contributing

Contributions are welcome! We need help with:

- Adding new conferences
- Improving keyword extraction
- UI/UX enhancements
- Bug fixes and testing
- Documentation

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Data Source**: [DBLP Computer Science Bibliography](https://dblp.org/) - Maintained by Schloss Dagstuhl
- **Visualization**: [D3.js](https://d3js.org/) by Mike Bostock
- **Word Cloud Layout**: [d3-cloud](https://github.com/jasondavies/d3-cloud) by Jason Davies
- **LLM API**: Google Gemini for intelligent keyword extraction

## Citation

If you use this tool in your research or find it helpful:

```bibtex
@misc{cs_conference_tagcloud,
  title={Top CS Conference Tag Cloud: Visualizing Research Trends},
  author={Yifan Li},
  year={2025},
  url={https://github.com/yourusername/top-cs-conference-tag-cloud}
}
```

## Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/top-cs-conference-tag-cloud/issues)
- **Email**: yli05@yahoo.com

---

**Made with ❤️ for the CS research community**
