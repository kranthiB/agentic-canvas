/**
 * Scenario 7: Dynamic Pricing & Revenue Optimization
 * Interactive demonstration of AI-driven pricing strategy
 */

class Scenario7Controller {
    constructor() {
        this.analysisActive = false;
        this.currentCorrelationId = null;
        this.eventStreamInterval = null;
        this.priceSimulation = {
            station_id: 'CNG-002',
            time_of_day: 19,
            demand_level: 'high',
            weather: 'sunny',
            customer_tier: 'diamond'
        };
        
        this.init();
    }

    init() {
        console.log('Scenario7Controller initializing...');
        // Small delay to ensure DOM is fully rendered
        setTimeout(() => {
            this.initCharts();
            this.bindEvents();
            this.loadInitialData();
        }, 100);
    }

    bindEvents() {
        // Phase 1: Activate Analysis
        document.getElementById('btnActivateAnalysis')?.addEventListener('click', () => {
            this.startPricingAnalysis();
        });

        // Canvas close button
        document.getElementById('btnCloseCanvas')?.addEventListener('click', () => {
            this.closeAgenticCanvas();
        });

        // Show simulator button
        document.getElementById('btnShowSimulator')?.addEventListener('click', () => {
            this.showPriceSimulator();
        });

        // Price simulator controls
        this.bindSimulatorControls();
    }

    bindSimulatorControls() {
        // Station selection
        document.getElementById('stationSelect')?.addEventListener('change', (e) => {
            this.priceSimulation.station_id = e.target.value;
            this.updatePriceSimulation();
        });

        // Time slider
        const timeSlider = document.getElementById('timeSlider');
        const timeValue = document.getElementById('timeValue');
        timeSlider?.addEventListener('input', (e) => {
            const hour = parseInt(e.target.value);
            this.priceSimulation.time_of_day = hour;
            timeValue.textContent = `${hour.toString().padStart(2, '0')}:00`;
            this.updatePriceSimulation();
        });

        // Demand level
        document.getElementById('demandSelect')?.addEventListener('change', (e) => {
            this.priceSimulation.demand_level = e.target.value;
            this.updatePriceSimulation();
        });

        // Weather
        document.getElementById('weatherSelect')?.addEventListener('change', (e) => {
            this.priceSimulation.weather = e.target.value;
            this.updatePriceSimulation();
        });

        // Customer tier
        document.getElementById('customerTierSelect')?.addEventListener('change', (e) => {
            this.priceSimulation.customer_tier = e.target.value;
            this.updatePriceSimulation();
        });

        // Price breakdown toggle
        document.getElementById('btnShowBreakdown')?.addEventListener('click', () => {
            const breakdown = document.getElementById('priceBreakdown');
            if (breakdown) {
                breakdown.style.display = breakdown.style.display === 'none' ? 'block' : 'none';
            }
        });
    }

    async loadInitialData() {
        try {
            const response = await fetch('/demo4/api/scenario7/current-pricing-state');
            const data = await response.json();
            
            if (data.success) {
                this.updateOpportunityMetrics(data.pricing_analysis);
            }
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    updateOpportunityMetrics(analysis) {
        // Update the opportunity banner with real data
        const banner = document.getElementById('opportunityBanner');
        if (banner && analysis) {
            // Update efficiency score
            const efficiencyScore = banner.querySelector('[data-efficiency-score]');
            if (efficiencyScore) {
                efficiencyScore.textContent = `${analysis.network_overview.revenue_efficiency_score}/100`;
            }

            // Update inefficiency metrics
            const inefficiencies = banner.querySelectorAll('.inefficiency-item');
            analysis.inefficiencies.forEach((inefficiency, index) => {
                if (inefficiencies[index]) {
                    const impactEl = inefficiencies[index].querySelector('.inefficiency-impact');
                    const detailsEl = inefficiencies[index].querySelector('.inefficiency-details');
                    if (impactEl) impactEl.textContent = inefficiency.impact;
                    if (detailsEl) detailsEl.textContent = inefficiency.description;
                }
            });
        }
    }

    initCharts() {
        this.initStaticPricingChart();
        this.initUtilizationChart();
    }

    initStaticPricingChart() {
        const ctx = document.getElementById('staticPricingChart');
        if (!ctx) {
            console.log('Static pricing chart canvas not found');
            return;
        }

        console.log('Initializing static pricing chart');
        // Simple visualization showing uniform pricing
        try {
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Premium', 'High Traffic', 'Standard', 'Economy'],
                    datasets: [{
                        label: 'Current Price (₹/kWh)',
                        data: [16.00, 16.00, 16.00, 16.00],
                        backgroundColor: '#ef4444',
                        borderColor: '#dc2626',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 25,
                            ticks: {
                                callback: function(value) {
                                    return '₹' + value;
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        title: {
                            display: true,
                            text: 'Uniform ₹16.00 across all station tiers'
                        }
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing static pricing chart:', error);
        }
    }

    initUtilizationChart() {
        const ctx = document.getElementById('utilizationChart');
        if (!ctx) {
            console.log('Utilization chart canvas not found');
            return;
        }

        console.log('Initializing utilization chart');
        // 24-hour utilization pattern
        const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
        const utilization = [
            20, 18, 15, 12, 10, 8, 15, 85, 90, 88, // 0-9
            70, 65, 70, 75, 80, 85, 88, 92, 90, 85, // 10-19
            75, 60, 45, 30 // 20-23
        ];

        try {
            new Chart(ctx, {
            type: 'line',
            data: {
                labels: hours,
                datasets: [{
                    label: 'Utilization %',
                    data: utilization,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    title: {
                        display: true,
                        text: 'Peak: 90%+ | Off-peak: 20%'
                    },
                    annotation: {
                        annotations: {
                            peakCongestion: {
                                type: 'box',
                                xMin: 7,
                                xMax: 9,
                                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                                borderColor: '#ef4444',
                                borderWidth: 1,
                                label: {
                                    content: 'Peak Congestion',
                                    enabled: true,
                                    position: 'top'
                                }
                            },
                            wastedCapacity: {
                                type: 'box',
                                xMin: 23,
                                xMax: 6,
                                backgroundColor: 'rgba(107, 114, 128, 0.2)',
                                borderColor: '#6b7280',
                                borderWidth: 1,
                                label: {
                                    content: 'Wasted Capacity',
                                    enabled: true,
                                    position: 'bottom'
                                }
                            }
                        }
                    }
                }
            }
            });
        } catch (error) {
            console.error('Error initializing utilization chart:', error);
        }
    }

    async startPricingAnalysis() {
        if (this.analysisActive) return;

        this.analysisActive = true;
        
        // Hide opportunity banner and show agentic canvas
        document.getElementById('opportunityBanner').style.display = 'none';
        document.getElementById('problemVisualization').style.display = 'none';
        document.getElementById('agenticCanvasView').style.display = 'block';

        try {
            // Start the analysis
            const response = await fetch('/demo4/api/scenario7/run-pricing-analysis', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: 'comprehensive'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentCorrelationId = data.correlation_id;
                this.startEventStream();
            }
        } catch (error) {
            console.error('Error starting analysis:', error);
        }
    }

    startEventStream() {
        const eventStream = document.getElementById('eventStream');
        if (!eventStream) return;

        // Clear existing events
        eventStream.innerHTML = '';

        // Simulate progressive event loading
        let eventIndex = 0;
        const events = [
            { time: 0, agent: 'Orchestrator', action: 'Workflow started. Deploying 4 specialized agents for dynamic pricing analysis.', type: 'orchestrator' },
            { time: 3000, agent: 'Financial Agent', action: 'Calculating price elasticity models across 311 stations...', details: 'Querying Finance ERP and Pricing Engine', type: 'financial' },
            { time: 6000, agent: 'Geographic Agent', action: 'Classifying 311 stations by location tier and traffic patterns...', details: 'Querying Census DB and Traffic Analytics', type: 'geographic' },
            { time: 9000, agent: 'Market Agent', action: 'Segmenting customer base and analyzing pricing sensitivity...', details: 'Using RAG Engine on Vector DB of market reports', type: 'market' },
            { time: 12000, agent: 'Network Agent', action: 'Modeling demand shifting potential and capacity optimization...', details: 'Querying Grid Monitor and ML Platform', type: 'network' },
            { time: 16000, agent: 'Financial Agent', action: '✅ Price elasticity analysis complete. Identified 4 pricing tiers with 15-35% revenue potential.', type: 'financial' },
            { time: 20000, agent: 'Geographic Agent', action: '✅ Location analysis complete. 45 premium sites, 89 high-traffic, 132 standard, 45 economy tier.', type: 'geographic' },
            { time: 24000, agent: 'Market Agent', action: '✅ Customer segmentation complete. 3 loyalty tiers identified with different price sensitivities.', type: 'market' },
            { time: 28000, agent: 'Network Agent', action: '✅ Demand modeling complete. Peak shifting potential: 23% improvement in utilization.', type: 'network' },
            { time: 32000, agent: 'Orchestrator', action: 'Synthesizing agent reports using Prompt Manager template "PricingStrategy"...', type: 'orchestrator' },
            { time: 36000, agent: 'Orchestrator', action: 'Applying Guardrails for price volatility limits and customer impact assessment...', type: 'orchestrator' },
            { time: 40000, agent: 'Orchestrator', action: '✅ ANALYSIS COMPLETE. Dynamic pricing model ready for review.', type: 'orchestrator' }
        ];

        const addEvent = (event) => {
            const eventEl = document.createElement('div');
            eventEl.className = `event-item agent-${event.type}`;
            
            const now = new Date();
            const timestamp = now.toLocaleTimeString();
            
            eventEl.innerHTML = `
                <div class="event-timestamp">[${timestamp}]</div>
                <div class="event-agent">${event.agent}:</div>
                <div class="event-details">${event.action}</div>
                ${event.details ? `<div class="event-details" style="margin-top: 4px; font-style: italic;">${event.details}</div>` : ''}
            `;
            
            eventStream.appendChild(eventEl);
            eventStream.scrollTop = eventStream.scrollHeight;
        };

        // Add events progressively
        events.forEach((event, index) => {
            setTimeout(() => {
                addEvent(event);
                
                // Show completion section after analysis is complete
                if (index === events.length - 1) {
                    setTimeout(() => {
                        this.showAnalysisComplete();
                    }, 2000);
                }
            }, event.time);
        });
    }

    showAnalysisComplete() {
        // Hide the analysis status spinner
        const analysisStatus = document.getElementById('analysisStatus');
        if (analysisStatus) {
            analysisStatus.innerHTML = `
                <i class="fas fa-check-circle" style="color: #10b981;"></i>
                <span style="color: #10b981;">Analysis Complete</span>
            `;
        }

        // Show the completion section
        const analysisComplete = document.getElementById('analysisComplete');
        if (analysisComplete) {
            analysisComplete.style.display = 'block';
        }
    }

    showPriceSimulator() {
        document.getElementById('agenticCanvasView').style.display = 'none';
        document.getElementById('priceSimulator').style.display = 'block';
        document.getElementById('revenueMetrics').style.display = 'block';
        
        // Initialize with default simulation
        this.updatePriceSimulation();
    }

    closeAgenticCanvas() {
        document.getElementById('agenticCanvasView').style.display = 'none';
        document.getElementById('opportunityBanner').style.display = 'block';
        document.getElementById('problemVisualization').style.display = 'grid';
        
        this.analysisActive = false;
        if (this.eventStreamInterval) {
            clearInterval(this.eventStreamInterval);
        }
    }

    async updatePriceSimulation() {
        try {
            const response = await fetch('/demo4/api/scenario7/simulate-price', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.priceSimulation)
            });

            const data = await response.json();
            
            if (data.success) {
                this.updateSimulatorDisplay(data.simulation);
            }
        } catch (error) {
            console.error('Error updating price simulation:', error);
        }
    }

    updateSimulatorDisplay(simulation) {
        // Update calculated price
        document.getElementById('calculatedPrice').textContent = `₹${simulation.calculated_price}`;
        
        // Update price breakdown
        const breakdown = simulation.price_breakdown;
        document.getElementById('basePrice').textContent = `₹${breakdown.base}`;
        document.getElementById('locationPremium').textContent = `+₹${breakdown.location_premium}`;
        document.getElementById('peakAdjustment').textContent = `${breakdown.peak_adjustment >= 0 ? '+' : ''}₹${breakdown.peak_adjustment}`;
        document.getElementById('demandAdjustment').textContent = `${breakdown.demand_adjustment >= 0 ? '+' : ''}₹${breakdown.demand_adjustment}`;
        document.getElementById('loyaltyDiscount').textContent = `₹${breakdown.loyalty_discount}`;
        document.getElementById('finalPrice').textContent = `₹${simulation.calculated_price}`;

        // Update customer app view
        const stationNames = {
            'CNG-002': 'Select Citywalk Mall',
            'CNG-004': 'Andheri SEEPZ Hub',
            'CNG-007': 'Malad Industrial Hub',
            'CNG-010': 'Thane West Hub'
        };
        
        document.getElementById('customerStationName').textContent = stationNames[simulation.station_id] || 'CNG Station';
        document.getElementById('customerPrice').textContent = `₹${simulation.calculated_price}/kWh`;
        document.getElementById('customerDemandIndicator').textContent = `⚡ ${simulation.parameters.demand_level.toUpperCase()} DEMAND PERIOD`;
        
        // Update forecast
        const forecast = simulation.price_forecast;
        document.getElementById('forecast9pm').textContent = `₹${forecast['21:00']}`;
        document.getElementById('forecast11pm').textContent = `₹${forecast['23:00']}`;
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Scenario7Controller();
});

// Export for global access if needed
window.Scenario7Controller = Scenario7Controller;