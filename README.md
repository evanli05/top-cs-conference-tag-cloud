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

- **Conferences Covered**: KDD (Knowledge Discovery and Data Mining)
- **Years**: 2020-2025
- **Papers Analyzed**: 3,016
- **Keywords Extracted**: 200+ unique research terms

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
# Install dependencies first
pip install -r scripts/requirements.txt

# Set up Gemini API key
export GEMINI_API_KEY="your-api-key-here"

# Run data pipeline
python scripts/run_pipeline.py
```

This will:
1. Fetch papers from DBLP
2. Extract keywords using LLM
3. Generate updated visualization data

## Conferences

### Currently Supported

| Conference | Full Name | Category | Years |
|------------|-----------|----------|-------|
| **KDD** | ACM SIGKDD Conference on Knowledge Discovery and Data Mining | Data Mining | 2020-2025 |

### Planned

**Data Mining**: ICDM, SDM, WSDM
**Artificial Intelligence**: IJCAI, AAAI
**Machine Learning**: NeurIPS, ICML, ICLR
**Computer Vision**: CVPR, ICCV, ECCV
**Natural Language Processing**: ACL, EMNLP, NAACL

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
- **Email**: yifan.li.1112@gmail.com

---

**Made with ❤️ for the CS research community**
