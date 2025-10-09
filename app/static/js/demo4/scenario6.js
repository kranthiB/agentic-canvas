/**
 * Scenario 6: Competitive Acquisition (M&A) Controller
 * Manages M&A sprint workflow, decision dashboard, and deal execution
 */

class Scenario6Controller {
    constructor() {
        this.currentPhase = 'alert';
        this.countdownTimer = null;
        this.sprintTimer = null;
        this.currentSprintId = null;
        this.eventStreamInterval = null;
        
        this.init();
    }

    init() {
        console.log('Initializing Scenario 6: Competitive Acquisition (M&A)');
        this.setupEventHandlers();
        this.startCountdownTimer();
        this.loadMaOpportunityData();
    }

    setupEventHandlers() {
        // M&A Sprint activation
        const btnActivateSprint = document.getElementById('btnActivateSprint');
        if (btnActivateSprint) {
            btnActivateSprint.addEventListener('click', () => this.activateMaSprint());
        }

        // Decision dashboard
        const btnShowDecision = document.getElementById('btnShowDecision');
        if (btnShowDecision) {
            btnShowDecision.addEventListener('click', () => this.showDecisionDashboard());
        }

        // Bid approval
        const btnApproveBid = document.getElementById('btnApproveBid');
        if (btnApproveBid) {
            btnApproveBid.addEventListener('click', () => this.approveBid());
        }

        // Show transformation results
        const btnShowTransformation = document.getElementById('btnShowTransformation');
        if (btnShowTransformation) {
            btnShowTransformation.addEventListener('click', () => this.showTransformation());
        }

        // Close buttons
        const btnCloseSprint = document.getElementById('btnCloseSprint');
        if (btnCloseSprint) {
            btnCloseSprint.addEventListener('click', () => this.closeSprint());
        }
    }

    startCountdownTimer() {
        let hoursRemaining = 72;
        let minutesRemaining = 0;
        let secondsRemaining = 0;

        this.countdownTimer = setInterval(() => {
            if (secondsRemaining > 0) {
                secondsRemaining--;
            } else if (minutesRemaining > 0) {
                minutesRemaining--;
                secondsRemaining = 59;
            } else if (hoursRemaining > 0) {
                hoursRemaining--;
                minutesRemaining = 59;
                secondsRemaining = 59;
            } else {
                clearInterval(this.countdownTimer);
                return;
            }

            const timeString = `${hoursRemaining.toString().padStart(2, '0')}:${minutesRemaining.toString().padStart(2, '0')}:${secondsRemaining.toString().padStart(2, '0')}`;
            
            const countdownElement = document.getElementById('countdownTimer');
            if (countdownElement) {
                countdownElement.textContent = timeString;
            }

            const sprintCountdownElement = document.getElementById('sprintCountdown');
            if (sprintCountdownElement && this.currentPhase === 'sprint') {
                sprintCountdownElement.textContent = timeString;
            }
        }, 1000);
    }

    async loadMaOpportunityData() {
        try {
            const response = await fetch('/demo4/api/scenario6/ma-opportunity');
            const data = await response.json();
            
            if (data.success) {
                this.updateOpportunityDisplay(data.data);
            }
        } catch (error) {
            console.error('Error loading M&A opportunity data:', error);
        }
    }

    updateOpportunityDisplay(data) {
        // Update countdown with actual deadline
        if (data.deadline && data.deadline.hours_remaining) {
            // Implementation would update countdown based on actual deadline
        }

        // Update target information dynamically if needed
        console.log('M&A Opportunity Data:', data);
    }

    async activateMaSprint() {
        try {
            console.log('Activating M&A analysis sprint...');
            
            // Hide alert banner and show sprint container
            const alertBanner = document.getElementById('maAlertBanner');
            const sprintContainer = document.getElementById('maSprint');
            
            if (alertBanner) alertBanner.style.display = 'none';
            if (sprintContainer) sprintContainer.style.display = 'block';
            
            this.currentPhase = 'sprint';

            // Start the sprint
            const response = await fetch('/demo4/api/scenario6/run-ma-sprint', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    target: 'Statiq Energy'
                })
            });

            const data = await response.json();
            
            if (data.success) {
                this.currentSprintId = data.sprint.correlation_id;
                this.startEventStream();
            }

        } catch (error) {
            console.error('Error activating M&A sprint:', error);
        }
    }

    startEventStream() {
        if (!this.currentSprintId) return;

        let eventIndex = 0;
        const eventInterval = 3000; // 3 seconds between events

        this.eventStreamInterval = setInterval(async () => {
            try {
                const response = await fetch(`/demo4/api/scenario6/sprint-events/${this.currentSprintId}`);
                const data = await response.json();

                if (data.success && data.events) {
                    // Show events progressively
                    const eventsToShow = data.events.slice(0, eventIndex + 1);
                    this.updateEventStream(eventsToShow);
                    
                    eventIndex++;

                    // Check if sprint is complete
                    if (data.sprint_complete && eventIndex >= data.events.length) {
                        clearInterval(this.eventStreamInterval);
                        this.showSprintComplete();
                    }
                }
            } catch (error) {
                console.error('Error fetching sprint events:', error);
                clearInterval(this.eventStreamInterval);
            }
        }, eventInterval);
    }

    updateEventStream(events) {
        const eventStream = document.getElementById('maEventStream');
        if (!eventStream) return;

        eventStream.innerHTML = '';

        events.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = `ma-event-item agent-${event.agent.toLowerCase().replace(/\s+/g, '-')}`;
            
            let agentClass = 'agent-orchestrator';
            if (event.agent.includes('Market')) agentClass = 'agent-market';
            else if (event.agent.includes('Geographic')) agentClass = 'agent-geographic';
            else if (event.agent.includes('Financial')) agentClass = 'agent-financial';
            else if (event.agent.includes('Permit')) agentClass = 'agent-permit';
            
            eventElement.className = `ma-event-item ${agentClass}`;

            eventElement.innerHTML = `
                <div class="ma-event-timestamp">[${event.timestamp}]</div>
                <div class="ma-event-agent">${event.agent}</div>
                <div class="ma-event-details">${event.action}</div>
                ${event.details ? `<div class="ma-event-details" style="font-style: italic; margin-top: 4px;">${event.details}</div>` : ''}
            `;

            eventStream.appendChild(eventElement);
        });

        // Scroll to bottom
        eventStream.scrollTop = eventStream.scrollHeight;
    }

    showSprintComplete() {
        const analysisStatus = document.getElementById('maAnalysisStatus');
        const sprintComplete = document.getElementById('sprintComplete');

        if (analysisStatus) {
            analysisStatus.innerHTML = `
                <i class="fas fa-check-circle" style="color: #10b981;"></i>
                <span>Sprint complete</span>
            `;
        }

        if (sprintComplete) {
            sprintComplete.style.display = 'block';
        }

        console.log('M&A sprint completed');
    }

    async showDecisionDashboard() {
        try {
            // Hide sprint container and show decision dashboard
            const sprintContainer = document.getElementById('maSprint');
            const decisionDashboard = document.getElementById('decisionDashboard');

            if (sprintContainer) sprintContainer.style.display = 'none';
            if (decisionDashboard) decisionDashboard.style.display = 'block';

            this.currentPhase = 'decision';

            // Load decision package data
            const response = await fetch('/demo4/api/scenario6/decision-package');
            const data = await response.json();

            if (data.success) {
                this.updateDecisionDashboard(data.decision);
            }

            // Animate valuation bars
            setTimeout(() => {
                this.animateValuationBars();
            }, 500);

        } catch (error) {
            console.error('Error showing decision dashboard:', error);
        }
    }

    updateDecisionDashboard(decision) {
        // Update confidence score
        const confidenceElement = document.querySelector('.confidence-score');
        if (confidenceElement) {
            confidenceElement.textContent = `Confidence Score: ${decision.confidence_score}/10 (Strong Buy)`;
        }

        // Update strategic fit metrics
        if (decision.strategic_fit) {
            const strategicFit = decision.strategic_fit;
            // Implementation would update the strategic fit card with real data
        }

        // Update network fit metrics
        if (decision.network_fit) {
            const networkFit = decision.network_fit;
            // Implementation would update the network fit card with real data
        }

        console.log('Decision dashboard updated with:', decision);
    }

    animateValuationBars() {
        const bars = document.querySelectorAll('.bar-fill');
        bars.forEach((bar, index) => {
            setTimeout(() => {
                const targetWidth = bar.style.width || '0%';
                bar.style.width = '0%';
                bar.style.transition = 'width 1s ease';
                
                setTimeout(() => {
                    bar.style.width = targetWidth;
                }, 100);
            }, index * 200);
        });
    }

    async approveBid() {
        try {
            console.log('Approving M&A bid...');

            const response = await fetch('/demo4/api/scenario6/approve-bid', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    bid_amount: 40
                })
            });

            const data = await response.json();

            if (data.success) {
                // Show deal execution tracker
                this.showDealExecution();
            }

        } catch (error) {
            console.error('Error approving bid:', error);
        }
    }

    showDealExecution() {
        const decisionDashboard = document.getElementById('decisionDashboard');
        const dealExecution = document.getElementById('dealExecution');

        if (decisionDashboard) decisionDashboard.style.display = 'none';
        if (dealExecution) dealExecution.style.display = 'block';

        this.currentPhase = 'execution';

        // Animate timeline items
        setTimeout(() => {
            this.animateTimelineItems();
        }, 500);
    }

    animateTimelineItems() {
        const timelineItems = document.querySelectorAll('.timeline-item');
        timelineItems.forEach((item, index) => {
            setTimeout(() => {
                item.style.opacity = '0';
                item.style.transform = 'translateX(-20px)';
                item.style.transition = 'all 0.5s ease';
                
                setTimeout(() => {
                    item.style.opacity = '1';
                    item.style.transform = 'translateX(0)';
                }, 100);
            }, index * 200);
        });
    }

    async showTransformation() {
        try {
            const dealExecution = document.getElementById('dealExecution');
            const transformation = document.getElementById('transformation');

            if (dealExecution) dealExecution.style.display = 'none';
            if (transformation) transformation.style.display = 'block';

            this.currentPhase = 'transformation';

            // Load post-merger results
            const response = await fetch('/demo4/api/scenario6/post-merger-results');
            const data = await response.json();

            if (data.success) {
                this.updateTransformationResults(data.results);
            }

            // Animate synergy progress bars
            setTimeout(() => {
                this.animateSynergyBars();
            }, 1000);

        } catch (error) {
            console.error('Error showing transformation results:', error);
        }
    }

    updateTransformationResults(results) {
        // Update synergy realization numbers
        if (results.synergy_realization) {
            const projectedElement = document.querySelector('.synergy-projected');
            const actualElement = document.querySelector('.synergy-actual');
            
            if (projectedElement) {
                projectedElement.textContent = `₹${results.synergy_realization.projected_annual} Cr`;
            }
            
            if (actualElement) {
                actualElement.textContent = `₹${results.synergy_realization.actual_6_months} Cr`;
            }
        }

        console.log('Transformation results updated:', results);
    }

    animateSynergyBars() {
        const progressBars = document.querySelectorAll('.progress-fill');
        progressBars.forEach((bar, index) => {
            setTimeout(() => {
                const targetWidth = bar.style.width || '0%';
                bar.style.width = '0%';
                bar.style.transition = 'width 1.5s ease';
                
                setTimeout(() => {
                    bar.style.width = targetWidth;
                }, 200);
            }, index * 500);
        });
    }

    closeSprint() {
        const sprintContainer = document.getElementById('maSprint');
        const alertBanner = document.getElementById('maAlertBanner');

        if (sprintContainer) sprintContainer.style.display = 'none';
        if (alertBanner) alertBanner.style.display = 'block';

        this.currentPhase = 'alert';

        // Clear event stream
        if (this.eventStreamInterval) {
            clearInterval(this.eventStreamInterval);
            this.eventStreamInterval = null;
        }
    }

    cleanup() {
        if (this.countdownTimer) {
            clearInterval(this.countdownTimer);
        }
        
        if (this.eventStreamInterval) {
            clearInterval(this.eventStreamInterval);
        }
        
        console.log('Scenario 6 controller cleaned up');
    }
}

// Export for use in HTML
if (typeof window !== 'undefined') {
    window.Scenario6Controller = Scenario6Controller;
}