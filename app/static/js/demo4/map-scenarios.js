/**
 * Demo 4: Map Scenarios
 * Handles scenario execution and visualization on the map
 */

class MapScenarioController {
    constructor(mapController) {
        this.mapController = mapController;
        this.activeScenario = null;
        this.initializeHandlers();
    }
    
    initializeHandlers() {
        // Expansion scenario
        document.getElementById('scenarioExpansion')?.addEventListener('click', () => {
            this.executeExpansionScenario();
        });
        
        // Optimization scenario
        document.getElementById('scenarioOptimization')?.addEventListener('click', () => {
            this.executeOptimizationScenario();
        });
        
        // Crisis scenario
        document.getElementById('scenarioCrisis')?.addEventListener('click', () => {
            this.executeCrisisScenario();
        });
        
        // Close scenario overlay
        document.getElementById('btnCloseScenario')?.addEventListener('click', () => {
            this.closeScenarioOverlay();
        });
    }
    
    async executeExpansionScenario() {
        this.showScenarioOverlay(
            'Mumbai Metro Expansion',
            'Analyzing 15 sites near new metro stations...'
        );
        
        try {
            // Get Mumbai sites
            const mumbaiSites = this.mapController.sitesData.filter(s => 
                s.city === 'Mumbai' || s.city === 'Pune'
            ).slice(0, 15);
            
            if (mumbaiSites.length === 0) {
                this.updateScenarioStatus('No Mumbai sites found');
                return;
            }
            
            // Fly to Mumbai
            this.mapController.map.flyTo([19.0760, 72.8777], 10, { duration: 2 });
            
            // Animate through sites
            for (let i = 0; i < mumbaiSites.length; i++) {
                const site = mumbaiSites[i];
                const progress = ((i + 1) / mumbaiSites.length) * 100;
                
                this.updateScenarioProgress(progress);
                this.updateScenarioStatus(
                    `Evaluating site ${i + 1}/${mumbaiSites.length}: ${site.site_id}`
                );
                
                // Highlight site
                this.mapController.highlightSites([site.site_id]);
                
                // Fly to site
                this.mapController.map.flyTo([site.latitude, site.longitude], 13, {
                    duration: 0.5
                });
                
                await this.sleep(800);
            }
            
            this.updateScenarioStatus('✓ Expansion analysis complete! 10 sites recommended.');
            
            // Show recommended sites
            setTimeout(() => {
                const recommended = mumbaiSites.filter(s => s.evaluated && s.score >= 65);
                this.mapController.highlightSites(recommended.map(s => s.site_id));
            }, 1000);
            
        } catch (error) {
            console.error('Expansion scenario error:', error);
            this.updateScenarioStatus('Error: ' + error.message);
        }
    }
    
    async executeOptimizationScenario() {
        this.showScenarioOverlay(
            'Network Optimization',
            'Optimizing site selection across India...'
        );
        
        try {
            // Get evaluated sites
            const evaluatedSites = this.mapController.sitesData.filter(s => s.evaluated);
            
            if (evaluatedSites.length === 0) {
                this.updateScenarioStatus('No evaluated sites available');
                return;
            }
            
            // Sort by score
            const sortedSites = [...evaluatedSites].sort((a, b) => b.score - a.score);
            const topSites = sortedSites.slice(0, 30);
            
            // Reset view
            this.mapController.map.setView([20.5937, 78.9629], 5);
            
            this.updateScenarioStatus('Analyzing all evaluated sites...');
            await this.sleep(1500);
            
            // Highlight top sites progressively
            for (let i = 0; i < topSites.length; i++) {
                const progress = ((i + 1) / topSites.length) * 100;
                this.updateScenarioProgress(progress);
                
                const site = topSites[i];
                this.updateScenarioStatus(
                    `Selected site ${i + 1}/30: ${site.city} (Score: ${Math.round(site.score)})`
                );
                
                // Highlight progressively
                const selectedIds = topSites.slice(0, i + 1).map(s => s.site_id);
                this.mapController.highlightSites(selectedIds);
                
                await this.sleep(200);
            }
            
            this.updateScenarioStatus(
                `✓ Optimization complete! Selected 30 sites with avg score ${Math.round(topSites.reduce((sum, s) => sum + s.score, 0) / topSites.length)}`
            );
            
        } catch (error) {
            console.error('Optimization scenario error:', error);
            this.updateScenarioStatus('Error: ' + error.message);
        }
    }
    
    async executeCrisisScenario() {
        this.showScenarioOverlay(
            'Permit Crisis Response',
            'Identifying sites with permit delays...'
        );
        
        try {
            // Get Bengaluru sites
            const bengaluruSites = this.mapController.sitesData.filter(s => 
                s.city === 'Bengaluru' || s.city === 'Bangalore'
            ).slice(0, 10);
            
            if (bengaluruSites.length === 0) {
                this.updateScenarioStatus('No Bengaluru sites found');
                return;
            }
            
            // Fly to Bengaluru
            this.mapController.map.flyTo([12.9716, 77.5946], 11, { duration: 2 });
            
            await this.sleep(2000);
            
            this.updateScenarioStatus('Checking permit status across 10 sites...');
            this.updateScenarioProgress(20);
            
            await this.sleep(1500);
            
            this.updateScenarioStatus('⚠ 6 sites identified with permit delays');
            this.updateScenarioProgress(40);
            
            // Highlight problem sites
            const problemSites = bengaluruSites.slice(0, 6);
            this.mapController.highlightSites(problemSites.map(s => s.site_id));
            
            await this.sleep(2000);
            
            this.updateScenarioStatus('Contacting agencies: BBMP, BESCOM, KSPCB...');
            this.updateScenarioProgress(60);
            
            await this.sleep(1500);
            
            this.updateScenarioStatus('Generating escalation plan...');
            this.updateScenarioProgress(80);
            
            await this.sleep(1500);
            
            this.updateScenarioStatus('✓ Crisis resolution plan ready. Estimated time reduction: 30 days');
            this.updateScenarioProgress(100);
            
        } catch (error) {
            console.error('Crisis scenario error:', error);
            this.updateScenarioStatus('Error: ' + error.message);
        }
    }
    
    showScenarioOverlay(title, initialStatus) {
        const overlay = document.getElementById('scenarioOverlay');
        const titleElem = document.getElementById('scenarioOverlayTitle');
        const statusElem = document.getElementById('scenarioStatus');
        const progressBar = document.getElementById('scenarioProgress');
        
        titleElem.textContent = title;
        statusElem.textContent = initialStatus;
        progressBar.style.width = '0%';
        
        overlay.style.display = 'block';
        
        this.activeScenario = {
            title: title,
            startTime: Date.now()
        };
    }
    
    updateScenarioProgress(percent) {
        const progressBar = document.getElementById('scenarioProgress');
        progressBar.style.width = `${percent}%`;
    }
    
    updateScenarioStatus(status) {
        const statusElem = document.getElementById('scenarioStatus');
        statusElem.textContent = status;
    }
    
    closeScenarioOverlay() {
        const overlay = document.getElementById('scenarioOverlay');
        overlay.style.display = 'none';
        
        // Clear all highlights
        this.mapController.highlightSites([]);
        
        this.activeScenario = null;
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize when map controller is ready
document.addEventListener('DOMContentLoaded', () => {
    // Wait for map controller to be ready
    const checkMapController = setInterval(() => {
        if (window.mapController) {
            window.mapScenarioController = new MapScenarioController(window.mapController);
            console.log('Map scenario controller initialized');
            clearInterval(checkMapController);
        }
    }, 100);
});
