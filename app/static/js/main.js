/* ============================================
   AGENTIC CANVAS - MAIN JAVASCRIPT
   ============================================ */

// Global Application State
const AppState = {
    socket: null,
    charts: {},
    simulator: {
        running: false,
        interval: null
    }
};

// Initialize Socket.IO Connection
const socket = io({
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5
});

AppState.socket = socket;

/* ============================================
   UTILITY FUNCTIONS
   ============================================ */

const Utils = {
    /**
     * Format number with commas
     */
    formatNumber: (num, decimals = 0) => {
        return parseFloat(num).toLocaleString('en-US', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    },
    
    /**
     * Format currency
     */
    formatCurrency: (amount, currency = 'USD') => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        }).format(amount);
    },
    
    /**
     * Format date/time
     */
    formatDateTime: (dateString, includeTime = true) => {
        const date = new Date(dateString);
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        };
        
        if (includeTime) {
            options.hour = '2-digit';
            options.minute = '2-digit';
        }
        
        return date.toLocaleDateString('en-US', options);
    },
    
    /**
     * Show toast notification
     */
    showToast: (message, type = 'info', duration = 3000) => {
        const iconMap = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        
        const icon = iconMap[type] || iconMap.info;
        
        const toastHtml = `
            <div class="toast align-items-center text-bg-${type} border-0" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi bi-${icon} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement, { delay: duration });
        toast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    },
    
    /**
     * Show loading state
     */
    showLoading: (element, show = true) => {
        if (show) {
            element.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-muted">Loading data...</p>
                </div>
            `;
        }
    },
    
    /**
     * API call wrapper with error handling
     */
    apiCall: async (url, options = {}) => {
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || data.message || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            Utils.showToast(error.message, 'danger');
            throw error;
        }
    },
    
    /**
     * Debounce function calls
     */
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    /**
     * Copy text to clipboard
     */
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            Utils.showToast('Copied to clipboard', 'success');
        } catch (error) {
            Utils.showToast('Failed to copy', 'danger');
        }
    }
};

/* ============================================
   CHART HELPERS
   ============================================ */

const ChartHelpers = {
    /**
     * Default chart options with vibrant theme
     */
    defaultOptions: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',
            intersect: false
        },
        plugins: {
            legend: {
                labels: {
                    color: '#1a202c',
                    font: {
                        size: 12,
                        weight: '600'
                    },
                    padding: 18,
                    usePointStyle: true,
                    pointStyle: 'circle'
                }
            },
            tooltip: {
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                titleColor: '#1a202c',
                bodyColor: '#4a5568',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                padding: 16,
                displayColors: true,
                cornerRadius: 8,
                shadowOffsetX: 0,
                shadowOffsetY: 4,
                shadowBlur: 12,
                shadowColor: 'rgba(0, 0, 0, 0.15)',
                callbacks: {
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += Utils.formatNumber(context.parsed.y, 2);
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            y: {
                ticks: { 
                    color: '#4a5568',
                    font: { size: 11, weight: '500' }
                },
                grid: { 
                    color: '#edf2f7',
                    drawBorder: false
                }
            },
            x: {
                ticks: { 
                    color: '#4a5568',
                    font: { size: 11, weight: '500' }
                },
                grid: { 
                    color: '#edf2f7',
                    drawBorder: false
                }
            }
        }
    },
    
    /**
     * Color schemes for charts
     */
    colors: {
        primary: '#0066ff',
        secondary: '#4285f4',
        success: '#00c851',
        warning: '#ff9500',
        danger: '#ff3547',
        info: '#00bcd4',
        purple: '#9c27b0',
        orange: '#ff6f00'
    },
    
    /**
     * Create line chart
     */
    createLineChart: (ctx, data, customOptions = {}) => {
        const options = {
            ...ChartHelpers.defaultOptions,
            ...customOptions
        };
        
        return new Chart(ctx, {
            type: 'line',
            data: data,
            options: options
        });
    },
    
    /**
     * Create bar chart
     */
    createBarChart: (ctx, data, customOptions = {}) => {
        const options = {
            ...ChartHelpers.defaultOptions,
            ...customOptions
        };
        
        return new Chart(ctx, {
            type: 'bar',
            data: data,
            options: options
        });
    },
    
    /**
     * Create doughnut chart
     */
    createDoughnutChart: (ctx, data, customOptions = {}) => {
        const options = {
            ...ChartHelpers.defaultOptions,
            ...customOptions,
            plugins: {
                ...ChartHelpers.defaultOptions.plugins,
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#1a202c',
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        };
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: options
        });
    },
    
    /**
     * Update chart data dynamically
     */
    updateChart: (chart, newData) => {
        if (!chart) return;
        
        chart.data.labels = newData.labels;
        chart.data.datasets.forEach((dataset, i) => {
            dataset.data = newData.datasets[i].data;
        });
        chart.update('none'); // Update without animation for real-time data
    },
    
    /**
     * Destroy chart safely
     */
    destroyChart: (chartId) => {
        if (AppState.charts[chartId]) {
            AppState.charts[chartId].destroy();
            delete AppState.charts[chartId];
        }
    }
};

/* ============================================
   SOCKET.IO EVENT HANDLERS
   ============================================ */

socket.on('connect', () => {
    console.log('✅ Connected to server');
    Utils.showToast('Real-time connection established', 'success');
});

socket.on('disconnect', () => {
    console.log('❌ Disconnected from server');
    Utils.showToast('Connection lost. Attempting to reconnect...', 'warning');
});

socket.on('connect_error', (error) => {
    console.error('Connection error:', error);
});

socket.on('demo_update', (data) => {
    console.log('📡 Demo update received:', data);
    // Dispatch custom event for demo-specific handlers
    document.dispatchEvent(new CustomEvent('demoUpdate', { 
        detail: data 
    }));
});

socket.on('agent_status', (data) => {
    console.log('🤖 Agent status:', data);
    document.dispatchEvent(new CustomEvent('agentStatusUpdate', { 
        detail: data 
    }));
});

/* ============================================
   AUTO-REFRESH FUNCTIONALITY
   ============================================ */

/**
 * Start auto-refreshing data
 */
function startAutoRefresh(callback, interval = 5000) {
    // Clear any existing interval
    if (AppState.simulator.interval) {
        clearInterval(AppState.simulator.interval);
    }
    
    // Start new interval
    const refreshInterval = setInterval(callback, interval);
    
    // Store interval ID
    AppState.simulator.interval = refreshInterval;
    AppState.simulator.running = true;
    
    console.log(`🔄 Auto-refresh started (${interval}ms interval)`);
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        stopAutoRefresh();
    });
    
    return refreshInterval;
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (AppState.simulator.interval) {
        clearInterval(AppState.simulator.interval);
        AppState.simulator.interval = null;
        AppState.simulator.running = false;
        console.log('⏹️ Auto-refresh stopped');
    }
}

/* ============================================
   DEMO-SPECIFIC HELPERS
   ============================================ */

/**
 * Initialize metric cards with animation
 */
function animateMetricCards() {
    const cards = document.querySelectorAll('.metric-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fade-in');
    });
}

/**
 * Handle agent action buttons
 */
function setupAgentActions() {
    const actionButtons = document.querySelectorAll('[data-agent-action]');
    actionButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const action = this.dataset.agentAction;
            const endpoint = this.dataset.endpoint;
            
            this.disabled = true;
            this.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
            
            try {
                const result = await Utils.apiCall(endpoint, {
                    method: 'POST',
                    body: JSON.stringify({ action })
                });
                
                Utils.showToast(result.message || 'Action completed', 'success');
                
                // Refresh data after action
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                Utils.showToast('Action failed', 'danger');
            } finally {
                this.disabled = false;
                this.innerHTML = this.dataset.originalText || 'Execute';
            }
        });
    });
}

/* ============================================
   INITIALIZATION
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Agentic Canvas Initialized');
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map(el => new bootstrap.Tooltip(el));
    
    // Initialize popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    [...popoverTriggerList].map(el => new bootstrap.Popover(el));
    
    // Animate metric cards if present
    if (document.querySelectorAll('.metric-card').length > 0) {
        animateMetricCards();
    }
    
    // Setup agent action buttons
    setupAgentActions();
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

/* ============================================
   EXPORT TO WINDOW
   ============================================ */

window.AppState = AppState;
window.Utils = Utils;
window.ChartHelpers = ChartHelpers;
window.startAutoRefresh = startAutoRefresh;
window.stopAutoRefresh = stopAutoRefresh;

console.log('📦 Agentic Canvas utilities loaded successfully');