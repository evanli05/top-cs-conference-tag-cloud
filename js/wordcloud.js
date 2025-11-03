/**
 * Word Cloud Visualization Module
 * Uses D3.js and d3-cloud to render interactive word clouds
 */

class WordCloud {
    constructor(containerId) {
        this.container = d3.select(`#${containerId}`);
        this.width = 0;
        this.height = 0;
        this.svg = null;
        this.tooltip = d3.select('#tooltip');
        this.currentWords = [];

        // Color scale for word cloud
        this.colorScale = d3.scaleOrdinal()
            .range([
                '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd',
                '#0ea5e9', '#06b6d4', '#14b8a6', '#10b981',
                '#6366f1', '#8b5cf6', '#a855f7', '#d946ef'
            ]);

        this.init();
    }

    /**
     * Initialize the SVG container
     */
    init() {
        // Clear any existing SVG
        this.container.selectAll('*').remove();

        // Get container dimensions
        const containerNode = this.container.node();
        const rect = containerNode.getBoundingClientRect();
        this.width = rect.width || 800;
        this.height = rect.height || 600;

        // Create SVG
        this.svg = this.container
            .append('svg')
            .attr('width', '100%')
            .attr('height', '100%')
            .attr('viewBox', `0 0 ${this.width} ${this.height}`)
            .attr('preserveAspectRatio', 'xMidYMid meet');

        // Create group for word cloud (centered)
        this.wordGroup = this.svg
            .append('g')
            .attr('transform', `translate(${this.width / 2}, ${this.height / 2})`);
    }

    /**
     * Render word cloud with given data
     * @param {Array} words - Array of {text, value, years} objects
     */
    render(words) {
        if (!words || words.length === 0) {
            this.showEmptyState();
            return;
        }

        this.currentWords = words;

        // Calculate font sizes
        const maxValue = d3.max(words, d => d.value);
        const minValue = d3.min(words, d => d.value);

        // Font size scale
        const fontSizeScale = d3.scaleLinear()
            .domain([minValue, maxValue])
            .range([16, 80]);

        // Prepare data for d3-cloud
        const cloudWords = words.map(w => ({
            text: w.text,
            size: fontSizeScale(w.value),
            value: w.value,
            years: w.years,
            color: this.colorScale(w.text)
        }));

        // Create word cloud layout
        const layout = d3.layout.cloud()
            .size([this.width, this.height])
            .words(cloudWords)
            .padding(5)
            .rotate(() => (Math.random() > 0.7 ? 90 : 0)) // Mostly horizontal, some vertical
            .font('sans-serif')
            .fontSize(d => d.size)
            .on('end', (words) => this.draw(words));

        layout.start();
    }

    /**
     * Draw the word cloud
     * @param {Array} words - Positioned words from d3-cloud
     */
    draw(words) {
        // Clear previous words
        this.wordGroup.selectAll('*').remove();

        // Draw words
        const text = this.wordGroup
            .selectAll('text')
            .data(words)
            .enter()
            .append('text')
            .attr('class', 'word')
            .style('font-size', d => `${d.size}px`)
            .style('font-family', 'sans-serif')
            .style('font-weight', '600')
            .style('fill', d => d.color)
            .attr('text-anchor', 'middle')
            .attr('transform', d => `translate(${d.x}, ${d.y}) rotate(${d.rotate})`)
            .text(d => d.text)
            .style('opacity', 0);

        // Animate appearance
        text.transition()
            .duration(600)
            .style('opacity', 1);

        // Add interactivity
        text
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mousemove', (event, d) => this.moveTooltip(event))
            .on('mouseout', () => this.hideTooltip())
            .on('click', (event, d) => this.onWordClick(d));
    }

    /**
     * Show tooltip on hover
     */
    showTooltip(event, data) {
        // Update tooltip content
        d3.select('#tooltip-word').text(data.text);
        d3.select('#tooltip-total').text(data.value);

        // Format years breakdown
        if (data.years) {
            const yearsHtml = Object.entries(data.years)
                .sort((a, b) => b[0] - a[0]) // Sort by year descending
                .map(([year, count]) => `${year}: ${count}`)
                .join(' | ');
            d3.select('#tooltip-years').html(yearsHtml);
        }

        // Show tooltip
        this.tooltip
            .style('display', 'block')
            .style('left', `${event.pageX + 15}px`)
            .style('top', `${event.pageY - 10}px`);
    }

    /**
     * Move tooltip with cursor
     */
    moveTooltip(event) {
        this.tooltip
            .style('left', `${event.pageX + 15}px`)
            .style('top', `${event.pageY - 10}px`);
    }

    /**
     * Hide tooltip
     */
    hideTooltip() {
        this.tooltip.style('display', 'none');
    }

    /**
     * Handle word click (can be extended later)
     */
    onWordClick(data) {
        console.log('Clicked word:', data.text, 'Value:', data.value);
        // Future: Show papers containing this keyword
    }

    /**
     * Show empty state when no data
     */
    showEmptyState() {
        this.wordGroup.selectAll('*').remove();

        this.wordGroup
            .append('text')
            .attr('text-anchor', 'middle')
            .attr('dy', '0.35em')
            .style('font-size', '1.25rem')
            .style('fill', '#94a3b8')
            .text('No keywords found for selected filters');
    }

    /**
     * Update word cloud with new data (with transition)
     */
    update(words) {
        this.render(words);
    }

    /**
     * Resize word cloud (call on window resize)
     */
    resize() {
        this.init();
        if (this.currentWords.length > 0) {
            this.render(this.currentWords);
        }
    }
}

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (window.wordCloudInstance) {
            window.wordCloudInstance.resize();
        }
    }, 250);
});
