/**
 * Demo 4: Interactive Map Controller
 * Manages Leaflet.js map, markers, layers, and user interactions
 */

class EVNetworkMapController {
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
        
        // Add tile layer (dark theme)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '© OpenStreetMap © CartoDB',
            subdomains: 'abcd',
            maxZoom: 19
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
                    html: `<div class="marker-cluster marker-cluster-${size}">${count}</div>`,
                    className: 'custom-cluster-icon',
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
                <i class="fas fa-charging-station"></i>
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
                                    <div class="score-fill" style="width: ${evaluation.scores.grid_infrastructure}%; background: #f59e0b;"></div>
                                </div>
                                <span class="score-label">Infrastructure: ${evaluation.scores.grid_infrastructure}/100</span>
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
                ` : '<p style="color: #a0aec0;">Site not yet evaluated.</p>'}
                
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
        this.showLoading(true);
        
        try {
            const response = await fetch(`/demo4/api/sites/evaluate-comprehensive`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ site_id: siteId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Reload sites data
                await this.loadSitesData();
                alert('Site evaluation completed successfully!');
            } else {
                alert('Evaluation failed: ' + (data.error || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error evaluating site:', error);
            alert('Evaluation failed');
        } finally {
            this.showLoading(false);
        }
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
        
        // Score range slider
        const scoreRange = document.getElementById('scoreRange');
        const scoreRangeValue = document.getElementById('scoreRangeValue');
        
        scoreRange.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            this.filters.minScore = value;
            scoreRangeValue.textContent = `${value}-100`;
            this.applyFilters();
        });
        
        // Layer toggles
        document.getElementById('layerSites').addEventListener('change', (e) => {
            this.layers.sites = e.target.checked;
            this.renderMarkers();
        });
        
        document.getElementById('layerClusters').addEventListener('change', (e) => {
            this.layers.clusters = e.target.checked;
            this.renderMarkers();
        });
        
        document.getElementById('layerHeatmap').addEventListener('change', (e) => {
            this.layers.heatmap = e.target.checked;
            this.toggleHeatmap(e.target.checked);
        });
        
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
    window.mapController = new EVNetworkMapController();
    console.log('Map controller initialized');
});
