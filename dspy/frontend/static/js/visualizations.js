/**
 * DSPy Frontend Visualizations
 * 
 * This file contains visualization components for the DSPy frontend dashboard.
 * It uses Chart.js for creating interactive charts and visualizations.
 */

/**
 * Create a responsive line chart for time series data
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data object with labels and datasets
 * @param {object} options - Chart options
 * @returns {Chart} Chart.js instance
 */
function createLineChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default options with sensible defaults
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            },
            title: {
                display: false,
            },
        },
        scales: {
            x: {
                ticks: {
                    maxRotation: 0,
                },
                grid: {
                    display: true,
                    drawBorder: true,
                    drawOnChartArea: true,
                    drawTicks: true,
                },
            },
            y: {
                beginAtZero: true,
                grid: {
                    drawBorder: true,
                    display: true,
                    drawOnChartArea: true,
                    drawTicks: true,
                },
            }
        },
        interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
        },
        elements: {
            line: {
                tension: 0.3, // Smoother curve
            },
            point: {
                radius: 3,
                hoverRadius: 5,
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create and return the chart
    return new Chart(ctx, {
        type: 'line',
        data: data,
        options: chartOptions
    });
}

/**
 * Create a doughnut chart for category distributions
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data object with labels and datasets
 * @param {object} options - Chart options
 * @returns {Chart} Chart.js instance
 */
function createDoughnutChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: ${percentage}% (${value})`;
                    }
                }
            },
        },
        cutout: '60%',
        animation: {
            animateScale: true,
            animateRotate: true
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create and return the chart
    return new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: chartOptions
    });
}

/**
 * Create a bar chart for comparison data
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data object with labels and datasets
 * @param {object} options - Chart options
 * @returns {Chart} Chart.js instance
 */
function createBarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            },
        },
        scales: {
            x: {
                grid: {
                    display: false,
                },
            },
            y: {
                beginAtZero: true,
                grid: {
                    borderDash: [2, 2],
                },
            }
        },
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create and return the chart
    return new Chart(ctx, {
        type: 'bar',
        data: data,
        options: chartOptions
    });
}

/**
 * Create a radar chart for multi-dimensional metrics
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data object with labels and datasets
 * @param {object} options - Chart options
 * @returns {Chart} Chart.js instance
 */
function createRadarChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `${context.dataset.label}: ${context.raw.toFixed(2)}`;
                    }
                }
            },
        },
        scales: {
            r: {
                angleLines: {
                    display: true,
                    color: 'rgba(0, 0, 0, 0.1)',
                },
                suggestedMin: 0,
                suggestedMax: 1,
                ticks: {
                    backdropColor: 'rgba(0, 0, 0, 0)',
                    precision: 1
                }
            }
        },
        elements: {
            line: {
                borderWidth: 2
            },
            point: {
                radius: 3,
                hoverRadius: 5
            }
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create and return the chart
    return new Chart(ctx, {
        type: 'radar',
        data: data,
        options: chartOptions
    });
}

/**
 * Create a scatter plot for correlation data
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {object} data - Chart data object with datasets
 * @param {object} options - Chart options
 * @returns {Chart} Chart.js instance
 */
function createScatterChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const point = context.raw;
                        return `${context.dataset.label} (${point.x.toFixed(2)}, ${point.y.toFixed(2)})`;
                    }
                }
            },
        },
        scales: {
            x: {
                type: 'linear',
                position: 'bottom',
                title: {
                    display: true,
                    text: 'X Axis'
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Y Axis'
                }
            }
        },
        animation: {
            duration: 1000
        }
    };
    
    // Merge options
    const chartOptions = { ...defaultOptions, ...options };
    
    // Create and return the chart
    return new Chart(ctx, {
        type: 'scatter',
        data: data,
        options: chartOptions
    });
}

/**
 * Create a heatmap for matrix data
 * 
 * @param {string} containerId - Container element ID (not canvas - will be created)
 * @param {Array} data - 2D array of values
 * @param {Array} rowLabels - Array of row labels
 * @param {Array} colLabels - Array of column labels
 * @param {object} options - Heatmap options
 */
function createHeatmap(containerId, data, rowLabels, colLabels, options = {}) {
    // Default options
    const defaultOptions = {
        colorScale: ['#FFFFFF', '#3B82F6', '#1E40AF'],
        cellSize: 30,
        fontSize: 12,
        showValues: true,
        valueSuffix: '',
        title: '',
    };
    
    // Merge options
    const heatmapOptions = { ...defaultOptions, ...options };
    
    // Get the container
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear container
    
    // Create title if provided
    if (heatmapOptions.title) {
        const titleEl = document.createElement('h3');
        titleEl.className = 'text-center font-medium mb-4';
        titleEl.textContent = heatmapOptions.title;
        container.appendChild(titleEl);
    }
    
    // Create the heatmap table
    const table = document.createElement('table');
    table.className = 'heatmap-table mx-auto border-collapse';
    
    // Add header row with column labels
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    // Add empty cell for top-left corner
    const cornerCell = document.createElement('th');
    cornerCell.className = 'px-2 py-1 text-center';
    headerRow.appendChild(cornerCell);
    
    // Add column headers
    colLabels.forEach(label => {
        const th = document.createElement('th');
        th.className = 'px-2 py-1 text-center font-medium';
        th.style.width = `${heatmapOptions.cellSize}px`;
        th.textContent = label;
        headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Create color scale function
    const colorScale = (value) => {
        // Find min and max values
        const flatData = data.flat();
        const min = Math.min(...flatData);
        const max = Math.max(...flatData);
        
        // Normalize value between 0 and 1
        const normalized = (value - min) / (max - min || 1);
        
        // Interpolate between colors
        if (normalized <= 0) return heatmapOptions.colorScale[0];
        if (normalized >= 1) return heatmapOptions.colorScale[heatmapOptions.colorScale.length - 1];
        
        // Find position in color scale
        const position = normalized * (heatmapOptions.colorScale.length - 1);
        const index = Math.floor(position);
        const fraction = position - index;
        
        // Interpolate between colors
        const color1 = hexToRgb(heatmapOptions.colorScale[index]);
        const color2 = hexToRgb(heatmapOptions.colorScale[index + 1]);
        
        const r = Math.round(color1.r + fraction * (color2.r - color1.r));
        const g = Math.round(color1.g + fraction * (color2.g - color1.g));
        const b = Math.round(color1.b + fraction * (color2.b - color1.b));
        
        return `rgb(${r}, ${g}, ${b})`;
    };
    
    // Add data rows
    const tbody = document.createElement('tbody');
    data.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        
        // Add row label
        const rowLabel = document.createElement('th');
        rowLabel.className = 'px-2 py-1 text-right font-medium';
        rowLabel.textContent = rowLabels[rowIndex];
        tr.appendChild(rowLabel);
        
        // Add data cells
        row.forEach((value, colIndex) => {
            const td = document.createElement('td');
            td.className = 'text-center';
            td.style.backgroundColor = colorScale(value);
            td.style.width = `${heatmapOptions.cellSize}px`;
            td.style.height = `${heatmapOptions.cellSize}px`;
            
            // Determine text color based on background brightness
            const rgb = hexToRgb(colorScale(value));
            const brightness = (rgb.r * 299 + rgb.g * 587 + rgb.b * 114) / 1000;
            td.style.color = brightness > 125 ? 'black' : 'white';
            
            // Add value text if showValues is true
            if (heatmapOptions.showValues) {
                td.textContent = `${value}${heatmapOptions.valueSuffix}`;
                td.style.fontSize = `${heatmapOptions.fontSize}px`;
            }
            
            // Add tooltip
            td.title = `${rowLabels[rowIndex]} / ${colLabels[colIndex]}: ${value}${heatmapOptions.valueSuffix}`;
            
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
    
    table.appendChild(tbody);
    container.appendChild(table);
}

/**
 * Helper function to convert hex color to RGB
 * 
 * @param {string} hex - Hex color code
 * @returns {object} RGB color object
 */
function hexToRgb(hex) {
    // Handle rgb format
    if (hex.startsWith('rgb')) {
        const match = hex.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
        if (match) {
            return {
                r: parseInt(match[1], 10),
                g: parseInt(match[2], 10),
                b: parseInt(match[3], 10)
            };
        }
    }
    
    // Handle hex format
    hex = hex.replace(/^#/, '');
    
    // Handle 3-digit hex
    if (hex.length === 3) {
        hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    }
    
    const bigint = parseInt(hex, 16);
    return {
        r: (bigint >> 16) & 255,
        g: (bigint >> 8) & 255,
        b: bigint & 255
    };
}

/**
 * Create a progress bar visualization
 * 
 * @param {string} containerId - Container element ID
 * @param {number} value - Current value
 * @param {number} maxValue - Maximum value
 * @param {object} options - Progress bar options
 */
function createProgressBar(containerId, value, maxValue, options = {}) {
    // Default options
    const defaultOptions = {
        height: '12px',
        backgroundColor: '#e5e7eb',
        barColor: '#3b82f6',
        showPercentage: true,
        showValue: false,
        label: '',
        valuePrefix: '',
        valueSuffix: '',
        animate: true,
    };
    
    // Merge options
    const progressOptions = { ...defaultOptions, ...options };
    
    // Calculate percentage
    const percentage = Math.min(100, Math.max(0, (value / maxValue) * 100));
    
    // Get container
    const container = document.getElementById(containerId);
    container.innerHTML = ''; // Clear container
    
    // Create progress bar container
    const progressContainer = document.createElement('div');
    progressContainer.className = 'w-full';
    
    // Add label if provided
    if (progressOptions.label) {
        const labelContainer = document.createElement('div');
        labelContainer.className = 'flex justify-between mb-1';
        
        const label = document.createElement('span');
        label.className = 'text-sm font-medium text-gray-700';
        label.textContent = progressOptions.label;
        labelContainer.appendChild(label);
        
        // Add value text if showValue is true
        if (progressOptions.showValue) {
            const valueText = document.createElement('span');
            valueText.className = 'text-sm font-medium text-gray-700';
            valueText.textContent = `${progressOptions.valuePrefix}${value}${progressOptions.valueSuffix} / ${maxValue}${progressOptions.valueSuffix}`;
            labelContainer.appendChild(valueText);
        }
        
        progressContainer.appendChild(labelContainer);
    }
    
    // Create progress bar
    const progressBar = document.createElement('div');
    progressBar.className = 'w-full bg-gray-200 rounded-full';
    progressBar.style.height = progressOptions.height;
    progressBar.style.backgroundColor = progressOptions.backgroundColor;
    
    // Create progress bar fill
    const progressFill = document.createElement('div');
    progressFill.className = 'rounded-full';
    progressFill.style.height = '100%';
    progressFill.style.backgroundColor = progressOptions.barColor;
    progressFill.style.width = progressOptions.animate ? '0%' : `${percentage}%`;
    
    // Add percentage text if showPercentage is true
    if (progressOptions.showPercentage) {
        progressFill.textContent = `${Math.round(percentage)}%`;
        progressFill.className += ' text-center text-xs text-white';
    }
    
    progressBar.appendChild(progressFill);
    progressContainer.appendChild(progressBar);
    container.appendChild(progressContainer);
    
    // Animate the progress bar fill
    if (progressOptions.animate) {
        setTimeout(() => {
            progressFill.style.transition = 'width 1s ease-in-out';
            progressFill.style.width = `${percentage}%`;
        }, 50);
    }
}

/**
 * Create a gauge chart for single metrics
 * 
 * @param {string} canvasId - Canvas element ID
 * @param {number} value - Current value
 * @param {number} maxValue - Maximum value
 * @param {object} options - Gauge options
 * @returns {Chart} Chart.js instance
 */
function createGaugeChart(canvasId, value, maxValue, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    // Default options
    const defaultOptions = {
        title: '',
        valueLabel: '',
        colorRanges: [
            { min: 0, max: 33, color: '#ef4444' },   // Red
            { min: 33, max: 67, color: '#f59e0b' },  // Yellow
            { min: 67, max: 100, color: '#10b981' }, // Green
        ],
    };
    
    // Merge options
    const gaugeOptions = { ...defaultOptions, ...options };
    
    // Calculate percentage
    const percentage = Math.min(100, Math.max(0, (value / maxValue) * 100));
    
    // Find color for current value
    const getColor = (percent) => {
        for (const range of gaugeOptions.colorRanges) {
            if (percent >= range.min && percent <= range.max) {
                return range.color;
            }
        }
        return gaugeOptions.colorRanges[gaugeOptions.colorRanges.length - 1].color;
    };
    
    const color = getColor(percentage);
    
    // Create data for gauge
    const data = {
        datasets: [{
            data: [percentage, 100 - percentage],
            backgroundColor: [color, '#e5e7eb'],
            borderWidth: 0,
            circumference: 180,
            rotation: 270,
        }]
    };
    
    // Create options for gauge
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false,
            },
            tooltip: {
                enabled: false,
            },
            title: {
                display: !!gaugeOptions.title,
                text: gaugeOptions.title,
                position: 'top',
                font: {
                    size: 16,
                }
            },
        },
        cutout: '70%',
        animation: {
            animateRotate: true,
            animateScale: false,
        }
    };
    
    // Create the chart
    const chart = new Chart(ctx, {
        type: 'doughnut',
        data: data,
        options: chartOptions,
    });
    
    // Add center text
    Chart.register({
        id: 'gaugeText',
        afterDraw: function(chart) {
            const width = chart.width;
            const height = chart.height;
            const ctx = chart.ctx;
            
            ctx.restore();
            
            // Font settings for value
            const valueFontSize = Math.round(height / 10);
            ctx.font = `bold ${valueFontSize}px sans-serif`;
            ctx.textBaseline = 'middle';
            ctx.textAlign = 'center';
            
            // Draw value text
            const text = `${value}${gaugeOptions.valueLabel}`;
            const textX = width / 2;
            const textY = height - height / 3;
            ctx.fillStyle = '#333';
            ctx.fillText(text, textX, textY);
            
            // Font settings for percentage
            const percentFontSize = Math.round(height / 15);
            ctx.font = `${percentFontSize}px sans-serif`;
            
            // Draw percentage text
            const percentText = `${Math.round(percentage)}%`;
            ctx.fillStyle = '#666';
            ctx.fillText(percentText, textX, textY + valueFontSize);
            
            ctx.save();
        }
    });
    
    return chart;
}

// Export all functions
window.DSPyViz = {
    createLineChart,
    createDoughnutChart,
    createBarChart,
    createRadarChart,
    createScatterChart,
    createHeatmap,
    createProgressBar,
    createGaugeChart,
};