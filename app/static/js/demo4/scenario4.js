/**
 * Scenario 4: Real-Time Operations & Continuous Optimization  
 * Interactive demonstration of 24/7 AI-managed CNG network operations
 */

class Scenario4Controller {
    constructor() {
        this.currentTime = new Date('2025-10-04T06:00:00');
        this.isPlaying = false;
        this.playInterval = null;
        this.eventStreamInterval = null;
        this.currentCorrelationId = null;
        this.networkMap = null;
        this.loadChart = null;
        this.dashboardData = null;
        
        // Demo timeline events (key operational events throughout the day)
        this.timelineEvents = [
            { time: '08:15:00', type: 'morning_peak', title: 'Morning Peak Load Management' },
            { time: '10:30:00', type: 'anomaly_detection', title: 'Charger Anomaly Detection' },
            { time: '12:30:00', type: 'lunch_surge', title: 'Lunch Hour Revenue Optimization' },
            { time: '15:45:00', type: 'predictive_maintenance', title: 'Predictive Maintenance Alert' },
            { time: '18:00:00', type: 'end_of_day', title: 'End of Day Report' },
            { time: '18:30:00', type: 'annual_impact', title: 'Annual Impact Projection' }
        ];
        
        this.init();
    }

    cleanup() {
        // Clean up existing map instance
        if (this.networkMap) {
            this.networkMap.remove();
            this.networkMap = null;
        }
        
        // Clean up intervals
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
        
        if (this.eventStreamInterval) {
            clearInterval(this.eventStreamInterval);
            this.eventStreamInterval = null;
        }
    }

    init() {
        console.log('Scenario4Controller initializing...');
        setTimeout(() => {
            this.loadDashboardData();
        }, 500);
    }

    async loadDashboardData() {
        console.log('Loading dashboard data...');
        try {
            const response = await fetch('/demo4/api/scenario4/noc-dashboard');
            const result = await response.json();
            
            if (result.success) {
                this.dashboardData = result.data;
                console.log('Dashboard data loaded:', this.dashboardData);
                this.populateNOCDashboard();
                this.populateAlerts();
                this.initLoadChart();
                
                // Delay map initialization to ensure DOM is ready
                setTimeout(() => {
                    this.initNetworkMap();
                }, 1000);
            } else {
                console.error('Failed to load dashboard data:', result);
            }
            
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
        
        // Initialize other components
        this.bindEvents();
        this.startRealTimeClock();
    }

    populateNOCDashboard() {
        if (!this.dashboardData) return;

        // Update status cards
        document.getElementById('networkStatus').innerHTML = 
            `🟢 ${this.dashboardData.network_status.toUpperCase()}`;
        document.getElementById('uptime24h').textContent = `${this.dashboardData.uptime_24h}%`;
        document.getElementById('activeSessions').textContent = this.dashboardData.active_sessions;
        document.getElementById('chargersAvailable').textContent = this.dashboardData.available_dispensers;
        document.getElementById('gridLoad').textContent = 
            `${this.dashboardData.supply_pressure_bar} bar (Stable)`;
        document.getElementById('solarGeneration').textContent = 
            `${this.dashboardData.compressor_load_kw} kW (Normal)`;
    }

    populateAlerts() {
        if (!this.dashboardData || !this.dashboardData.alerts) return;

        const alertsList = document.getElementById('alertsList');
        alertsList.innerHTML = '';

        this.dashboardData.alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = 'alert-item';
            
            alertItem.innerHTML = `
                <div class="alert-icon alert-${alert.level}">
                    <i class="fas fa-${alert.icon}"></i>
                </div>
                <div class="alert-content">
                    <p class="alert-message">${alert.message}</p>
                    <p class="alert-timestamp">${new Date(alert.timestamp).toLocaleString()}</p>
                </div>
            `;
            
            alertsList.appendChild(alertItem);
        });
    }

    initNetworkMap() {
        console.log('Initializing network map, dashboardData:', this.dashboardData);
        if (!this.dashboardData) {
            console.error('No dashboard data available for map initialization');
            return;
        }

        // Prevent multiple initializations
        if (this.networkMap) {
            console.log('Map already initialized, skipping...');
            return;
        }

        try {
            // Ensure the container is visible and has proper dimensions
            const mapContainer = document.getElementById('networkMap');
            if (!mapContainer) {
                console.error('Map container not found');
                return;
            }
            
            // Clear any existing map content
            mapContainer.innerHTML = '';
            
            console.log('Map container dimensions:', {
                width: mapContainer.offsetWidth,
                height: mapContainer.offsetHeight,
                display: window.getComputedStyle(mapContainer).display,
                visibility: window.getComputedStyle(mapContainer).visibility
            });
            
            // Initialize Leaflet map centered on Bangalore with better zoom for CNG stations
            this.networkMap = L.map('networkMap', {
                zoomControl: true,
                scrollWheelZoom: true,
                preferCanvas: false,
                renderer: L.svg()
            }).setView([12.9716, 77.6271], 12);
            
            // Force immediate rendering
            this.networkMap._onResize();
            console.log('Map initialized successfully');
        } catch (error) {
            console.error('Error initializing map:', error);
            return;
        }

        // Try multiple tile servers for better reliability
        const tileServers = [
            'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
            'https://tile.opentopomap.org/{z}/{x}/{y}.png'
        ];
        
        const tileLayer = L.tileLayer(tileServers[0], {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
            detectRetina: true,
            crossOrigin: true
        });
        
        tileLayer.on('tileerror', function(error) {
            console.error('Tile loading error:', error);
        });
        
        tileLayer.on('tileloadstart', function() {
            console.log('Tiles started loading...');
        });
        
        tileLayer.on('tileload', function() {
            console.log('Tile loaded successfully');
        });
        
        tileLayer.addTo(this.networkMap);
        console.log('Tile layer added to map');

        // Add site markers
        console.log('Adding site markers, sites data:', this.dashboardData.sites);
        this.dashboardData.sites.forEach((site, index) => {
            console.log(`Creating marker for site ${index}:`, site);
            const marker = this.createSiteMarker(site);
            marker.addTo(this.networkMap);
            console.log(`Marker added for ${site.name} at [${site.location[0]}, ${site.location[1]}]`);
        });

        // Ensure map renders properly with multiple attempts
        setTimeout(() => {
            this.networkMap.invalidateSize();
            console.log('Map size invalidated (first attempt)');
        }, 500);
        
        setTimeout(() => {
            this.networkMap.invalidateSize();
            this.networkMap.setView([12.9716, 77.5946], 11);
            console.log('Map size invalidated and view reset (second attempt)');
        }, 1000);
        
        // Add debugging functions
        window.refreshMap = () => {
            if (this.networkMap) {
                this.networkMap.invalidateSize();
                this.networkMap.setView([12.9716, 77.5946], 11);
                console.log('Map manually refreshed');
            }
        };
        
        window.debugMap = () => {
            const container = document.getElementById('networkMap');
            const leafletContainer = container.querySelector('.leaflet-container');
            console.log('Map debug info:', {
                container: container,
                containerStyle: container ? window.getComputedStyle(container) : null,
                leafletContainer: leafletContainer,
                leafletStyle: leafletContainer ? window.getComputedStyle(leafletContainer) : null,
                mapInstance: this.networkMap,
                mapReady: !!this.networkMap
            });
        };
        
        window.testSimpleMap = () => {
            console.log('Creating simple test map...');
            const container = document.getElementById('networkMap');
            
            // Properly clean up existing map
            if (window.scenario4Controller && window.scenario4Controller.networkMap) {
                window.scenario4Controller.networkMap.remove();
                window.scenario4Controller.networkMap = null;
            }
            
            container.innerHTML = '';
            
            try {
                const testMap = L.map('networkMap').setView([12.9716, 77.5946], 11);
                L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
                    attribution: '© CartoDB'
                }).addTo(testMap);
                
                L.marker([12.9716, 77.5946]).addTo(testMap);
                console.log('Simple test map created');
                
                setTimeout(() => {
                    testMap.invalidateSize();
                    console.log('Test map size invalidated');
                }, 500);
            } catch (error) {
                console.error('Error creating test map:', error);
            }
        };
        
        console.log('Map initialization complete. Try calling refreshMap() or debugMap() from console if map is still empty.');
        
        // Add a fallback visual indicator (but don't re-initialize)
        setTimeout(() => {
            const mapContainer = document.getElementById('networkMap');
            const leafletContainer = mapContainer.querySelector('.leaflet-container');
            
            if (!leafletContainer || leafletContainer.children.length === 0) {
                console.warn('Map tiles may not be loading properly');
                // Don't replace content or re-initialize, just log the issue
                console.log('Map container state:', {
                    hasContainer: !!mapContainer,
                    hasLeafletContainer: !!leafletContainer,
                    containerChildren: leafletContainer ? leafletContainer.children.length : 0
                });
            }
        }, 3000);
    }

    createSiteMarker(site) {
        // Create custom marker based on site status
        const statusColors = {
            online: '#10b981',
            maintenance: '#f59e0b',
            offline: '#ef4444'
        };

        const marker = L.circleMarker([site.location[0], site.location[1]], {
            radius: 12,
            fillColor: statusColors[site.status] || '#6b7280',
            color: '#ffffff',
            weight: 3,
            opacity: 1,
            fillOpacity: 0.9
        });

        // Add popup with site details - Enhanced UI
        const utilizationPercent = Math.round(site.utilization * 100);
        const statusIcon = site.status === 'online' ? '🟢' : site.status === 'maintenance' ? '🟡' : '🔴';
        
        const popupContent = `
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; min-width: 300px; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 32px rgba(0,0,0,0.12);">
                <!-- Header with gradient background -->
                <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 16px; margin: -9px -9px 0 -9px; position: relative; box-shadow: 0 2px 8px rgba(30, 60, 114, 0.3);">
                    <div style="position: absolute; top: 8px; right: 12px; background: rgba(255,255,255,0.2); color: white; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; text-transform: uppercase;">
                        TIER 2
                    </div>
                    <h3 style="margin: 0; font-size: 18px; font-weight: 600; line-height: 1.3; padding-right: 80px;">
                        ${site.name}
                    </h3>
                    <p style="margin: 4px 0 0 0; font-size: 13px; opacity: 0.8;">${site.id}</p>
                </div>
                
                <!-- Content area with clean white background -->
                <div style="padding: 20px; background: white;">
                    <!-- Site ID Row -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <span style="font-size: 16px; color: #64748b; font-weight: 500;">Site ID:</span>
                        <span style="font-size: 16px; color: #1e293b; font-weight: 600;">${site.id}</span>
                    </div>
                    
                    <!-- Supply Pressure Row -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <span style="font-size: 16px; color: #64748b; font-weight: 500;">Pressure:</span>
                        <span style="font-size: 16px; color: #1e293b; font-weight: 600;">${site.current_pressure_bar} bar</span>
                    </div>
                    
                    <!-- Status Row -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <span style="font-size: 16px; color: #64748b; font-weight: 500;">Status:</span>
                        <span style="font-size: 16px; color: #1e293b; font-weight: 600;">${site.status === 'online' ? 'Operational' : site.status === 'maintenance' ? 'Under Maintenance' : 'Offline'}</span>
                    </div>
                    
                    <!-- Dispensers Row -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                        <span style="font-size: 16px; color: #64748b; font-weight: 500;">Dispensers:</span>
                        <span style="font-size: 16px; color: #1e293b; font-weight: 600;">${site.dispensers} units</span>
                    </div>
                    
                    <!-- Buttons Row -->
                    <div style="display: flex; gap: 12px;">
                        <button onclick="window.scenario4Controller.showSiteDetails('${site.id}')" 
                                style="flex: 1; padding: 12px 16px; background: #f8fafc; color: #374151; border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s ease;"
                                onmouseover="this.style.background='#f1f5f9'; this.style.borderColor='#d1d5db'"
                                onmouseout="this.style.background='#f8fafc'; this.style.borderColor='#e5e7eb'">
                            <span style="font-size: 16px;">ℹ️</span> View Details
                        </button>
                        ${site.status === 'online' ? 
                            `<button onclick="window.scenario4Controller.showDispenserHealth('${site.id}')" 
                                    style="flex: 1; padding: 12px 16px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 6px; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(30, 60, 114, 0.3);"
                                    onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 8px rgba(76, 99, 210, 0.3)'"
                                    onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(76, 99, 210, 0.2)'">
                                <span style="font-size: 16px;">📊</span> Evaluate
                            </button>` : 
                            `<button disabled 
                                    style="flex: 1; padding: 12px 16px; background: #e5e7eb; color: #9ca3af; border: 1px solid #d1d5db; border-radius: 8px; cursor: not-allowed; font-size: 14px; font-weight: 500; display: flex; align-items: center; justify-content: center; gap: 6px;">
                                <span style="font-size: 16px;">🚧</span> Unavailable
                            </button>`
                        }
                    </div>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent);
        return marker;
    }

    initLoadChart() {
        console.log('Initializing load chart, dashboardData:', this.dashboardData);
        if (!this.dashboardData) {
            console.error('No dashboard data available for chart');
            return;
        }

        const chartElement = document.getElementById('loadChart');
        if (!chartElement) {
            console.error('Chart canvas element not found');
            return;
        }

        const ctx = chartElement.getContext('2d');
        const chartData = this.dashboardData.load_chart_data;
        console.log('Chart data structure:', chartData);

        this.loadChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: [
                    {
                        label: 'Supply Pressure',
                        data: chartData.supply_pressure,
                        borderColor: '#1e3c72',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Compressor Load',
                        data: chartData.compressor_load,
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderDash: [5, 5],
                        fill: false,
                        tension: 0.4,
                        yAxisID: 'y1'
                    },
                    {
                        label: 'Pressure Threshold',
                        data: chartData.pressure_threshold,
                        borderColor: '#ef4444',
                        backgroundColor: 'rgba(239, 68, 68, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        yAxisID: 'y'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        min: 30,
                        max: 60,
                        title: {
                            display: true,
                            text: 'Supply Pressure (bar)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        min: 0,
                        max: 2000,
                        title: {
                            display: true,
                            text: 'Compressor Load (kW)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Time of Day'
                        }
                    }
                }
            }
        });
    }

    bindEvents() {
        // Network Optimization button
        document.getElementById('networkOptimizeButton')?.addEventListener('click', () => {
            this.runNetworkOptimization();
        });

        // Analysis modal close
        document.getElementById('analysisModalClose')?.addEventListener('click', () => {
            this.hideAnalysisModal();
        });

        // View results button
        document.getElementById('viewResultsButton')?.addEventListener('click', () => {
            this.showOptimizationResults();
        });

        // Results modal close
        document.getElementById('resultsModalClose')?.addEventListener('click', () => {
            this.hideResultsModal();
        });

        // Dispenser modal close
        document.getElementById('dispenserModalClose')?.addEventListener('click', () => {
            this.hideDispenserModal();
        });

        // Close modals on outside click
        document.getElementById('analysisModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'analysisModal') {
                this.hideAnalysisModal();
            }
        });

        document.getElementById('resultsModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'resultsModal') {
                this.hideResultsModal();
            }
        });

        document.getElementById('dispenserModal')?.addEventListener('click', (e) => {
            if (e.target.id === 'dispenserModal') {
                this.hideDispenserModal();
            }
        });
    }

    toggleDemo() {
        const playButton = document.getElementById('playButton');
        
        if (this.isPlaying) {
            this.pauseDemo();
            playButton.innerHTML = '<i class="fas fa-play"></i> Resume Demo';
        } else {
            this.startDemo();
            playButton.innerHTML = '<i class="fas fa-pause"></i> Pause Demo';
        }
        
        this.isPlaying = !this.isPlaying;
    }

    startDemo() {
        // Start time progression
        this.playInterval = setInterval(() => {
            this.advanceTime();
        }, 2000); // Advance every 2 seconds for demo purposes
    }

    pauseDemo() {
        if (this.playInterval) {
            clearInterval(this.playInterval);
            this.playInterval = null;
        }
        
        if (this.eventStreamInterval) {
            clearInterval(this.eventStreamInterval);
            this.eventStreamInterval = null;
        }
    }

    advanceTime() {
        // Advance time by 15 minutes each step
        this.currentTime.setMinutes(this.currentTime.getMinutes() + 15);
        this.updateTimeDisplay();
        this.checkForEvents();
        
        // Stop at end of day
        if (this.currentTime.getHours() >= 19) {
            this.pauseDemo();
            document.getElementById('playButton').innerHTML = '<i class="fas fa-refresh"></i> Restart Demo';
        }
    }

    updateTimeDisplay() {
        // Use actual current time instead of simulated time
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: true 
        });
        
        document.getElementById('timeDisplay').textContent = timeString;
        
        // Update timestamp in header with current date and time
        const dateString = now.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        document.getElementById('currentTimestamp').textContent = 
            `${dateString} | ${timeString} IST`;
        
        // Update progress bar based on simulation time for demo purposes
        const startOfDay = new Date(this.currentTime);
        startOfDay.setHours(6, 0, 0, 0);
        const endOfDay = new Date(this.currentTime);
        endOfDay.setHours(19, 0, 0, 0);
        
        const progress = Math.min(100, Math.max(0, 
            ((this.currentTime - startOfDay) / (endOfDay - startOfDay)) * 100
        ));
        
        document.getElementById('timeProgress').style.width = `${progress}%`;
    }

    startRealTimeClock() {
        // Update time display immediately
        this.updateTimeDisplay();
        
        // Update every second for real-time display
        this.clockInterval = setInterval(() => {
            this.updateTimeDisplay();
        }, 1000);
    }

    stopRealTimeClock() {
        if (this.clockInterval) {
            clearInterval(this.clockInterval);
            this.clockInterval = null;
        }
    }

    checkForEvents() {
        const currentTimeString = this.currentTime.toTimeString().slice(0, 8);
        
        const event = this.timelineEvents.find(e => e.time === currentTimeString);
        if (event) {
            this.triggerEvent(event);
        }
    }

    async triggerEvent(event) {
        try {
            console.log(`Triggering event: ${event.type} at ${event.time}`);
            
            // Special handling for report events
            if (event.type === 'end_of_day') {
                this.showEndOfDayReport();
                return;
            }
            
            if (event.type === 'annual_impact') {
                this.showAnnualImpact();
                return;
            }
            
            // Trigger operational event
            const response = await fetch('/demo4/api/scenario4/trigger-event', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_type: event.type,
                    timestamp: event.time
                })
            });
            
            const result = await response.json();
            if (result.success) {
                this.currentCorrelationId = result.correlation_id;
                this.showAgenticCanvas(event);
                this.startEventStream();
            }
            
        } catch (error) {
            console.error('Error triggering event:', error);
        }
    }

    showAgenticCanvas(event) {
        const section = document.getElementById('agenticCanvasSection');
        section.style.display = 'block';
        
        // Update title
        document.getElementById('eventStreamTitle').textContent = 
            `${event.title.toUpperCase()} - REAL-TIME AGENT ACTIVITY`;
        
        // Clear previous events
        document.getElementById('eventsList').innerHTML = '';
        
        // Reset component states
        document.querySelectorAll('.canvas-component').forEach(comp => {
            comp.classList.remove('active');
        });
        
        // Scroll to section
        section.scrollIntoView({ behavior: 'smooth' });
    }

    async startEventStream() {
        if (!this.currentCorrelationId) return;
        
        try {
            const response = await fetch(`/demo4/api/scenario4/live-stream/${this.currentCorrelationId}`);
            const result = await response.json();
            
            if (result.success && result.events) {
                this.displayEventStream(result.events);
            }
            
        } catch (error) {
            console.error('Error fetching event stream:', error);
        }
    }

    displayEventStream(events) {
        const eventsList = document.getElementById('eventsList');
        
        events.forEach((event, index) => {
            setTimeout(() => {
                this.addEventToStream(event);
                this.activateComponents(event.components_activated || []);
            }, index * 2000); // 2 second delay between events
        });
    }

    addEventToStream(event) {
        const eventsList = document.getElementById('eventsList');
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        
        const isSuccess = event.action.includes('✅');
        const eventClass = isSuccess ? 'event-success' : 'event-action';
        
        eventItem.innerHTML = `
            <span class="event-timestamp">[${event.timestamp}]</span>
            <span class="event-agent">${event.agent}:</span>
            <span class="${eventClass}">${event.action}</span>
        `;
        
        eventsList.appendChild(eventItem);
        eventsList.scrollTop = eventsList.scrollHeight;
    }

    activateComponents(componentNames) {
        // Reset all components
        document.querySelectorAll('.canvas-component').forEach(comp => {
            comp.classList.remove('active');
        });
        
        // Activate specified components
        componentNames.forEach(componentName => {
            const component = document.querySelector(`[data-component="${componentName.toLowerCase().replace(/\s+/g, '-')}"]`);
            if (component) {
                component.classList.add('active');
            }
        });
    }

    handleTimeScrubberClick(e) {
        const scrubber = document.getElementById('timeScrubber');
        const rect = scrubber.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const progress = clickX / rect.width;
        
        // Calculate time based on progress (6 AM to 7 PM = 13 hours)
        const startHour = 6;
        const totalHours = 13;
        const targetHour = startHour + (progress * totalHours);
        
        this.currentTime.setHours(Math.floor(targetHour), (targetHour % 1) * 60, 0, 0);
        this.updateTimeDisplay();
        
        // Check if we should trigger any events at this time
        this.checkForEvents();
    }

    async showDispenserHealth(dispenserId) {
        try {
            const response = await fetch(`/demo4/api/scenario4/dispenser-health/${dispenserId}`);
            const result = await response.json();
            
            if (result.success) {
                this.displayDispenserModal(result.data);
            }
            
        } catch (error) {
            console.error('Error fetching dispenser health:', error);
        }
    }

    showSiteDetails(siteId) {
        // Find the site data from dashboard data
        const siteData = this.dashboardData?.sites?.find(site => site.id === siteId);
        if (!siteData) {
            this.showNotification('Site information not available', 'warning');
            return;
        }

        // Create and show detailed site information modal
        const modal = document.getElementById('dispenserModal');
        const title = document.getElementById('dispenserModalTitle');
        const body = document.getElementById('dispenserModalBody');
        
        title.innerHTML = `<i class="fas fa-map-marker-alt"></i> CNG Station Details - ${siteData.name}`;
        
        body.innerHTML = `
            <div style="background: white; border-radius: 12px; overflow: hidden;">
                <!-- Site Overview -->
                <div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 20px; margin: -20px -20px 20px -20px; box-shadow: 0 2px 8px rgba(30, 60, 114, 0.3);">
                    <h3 style="margin: 0 0 8px 0; font-size: 20px; font-weight: 600;">${siteData.name}</h3>
                    <p style="margin: 0; opacity: 0.9; font-size: 14px;">Station ID: ${siteData.id} • Tier 2 Location</p>
                </div>
                
                <!-- Key Metrics Grid -->
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin-bottom: 20px;">
                    <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #10b981;">
                        <h4 style="margin: 0 0 8px 0; color: #374151; font-size: 14px; font-weight: 600;">Operational Status</h4>
                        <p style="margin: 0; font-size: 18px; font-weight: 700; color: #10b981;">
                            ${siteData.status === 'online' ? 'OPERATIONAL' : siteData.status.toUpperCase()}
                        </p>
                    </div>
                    <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #1e3c72;">
                        <h4 style="margin: 0 0 8px 0; color: #374151; font-size: 14px; font-weight: 600;">Supply Pressure</h4>
                        <p style="margin: 0; font-size: 18px; font-weight: 700; color: #1e293b;">
                            ${siteData.current_pressure_bar} bar
                        </p>
                    </div>
                    <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <h4 style="margin: 0 0 8px 0; color: #374151; font-size: 14px; font-weight: 600;">Active Dispensers</h4>
                        <p style="margin: 0; font-size: 18px; font-weight: 700; color: #1e293b;">
                            ${siteData.dispensers} units
                        </p>
                    </div>
                    <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #1e3c72;">
                        <h4 style="margin: 0 0 8px 0; color: #374151; font-size: 14px; font-weight: 600;">Daily Traffic</h4>
                        <p style="margin: 0; font-size: 18px; font-weight: 700; color: #1e293b;">
                            ${Math.floor(Math.random() * 5000 + 8000)} vehicles
                        </p>
                    </div>
                </div>
                
                <!-- Location & Contact -->
                <div style="background: #f1f5f9; padding: 16px; border-radius: 8px; margin-bottom: 20px;">
                    <h4 style="margin: 0 0 12px 0; color: #1e293b; font-size: 16px; font-weight: 600;">Location Information</h4>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748b; font-weight: 500;">Address:</span>
                            <span style="color: #1e293b; font-weight: 600;">${siteData.name}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748b; font-weight: 500;">Coordinates:</span>
                            <span style="color: #1e293b; font-weight: 600;">${siteData.location[0].toFixed(4)}, ${siteData.location[1].toFixed(4)}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #64748b; font-weight: 500;">Utilization:</span>
                            <span style="color: #1e293b; font-weight: 600;">${Math.round(siteData.utilization * 100)}%</span>
                        </div>
                    </div>
                </div>
                
                <!-- Action Buttons -->
                <div style="display: flex; gap: 12px; justify-content: flex-end;">
                    <button onclick="window.scenario4Controller.hideDispenserModal()" 
                            style="padding: 10px 20px; background: #f8fafc; color: #374151; border: 1px solid #e5e7eb; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500;">
                        Close
                    </button>
                    ${siteData.status === 'online' ? 
                        `<button onclick="window.scenario4Controller.showDispenserHealth('${siteData.id}')" 
                                style="padding: 10px 20px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500; box-shadow: 0 2px 4px rgba(30, 60, 114, 0.3);">
                            📊 View Dispensers
                        </button>` : ''
                    }
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    displayDispenserModal(dispenserData) {
        const modal = document.getElementById('dispenserModal');
        const title = document.getElementById('dispenserModalTitle');
        const body = document.getElementById('dispenserModalBody');
        
        title.innerHTML = `<i class="fas fa-gas-pump"></i> CNG Dispenser Health - ${dispenserData.dispenser_id}`;
        
        const statusColor = dispenserData.status === 'critical' ? '#ef4444' : 
                           dispenserData.status === 'warning' ? '#f59e0b' : '#10b981';
        
        body.innerHTML = `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-bottom: 1.5rem;">
                <div style="background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid ${statusColor};">
                    <h4 style="margin: 0 0 0.8rem 0; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-heartbeat" style="color: ${statusColor};"></i>
                        Current Status
                    </h4>
                    <p style="margin: 0; font-size: 20px; font-weight: 700; color: ${statusColor};">
                        ${dispenserData.status.toUpperCase()}
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 12px; color: #64748b;">
                        Last Updated: ${new Date(dispenserData.last_update).toLocaleString()}
                    </p>
                </div>
                
                <div style="background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #1e3c72;">
                    <h4 style="margin: 0 0 0.8rem 0; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-tachometer-alt" style="color: #1e3c72;"></i>
                        Valve Pressure
                    </h4>
                    <p style="margin: 0; font-size: 20px; font-weight: 700; color: #6b21a8;">
                        ${dispenserData.valve_pressure.current} bar
                    </p>
                    <div style="background: #e0e7ff; height: 6px; border-radius: 3px; margin-top: 8px; overflow: hidden;">
                        <div style="background: #1e3c72; height: 100%; width: ${(dispenserData.valve_pressure.current / 300) * 100}%; border-radius: 3px;"></div>
                    </div>
                </div>
                
                <div style="background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #22c55e;">
                    <h4 style="margin: 0 0 0.8rem 0; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-wind" style="color: #22c55e;"></i>
                        Flow Rate
                    </h4>
                    <p style="margin: 0; font-size: 20px; font-weight: 700; color: #15803d;">
                        ${dispenserData.flow_rate.current} kg/min
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 12px; color: #16a34a;">
                        Target: ${dispenserData.flow_rate.rated} kg/min (${dispenserData.flow_rate.efficiency}% efficiency)
                    </p>
                </div>
                
                <div style="background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f59e0b;">
                    <h4 style="margin: 0 0 0.8rem 0; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-thermometer-half" style="color: #f59e0b;"></i>
                        Temperature
                    </h4>
                    <p style="margin: 0; font-size: 20px; font-weight: 700; color: #d97706;">
                        ${dispenserData.temperature.current}°C
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 12px; color: #a16207;">
                        Max Safe: ${dispenserData.temperature.max_safe}°C
                    </p>
                </div>
            </div>
            
            <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                <h4 style="margin: 0 0 1rem 0; color: #1e293b; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-chart-line" style="color: #1e3c72;"></i>
                    Recent Activity & Alerts
                </h4>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    ${dispenserData.recent_alerts ? dispenserData.recent_alerts.map(alert => `
                        <div style="background: white; padding: 0.75rem; border-radius: 6px; border-left: 3px solid ${alert.level === 'warning' ? '#f59e0b' : '#ef4444'}; font-size: 14px;">
                            <span style="color: ${alert.level === 'warning' ? '#d97706' : '#dc2626'}; font-weight: 600;">
                                ${alert.level === 'warning' ? '⚠️' : '🚨'} ${alert.message}
                            </span>
                            <div style="font-size: 12px; color: #64748b; margin-top: 4px;">
                                ${new Date(alert.timestamp).toLocaleString()}
                            </div>
                        </div>
                    `).join('') : '<p style="color: #64748b; font-style: italic;">No recent alerts</p>'}
                </div>
            </div>
            
            <div style="margin-top: 1rem;">
                <h4 style="margin: 0 0 1rem 0; color: #1e293b;">Maintenance Information</h4>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;">
                    <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                        <p style="margin: 0; font-size: 14px; color: #6b7280;">Last Maintenance:</p>
                        <p style="margin: 0; font-size: 16px; font-weight: 600; color: #374151;">
                            ${dispenserData.last_maintenance ? new Date(dispenserData.last_maintenance).toLocaleDateString() : 'Not recorded'}
                        </p>
                    </div>
                    <div style="background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e5e7eb;">
                        <p style="margin: 0; font-size: 14px; color: #6b7280;">Total Sessions:</p>
                        <p style="margin: 0; font-size: 16px; font-weight: 600; color: #374151;">
                            ${dispenserData.session_count ? dispenserData.session_count.toLocaleString() : '0'}
                        </p>
                    </div>
                </div>
            </div>
            
            <div style="display: flex; gap: 1rem; justify-content: flex-end; padding-top: 1rem; border-top: 1px solid #e5e7eb; margin-top: 1.5rem;">
                <button onclick="window.scenario4Controller.hideDispenserModal()" 
                        style="padding: 10px 20px; background: #64748b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500;">
                    Close
                </button>
                <button onclick="window.scenario4Controller.triggerMaintenanceAlert('${dispenserData.dispenser_id}')" 
                        style="padding: 10px 20px; background: #dc2626; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 500;">
                    🔧 Schedule Maintenance
                </button>
            </div>
        `;
        
        modal.style.display = 'block';
    }

    hideDispenserModal() {
        document.getElementById('dispenserModal').style.display = 'none';
    }

    async runNetworkOptimization() {
        console.log('Starting network optimization analysis...');
        
        // Show the analysis modal
        this.showAnalysisModal();
        
        // Start the agent activity simulation
        await this.simulateOptimizationAnalysis();
    }

    showAnalysisModal() {
        const modal = document.getElementById('analysisModal');
        modal.style.display = 'block';
        
        // Reset modal content
        const stream = document.getElementById('agentActivityStream');
        stream.innerHTML = '';
        
        const actions = document.getElementById('analysisActions');
        actions.style.display = 'none';
        
        const status = document.getElementById('analysisStatus');
        status.innerHTML = '<span class="spinner"></span> Analysis in progress...';
    }

    hideAnalysisModal() {
        document.getElementById('analysisModal').style.display = 'none';
    }

    async simulateOptimizationAnalysis() {
        const analysisEvents = [
            {
                time: 0,
                agent: 'Orchestrator',
                action: 'Network optimization workflow initiated. Deploying 4 specialized agents.',
                details: 'Analyzing 18 CNG stations across Bangalore network for optimization opportunities.'
            },
            {
                time: 3000,
                agent: 'Operations Agent',
                action: 'Querying real-time telemetry from all network dispensers...',
                details: 'Collecting pressure, flow rate, and utilization data from Grid Monitor.'
            },
            {
                time: 6000,
                agent: 'Predictive Agent',
                action: 'Running ML models on historical demand patterns...',
                details: 'Using Reasoning Engine to forecast peak demand windows and capacity requirements.'
            },
            {
                time: 9000,
                agent: 'Financial Agent',
                action: 'Calculating cost optimization opportunities...',
                details: 'Querying Finance ERP for energy costs, maintenance schedules, and revenue data.'
            },
            {
                time: 12000,
                agent: 'Network Agent',
                action: 'Modeling load balancing and pressure optimization scenarios...',
                details: 'Using RAG Engine on Vector DB of network topology and engineering specifications.'
            },
            {
                time: 15000,
                agent: 'Operations Agent',
                action: '✅ Telemetry analysis complete. 3 dispensers showing efficiency degradation.',
                details: 'BLR-002-DC-01, BLR-003-DC-02, BLR-005-DC-01 require attention.'
            },
            {
                time: 18000,
                agent: 'Predictive Agent',
                action: '✅ Demand forecasting complete. Peak shift potential identified.',
                details: 'Morning peak can be reduced by 15% through dynamic pricing incentives.'
            },
            {
                time: 21000,
                agent: 'Financial Agent',
                action: '✅ Cost analysis complete. ₹2.8L annual savings opportunity found.',
                details: 'Energy optimization: ₹1.6L, Maintenance scheduling: ₹1.2L'
            },
            {
                time: 24000,
                agent: 'Network Agent',
                action: '✅ Load balancing optimization complete. 18% efficiency improvement possible.',
                details: 'Pressure cascade optimization can reduce compressor load by 180kW average.'
            },
            {
                time: 27000,
                agent: 'Orchestrator',
                action: 'Synthesizing multi-agent recommendations using Prompt Manager...',
                details: 'Applying Guardrails for safety constraints and operational continuity.'
            },
            {
                time: 30000,
                agent: 'Orchestrator',
                action: '✅ NETWORK OPTIMIZATION ANALYSIS COMPLETE',
                details: 'Comprehensive recommendations ready for review and implementation.'
            }
        ];

        // Display events progressively
        for (const event of analysisEvents) {
            await new Promise(resolve => setTimeout(resolve, event.time === 0 ? 0 : 3000));
            this.addAgentActivity(event);
            
            // Show results button after last event
            if (event === analysisEvents[analysisEvents.length - 1]) {
                document.getElementById('analysisStatus').innerHTML = 
                    '<i class="fas fa-check-circle" style="color: #10b981;"></i> Analysis complete';
                document.getElementById('analysisActions').style.display = 'block';
            }
        }
    }

    addAgentActivity(event) {
        const stream = document.getElementById('agentActivityStream');
        const now = new Date();
        const timestamp = now.toLocaleTimeString('en-US', { 
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        const activityItem = document.createElement('div');
        activityItem.className = 'agent-activity-item';
        
        const isComplete = event.action.includes('✅');
        const agentClass = isComplete ? 'agent-success' : 'agent-processing';
        
        activityItem.innerHTML = `
            <div>
                <span class="agent-timestamp">[${timestamp}]</span>
                <span class="agent-name">${event.agent}:</span>
            </div>
            <div class="agent-action ${agentClass}">${event.action}</div>
            ${event.details ? `<div class="agent-details">${event.details}</div>` : ''}
        `;
        
        stream.appendChild(activityItem);
        stream.scrollTop = stream.scrollHeight;
    }

    showOptimizationResults() {
        // Hide the analysis modal
        this.hideAnalysisModal();
        
        // Show the results modal
        this.showResultsModal();
    }

    showResultsModal() {
        const modal = document.getElementById('resultsModal');
        modal.style.display = 'block';
        
        // Populate the results content
        this.populateResultsModal();
    }

    hideResultsModal() {
        document.getElementById('resultsModal').style.display = 'none';
    }

    populateResultsModal() {
        // Update the daily score and metrics in the modal
        document.getElementById('resultsModalDailyScore').textContent = '96.2/100';
        
        // Populate performance metrics in modal
        const metricsContainer = document.getElementById('resultsModalPerformanceMetrics');
        metricsContainer.innerHTML = `
            <div class="report-card">
                <h4>Network Efficiency</h4>
                <div class="report-value">94.7%</div>
                <p class="report-description">+18% improvement potential identified</p>
            </div>
            <div class="report-card">
                <h4>Energy Optimization</h4>
                <div class="report-value">₹1.6L</div>
                <p class="report-description">Annual savings through load balancing</p>
            </div>
            <div class="report-card">
                <h4>Maintenance Scheduling</h4>
                <div class="report-value">₹1.2L</div>
                <p class="report-description">Predictive maintenance savings</p>
            </div>
        `;
        
        // Populate AI optimizations in modal
        const optimizationsContainer = document.getElementById('resultsModalAiOptimizations');
        optimizationsContainer.innerHTML = `
            <div class="report-card">
                <h4>✅ Pressure Cascade Optimization</h4>
                <div class="report-value">₹28,340</div>
                <p class="report-description">180kW compressor load reduction</p>
            </div>
            <div class="report-card">
                <h4>✅ Dynamic Load Balancing</h4>
                <div class="report-value">₹15,200</div>
                <p class="report-description">Peak demand distribution optimization</p>
            </div>
            <div class="report-card">
                <h4>✅ Predictive Maintenance</h4>
                <div class="report-value">₹17,400</div>
                <p class="report-description">3 dispensers scheduled for optimization</p>
            </div>
            <div class="report-card">
                <h4>✅ Energy Cost Management</h4>
                <div class="report-value">₹9,380</div>
                <p class="report-description">Off-peak energy utilization</p>
            </div>
        `;
        
        document.getElementById('resultsModalTotalDailyValue').textContent = '₹70,320';
        
        // Populate annual impact data in modal
        this.populateAnnualImpactInModal();
    }

    populateAnnualImpactInModal() {
        const tableBody = document.getElementById('resultsModalAnnualComparisonTable');
        
        tableBody.innerHTML = `
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6; font-weight: 500;">Network Efficiency</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">76.5%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">94.7%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">+18.2%</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6; font-weight: 500;">Annual Energy Costs</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹37.6 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹27.1 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">₹10.5 Cr saved</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6; font-weight: 500;">Annual Maintenance Costs</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹4.2 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹2.5 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">₹1.7 Cr saved</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6; font-weight: 500;">Network Uptime</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">92.0%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">97.9%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">+5.9%</td>
            </tr>
            <tr>
                <td style="padding: 1rem; font-weight: 500;">Customer Satisfaction</td>
                <td style="padding: 1rem; text-align: center;">68 NPS</td>
                <td style="padding: 1rem; text-align: center;">79 NPS</td>
                <td style="padding: 1rem; text-align: center; color: #10b981; font-weight: 600;">+11 points</td>
            </tr>
        `;
        
        document.getElementById('resultsModalTotalAnnualBenefit').textContent = '₹12.2 Crore';
        document.getElementById('resultsModalRoiPercentage').textContent = '180%';
    }

    // This method is kept for backwards compatibility but not used in the modal flow
    async showAnnualImpact() {
        const section = document.getElementById('annualImpactSection');
        section.style.display = 'block';
        
        const tableBody = document.getElementById('annualComparisonTable');
        
        tableBody.innerHTML = `
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Network Efficiency</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">76.5%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">94.7%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">+18.2%</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Annual Energy Costs</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹37.6 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹27.1 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">₹10.5 Cr saved</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Annual Maintenance Costs</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹4.2 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹2.5 Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">₹1.7 Cr saved</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Network Uptime</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">92.0%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">97.9%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">+5.9%</td>
            </tr>
            <tr>
                <td style="padding: 1rem;">Customer Satisfaction</td>
                <td style="padding: 1rem; text-align: center;">68 NPS</td>
                <td style="padding: 1rem; text-align: center;">79 NPS</td>
                <td style="padding: 1rem; text-align: center; color: #10b981; font-weight: 600;">+11 points</td>
            </tr>
        `;
        
        document.getElementById('totalAnnualBenefit').textContent = '₹12.2 Crore';
        document.getElementById('roiPercentage').textContent = '180%';
        
        section.scrollIntoView({ behavior: 'smooth' });
    }

    triggerMaintenanceAlert(dispenserId) {
        // Close the modal first
        this.hideDispenserModal();
        
        // Show confirmation alert
        const confirmed = confirm(`Schedule maintenance for CNG Dispenser ${dispenserId}?\n\nThis will:\n• Create a maintenance ticket\n• Alert the technical team\n• Block the dispenser for new sessions`);
        
        if (confirmed) {
            // Show success notification
            this.showNotification(`🔧 Maintenance scheduled for Dispenser ${dispenserId}`, 'success');
            
            // In a real system, this would make an API call to schedule maintenance
            console.log(`Maintenance scheduled for dispenser: ${dispenserId}`);
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'warning' ? '#f59e0b' : '#1e3c72'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            z-index: 10000;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease-out;
        `;
        notification.textContent = message;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    async showEndOfDayReport() {
        try {
            const response = await fetch('/demo4/api/scenario4/end-of-day-report');
            const result = await response.json();
            
            if (result.success) {
                this.displayEndOfDayReport(result.data);
            }
            
        } catch (error) {
            console.error('Error fetching end of day report:', error);
        }
    }

    displayEndOfDayReport(reportData) {
        const section = document.getElementById('endOfDaySection');
        section.style.display = 'block';
        
        // Update daily score
        document.getElementById('dailyScore').textContent = `${reportData.daily_score}/100`;
        
        // Populate performance metrics
        const metricsContainer = document.getElementById('performanceMetrics');
        metricsContainer.innerHTML = `
            <div class="report-card">
                <h4>Network Uptime</h4>
                <div class="report-value">${reportData.performance_metrics.network_uptime}%</div>
                <p class="report-description">System availability</p>
            </div>
            <div class="report-card">
                <h4>Revenue Beat Target</h4>
                <div class="report-value">+₹${reportData.performance_metrics.revenue_beat_amount.toLocaleString()}</div>
                <p class="report-description">+${reportData.performance_metrics.revenue_beat_target}% above target</p>
            </div>
            <div class="report-card">
                <h4>Average Wait Time</h4>
                <div class="report-value">${reportData.performance_metrics.avg_wait_time} min</div>
                <p class="report-description">Customer experience metric</p>
            </div>
        `;
        
        // Populate AI optimizations
        const optimizationsContainer = document.getElementById('aiOptimizations');
        optimizationsContainer.innerHTML = reportData.ai_optimizations.map(opt => `
            <div class="report-card">
                <h4>✅ ${opt.title}</h4>
                <div class="report-value">₹${opt.value.toLocaleString()}</div>
                <p class="report-description">${opt.description}</p>
            </div>
        `).join('');
        
        document.getElementById('totalDailyValue').textContent = `₹${reportData.total_daily_value.toLocaleString()}`;
        
        section.scrollIntoView({ behavior: 'smooth' });
    }

    async showAnnualImpact() {
        try {
            const response = await fetch('/demo4/api/scenario4/annual-impact');
            const result = await response.json();
            
            if (result.success) {
                this.displayAnnualImpact(result.data);
            }
            
        } catch (error) {
            console.error('Error fetching annual impact:', error);
        }
    }

    displayAnnualImpact(impactData) {
        const section = document.getElementById('annualImpactSection');
        section.style.display = 'block';
        
        const tableBody = document.getElementById('annualComparisonTable');
        const comparison = impactData.comparison;
        
        tableBody.innerHTML = `
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Network Uptime</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">${comparison.without_ai.network_uptime}%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">${comparison.with_agentic_canvas.network_uptime}%</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">+${comparison.improvements.network_uptime}%</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Annual Revenue</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹${comparison.without_ai.annual_revenue} Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹${comparison.with_agentic_canvas.annual_revenue} Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">+₹${comparison.improvements.annual_revenue} Cr</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Annual Energy Costs</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹${comparison.without_ai.annual_energy_costs} Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹${comparison.with_agentic_canvas.annual_energy_costs} Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">₹${comparison.improvements.annual_energy_costs} Cr</td>
            </tr>
            <tr>
                <td style="padding: 1rem; border-bottom: 1px solid #f3f4f6;">Annual Maintenance Costs</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹${comparison.without_ai.annual_maint_costs} Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6;">₹${comparison.with_agentic_canvas.annual_maint_costs} Cr</td>
                <td style="padding: 1rem; text-align: center; border-bottom: 1px solid #f3f4f6; color: #10b981; font-weight: 600;">₹${comparison.improvements.annual_maint_costs} Cr</td>
            </tr>
            <tr>
                <td style="padding: 1rem;">Customer NPS</td>
                <td style="padding: 1rem; text-align: center;">${comparison.without_ai.customer_nps}</td>
                <td style="padding: 1rem; text-align: center;">${comparison.with_agentic_canvas.customer_nps}</td>
                <td style="padding: 1rem; text-align: center; color: #10b981; font-weight: 600;">+${comparison.improvements.customer_nps} points</td>
            </tr>
        `;
        
        document.getElementById('totalAnnualBenefit').textContent = `₹${impactData.total_annual_benefit} Crore`;
        document.getElementById('roiPercentage').textContent = `${impactData.roi_percentage}%`;
        
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Make controller globally accessible
window.Scenario4Controller = Scenario4Controller;