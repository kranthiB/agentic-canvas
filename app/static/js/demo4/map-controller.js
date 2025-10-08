/**
 * Demo 4: Interactive Map Controller
 * Manages Leaflet.js map, markers, layers, and user interactions
 */

class CNGNetworkMapController {
    constructor() {
        this.map = null;
        this.markers = new Map();
        this.markerClusterGroup = null;
        this.heatmapLayer = null;
        this.sitesData = [];
        this.filteredSites = [];
        
        this.filters = {
            tier: 'all',
            status: 'all',
            minScore: 0
        };
        
        this.layers = {
            sites: true,
            clusters: true,
            heatmap: false,
            cityLabels: true
        };
        
        this.initializeMap();
        this.loadSitesData();
        this.initializeEventHandlers();
    }
    
    initializeMap() {
        // Create map centered on India
        this.map = L.map('networkMap', {
            center: [20.5937, 78.9629],
            zoom: 5,
            zoomControl: false,
            minZoom: 4,
            maxZoom: 18
        });
        
        // Add tile layer (OpenStreetMap theme - matching scenario1)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18
        }).addTo(this.map);
        
        // Initialize marker cluster group
        this.markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: 50,
            iconCreateFunction: (cluster) => {
                const count = cluster.getChildCount();
                let size = 'small';
                if (count > 10) size = 'medium';
                if (count > 25) size = 'large';
                
                return L.divIcon({
                    html: `<div style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; width: 100%; height: 100%; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; text-shadow: 0 1px 3px rgba(0,0,0,0.4);">${count}</div>`,
                    className: `marker-cluster marker-cluster-${size}`,
                    iconSize: L.point(40, 40)
                });
            }
        });
        
        this.map.addLayer(this.markerClusterGroup);
        
        console.log('Map initialized');
    }
    
    async loadSitesData() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/demo4/api/sites/map-data');
            const data = await response.json();
            
            if (data.success) {
                this.sitesData = data.sites;
                this.filteredSites = [...this.sitesData];
                this.renderMarkers();
                this.updateStatistics();
                console.log(`Loaded ${this.sitesData.length} sites`);
            }
        } catch (error) {
            console.error('Error loading sites data:', error);
        } finally {
            this.showLoading(false);
        }
    }
    
    renderMarkers() {
        // Clear existing markers
        this.markerClusterGroup.clearLayers();
        this.markers.clear();
        
        // Add markers for filtered sites
        this.filteredSites.forEach(site => {
            const marker = this.createMarker(site);
            if (marker) {
                this.markers.set(site.site_id, marker);
                
                if (this.layers.clusters) {
                    this.markerClusterGroup.addLayer(marker);
                } else {
                    marker.addTo(this.map);
                }
            }
        });
        
        console.log(`Rendered ${this.filteredSites.length} markers`);
    }
    
    createMarker(site) {
        const { latitude, longitude } = site;
        
        if (!latitude || !longitude) return null;
        
        // Determine marker color based on score
        const color = this.getMarkerColor(site);
        const icon = this.createCustomIcon(site, color);
        
        const marker = L.marker([latitude, longitude], { icon });
        
        // Create popup
        const popupContent = this.createPopupContent(site);
        marker.bindPopup(popupContent, {
            maxWidth: 300,
            className: 'custom-popup'
        });
        
        // Add click handler
        marker.on('click', () => {
            this.onMarkerClick(site);
        });
        
        return marker;
    }
    
    createCustomIcon(site, color) {
        const iconHtml = `
            <div class="marker-icon" style="background-color: ${color};">
                <i class="fas fa-gas-pump"></i>
            </div>
        `;
        
        return L.divIcon({
            html: iconHtml,
            className: 'custom-marker',
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -15]
        });
    }
    
    getMarkerColor(site) {
        if (!site.evaluated) {
            return '#6b7280'; // Gray - unevaluated
        }
        
        const score = site.score || 0;
        
        if (score >= 80) return '#10b981'; // Green - excellent
        if (score >= 65) return '#3b82f6'; // Blue - good
        if (score >= 50) return '#f59e0b'; // Orange - fair
        return '#ef4444'; // Red - poor
    }
    
    createPopupContent(site) {
        const scoreColor = this.getMarkerColor(site);
        const scoreDisplay = site.evaluated ? Math.round(site.score) : 'N/A';
        
        return `
            <div class="site-popup">
                <div class="popup-header">
                    <h4>${site.city}, ${site.state}</h4>
                    <span class="popup-badge" style="background: ${scoreColor}20; color: ${scoreColor}; border: 1px solid ${scoreColor};">
                        ${site.city_tier.replace('_', ' ')}
                    </span>
                </div>
                
                <div class="popup-info">
                    <div class="info-row">
                        <span class="info-label">Site ID:</span>
                        <span class="info-value">${site.site_id}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Score:</span>
                        <span class="info-value" style="color: ${scoreColor}; font-weight: 700;">
                            ${scoreDisplay}/100
                        </span>
                    </div>
                    ${site.evaluated ? `
                        <div class="info-row">
                            <span class="info-label">Recommendation:</span>
                            <span class="info-value">${this.formatRecommendation(site.recommendation)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">NPV:</span>
                            <span class="info-value">₹${this.formatCurrency(site.npv)}</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">IRR:</span>
                            <span class="info-value">${site.irr ? site.irr.toFixed(1) + '%' : 'N/A'}</span>
                        </div>
                    ` : `
                        <div class="info-row">
                            <span class="info-label">Status:</span>
                            <span class="info-value">Not Evaluated</span>
                        </div>
                        <div class="info-row">
                            <span class="info-label">Traffic:</span>
                            <span class="info-value">${site.daily_traffic || 'N/A'}/day</span>
                        </div>
                    `}
                </div>
                
                <div class="popup-actions">
                    <button class="btn-popup" onclick="window.mapController.showSiteDetails('${site.site_id}')">
                        <i class="fas fa-info-circle"></i> View Details
                    </button>
                    ${!site.evaluated ? `
                        <button class="btn-popup btn-primary" onclick="window.mapController.evaluateSite('${site.site_id}')">
                            <i class="fas fa-chart-line"></i> Evaluate
                        </button>
                    ` : ''}
                </div>
            </div>
        `;
    }
    
    formatRecommendation(rec) {
        const map = {
            'strong_select': 'Strong Select',
            'select': 'Select',
            'consider': 'Consider',
            'reject': 'Reject'
        };
        return map[rec] || rec;
    }
    
    formatCurrency(value) {
        if (!value) return '0';
        if (value >= 10000000) return (value / 10000000).toFixed(1) + 'Cr';
        if (value >= 100000) return (value / 100000).toFixed(1) + 'L';
        return value.toFixed(0);
    }
    
    onMarkerClick(site) {
        // Animate marker
        const marker = this.markers.get(site.site_id);
        if (marker) {
            const icon = marker.getElement();
            if (icon) {
                const markerIcon = icon.querySelector('.marker-icon');
                if (markerIcon) {
                    markerIcon.classList.add('marker-pulse');
                    setTimeout(() => {
                        markerIcon.classList.remove('marker-pulse');
                    }, 2000);
                }
            }
        }
    }
    
    async showSiteDetails(siteId) {
        try {
            const response = await fetch(`/demo4/api/sites/${siteId}/detailed`);
            const data = await response.json();
            
            if (data.success) {
                this.displaySiteModal(data.site, data.evaluation, data.permits);
            }
        } catch (error) {
            console.error('Error loading site details:', error);
        }
    }
    
    displaySiteModal(site, evaluation, permits) {
        const modal = document.getElementById('siteDetailModal');
        const modalTitle = document.getElementById('modalSiteTitle');
        const modalBody = document.getElementById('modalBody');
        
        modalTitle.textContent = `${site.city}, ${site.state} (${site.site_id})`;
        
        const content = `
            <div class="site-detail-content">
                <div class="detail-section">
                    <h4><i class="fas fa-map-marker-alt"></i> Location Information</h4>
                    <div class="detail-grid">
                        <div class="detail-item">
                            <span class="detail-label">City Tier</span>
                            <span class="detail-value">${site.city_tier.replace('_', ' ')}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Network Position</span>
                            <span class="detail-value">${site.network_position}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Daily Traffic</span>
                            <span class="detail-value">${site.daily_traffic_count || 'N/A'}</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">${site.status}</span>
                        </div>
                    </div>
                </div>
                
                ${evaluation ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-chart-line"></i> Evaluation Results</h4>
                        <div class="score-breakdown">
                            <div class="score-item">
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${evaluation.scores.traffic}%; background: #3b82f6;"></div>
                                </div>
                                <span class="score-label">Traffic: ${evaluation.scores.traffic}/100</span>
                            </div>
                            <div class="score-item">
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${evaluation.scores.demographics}%; background: #10b981;"></div>
                                </div>
                                <span class="score-label">Demographics: ${evaluation.scores.demographics}/100</span>
                            </div>
                            <div class="score-item">
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${evaluation.scores.pipeline_infrastructure}%; background: #f59e0b;"></div>
                                </div>
                                <span class="score-label">Pipeline Infrastructure: ${evaluation.scores.pipeline_infrastructure}/100</span>
                            </div>
                            <div class="score-item">
                                <div class="score-bar">
                                    <div class="score-fill" style="width: ${evaluation.scores.overall}%; background: #8b5cf6;"></div>
                                </div>
                                <span class="score-label"><strong>Overall: ${evaluation.scores.overall}/100</strong></span>
                            </div>
                        </div>
                        
                        <div class="financial-summary">
                            <h5>Financial Projections</h5>
                            <div class="detail-grid">
                                <div class="detail-item">
                                    <span class="detail-label">CAPEX</span>
                                    <span class="detail-value">₹${this.formatCurrency(evaluation.financials.capex_inr)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">NPV</span>
                                    <span class="detail-value">₹${this.formatCurrency(evaluation.financials.npv_inr)}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">IRR</span>
                                    <span class="detail-value">${evaluation.financials.irr_percentage?.toFixed(1)}%</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Payback</span>
                                    <span class="detail-value">${evaluation.financials.payback_years?.toFixed(1)} years</span>
                                </div>
                            </div>
                        </div>
                    </div>
                ` : `
                    <div class="detail-section" style="text-align: center; padding: 40px 20px;">
                        <p style="color: var(--text-muted); margin-bottom: 20px; font-size: 15px;">Site not yet evaluated.</p>
                        <button class="btn-evaluate" onclick="window.mapController.evaluateSite('${site.site_id}')">
                            <i class="fas fa-chart-line"></i>
                            <span>Evaluate Site</span>
                        </button>
                    </div>
                `}
                
                ${permits && permits.length > 0 ? `
                    <div class="detail-section">
                        <h4><i class="fas fa-clipboard-check"></i> Permits (${permits.length})</h4>
                        <div class="permits-list">
                            ${permits.map(p => `
                                <div class="permit-item">
                                    <div class="permit-header">
                                        <span class="permit-type">${p.permit_type.replace('_', ' ')}</span>
                                        <span class="permit-status status-${p.status}">${p.status.replace('_', ' ')}</span>
                                    </div>
                                    <div class="permit-agency">${p.agency_name}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        modalBody.innerHTML = content;
        modal.style.display = 'flex';
    }
    
    async evaluateSite(siteId) {
        // Close modal if open
        document.getElementById('siteDetailModal').style.display = 'none';
        
        // Show evaluation progress overlay
        const progressOverlay = this.createEvaluationProgressOverlay(siteId);
        document.body.appendChild(progressOverlay);
        
        const steps = [
            { id: 'traffic', text: 'Analyzing traffic patterns', duration: 800 },
            { id: 'demographics', text: 'Evaluating demographics', duration: 900 },
            { id: 'infrastructure', text: 'Assessing infrastructure', duration: 1000 },
            { id: 'financial', text: 'Calculating financials', duration: 1100 },
            { id: 'permits', text: 'Checking permits', duration: 700 }
        ];
        
        // Animate steps
        for (let i = 0; i < steps.length; i++) {
            const step = steps[i];
            const stepEl = progressOverlay.querySelector(`#step-${step.id}`);
            const progressBar = progressOverlay.querySelector('.evaluation-progress-fill');
            
            // Mark as active
            stepEl.classList.add('active');
            
            // Update progress bar
            const progress = ((i + 1) / steps.length) * 100;
            progressBar.style.width = `${progress}%`;
            
            // Wait for step duration
            await new Promise(resolve => setTimeout(resolve, step.duration));
            
            // Mark as completed
            stepEl.classList.remove('active');
            stepEl.classList.add('completed');
        }
        
        try {
            const response = await fetch(`/demo4/api/sites/evaluate-comprehensive`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ site_id: siteId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Show success state
                await new Promise(resolve => setTimeout(resolve, 500));
                progressOverlay.remove();
                
                // Reload data and show updated modal
                await this.loadSitesData();
                await this.showSiteDetails(siteId);
                
                // Show success message
                this.showToast('Evaluation completed successfully!', 'success');
            } else {
                throw new Error(data.error || 'Evaluation failed');
            }
        } catch (error) {
            console.error('Error evaluating site:', error);
            progressOverlay.remove();
            this.showToast('Evaluation failed: ' + error.message, 'error');
        }
    }
    
    createEvaluationProgressOverlay(siteId) {
        const site = this.sitesData.find(s => s.site_id === siteId);
        const siteName = site ? `${site.city}, ${site.state}` : siteId;
        
        const overlay = document.createElement('div');
        overlay.className = 'evaluation-progress';
        overlay.innerHTML = `
            <div class="evaluation-card">
                <div class="evaluation-header">
                    <div class="evaluation-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3 class="evaluation-title">Evaluating Site</h3>
                    <p class="evaluation-subtitle">${siteName}</p>
                </div>
                
                <div class="evaluation-steps">
                    <div class="evaluation-step" id="step-traffic">
                        <div class="step-icon"><i class="fas fa-car"></i></div>
                        <div class="step-text">Analyzing traffic patterns</div>
                    </div>
                    <div class="evaluation-step" id="step-demographics">
                        <div class="step-icon"><i class="fas fa-users"></i></div>
                        <div class="step-text">Evaluating demographics</div>
                    </div>
                    <div class="evaluation-step" id="step-infrastructure">
                        <div class="step-icon"><i class="fas fa-road"></i></div>
                        <div class="step-text">Assessing infrastructure</div>
                    </div>
                    <div class="evaluation-step" id="step-financial">
                        <div class="step-icon"><i class="fas fa-dollar-sign"></i></div>
                        <div class="step-text">Calculating financials</div>
                    </div>
                    <div class="evaluation-step" id="step-permits">
                        <div class="step-icon"><i class="fas fa-clipboard-check"></i></div>
                        <div class="step-text">Checking permits</div>
                    </div>
                </div>
                
                <div class="evaluation-progress-bar">
                    <div class="evaluation-progress-fill" style="width: 0%;"></div>
                </div>
            </div>
        `;
        
        return overlay;
    }
    
    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)'};
            color: white;
            padding: 16px 24px;
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
            z-index: 30000;
            font-weight: 600;
            animation: slideInRight 0.3s ease;
        `;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    // Continued in next part...
    
    applyFilters() {
        this.filteredSites = this.sitesData.filter(site => {
            // Tier filter
            if (this.filters.tier !== 'all' && site.city_tier !== this.filters.tier) {
                return false;
            }
            
            // Status filter
            if (this.filters.status !== 'all') {
                if (this.filters.status === 'evaluated' && !site.evaluated) {
                    return false;
                }
                if (this.filters.status !== 'evaluated' && site.status !== this.filters.status) {
                    return false;
                }
            }
            
            // Score filter
            if (site.evaluated && site.score < this.filters.minScore) {
                return false;
            }
            
            return true;
        });
        
        this.renderMarkers();
        this.updateStatistics();
    }
    
    updateStatistics() {
        const total = this.sitesData.length;
        const evaluated = this.sitesData.filter(s => s.evaluated).length;
        const highScore = this.sitesData.filter(s => s.evaluated && s.score >= 80).length;
        const cities = new Set(this.sitesData.map(s => s.city)).size;
        
        document.getElementById('totalSites').textContent = total;
        document.getElementById('evaluatedSites').textContent = evaluated;
        document.getElementById('highScoreSites').textContent = highScore;
        document.getElementById('citiesCount').textContent = cities;
    }
    
    initializeEventHandlers() {
        // Filter buttons
        document.querySelectorAll('.btn-filter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filterType = btn.dataset.filter;
                const filterValue = btn.dataset.value;
                
                // Update active state
                document.querySelectorAll(`[data-filter="${filterType}"]`).forEach(b => {
                    b.classList.remove('active');
                });
                btn.classList.add('active');
                
                // Apply filter
                this.filters[filterType] = filterValue;
                this.applyFilters();
            });
        });
        
        // Score range slider (removed - no longer in UI)
        // const scoreRange = document.getElementById('scoreRange');
        // const scoreRangeValue = document.getElementById('scoreRangeValue');
        
        // Layer toggles (removed from UI - keeping defaults)
        // document.getElementById('layerSites').addEventListener('change', (e) => {
        //     this.layers.sites = e.target.checked;
        //     this.renderMarkers();
        // });
        
        // document.getElementById('layerClusters').addEventListener('change', (e) => {
        //     this.layers.clusters = e.target.checked;
        //     this.renderMarkers();
        // });
        
        // document.getElementById('layerHeatmap').addEventListener('change', (e) => {
        //     this.layers.heatmap = e.target.checked;
        //     this.toggleHeatmap(e.target.checked);
        // });
        
        // Map controls
        document.getElementById('btnZoomIn').addEventListener('click', () => {
            this.map.zoomIn();
        });
        
        document.getElementById('btnZoomOut').addEventListener('click', () => {
            this.map.zoomOut();
        });
        
        document.getElementById('btnResetView').addEventListener('click', () => {
            this.map.setView([20.5937, 78.9629], 5);
        });
        
        document.getElementById('btnFullscreen').addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        // Search
        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');
        const btnClearSearch = document.getElementById('btnClearSearch');
        
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            
            if (query.length > 0) {
                btnClearSearch.style.display = 'block';
                const results = this.searchSites(query);
                this.displaySearchResults(results);
            } else {
                btnClearSearch.style.display = 'none';
                searchResults.style.display = 'none';
            }
        });
        
        btnClearSearch.addEventListener('click', () => {
            searchInput.value = '';
            btnClearSearch.style.display = 'none';
            searchResults.style.display = 'none';
        });
        
        // Modal close
        document.getElementById('btnCloseModal').addEventListener('click', () => {
            document.getElementById('siteDetailModal').style.display = 'none';
        });
    }
    
    searchSites(query) {
        return this.sitesData.filter(site => {
            return (
                site.city.toLowerCase().includes(query) ||
                site.state.toLowerCase().includes(query) ||
                site.site_id.toLowerCase().includes(query)
            );
        }).slice(0, 10); // Limit to 10 results
    }
    
    displaySearchResults(results) {
        const searchResults = document.getElementById('searchResults');
        
        if (results.length === 0) {
            searchResults.innerHTML = '<div style="padding: 12px; color: #a0aec0;">No results found</div>';
        } else {
            searchResults.innerHTML = results.map(site => `
                <div class="search-result-item" onclick="window.mapController.flyToSite('${site.site_id}')">
                    <div class="search-result-name">${site.city}, ${site.state}</div>
                    <div class="search-result-details">
                        ${site.site_id} • ${site.city_tier.replace('_', ' ')} • 
                        ${site.evaluated ? `Score: ${Math.round(site.score)}` : 'Not evaluated'}
                    </div>
                </div>
            `).join('');
        }
        
        searchResults.style.display = 'block';
    }
    
    flyToSite(siteId) {
        const site = this.sitesData.find(s => s.site_id === siteId);
        if (site) {
            this.map.flyTo([site.latitude, site.longitude], 12, {
                duration: 1.5
            });
            
            // Open popup
            setTimeout(() => {
                const marker = this.markers.get(siteId);
                if (marker) {
                    marker.openPopup();
                }
            }, 1500);
            
            // Hide search results
            document.getElementById('searchResults').style.display = 'none';
        }
    }
    
    toggleHeatmap(show) {
        if (show) {
            // Create heatmap data
            const heatData = this.sitesData
                .filter(s => s.latitude && s.longitude)
                .map(s => [
                    s.latitude,
                    s.longitude,
                    s.evaluated ? s.score / 100 : 0.3
                ]);
            
            this.heatmapLayer = L.heatLayer(heatData, {
                radius: 25,
                blur: 35,
                maxZoom: 10,
                gradient: {
                    0.0: '#3b82f6',
                    0.5: '#f59e0b',
                    1.0: '#10b981'
                }
            }).addTo(this.map);
        } else {
            if (this.heatmapLayer) {
                this.map.removeLayer(this.heatmapLayer);
                this.heatmapLayer = null;
            }
        }
    }
    
    toggleFullscreen() {
        const elem = document.documentElement;
        
        if (!document.fullscreenElement) {
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) {
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) {
                elem.msRequestFullscreen();
            }
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    }
    
    highlightSites(siteIds) {
        // Clear all highlights
        this.markers.forEach(marker => {
            const icon = marker.getElement();
            if (icon) {
                icon.style.transform = 'scale(1)';
                icon.style.zIndex = '0';
            }
        });
        
        // Highlight specified sites
        siteIds.forEach(siteId => {
            const marker = this.markers.get(siteId);
            if (marker) {
                const icon = marker.getElement();
                if (icon) {
                    icon.style.transform = 'scale(1.5)';
                    icon.style.zIndex = '1000';
                    
                    const markerIcon = icon.querySelector('.marker-icon');
                    if (markerIcon) {
                        markerIcon.classList.add('marker-pulse');
                    }
                }
            }
        });
    }
    
    showLoading(show) {
        const overlay = document.getElementById('mapLoadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.mapController = new CNGNetworkMapController();
    console.log('Map controller initialized');
});
