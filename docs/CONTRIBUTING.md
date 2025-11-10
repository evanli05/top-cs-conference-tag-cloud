# Contributing to Top CS Conference Tag Cloud

Thank you for your interest in contributing to this project! This guide will help you get started.

## Table of Contents

- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Data Update Process](#data-update-process)
- [Code Style Guidelines](#code-style-guidelines)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Areas We Need Help](#areas-we-need-help)

## How to Contribute

There are many ways to contribute to this project:

- **Add new conferences**: Implement data fetching for additional conferences (IJCAI, ICML, ACL, EMNLP, etc.)
  - **Completed**: KDD (2020-2025), ICLR (2020-2025), AAAI (2020-2025)
  - **In Progress**: NeurIPS (2020-2024), CVPR (2020-2025)
- **Improve keyword extraction**: Enhance the LLM prompts or processing pipeline for better keyword quality
- **UI/UX improvements**: Suggest or implement design enhancements
- **Bug fixes**: Report or fix issues
- **Documentation**: Improve or expand documentation
- **Testing**: Help test the application across different browsers and devices
- **Feature requests**: Suggest new features or improvements

## Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR-USERNAME/top-cs-conference-tag-cloud.git
   cd top-cs-conference-tag-cloud
   ```

3. **Install dependencies:**
   ```bash
   pip install -r scripts/requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   # Copy the example .env file
   cp .env.example .env

   # Edit .env and add your API keys
   # Get Gemini API key from: https://makersuite.google.com/app/apikey
   ```

5. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

6. **Start local development server:**
   ```bash
   python3 -m http.server 8000
   # Visit http://localhost:8000
   ```

For detailed setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

## Making Changes

### Before You Start

1. **Check existing issues** to see if someone is already working on it
2. **Open an issue** to discuss major changes before implementing
3. **Read the code** to understand the current architecture
4. **Test locally** before submitting changes

### Development Workflow

1. **Make your changes** in your feature branch
2. **Test thoroughly** (see testing checklist in [DEVELOPMENT.md](DEVELOPMENT.md))
3. **Commit with clear messages**:
   ```bash
   git commit -m "Add: Brief description of what you added"
   git commit -m "Fix: Brief description of what you fixed"
   git commit -m "Update: Brief description of what you updated"
   ```
4. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
5. **Open a Pull Request** on GitHub

### Testing Your Changes

Before submitting a pull request, ensure:

- [ ] Code runs without errors
- [ ] All existing features still work
- [ ] New features have been tested
- [ ] Changes work across browsers (Chrome, Firefox, Safari)
- [ ] Changes work on mobile devices
- [ ] Console shows no errors or warnings
- [ ] Code follows the style guidelines below

## Data Update Process

### Annual Conference Data Updates

After conference proceedings are published, update the data:

1. **Update configuration** (if needed):
   ```python
   # scripts/config.py
   CONFERENCES = {
       'kdd': {
           'years': [2020, 2021, 2022, 2023, 2024, 2025]  # Add new year
       }
   }
   ```

2. **Run the data pipeline:**
   ```bash
   python scripts/run_pipeline.py
   ```

3. **Review generated data:**
   - Check `data/processed/wordcloud_data.json`
   - Verify keyword quality
   - Ensure year counts are correct
   - Confirm metadata is accurate

4. **Test locally:**
   ```bash
   python3 -m http.server 8000
   # Open http://localhost:8000
   # Test all filters and features
   ```

5. **Commit and push:**
   ```bash
   git add data/processed/wordcloud_data.json
   git commit -m "Update KDD data for 2025"
   git push origin main
   ```

### Adding a New Conference

1. **Update configuration:**
   ```python
   # scripts/config.py
   CONFERENCES = {
       'kdd': { ... },
       'ijcai': {
           'name': 'IJCAI',
           'full_name': 'International Joint Conference on Artificial Intelligence',
           'dblp_venue': 'ijcai',
           'categories': ['Artificial Intelligence'],
           'years': [2020, 2021, 2022, 2023, 2024]
       }
   }
   ```

2. **Test data fetching:**
   ```bash
   python scripts/fetch_papers.py
   # Verify data in data/raw/
   ```

3. **Run full pipeline:**
   ```bash
   python scripts/run_pipeline.py
   ```

4. **Update frontend** (index.html):
   ```html
   <select id="conference-filter">
       <option value="all">All Conferences</option>
       <option value="KDD" data-category="Data Mining">KDD</option>
       <option value="IJCAI" data-category="Artificial Intelligence">IJCAI</option>
   </select>
   ```

5. **Test thoroughly** and submit PR

## Code Style Guidelines

### Python

- **PEP 8** style guide
- **4 spaces** for indentation (no tabs)
- **Type hints** for function parameters when possible
- **Docstrings** for all functions and classes
- **Meaningful variable names**
- **Comments** for complex logic

Example:
```python
def extract_keywords(paper: Dict, max_keywords: int = 3) -> List[str]:
    """
    Extract keywords from a paper title using LLM.

    Args:
        paper (Dict): Paper dictionary with 'title' field
        max_keywords (int): Maximum keywords to extract

    Returns:
        List[str]: List of extracted keywords
    """
    # Implementation here
    pass
```

### JavaScript

- **ES6+** syntax (const, let, arrow functions)
- **2 spaces** for indentation
- **camelCase** for variables and functions
- **JSDoc comments** for complex functions
- **Semicolons** at end of statements
- **Template literals** for string interpolation

Example:
```javascript
/**
 * Apply filters to word cloud data
 * @param {Object} filters - Filter configuration
 * @returns {Array} Filtered word array
 */
applyFilters(filters) {
  const filteredWords = this.data.words.filter(word => {
    // Filter logic here
    return true;
  });
  return filteredWords;
}
```

### CSS

- **CSS custom properties** for theming
- **Mobile-first** responsive design
- **BEM naming** for classes when applicable
- **Comments** for complex layouts
- **Consistent spacing**

Example:
```css
/* Word cloud container */
.wordcloud-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 600px;
  background: var(--color-bg-secondary);
}
```

### HTML

- **Semantic elements** (header, nav, main, section)
- **Indentation** of 2 or 4 spaces (consistent)
- **Comments** for major sections
- **Accessibility** attributes (alt, aria-label, etc.)

## Submitting Pull Requests

### Pull Request Process

1. **Ensure your PR**:
   - Has a clear title (e.g., "Add IJCAI conference support")
   - Includes a description of changes
   - References related issues (e.g., "Fixes #123")
   - Has been tested locally
   - Follows code style guidelines

2. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation update
   - [ ] Code refactoring

   ## Testing
   - [ ] Tested locally
   - [ ] Works in Chrome, Firefox, Safari
   - [ ] Works on mobile
   - [ ] No console errors

   ## Screenshots (if applicable)
   Add screenshots of visual changes
   ```

3. **Code Review**:
   - Be responsive to feedback
   - Make requested changes promptly
   - Discuss if you disagree (respectfully)
   - Mark resolved comments

4. **After Approval**:
   - Maintainer will merge your PR
   - Your contribution will be acknowledged
   - GitHub Pages will auto-deploy

## Areas We Need Help

### High Priority

1. **Add new conferences**:
   - **Completed**: KDD, ICLR, AAAI ✅
   - **In Progress**: NeurIPS (2020-2024), CVPR (2020-2025) 🔄
   - **Planned**: IJCAI (AI), ICML (ML), ICCV, ECCV (CV), ACL, EMNLP, NAACL (NLP)

2. **Keyword quality improvements**:
   - Better LLM prompts
   - Post-processing filters
   - Manual curation tools

### Medium Priority

3. **UI/UX enhancements**:
   - Trending topics view
   - Multi-year comparison
   - Export word cloud as image
   - Search functionality

### Low Priority

4. **Advanced features**:
   - Author network visualization
   - Topic clustering
   - Real-time updates

## Questions or Issues?

- **Open an issue** on GitHub for bugs or feature requests
- **Email**: yli05@yahoo.com for questions
- **Discussions**: Use GitHub Discussions for general questions

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Give constructive feedback
- Focus on the code, not the person
- Follow the Golden Rule

---

Thank you for contributing to the CS research community! 🎓✨
