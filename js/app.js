/**
 * Main Application Logic
 * Handles data loading, filtering, and UI updates
 */

class App {
    constructor() {
        this.data = null;
        this.filteredData = null;
        this.wordCloud = null;
        this.filters = {
            year: 'all',
            category: 'all'
        };

        this.init();
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            // Show loading state
            this.showLoading();

            // Initialize word cloud
            this.wordCloud = new WordCloud('wordcloud');
            window.wordCloudInstance = this.wordCloud;

            // Load data
            await this.loadData();

            // Setup event listeners
            this.setupEventListeners();

            // Initial render
            this.applyFilters();

            // Hide loading
            this.hideLoading();
        } catch (error) {
            console.error('Error initializing app:', error);
            this.showError(error.message);
        }
    }

    /**
     * Load data from JSON file
     */
    async loadData() {
        try {
            // Try to load processed data first, fallback to sample data
            let dataPath = 'data/processed/wordcloud_data.json';

            let response = await fetch(dataPath);

            // If processed data doesn't exist, use sample data
            if (!response.ok) {
                console.log('Processed data not found, using sample data');
                dataPath = 'data/sample/wordcloud_sample.json';
                response = await fetch(dataPath);
            }

            if (!response.ok) {
                throw new Error(`Failed to load data: ${response.statusText}`);
            }

            this.data = await response.json();
            this.filteredData = this.data;

            // Update UI with metadata
            this.updateMetadata();

            console.log('Data loaded successfully:', this.data);
        } catch (error) {
            console.error('Error loading data:', error);
            throw error;
        }
    }

    /**
     * Update metadata display
     */
    updateMetadata() {
        const { metadata } = this.data;

        // Conference name
        document.getElementById('conference-name').textContent = metadata.conference || 'N/A';

        // Category badge
        const categoryBadge = document.getElementById('conference-category');
        if (metadata.categories && metadata.categories.length > 0) {
            categoryBadge.textContent = metadata.categories.join(', ');
        }

        // Total papers
        document.getElementById('total-papers').textContent =
            metadata.total_papers ? metadata.total_papers.toLocaleString() : '-';

        // Total keywords
        document.getElementById('total-keywords').textContent =
            metadata.total_keywords ? metadata.total_keywords.toLocaleString() : '-';

        // Last updated
        document.getElementById('last-updated').textContent =
            metadata.last_updated || '-';
    }

    /**
     * Setup event listeners for filters
     */
    setupEventListeners() {
        // Year filter
        document.getElementById('year-filter').addEventListener('change', (e) => {
            this.filters.year = e.target.value;
            this.applyFilters();
        });

        // Category filter
        document.getElementById('category-filter').addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.applyFilters();
        });

        // Reset filters button
        document.getElementById('reset-filters').addEventListener('click', () => {
            this.resetFilters();
        });
    }

    /**
     * Apply current filters to data
     */
    applyFilters() {
        if (!this.data || !this.data.words) {
            console.error('No data available to filter');
            return;
        }

        let filteredWords = [...this.data.words];

        // Apply year filter
        if (this.filters.year !== 'all') {
            const selectedYear = this.filters.year;
            filteredWords = filteredWords
                .map(word => {
                    // Calculate value for selected year
                    const yearValue = word.years && word.years[selectedYear]
                        ? word.years[selectedYear]
                        : 0;

                    return {
                        ...word,
                        value: yearValue,
                        originalValue: word.value
                    };
                })
                .filter(word => word.value > 0); // Only keep words that appear in selected year
        }

        // Apply category filter (conference-level)
        // For now, this filters at the data source level
        // In future with multiple conferences, this would filter which conferences to show
        if (this.filters.category !== 'all') {
            const categories = this.data.metadata.categories || [];
            if (!categories.includes(this.filters.category)) {
                filteredWords = []; // No match, clear results
            }
        }

        // Sort by value (descending) and limit to top 100 for performance
        filteredWords.sort((a, b) => b.value - a.value);
        filteredWords = filteredWords.slice(0, 100);

        console.log('Filtered words:', filteredWords.length);

        // Update word cloud
        this.wordCloud.update(filteredWords);

        // Update keyword count
        document.getElementById('total-keywords').textContent = filteredWords.length;
    }

    /**
     * Reset all filters
     */
    resetFilters() {
        this.filters.year = 'all';
        this.filters.category = 'all';

        // Reset UI
        document.getElementById('year-filter').value = 'all';
        document.getElementById('category-filter').value = 'all';

        // Reset metadata display
        this.updateMetadata();

        // Reapply filters (which will show all data)
        this.applyFilters();
    }

    /**
     * Show loading state
     */
    showLoading() {
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('wordcloud').style.display = 'none';
        document.getElementById('error').style.display = 'none';
    }

    /**
     * Hide loading state
     */
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('wordcloud').style.display = 'block';
    }

    /**
     * Show error state
     */
    showError(message) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('wordcloud').style.display = 'none';
        const errorEl = document.getElementById('error');
        errorEl.style.display = 'block';
        errorEl.querySelector('p').textContent = message || 'An error occurred';
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing CS Conference Tag Cloud...');
    window.app = new App();
});
