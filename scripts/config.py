"""
Configuration settings for CS Conference Tag Cloud
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

# ===================================
# Project Paths
# ===================================

# Get project root directory (parent of scripts/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Data directories
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
SAMPLE_DATA_DIR = os.path.join(DATA_DIR, 'sample')

# Output files
# Note: RAW_PAPERS_FILE is now dynamically generated per conference
# Use get_raw_papers_file(conference_key) to get the correct path
PROCESSED_KEYWORDS_FILE = os.path.join(PROCESSED_DATA_DIR, 'keywords_intermediate.json')
FINAL_DATA_FILE = os.path.join(PROCESSED_DATA_DIR, 'wordcloud_data.json')

# ===================================
# DBLP Configuration
# ===================================

# DBLP base URL for conference pages
DBLP_BASE_URL = "https://dblp.org"

# DBLP conference page URL pattern
# Format: https://dblp.org/db/conf/{venue}/{venue}{year}.html
DBLP_CONF_URL_PATTERN = "{base}/db/conf/{venue}/{venue}{year}.html"

# Some conferences have multiple parts (e.g., KDD 2025 has -1 and -2)
# Map of (venue, year) -> list of page suffixes
DBLP_MULTI_PART_CONFERENCES = {
    ('kdd', 2025): ['', '-1', '-2'],  # Will generate kdd2025.html, kdd2025-1.html, kdd2025-2.html
}

# Conference configurations (organized by CSRankings categories)
# Format: {conference_key: {name, full_name, dblp_venue, categories, years}}

# ===================================
# Machine Learning Conferences
# ===================================
CONFERENCES = {
    'kdd': {
        'name': 'KDD',
        'full_name': 'ACM SIGKDD Conference on Knowledge Discovery and Data Mining',
        'dblp_venue': 'kdd',
        'categories': ['Machine Learning'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    # ICLR - International Conference on Learning Representations
    'iclr': {
        'name': 'ICLR',
        'full_name': 'International Conference on Learning Representations',
        'dblp_venue': 'iclr',
        'categories': ['Machine Learning'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    # ICML - International Conference on Machine Learning
    # 'icml': {
    #     'name': 'ICML',
    #     'full_name': 'International Conference on Machine Learning',
    #     'dblp_venue': 'icml',
    #     'categories': ['Machine Learning'],
    #     'years': [2020, 2021, 2022, 2023, 2024]
    # },
    # NeurIPS - Conference on Neural Information Processing Systems
    # 'neurips': {
    #     'name': 'NeurIPS',
    #     'full_name': 'Conference on Neural Information Processing Systems',
    #     'dblp_venue': 'nips',  # Note: DBLP uses 'nips' as venue identifier
    #     'categories': ['Machine Learning'],
    #     'years': [2020, 2021, 2022, 2023, 2024]
    # },
}

# ===================================
# Future Conference Tracks (CSRankings)
# ===================================

# Artificial Intelligence
# - AAAI: AAAI Conference on Artificial Intelligence
# - IJCAI: International Joint Conference on Artificial Intelligence

# Computer Vision
# - CVPR: IEEE/CVF Conference on Computer Vision and Pattern Recognition
# - ECCV: European Conference on Computer Vision
# - ICCV: IEEE International Conference on Computer Vision

# Natural Language Processing
# - ACL: Annual Meeting of the Association for Computational Linguistics
# - EMNLP: Conference on Empirical Methods in Natural Language Processing
# - NAACL: North American Chapter of the Association for Computational Linguistics

# The Web & Information Retrieval
# - SIGIR: International ACM SIGIR Conference on Research and Development in Information Retrieval
# - WWW: The Web Conference

# Default conference for initial implementation
DEFAULT_CONFERENCE = 'iclr'

# ===================================
# API Request Settings
# ===================================

# Maximum results per API request (DBLP limit is 1000)
MAX_RESULTS_PER_REQUEST = 1000

# Request timeout in seconds
REQUEST_TIMEOUT = 30

# Delay between requests (seconds) to be respectful to DBLP servers
REQUEST_DELAY = 1.0

# User agent for API requests
USER_AGENT = 'CS-Conference-TagCloud/1.0 (Educational Project; https://github.com/yourusername/top-cs-conference-tag-cloud)'

# ===================================
# Abstract Fetching APIs
# ===================================

# OpenAlex API Configuration (Primary source for abstracts)
OPENALEX_API_URL = "https://api.openalex.org/works"
OPENALEX_BATCH_SIZE = 100  # Up to 100 DOIs per request
OPENALEX_RATE_LIMIT = 10  # requests per second (polite pool)
OPENALEX_EMAIL = "yli05@yahoo.com"  # For polite pool access

# Semantic Scholar API Configuration (Fallback for missing abstracts)
SEMANTIC_SCHOLAR_API_URL = "https://api.semanticscholar.org/graph/v1/paper"
SEMANTIC_SCHOLAR_RATE_LIMIT = 0.33  # 1 request per 3 seconds (free tier)
SEMANTIC_SCHOLAR_FIELDS = "abstract,citationCount"
SEMANTIC_SCHOLAR_TIMEOUT = 10  # API request timeout in seconds

# OpenReview API Configuration (For conferences using OpenReview platform)
OPENREVIEW_API_V1_URL = "https://api.openreview.net"  # For conferences 2023 and earlier
OPENREVIEW_API_V2_URL = "https://api2.openreview.net"  # For conferences 2024 and later
OPENREVIEW_RATE_LIMIT = 1.0  # 1 request per second (polite rate limiting)
OPENREVIEW_TIMEOUT = 10  # API request timeout in seconds
OPENREVIEW_API_V2_YEAR_THRESHOLD = 2024  # Conferences from 2024+ use API v2

# Map conferences to OpenReview venue IDs
OPENREVIEW_VENUES = {
    'iclr': 'ICLR.cc',
    'neurips': 'NeurIPS.cc',
    'icml': 'ICML.cc',
}

# ===================================
# Keyword Extraction Settings
# ===================================

# Maximum number of keywords in final output
MAX_KEYWORDS = 200

# Minimum frequency for a keyword to be included
MIN_KEYWORD_FREQUENCY = 1

# Minimum word length (characters)
MIN_WORD_LENGTH = 3

# Maximum word length (to filter out very long strings)
MAX_WORD_LENGTH = 30

# ===================================
# LLM-Based Keyword Extraction
# ===================================

# LLM Backend Selection
# Options: 'local' (Ollama/Mixtral) or 'gemini' (Google Gemini API)
LLM_BACKEND = 'gemini'  # Use Gemini API

# Local LLM Configuration (Ollama)
OLLAMA_BASE_URL = 'http://localhost:11434'
OLLAMA_MODEL = 'mixtral:8x7b-instruct-v0.1-q4_K_M'  # Mixtral 8x7B quantized model

# Gemini API Configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
if not GEMINI_API_KEY and LLM_BACKEND == 'gemini':
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables. "
        "Please set it in the .env file or as an environment variable. "
        "Get your API key from: https://makersuite.google.com/app/apikey"
    )
GEMINI_MODEL = 'gemini-2.5-flash-lite'
# Rate limits for gemini-2.5-flash-lite: 15 RPM, 250K TPM, 1K RPD

# LLM extraction parameters
LLM_KEYWORDS_PER_TITLE = 3  # Extract 2-3 high-quality keywords per title
LLM_TEMPERATURE = 0.0  # Deterministic output (0.0 = no randomness)
LLM_BATCH_SIZE = 50  # Number of titles to process in one API call (optimized for 250K TPM limit)
LLM_MAX_RETRIES = 3  # Maximum retry attempts on failures
LLM_RETRY_DELAY = 2.0  # Initial retry delay in seconds (exponential backoff)
LLM_REQUEST_TIMEOUT = 60  # API request timeout in seconds

# ===================================
# Stopwords
# ===================================

# Common English stopwords
COMMON_STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'or', 'but', 'not', 'can', 'had',
    'been', 'have', 'were', 'when', 'where', 'which', 'who', 'why',
    'how', 'what', 'this', 'these', 'those', 'their', 'them', 'they',
    'we', 'you', 'your', 'our', 'all', 'each', 'if', 'no', 'some',
    'such', 'than', 'then', 'there', 'into', 'through', 'during',
    'before', 'after', 'above', 'below', 'between', 'under', 'again',
    'further', 'once', 'here', 'both', 'few', 'more', 'most', 'other',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 'any', 'every',
    'either', 'neither', 'because', 'while', 'until', 'since', 'about'
}

# Academic/generic terms to filter out
ACADEMIC_STOPWORDS = {
    'paper', 'study', 'research', 'approach', 'method', 'methods',
    'novel', 'new', 'proposed', 'using', 'based', 'via', 'toward',
    'towards', 'analysis', 'framework', 'system', 'technique', 'model',
    'application', 'applications', 'case', 'efficient', 'effective',
    'improved', 'improving', 'improvement', 'enhanced', 'enhancing',
    'algorithm', 'algorithms', 'evaluation', 'experimental', 'results',
    'performance', 'comparison', 'survey', 'review', 'overview',
    'introduction', 'conclusion', 'future', 'work', 'works', 'problem',
    'problems', 'solution', 'solutions', 'issue', 'issues', 'challenge',
    'challenges', 'general', 'specific', 'particular', 'various', 'different',
    'large', 'small', 'scale', 'high', 'low', 'fast', 'slow', 'better',
    'best', 'optimal', 'optimized', 'optimization', 'scalable', 'robust'
}

# Domain-specific terms that might look generic but are actually meaningful
KEEP_TERMS = {
    'learning', 'network', 'networks', 'data', 'mining', 'graph', 'graphs',
    'neural', 'deep', 'machine', 'detection', 'classification', 'clustering',
    'prediction', 'recommendation', 'knowledge', 'information', 'social',
    'time', 'series', 'temporal', 'spatial', 'visual', 'text', 'image',
    'video', 'language', 'natural', 'processing', 'understanding', 'generation',
    'privacy', 'security', 'adversarial', 'reinforcement', 'supervised',
    'unsupervised', 'semi', 'federated', 'distributed', 'online', 'offline',
    'real', 'anomaly', 'outlier', 'attention', 'transformer', 'embedding'
}

# Combined stopwords (common + academic, excluding keep terms)
STOPWORDS = (COMMON_STOPWORDS | ACADEMIC_STOPWORDS) - KEEP_TERMS

# ===================================
# Logging Settings
# ===================================

# Enable verbose logging
VERBOSE = True

# Log file (None = console only)
LOG_FILE = None

# ===================================
# Helper Functions
# ===================================

def get_conference_config(conference_key=None):
    """
    Get configuration for a specific conference

    Args:
        conference_key (str): Conference key (e.g., 'kdd')

    Returns:
        dict: Conference configuration
    """
    if conference_key is None:
        conference_key = DEFAULT_CONFERENCE

    if conference_key not in CONFERENCES:
        raise ValueError(f"Unknown conference: {conference_key}. Available: {list(CONFERENCES.keys())}")

    return CONFERENCES[conference_key]


def get_raw_papers_file(conference_key=None):
    """
    Get the raw papers JSON file path for a specific conference

    Args:
        conference_key (str): Conference key (e.g., 'kdd', 'iclr')

    Returns:
        str: Path to the raw papers JSON file
    """
    if conference_key is None:
        conference_key = DEFAULT_CONFERENCE

    return os.path.join(RAW_DATA_DIR, f'{conference_key}_papers.json')


def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(SAMPLE_DATA_DIR, exist_ok=True)


if __name__ == '__main__':
    # Test configuration
    print("CS Conference Tag Cloud Configuration")
    print("=" * 50)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Raw Data: {RAW_DATA_DIR}")
    print(f"Processed Data: {PROCESSED_DATA_DIR}")
    print(f"\nDefault Conference: {DEFAULT_CONFERENCE}")
    print(f"Available Conferences: {list(CONFERENCES.keys())}")
    print(f"\nKDD Config: {get_conference_config('kdd')}")
    print(f"\nTotal Stopwords: {len(STOPWORDS)}")
    print(f"Total Keep Terms: {len(KEEP_TERMS)}")
