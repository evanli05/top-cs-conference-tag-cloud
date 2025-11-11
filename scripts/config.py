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

# Log directories
LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
PROGRESS_LOG_DIR = os.path.join(LOG_DIR, 'progress')

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
# AI Parent Area Conferences (CSRankings)
# ===================================

CONFERENCES = {
    # ===================================
    # Machine Learning
    # ===================================
    'kdd': {
        'name': 'KDD',
        'full_name': 'ACM SIGKDD Conference on Knowledge Discovery and Data Mining',
        'dblp_venue': 'kdd',
        'categories': ['Machine Learning'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'iclr': {
        'name': 'ICLR',
        'full_name': 'International Conference on Learning Representations',
        'dblp_venue': 'iclr',
        'categories': ['Machine Learning'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'icml': {
        'name': 'ICML',
        'full_name': 'International Conference on Machine Learning',
        'dblp_venue': 'icml',
        'categories': ['Machine Learning'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'neurips': {
        'name': 'NeurIPS',
        'full_name': 'Conference on Neural Information Processing Systems',
        'dblp_venue': 'neurips',  # Filename prefix (e.g., neurips2024.html)
        'dblp_dir': 'nips',  # Directory in DBLP URL (e.g., /conf/nips/)
        'categories': ['Machine Learning'],
        'years': [2020, 2021, 2022, 2023, 2024]  # 2025 not available yet
    },

    # ===================================
    # Artificial Intelligence
    # ===================================
    'aaai': {
        'name': 'AAAI',
        'full_name': 'AAAI Conference on Artificial Intelligence',
        'dblp_venue': 'aaai',
        'categories': ['Artificial Intelligence'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'ijcai': {
        'name': 'IJCAI',
        'full_name': 'International Joint Conference on Artificial Intelligence',
        'dblp_venue': 'ijcai',
        'categories': ['Artificial Intelligence'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },

    # ===================================
    # Computer Vision
    # ===================================
    'cvpr': {
        'name': 'CVPR',
        'full_name': 'IEEE/CVF Conference on Computer Vision and Pattern Recognition',
        'dblp_venue': 'cvpr',
        'categories': ['Computer Vision'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'eccv': {
        'name': 'ECCV',
        'full_name': 'European Conference on Computer Vision',
        'dblp_venue': 'eccv',
        'categories': ['Computer Vision'],
        'years': [2020, 2022, 2024]  # Biennial conference (even years only)
    },
    'iccv': {
        'name': 'ICCV',
        'full_name': 'IEEE International Conference on Computer Vision',
        'dblp_venue': 'iccv',
        'categories': ['Computer Vision'],
        'years': [2021, 2023, 2025]  # Biennial conference (odd years only)
    },

    # ===================================
    # Natural Language Processing
    # ===================================
    'acl': {
        'name': 'ACL',
        'full_name': 'Annual Meeting of the Association for Computational Linguistics',
        'dblp_venue': 'acl',
        'categories': ['Natural Language Processing'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'emnlp': {
        'name': 'EMNLP',
        'full_name': 'Conference on Empirical Methods in Natural Language Processing',
        'dblp_venue': 'emnlp',
        'categories': ['Natural Language Processing'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'naacl': {
        'name': 'NAACL',
        'full_name': 'North American Chapter of the Association for Computational Linguistics',
        'dblp_venue': 'naacl',
        'categories': ['Natural Language Processing'],
        'years': [2021, 2022, 2024, 2025]  # Not held every year
    },

    # ===================================
    # The Web & Information Retrieval
    # ===================================
    'sigir': {
        'name': 'SIGIR',
        'full_name': 'International ACM SIGIR Conference on Research and Development in Information Retrieval',
        'dblp_venue': 'sigir',
        'categories': ['The Web & Information Retrieval'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
    'www': {
        'name': 'WWW',
        'full_name': 'The Web Conference',
        'dblp_venue': 'www',
        'categories': ['The Web & Information Retrieval'],
        'years': [2020, 2021, 2022, 2023, 2024, 2025]
    },
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
DEFAULT_CONFERENCE = 'cvpr'  # Currently fetching CVPR abstracts with title-based fallback

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
SEMANTIC_SCHOLAR_SEARCH_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
SEMANTIC_SCHOLAR_RATE_LIMIT = 1.0  # 1 request every 5 second (aligns with authenticated search endpoint limit)
SEMANTIC_SCHOLAR_FIELDS = "abstract,citationCount"
SEMANTIC_SCHOLAR_TIMEOUT = 10  # API request timeout in seconds

# OpenReview API Configuration (For conferences using OpenReview platform)
OPENREVIEW_API_V1_URL = "https://api.openreview.net"  # For conferences 2023 and earlier
OPENREVIEW_API_V2_URL = "https://api2.openreview.net"  # For conferences 2024 and later
OPENREVIEW_RATE_LIMIT = 1.0  # 1 request per second (polite rate limiting)
OPENREVIEW_TIMEOUT = 10  # API request timeout in seconds
OPENREVIEW_API_V2_YEAR_THRESHOLD = 2024  # Conferences from 2024+ use API v2
OPENREVIEW_SEARCH_ENABLED = True  # Enable searching for papers by title if ID missing

# Map conferences to OpenReview venue IDs
OPENREVIEW_VENUES = {
    'iclr': 'ICLR.cc',
    'icml': 'ICML.cc',
}

# NeurIPS Proceedings Configuration (For conferences 2020-2024 without OpenReview)
# NeurIPS publishes conference proceedings at proceedings.nips.cc
# Papers can be accessed directly using hash extracted from DBLP links
NEURIPS_PROCEEDINGS_BASE_URL = "https://proceedings.nips.cc"
NEURIPS_PROCEEDINGS_RATE_LIMIT = 2  # 2 requests per second (reduced from 4 for more conservative rate limiting)
NEURIPS_PROCEEDINGS_TIMEOUT = 10  # API request timeout in seconds

# ===================================
# Progress Logging & Recovery
# ===================================

# Progress logging intervals
DBLP_PROGRESS_LOG_INTERVAL = 1000  # Log every N papers during DBLP fetching
ABSTRACT_PROGRESS_LOG_INTERVAL = 100  # Log every N abstracts fetched
INCREMENTAL_SAVE_INTERVAL = 100  # Save JSON every N abstracts fetched

# Enable incremental saves and recovery
ENABLE_INCREMENTAL_SAVES = True  # Save partial results during fetching
ENABLE_RECOVERY_MODE = True  # Skip papers with existing abstracts on restart

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
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(PROGRESS_LOG_DIR, exist_ok=True)


def get_progress_log_file(conference_key: str) -> str:
    """
    Get progress log file path for a conference

    Args:
        conference_key (str): Conference identifier (e.g., 'neurips', 'cvpr')

    Returns:
        str: Full path to progress log file
    """
    ensure_directories()  # Ensure logs directory exists
    return os.path.join(PROGRESS_LOG_DIR, f'{conference_key}_progress.log')


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
