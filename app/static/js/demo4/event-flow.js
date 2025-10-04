/**
 * Demo 4: Enhanced Event Flow Visualizer for Mobility Maestro
 * Based on Demo 5's pattern with scenario dropdown and simulation
 */

class EventFlowVisualizer {
    constructor() {
        this.canvas = document.getElementById('architectureCanvas');
        this.svg = document.getElementById('connectionsSvg');
        this.eventLog = document.getElementById('eventLog');
        this.isSimulating = false;
        this.currentScenario = null;
        this.eventCount = 0;
        this.animationPaused = false;
        this.eventQueue = [];
        this.stats = {
            activeEvents: 0,
            agentsInvoked: 0,
            systemsQueried: 0,
            processingTime: 0,
            successRate: 100
        };
        
        this.init();
    }
    
    init() {
        this.initializeEventHandlers();
        this.initializeTooltips();
        this.startRealtimeStatsUpdate();
        this.loadScenarios();
        
        console.log('Demo 4 Event Flow Visualizer initialized');
    }
    
    initializeEventHandlers() {
        // Scenario selection
        const scenarioSelect = document.getElementById('scenarioSelect');
        const simulateBtn = document.getElementById('simulateFlow');
        
        if (scenarioSelect) {
            scenarioSelect.addEventListener('change', () => {
                simulateBtn.disabled = !scenarioSelect.value;
            });
        }
        
        if (simulateBtn) {
            simulateBtn.addEventListener('click', () => {
                this.simulateSelectedScenario();
            });
        }
        
        // Quick action buttons
        const randomBtn = document.getElementById('runRandomScenario');
        const crisisBtn = document.getElementById('runCrisisScenario');
        
        if (randomBtn) {
            randomBtn.addEventListener('click', () => this.simulateRandomScenario());
        }
        
        if (crisisBtn) {
            crisisBtn.addEventListener('click', () => this.simulateCrisisScenario());
        }
        
        // Control buttons
        const clearBtn = document.getElementById('clearEvents');
        const pauseBtn = document.getElementById('pauseAnimation');
        const resumeBtn = document.getElementById('resumeAnimation');
        const clearLogBtn = document.getElementById('clearLog');
        
        if (clearBtn) {
            clearBtn.addEventListener('click', () => this.clear());
        }
        
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => this.pauseAnimation());
        }
        
        if (resumeBtn) {
            resumeBtn.addEventListener('click', () => this.resumeAnimation());
        }
        
        if (clearLogBtn) {
            clearLogBtn.addEventListener('click', () => this.clearEventLog());
        }
        
                document.getElementById('resumeAnimation').addEventListener('click', () => {
            this.resumeAnimation();
        });
    }

    async loadScenarios() {
        try {
            const response = await fetch('/demo4/api/scenarios');
            const data = await response.json();
            
            if (data.success) {
                this.populateScenarioDropdown(data.scenarios);
            }
        } catch (error) {
            console.error('Failed to load scenarios:', error);
        }
    }
    
    populateScenarioDropdown(scenarios) {
        const select = document.getElementById('scenarioSelect');
        if (!select) return;
        
        // Clear existing options except the first one
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // Add scenario options
        Object.entries(scenarios).forEach(([key, scenario]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = scenario.name;
            select.appendChild(option);
        });
    }

    async simulateSelectedScenario() {
        const select = document.getElementById('scenarioSelect');
        if (!select || !select.value) return;
        
        await this.simulateScenario(select.value);
    }
    
    async simulateRandomScenario() {
        try {
            const response = await fetch('/demo4/api/scenarios');
            const data = await response.json();
            
            if (data.success) {
                const scenarios = Object.keys(data.scenarios);
                const randomKey = scenarios[Math.floor(Math.random() * scenarios.length)];
                await this.simulateScenario(randomKey);
            }
        } catch (error) {
            console.error('Failed to simulate random scenario:', error);
        }
    }
    
    async simulateCrisisScenario() {
        await this.simulateScenario('scenario_1_crisis');
    }
    
    async getAvailableScenarios() {
        try {
            const response = await fetch('/demo4/api/scenarios');
            const data = await response.json();
            return data.success ? Object.keys(data.scenarios) : [];
        } catch (error) {
            console.error('Failed to get available scenarios:', error);
            return [];
        }
    }
    


    async simulateScenario(scenarioId) {
        if (this.isSimulating) {
            this.showToast('Simulation already in progress', 'warning');
            return;
        }
        
        // Complete reset before starting new simulation
        console.log('🔄 Starting new simulation - clearing all previous state');
        this.clear();
        this.isSimulating = true;
        
        const simulateBtn = document.getElementById('simulateFlow');
        if (simulateBtn) {
            simulateBtn.disabled = true;
            simulateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Simulating...';
        }
        
        try {
            // Get scenario data
            const response = await fetch(`/demo4/api/scenarios/${scenarioId}/simulate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentScenario = data.scenario;
                this.showScenarioInfo(data.scenario);
                
                // Animate the flow steps
                await this.animateFlowSteps(data.flow_steps);
                
                // Show scenario outcome if available
                if (data.scenario.outcome) {
                    this.showScenarioOutcome(data.scenario.outcome);
                }
                
                this.showToast(`Scenario "${data.scenario.name}" completed successfully!`, 'success');
            } else {
                this.showToast(`Simulation failed: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Simulation error:', error);
            this.showToast(`Network error: ${error.message}`, 'error');
        } finally {
            this.isSimulating = false;
            if (simulateBtn) {
                simulateBtn.disabled = false;
                simulateBtn.innerHTML = '<i class="fas fa-play"></i> Simulate Flow';
            }
        }
    }
    
    showScenarioInfo(scenario) {
        const scenarioInfo = document.getElementById('scenarioInfo');
        const scenarioBadge = document.getElementById('scenarioBadge');
        const scenarioName = document.getElementById('scenarioName');
        const scenarioDescription = document.getElementById('scenarioDescription');
        
        if (scenarioInfo && scenarioBadge && scenarioName && scenarioDescription) {
            // Set badge color based on scenario type
            const badgeClass = this.getScenarioBadgeColor(scenario.type);
            scenarioBadge.className = `scenario-badge ${badgeClass}`;
            scenarioBadge.textContent = scenario.type.toUpperCase();
            
            scenarioName.textContent = scenario.name;
            scenarioDescription.textContent = scenario.description;
            
            scenarioInfo.style.display = 'block';
            
            // Auto-hide after 10 seconds
            setTimeout(() => {
                scenarioInfo.style.display = 'none';
            }, 10000);
        }
    }
    
    getScenarioBadgeColor(type) {
        switch (type) {
            case 'crisis': return 'badge-danger';
            case 'expansion': return 'badge-success';
            case 'competitive': return 'badge-warning';
            case 'operations': return 'badge-info';
            default: return 'badge-secondary';
        }
    }
    
    showScenarioOutcome(outcome) {
        const outcomeElement = document.getElementById('scenarioOutcome');
        const outcomeTitle = document.getElementById('outcomeTitle');
        const outcomeSummary = document.getElementById('outcomeSummary');
        const businessResults = document.getElementById('businessResults');
        const problemsSolved = document.getElementById('problemsSolved');
        const keyInnovations = document.getElementById('keyInnovations');
        
        if (!outcomeElement || !outcomeTitle || !outcomeSummary || 
            !businessResults || !problemsSolved || !keyInnovations) {
            console.warn('Outcome elements not found in DOM');
            return;
        }
        
        // Set outcome content
        outcomeTitle.textContent = outcome.title || 'Scenario Complete';
        outcomeSummary.textContent = outcome.summary || '';
        
        // Populate business results
        businessResults.innerHTML = '';
        if (outcome.business_results && Array.isArray(outcome.business_results)) {
            outcome.business_results.forEach(result => {
                const li = document.createElement('li');
                li.textContent = result;
                businessResults.appendChild(li);
            });
        }
        
        // Populate problems solved
        problemsSolved.innerHTML = '';
        if (outcome.problems_solved && Array.isArray(outcome.problems_solved)) {
            outcome.problems_solved.forEach(problem => {
                const li = document.createElement('li');
                li.textContent = problem;
                problemsSolved.appendChild(li);
            });
        }
        
        // Populate key innovations
        keyInnovations.innerHTML = '';
        if (outcome.key_innovations && Array.isArray(outcome.key_innovations)) {
            outcome.key_innovations.forEach(innovation => {
                const li = document.createElement('li');
                li.textContent = innovation;
                keyInnovations.appendChild(li);
            });
        }
        
        // Show the outcome section with animation
        setTimeout(() => {
            outcomeElement.style.display = 'block';
            // Smooth scroll to outcome section
            outcomeElement.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
        }, 1000); // Delay to allow final event to complete
    }

    async animateFlowSteps(flowSteps) {
        this.clearEventLog();
        this.eventCount = 0;
        
        // Update stats
        this.stats.activeEvents = flowSteps.length;
        
        // Count unique AGENTS based on actual nodes that get highlighted
        const uniqueAgentNodes = new Set();
        this.currentScenario.involved_agents.forEach(agent => {
            const nodeId = this.getNodeById(agent)?.id;
            if (nodeId) {
                uniqueAgentNodes.add(nodeId);
            }
        });
        this.stats.agentsInvoked = uniqueAgentNodes.size;
        
        // Count unique SYSTEMS based on actual nodes that get highlighted
        const uniqueSystemNodes = new Set();
        flowSteps.forEach(step => {
            const fromNodeId = this.getNodeById(step.from)?.id;
            const toNodeId = this.getNodeById(step.to)?.id;
            if (fromNodeId) uniqueSystemNodes.add(fromNodeId);
            if (toNodeId) uniqueSystemNodes.add(toNodeId);
        });
        this.currentScenario.involved_systems.forEach(system => {
            const nodeId = this.getNodeById(system)?.id;
            if (nodeId) {
                uniqueSystemNodes.add(nodeId);
            }
        });
        this.stats.systemsQueried = uniqueSystemNodes.size;
        
        this.updateStatistics();
        
        let totalTime = 0;
        
        for (let i = 0; i < flowSteps.length; i++) {
            const step = flowSteps[i];
            
            // Check for pause
            await this.waitForResume();
            
            // Animate step
            await this.animateStep(step, i + 1, flowSteps.length);
            
            // Update processing time
            totalTime += step.delay || 500;
            this.stats.processingTime = totalTime;
            this.updateStatistics();
            
            // Wait for step delay
            await this.sleep(step.delay || 500);
        }
        
        // Note: Component highlights will persist until "Clear Log" is clicked
    }
    
    async animateStep(step, stepNumber, totalSteps) {
        const sourceNode = this.getNodeById(step.from);
        const targetNode = this.getNodeById(step.to);
        
        // Highlight source node
        if (sourceNode) {
            sourceNode.classList.add('active', 'scenario-active', 'processing');
            this.addPulseEffect(sourceNode);
            console.log(`✅ Highlighted source: ${step.from} → ${sourceNode.id}`);
        } else {
            console.warn(`❌ Node not found for source: ${step.from}`);
        }
        
        // Animate connection
        if (sourceNode && targetNode) {
            await this.animateConnection(sourceNode, targetNode);
        }
        
        // Highlight target node
        if (targetNode) {
            targetNode.classList.add('active', 'scenario-active', 'receiving');
            this.addPulseEffect(targetNode);
            console.log(`✅ Highlighted target: ${step.to} → ${targetNode.id}`);
        } else {
            console.warn(`❌ Node not found for target: ${step.to}`);
        }
        
        // Add to event log
        this.addEnhancedEventToLog(step, stepNumber, totalSteps);
        
        // Update event count
        this.eventCount++;
        this.stats.activeEvents = this.eventCount;
        this.updateStatistics();
        
        // Clean up after animation
        setTimeout(() => {
            if (sourceNode) {
                sourceNode.classList.remove('active', 'processing');
            }
            if (targetNode) {
                targetNode.classList.remove('active', 'receiving');
            }
        }, 800);
    }
    
    getNodeById(systemId) {
        // Define specific mappings for known mismatches
        const specialMappings = {
            'PromptManager': 'node-prompt-mgr',
            'ReasoningEngine': 'node-reasoning',
            'AgentMemory': 'node-agent-memory',
            'LLMGateway': 'node-llm-gateway',
            'LLMService': 'node-llm-service',
            'SemanticCache': 'node-semantic-cache',
            'VectorDB': 'node-vector-db',
            'RAGEngine': 'node-rag-engine',
            'Guardrails': 'node-guardrails',
            'ToolRegistry': 'node-tool-registry',
            'ContextManager': 'node-context-mgr',
            'Observability': 'node-observability',
            'GeographicIntelligence': 'node-geographic',
            'MarketIntelligence': 'node-market',
            'NetworkOptimization': 'node-network',
            'EnergyOptimization': 'node-network',
            'MunicipalPortal': 'node-municipal',
            'Competitor_DB': 'node-competitor',
            'Financial_System': 'node-finance-sys',
            'VAHAN_API': 'node-vahan',
            'Census_DB': 'node-census',
            'TrafficAnalysis': 'node-traffic',
            'WebScraper': 'node-ml',
            'PricingEngine': 'node-pricing',
            'WeatherAPI': 'node-weather',
            'MLPlatform': 'node-ml',
            'PGCIL': 'node-pgcil',
            'DISCOM': 'node-discom',
            'GridMonitor': 'node-grid',
            'SolarGeneration': 'node-solar',
            'BatteryMgmt': 'node-battery',
            'CRM': 'node-crm',
            'ContractMgmt': 'node-contract',
            'AlertSystem': 'node-alerts',
            'MobileApp': 'node-mobile',
            'RenewableEnergy_System': 'node-solar',
            'SolarMonitoring': 'node-solar',
            'BatteryManagement': 'node-battery',
            'GridMonitoring': 'node-grid',
            'EnergyOptimization': 'node-network',
            'ChargerDiagnostics': 'node-battery',
            'Operations': 'node-network',
            'MaintenanceSystem': 'node-alerts',
            'CustomerApp': 'node-crm',
            'MobileUnits': 'node-mobile',
            'BackupPower_System': 'node-battery',
            'EmergencyResponse_System': 'node-alerts'
        };
        
        // Check special mappings first
        if (specialMappings[systemId]) {
            const node = document.getElementById(specialMappings[systemId]);
            if (node) return node;
        }
        
        // Try direct match first
        let node = document.getElementById(`node-${systemId.toLowerCase()}`);
        if (node) return node;
        
        // Try different variations
        const variations = [
            `node-${systemId}`,
            `node-${systemId.toLowerCase().replace('_', '-')}`,
            `node-${systemId.toLowerCase().replace(' ', '-')}`,
            `node-${systemId.replace(/([A-Z])/g, '-$1').toLowerCase().substring(1)}`
        ];
        
        for (const variation of variations) {
            node = document.getElementById(variation);
            if (node) return node;
        }
        
        console.warn(`Node not found for system: ${systemId}`, 'Tried variations:', variations);
        return null;
    }
    
    addPulseEffect(node) {
        node.style.transform = 'scale(1.1)';
        node.style.boxShadow = '0 0 20px rgba(66, 153, 225, 0.6)';
        
        setTimeout(() => {
            node.style.transform = 'scale(1)';
            node.style.boxShadow = '';
        }, 600);
    }
    
    async animateConnection(sourceNode, targetNode) {
        if (!this.svg) return;
        
        const sourceRect = sourceNode.getBoundingClientRect();
        const targetRect = targetNode.getBoundingClientRect();
        const canvasRect = this.canvas.getBoundingClientRect();
        
        const x1 = sourceRect.left + sourceRect.width / 2 - canvasRect.left;
        const y1 = sourceRect.top + sourceRect.height / 2 - canvasRect.top;
        const x2 = targetRect.left + targetRect.width / 2 - canvasRect.left;
        const y2 = targetRect.top + targetRect.height / 2 - canvasRect.top;
        
        // Create animated line
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('stroke', '#4299e1');
        line.setAttribute('stroke-width', '2');
        line.setAttribute('marker-end', 'url(#arrowhead-active)');
        line.setAttribute('opacity', '0.8');
        
        this.svg.appendChild(line);
        
        // Remove line after animation
        setTimeout(() => {
            if (this.svg.contains(line)) {
                this.svg.removeChild(line);
            }
        }, 1000);
    }
    
    addEnhancedEventToLog(step, stepNumber, totalSteps) {
        if (!this.eventLog) return;
        
        // Remove empty state if present
        const emptyState = this.eventLog.querySelector('.event-log-empty');
        if (emptyState) {
            emptyState.remove();
        }
        
        const entry = document.createElement('div');
        entry.className = 'event-entry';
        
        const timestamp = new Date().toLocaleTimeString();
        
        // Enhanced system name mapping for display
        const getSystemDisplayName = (systemId) => {
            const displayNames = {
                'UI': 'User Interface',
                'Orchestrator': 'EV Orchestrator',
                'LLMGateway': 'LLM Gateway',
                'LLMService': 'LLM Service',
                'SemanticCache': 'Semantic Cache',
                'VectorDB': 'Vector Database',
                'PromptManager': 'Prompt Manager',
                'RAGEngine': 'RAG Engine',
                'ReasoningEngine': 'Reasoning Engine',
                'AgentMemory': 'Agent Memory',
                'GeographicIntelligence': 'Geographic Intelligence Agent',
                'MarketIntelligence': 'Market Intelligence Agent',
                'NetworkOptimization': 'Network Optimization Agent',
                'Financial': 'Financial Analysis Agent',
                'Permit': 'Permit Processing Agent',
                'MunicipalPortal': 'Municipal Portal API',
                'Competitor_DB': 'Competitor Database',
                'Financial_System': 'Financial System',
                'VAHAN_API': 'VAHAN API',
                'Census_DB': 'Census Database',
                'TrafficAnalysis': 'Traffic Analysis API'
            };
            return displayNames[systemId] || systemId;
        };
        
        // Determine event type for better categorization
        const getEventType = (step) => {
            if (step.description.includes('ERROR') || step.description.includes('🔴')) return 'error';
            if (step.description.includes('CRISIS') || step.description.includes('⚠️')) return 'warning';
            if (step.description.includes('SUCCESS') || step.description.includes('✅')) return 'success';
            if (step.description.includes('Query') || step.description.includes('Check')) return 'query';
            if (step.description.includes('Response') || step.description.includes('Retrieved')) return 'response';
            return 'process';
        };
        
        const eventType = getEventType(step);
        const sourceDisplay = getSystemDisplayName(step.from);
        const targetDisplay = getSystemDisplayName(step.to);
        
        entry.innerHTML = `
            <div class="event-header">
                <div class="event-step">Step ${stepNumber}/${totalSteps}</div>
                <div class="event-type event-type-${eventType}">${eventType.toUpperCase()}</div>
                <div class="event-time">${timestamp}</div>
            </div>
            <div class="event-flow">
                <span class="event-source" title="${step.from}">${sourceDisplay}</span>
                <i class="fas fa-arrow-right"></i>
                <span class="event-target" title="${step.to}">${targetDisplay}</span>
            </div>
            <div class="event-description">${step.description}</div>
            <div class="event-meta">
                <span class="event-delay">⏱️ ${step.delay}ms</span>
                <span class="event-progress">${Math.round((stepNumber/totalSteps)*100)}% Complete</span>
            </div>
        `;
        
        // Insert at top
        this.eventLog.insertBefore(entry, this.eventLog.firstChild);
        
        // Limit to 50 entries
        while (this.eventLog.children.length > 50) {
            this.eventLog.removeChild(this.eventLog.lastChild);
        }
        
        // Scroll to top
        this.eventLog.scrollTop = 0;
    }

    clear() {
        console.log('🧹 Clearing all simulation state...');
        
        // Clean up component highlights
        this.cleanupAllNodeStates();
        
        // Clear connections and visual elements
        this.clearConnections();
        
        // Reset statistics
        this.resetStats();
        
        // Clear event log directly
        if (this.eventLog) {
            this.eventLog.innerHTML = `
                <div class="event-log-empty">
                    <i class="fas fa-info-circle"></i>
                    <p>No events yet. Run a scenario to see the event flow.</p>
                </div>
            `;
        }
        
        // Hide scenario info
        const scenarioInfo = document.getElementById('scenarioInfo');
        if (scenarioInfo) {
            scenarioInfo.style.display = 'none';
        }
        
        // Reset simulation state
        this.isSimulating = false;
        this.eventCount = 0;
        
        console.log('✅ All state cleared - ready for new simulation');
    }
    
    cleanupAllNodeStates() {
        const nodes = this.canvas ? this.canvas.querySelectorAll('.system-node') : 
                      document.querySelectorAll('.system-node');
        nodes.forEach(node => {
            node.classList.remove('active', 'scenario-active', 'processing', 'receiving');
            node.style.transform = '';
            node.style.boxShadow = '';
        });
    }
    

    
    clearConnections() {
        if (this.svg) {
            // Remove all line elements
            const lines = this.svg.querySelectorAll('line');
            lines.forEach(line => this.svg.removeChild(line));
        }
    }
    
    resetStats() {
        this.stats = {
            activeEvents: 0,
            agentsInvoked: 0,
            systemsQueried: 0,
            processingTime: 0,
            successRate: 100
        };
        this.updateStatistics();
        this.eventCount = 0;
    }
    
    showToast(message, type = 'info') {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-weight: 500;
            z-index: 9999;
            animation: slideIn 0.3s ease;
        `;
        
        // Set background color based on type
        switch (type) {
            case 'success': toast.style.backgroundColor = '#10b981'; break;
            case 'error': toast.style.backgroundColor = '#ef4444'; break;
            case 'warning': toast.style.backgroundColor = '#f59e0b'; break;
            default: toast.style.backgroundColor = '#3b82f6';
        }
        
        document.body.appendChild(toast);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (document.body.contains(toast)) {
                document.body.removeChild(toast);
            }
        }, 3000);
    }
    
    initializeTooltips() {
        const nodes = document.querySelectorAll('.system-node');
        const tooltip = document.getElementById('systemTooltip');
        
        nodes.forEach(node => {
            node.addEventListener('mouseenter', (e) => {
                const system = node.dataset.system;
                const description = node.dataset.description;
                const nodeName = node.querySelector('.node-name').textContent;
                
                document.getElementById('tooltipTitle').textContent = nodeName;
                document.getElementById('tooltipContent').textContent = description;
                
                tooltip.style.display = 'block';
                this.positionTooltip(e, tooltip);
            });
            
            node.addEventListener('mousemove', (e) => {
                this.positionTooltip(e, tooltip);
            });
            
            node.addEventListener('mouseleave', () => {
                tooltip.style.display = 'none';
            });
        });
    }
    
    positionTooltip(e, tooltip) {
        const x = e.clientX + 15;
        const y = e.clientY + 15;
        
        tooltip.style.left = `${x}px`;
        tooltip.style.top = `${y}px`;
    }
    
    async executeScenario(type) {
        this.showLoading(true);
        this.clearAllEvents();
        
        try {
            let response;
            
            if (type === 'random') {
                // Use random scenario since simulate-event-flow endpoint was removed
                const scenarios = await this.getAvailableScenarios();
                if (scenarios.length > 0) {
                    const randomScenario = scenarios[Math.floor(Math.random() * scenarios.length)];
                    response = await fetch(`/demo4/api/scenarios/${randomScenario}/simulate`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' }
                    });
                }
            } else {
                // Get first scenario of type
                const scenariosResponse = await fetch('/demo4/api/scenarios');
                const scenariosData = await scenariosResponse.json();
                
                if (scenariosData.success) {
                    // Find scenario by type
                    const scenarioKeys = Object.keys(scenariosData.scenarios);
                    const matchingKey = scenarioKeys.find(key => 
                        scenariosData.scenarios[key].type === type
                    );
                    
                    if (matchingKey) {
                        response = await fetch(`/demo4/api/scenarios/${matchingKey}/simulate`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' }
                        });
                    }
                }
            }
            
            if (response && response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.activeWorkflowId = data.workflow_id;
                    this.displayScenarioInfo(data.scenario);
                    await this.animateEventFlow(data.events);
                    this.stats.processingTime = data.total_duration_ms;
                    this.updateStatistics();
                }
            }
        } catch (error) {
            console.error('Error executing scenario:', error);
            this.addEventToLog('ERROR', 'System', 'Error', `Failed to execute scenario: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
    
    displayScenarioInfo(scenario) {
        const scenarioInfo = document.getElementById('scenarioInfo');
        const scenarioBadge = document.getElementById('scenarioBadge');
        const scenarioName = document.getElementById('scenarioName');
        const scenarioDescription = document.getElementById('scenarioDescription');
        
        scenarioInfo.style.display = 'flex';
        scenarioBadge.textContent = scenario.scenario_type;
        scenarioBadge.className = `scenario-badge ${scenario.scenario_type}`;
        scenarioName.textContent = scenario.scenario_name;
        scenarioDescription.textContent = scenario.description;
        
        // Highlight involved systems
        this.highlightInvolvedSystems(scenario);
    }
    
    highlightInvolvedSystems(scenario) {
        // Clear previous highlights
        document.querySelectorAll('.system-node').forEach(node => {
            node.classList.remove('scenario-active', 'scenario-involved');
        });
        
        // Highlight AI infrastructure (always involved in agentic workflows)
        document.querySelectorAll('.ai-node').forEach(node => {
            node.classList.add('scenario-involved');
        });
        
        // Highlight agents
        if (scenario.agents_involved) {
            scenario.agents_involved.forEach(agent => {
                const nodeId = `node-${agent.toLowerCase().replace(/([A-Z])/g, '-$1').toLowerCase()}`;
                const node = document.getElementById(nodeId);
                if (node) {
                    node.classList.add('scenario-involved');
                }
            });
        }
        
        // Highlight systems
        if (scenario.systems_involved) {
            scenario.systems_involved.forEach(system => {
                const nodeId = `node-${system.toLowerCase().replace(/_/g, '-')}`;
                const node = document.getElementById(nodeId);
                if (node) {
                    node.classList.add('scenario-involved');
                }
            });
        }
    }
    
    async animateEventFlow(events) {
        if (!events || events.length === 0) return;
        
        for (const event of events) {
            if (this.animationPaused) {
                await this.waitForResume();
            }
            
            await this.animateSingleEvent(event);
            await this.sleep(Math.min(event.processing_time_ms || 500, 1000));
        }
        
        // Clear all highlights after animation
        setTimeout(() => {
            document.querySelectorAll('.system-node').forEach(node => {
                node.classList.remove('active', 'processing');
            });
            this.clearConnections();
        }, 2000);
    }
    
    async animateSingleEvent(event) {
        this.stats.activeEvents++;
        
        // Highlight source and target nodes
        const sourceNode = this.getNodeBySystem(event.source_system);
        const targetNode = this.getNodeBySystem(event.target_system);
        
        if (sourceNode) {
            sourceNode.classList.add('active', 'processing');
            
            // Track agent invocations (including AI infrastructure)
            if (sourceNode.classList.contains('agent-node') || sourceNode.classList.contains('ai-node')) {
                this.stats.agentsInvoked++;
            }
        }
        
        if (targetNode) {
            targetNode.classList.add('active');
            
            // Track system queries
            if (targetNode.classList.contains('external-node')) {
                this.stats.systemsQueried++;
            }
        }
        
        // Draw connection
        if (sourceNode && targetNode) {
            this.drawConnection(sourceNode, targetNode, true);
        }
        
        // Add to event log
        this.addEventToLog(
            event.event_type,
            event.source_system,
            event.target_system,
            this.formatEventPayload(event.payload)
        );
        
        this.updateStatistics();
        
        // Remove processing state after animation
        setTimeout(() => {
            if (sourceNode) {
                sourceNode.classList.remove('processing');
            }
        }, event.processing_time_ms || 500);
    }
    
    getNodeBySystem(systemName) {
        if (!systemName) return null;
        
        // Map system names to node IDs
        const systemMap = {
            'UI': 'node-ui',
            'Unified_Gateway': 'node-gateway',
            'Gateway': 'node-gateway',
            'ev-charging-orchestrator-001': 'node-orchestrator',
            'Orchestrator': 'node-orchestrator',
            // AI Infrastructure (GenAI/Agentic)
            'LLMGateway': 'node-llm-gateway',
            'LLMService': 'node-llm-service',
            'ClaudeAPI': 'node-llm-service',  // Backwards compatibility
            'SemanticCache': 'node-semantic-cache',
            'VectorDB': 'node-vector-db',
            'AgentMemory': 'node-agent-memory',
            'PromptManager': 'node-prompt-mgr',
            'RAGEngine': 'node-rag-engine',
            'ToolRegistry': 'node-tool-registry',
            'ReasoningEngine': 'node-reasoning',
            'Guardrails': 'node-guardrails',
            'ContextManager': 'node-context-mgr',
            'Observability': 'node-observability',
            // Specialized Agents
            'geographic-intelligence-001': 'node-geographic',
            'GeographicIntelligence': 'node-geographic',
            'financial-analysis-001': 'node-financial',
            'Financial': 'node-financial',
            'market-intelligence-001': 'node-market',
            'MarketIntelligence': 'node-market',
            'permit-management-001': 'node-permit',
            'Permit': 'node-permit',
            'network-optimization-001': 'node-network',
            'NetworkOptimization': 'node-network',
            // Government & Regulatory
            'VAHAN_API': 'node-vahan',
            'Census_DB': 'node-census',
            'MunicipalPortal': 'node-municipal',
            'NHAI': 'node-nhai',
            'StatePWD': 'node-pwd',
            'Environmental': 'node-environmental',
            // Power & Energy
            'PGCIL': 'node-pgcil',
            'DISCOM': 'node-discom',
            'GridMonitoring': 'node-grid',
            'SolarMonitoring': 'node-solar',
            'BatteryManagement': 'node-battery',
            'MNRE': 'node-mnre',
            // Market Intelligence
            'Competitor_DB': 'node-competitor',
            'TrafficAnalysis': 'node-traffic',
            'WeatherAPI': 'node-weather',
            'MLPlatform': 'node-ml',
            'PricingEngine': 'node-pricing',
            // Business Systems
            'Financial_System': 'node-finance-sys',
            'CRM': 'node-crm',
            'ContractMgmt': 'node-contract',
            'AlertSystem': 'node-alerts',
            'MobileUnits': 'node-mobile'
        };
        
        const nodeId = systemMap[systemName] || `node-${systemName.toLowerCase()}`;
        return document.getElementById(nodeId);
    }
    
    drawConnection(sourceNode, targetNode, animated = false) {
        const sourceRect = sourceNode.getBoundingClientRect();
        const targetRect = targetNode.getBoundingClientRect();
        const canvasRect = this.svg.getBoundingClientRect();
        
        const x1 = sourceRect.left + sourceRect.width / 2 - canvasRect.left;
        const y1 = sourceRect.top + sourceRect.height / 2 - canvasRect.top;
        const x2 = targetRect.left + targetRect.width / 2 - canvasRect.left;
        const y2 = targetRect.top + targetRect.height / 2 - canvasRect.top;
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', x1);
        line.setAttribute('y1', y1);
        line.setAttribute('x2', x2);
        line.setAttribute('y2', y2);
        line.setAttribute('class', animated ? 'connection-line active' : 'connection-line');
        line.setAttribute('stroke-dasharray', '5,5');
        line.setAttribute('marker-end', animated ? 'url(#arrowhead-active)' : 'url(#arrowhead)');
        
        this.svg.appendChild(line);
        
        // Remove line after animation
        if (animated) {
            setTimeout(() => {
                if (line.parentNode) {
                    line.parentNode.removeChild(line);
                }
            }, 2000);
        }
    }
    
    clearConnections() {
        while (this.svg.lastChild && this.svg.lastChild.tagName !== 'defs') {
            this.svg.removeChild(this.svg.lastChild);
        }
    }
    
    addEventToLog(eventType, source, target, payload) {
        // If parameters suggest this is a basic event call, use enhanced format
        if (typeof eventType === 'string' && typeof source === 'string' && typeof target === 'string') {
            // Convert to enhanced step format
            const step = {
                from: source,
                to: target,
                description: payload || eventType,
                delay: 500
            };
            // Call the enhanced event logging directly (avoid recursion)
            return this.addEnhancedEventToLog(step, 1, 1);
        }
        
        // Otherwise proceed with legacy format (shouldn't happen in current implementation)
        const emptyState = this.eventLog.querySelector('.event-log-empty');
        if (emptyState) {
            emptyState.remove();
        }
        
        const eventItem = document.createElement('div');
        eventItem.className = 'event-item';
        
        const time = new Date().toLocaleTimeString();
        
        eventItem.innerHTML = `
            <div class="event-time">${time}</div>
            <div class="event-content">
                <span class="event-route">${source} → ${target}</span>
                <div style="margin-top: 4px; color: #a0aec0; font-size: 11px;">${eventType}</div>
                ${payload ? `<div style="margin-top: 4px; color: #718096; font-size: 11px;">${payload}</div>` : ''}
            </div>
        `;
        
        this.eventLog.insertBefore(eventItem, this.eventLog.firstChild);
        
        // Limit log size
        while (this.eventLog.children.length > 50) {
            this.eventLog.removeChild(this.eventLog.lastChild);
        }
    }
    
    formatEventPayload(payload) {
        if (!payload) return '';
        
        if (typeof payload === 'string') return payload;
        
        const keys = Object.keys(payload);
        if (keys.length === 0) return '';
        
        return keys.slice(0, 2).map(key => `${key}: ${payload[key]}`).join(', ');
    }
    
    clearEventLog() {
        console.log('🧹 Clear Log clicked - performing complete reset...');
        
        // Complete reset: clear stats, highlights, connections, and events
        this.cleanupAllNodeStates();
        this.clearConnections();
        this.resetStats();
        
        // Clear the event log
        if (this.eventLog) {
            this.eventLog.innerHTML = `
                <div class="event-log-empty">
                    <i class="fas fa-info-circle"></i>
                    <p>No events yet. Run a scenario to see the event flow.</p>
                </div>
            `;
        }
        
        // Hide scenario info
        const scenarioInfo = document.getElementById('scenarioInfo');
        if (scenarioInfo) {
            scenarioInfo.style.display = 'none';
        }
        
        // Hide scenario outcome
        const scenarioOutcome = document.getElementById('scenarioOutcome');
        if (scenarioOutcome) {
            scenarioOutcome.style.display = 'none';
        }
        
        // Reset simulation state
        this.isSimulating = false;
        this.eventCount = 0;
        
        console.log('✅ Complete reset finished - stats, highlights, and events cleared');
        this.showToast('All cleared - ready for new simulation', 'success');
    }
    
    clearAllEvents() {
        // Clear all node states
        document.querySelectorAll('.system-node').forEach(node => {
            node.classList.remove('active', 'processing', 'scenario-active', 'scenario-involved');
        });
        
        // Clear connections
        this.clearConnections();
        
        // Reset stats
        this.stats = {
            activeEvents: 0,
            agentsInvoked: 0,
            systemsQueried: 0,
            processingTime: 0,
            successRate: 100
        };
        
        this.updateStatistics();
        
        // Hide scenario info
        document.getElementById('scenarioInfo').style.display = 'none';
    }
    
    updateStatistics() {
        document.getElementById('activeEvents').textContent = this.stats.activeEvents;
        document.getElementById('agentsInvoked').textContent = this.stats.agentsInvoked;
        document.getElementById('systemsQueried').textContent = this.stats.systemsQueried;
        document.getElementById('processingTime').textContent = `${this.stats.processingTime}ms`;
        document.getElementById('successRate').textContent = `${this.stats.successRate}%`;
    }
    
    async startRealtimeStatsUpdate() {
        // Poll for real-time stats every 5 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/demo4/api/events/realtime-stats');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success && data.stats) {
                        // Update global stats in background
                        console.log('Real-time stats:', data.stats);
                    }
                }
            } catch (error) {
                console.error('Error fetching real-time stats:', error);
            }
        }, 5000);
    }
    
    pauseAnimation() {
        this.animationPaused = true;
        document.getElementById('pauseAnimation').style.display = 'none';
        document.getElementById('resumeAnimation').style.display = 'inline-flex';
    }
    
    resumeAnimation() {
        this.animationPaused = false;
        document.getElementById('pauseAnimation').style.display = 'inline-flex';
        document.getElementById('resumeAnimation').style.display = 'none';
    }
    
    async waitForResume() {
        while (this.animationPaused) {
            await this.sleep(100);
        }
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const visualizer = new EventFlowVisualizer();
    
    // Make it globally accessible for debugging
    window.eventFlowVisualizer = visualizer;
    
    console.log('Event Flow Visualizer initialized');
});
