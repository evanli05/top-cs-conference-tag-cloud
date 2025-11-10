# Conference Data Fetching Progress

This document tracks the progress of fetching paper data for top CS conferences.

## Completed Conferences

### ✅ KDD (ACM SIGKDD Conference on Knowledge Discovery and Data Mining)
- **Status**: Complete
- **Years**: 2020-2025
- **Total Papers**: 3,016
- **Abstract Coverage**: 99.8% (3,010/3,016)
- **Data Source**: DBLP + OpenAlex + Semantic Scholar
- **Output File**: `data/raw/kdd_papers.json`
- **Completion Date**: 2025-11-09

### ✅ ICLR (International Conference on Learning Representations)
- **Status**: Complete
- **Years**: 2020-2025
- **Total Papers**: 7,335
- **Abstract Coverage**: ~99%+ (OpenReview-based conference)
- **Data Source**: DBLP + OpenReview API (v1 for ≤2023, v2 for ≥2024)
- **Output File**: `data/raw/iclr_papers.json`
- **Completion Date**: 2025-11-09
- **Notes**: First OpenReview-based conference with dual API version support

### ✅ AAAI (AAAI Conference on Artificial Intelligence)
- **Status**: Complete
- **Years**: 2020-2025
- **Total Papers**: ~13,828
- **Abstract Coverage**: ~98%+ (99.9% DOI coverage)
- **Data Source**: DBLP + OpenAlex + Semantic Scholar
- **Output File**: `data/raw/aaai_papers.json`
- **Completion Date**: 2025-11-09
- **Notes**: Largest single-venue fetch completed; excellent DOI coverage

### 🔄 NeurIPS (Conference on Neural Information Processing Systems)
- **Status**: In Progress (68% - fetching abstracts from proceedings)
- **Years**: 2020-2024
- **Total Papers**: 15,105
- **Abstract Coverage**: ~32% (4,800+ fetched, ongoing)
- **Data Source**: DBLP + NeurIPS Proceedings (Tier 4 custom fetcher)
- **Output File**: `data/raw/neurips_papers.json`
- **Started**: 2025-11-09
- **Notes**: Uses custom NeurIPS Proceedings fetcher for 2020-2024; hybrid approach with proceedings.nips.cc

### 🔄 CVPR (IEEE/CVF Conference on Computer Vision and Pattern Recognition)
- **Status**: In Progress (83.3% - fetching year 2025)
- **Years**: 2020-2025
- **Expected Papers**: ~13,145
- **Expected Abstract Coverage**: 97-99% (99.98% DOI coverage)
- **Data Source**: DBLP + OpenAlex + Semantic Scholar
- **Output File**: `data/raw/cvpr_papers.json`
- **Started**: 2025-11-09
- **Notes**: Largest conference by paper count; no code changes needed (excellent DOI coverage)

## Summary Statistics (Completed & In Progress)

| Conference | Years | Papers | Abstract % | Primary Source | Notes |
|------------|-------|--------|------------|----------------|-------|
| KDD | 2020-2025 | 3,016 | 99.8% | DOI-based | Multi-part proceedings (2025) |
| ICLR | 2020-2025 | 7,335 | 99%+ | OpenReview | Dual API version support |
| AAAI | 2020-2025 | ~13,828 | 98%+ | DOI-based | Excellent DOI coverage |
| NeurIPS | 2020-2024 | 15,105 | ~32% (in progress) | NeurIPS Proceedings | Custom Tier 4 fetcher |
| CVPR | 2020-2025 | ~13,145 | 97-99% (est.) | DOI-based | In progress |

**Total Papers Fetched**: ~52,429 (when all complete)
**Overall Abstract Coverage**: ~95%+ (estimated final)

## Technical Infrastructure

### Multi-Tier Abstract Fetching System
- **Tier 0**: OpenReview ID search by title (for OpenReview conferences)
- **Tier 1**: OpenReview API (v1 for ≤2023, v2 for ≥2024)
- **Tier 2**: OpenAlex API (batch processing, 100 DOIs per request)
- **Tier 3**: Semantic Scholar API (fallback, 1 request per 3 seconds)
- **Tier 4**: NeurIPS Proceedings (custom fetcher for NeurIPS 2020-2024)

### Features Implemented
- ✅ Conference-specific filename generation
- ✅ Progress logging and incremental saves
- ✅ Recovery mode (resume from interruptions)
- ✅ OpenReview API dual-version support (v1/v2)
- ✅ OpenReview ID search by title
- ✅ Multi-part conference support (KDD 2025)
- ✅ NeurIPS Proceedings Tier 4 fetcher (proceedings.nips.cc)
- ✅ Hash extraction from proceedings URLs
- ✅ Comprehensive error handling
- ✅ Rate limiting for all APIs

## Next Conferences (Planned)

### Machine Learning
- [ ] ICML (International Conference on Machine Learning)

### Artificial Intelligence
- [ ] IJCAI (International Joint Conference on Artificial Intelligence)

### Computer Vision
- [ ] ECCV (European Conference on Computer Vision) - Biennial
- [ ] ICCV (IEEE International Conference on Computer Vision) - Biennial

### Natural Language Processing
- [ ] ACL (Annual Meeting of the Association for Computational Linguistics)
- [ ] EMNLP (Conference on Empirical Methods in Natural Language Processing)
- [ ] NAACL (North American Chapter of the ACL)

### The Web & Information Retrieval
- [ ] SIGIR (International ACM SIGIR Conference)
- [ ] WWW (The Web Conference)

## Implementation Notes

### Conference-Specific Considerations

**OpenReview-based Conferences** (ICLR, ICML):
- Use OpenReview API for abstract fetching
- Dual API version support (v1 for ≤2023, v2 for ≥2024)
- ID search by title for missing forum IDs
- ~100% abstract coverage expected

**NeurIPS (Special Case)**:
- NeurIPS 2020-2024 use custom Tier 4 fetcher (proceedings.nips.cc)
- NeurIPS 2025+ may use OpenReview API (to be determined)
- Hash extraction from DBLP proceedings URLs
- Direct HTML parsing for abstracts
- ~60-70% abstract coverage expected (proceedings URLs only)

**DOI-based Conferences** (KDD, AAAI, CVPR, most others):
- Use OpenAlex + Semantic Scholar pipeline
- No code changes needed if DOI coverage ≥70%
- 97-99% abstract coverage expected

**Biennial Conferences** (ECCV, ICCV):
- ECCV: Even years only (2020, 2022, 2024)
- ICCV: Odd years only (2021, 2023, 2025)

### Data Quality Metrics

All fetched data includes:
- Paper metadata (title, authors, year, venue)
- DOI or OpenReview URLs
- Abstracts (98%+ coverage)
- Citation counts (where available)
- Source tracking (openalex/semantic_scholar/openreview)

### Performance Characteristics

**DBLP Scraping**:
- Speed: ~2-3 minutes per 1,000 papers
- Rate limiting: 1 second between requests

**Abstract Fetching**:
- OpenReview: ~1 second per paper
- OpenAlex: ~0.1 seconds per batch (100 papers)
- Semantic Scholar: 3 seconds per paper

**Estimated Total Time per Conference**:
- Small (3K papers): 15-20 minutes
- Medium (7K papers): 20-30 minutes
- Large (13K papers): 30-45 minutes

---

*Last Updated: 2025-11-09*
