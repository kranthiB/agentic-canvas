/**
 * Enhanced Event Flow Visualizer with Dynamic Scenario Support
 * Dynamically picks scenarios from Demo5-Scenarios.md and animates them
 */

class EnhancedEventFlowVisualizer {
    constructor() {
        this.canvas = document.getElementById('architectureCanvas');
        this.eventLogContent = document.getElementById('eventLogContent');
        this.eventLogSidebar = document.getElementById('eventLogSidebar');
        this.isSimulating = false;
        this.currentScenario = null;
        this.eventCount = 0;
        
        this.init();
    }
    
    init() {
        // Button event listeners
        document.getElementById('btnSimulate').addEventListener('click', () => this.simulateRandomScenario());
        document.getElementById('btnClear').addEventListener('click', () => this.clear());
        document.getElementById('btnToggleLog').addEventListener('click', () => this.toggleLog());
        
        // Close button for event log
        const closeBtn = document.getElementById('btnCloseLog');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.toggleLog());
        }
        
        // Close button for scenario panel
        const closeScenarioBtn = document.getElementById('btnCloseScenario');
        if (closeScenarioBtn) {
            closeScenarioBtn.addEventListener('click', () => this.hideScenarioPanel());
        }
        
        // Initialize persona tooltip
        this.initPersonaTooltip();
        
        // Initialize real-time updates
        this.startRealtimeUpdates();
        
        // Initialized successfully
    }

    // Initialize persona tooltip functionality
    initPersonaTooltip() {
        const engineerUI = document.getElementById('node-UI');
        const tooltip = document.getElementById('personaTooltip');
        
        if (engineerUI && tooltip) {
            engineerUI.addEventListener('mouseenter', (e) => {
                const rect = engineerUI.getBoundingClientRect();
                const canvasRect = this.canvas.getBoundingClientRect();
                
                // Position tooltip directly to the right of the Engineer UI box
                tooltip.style.left = `${rect.right - canvasRect.left + 15}px`;
                tooltip.style.top = `${rect.top - canvasRect.top}px`;
                tooltip.classList.add('visible');
            });
            
            engineerUI.addEventListener('mouseleave', () => {
                tooltip.classList.remove('visible');
            });
        }
    }

    // Start real-time statistics updates
    startRealtimeUpdates() {
        // Update every 2 seconds during simulation
        this.realtimeInterval = setInterval(() => {
            if (this.isSimulating) {
                this.updateRealtimeStatistics();
                this.updateQueryContext();
            }
        }, 2000);
    }

    // Update real-time statistics from server
    async updateRealtimeStatistics() {
        try {
            const response = await fetch('/demo5/api/events/realtime-stats');
            const data = await response.json();
            
            if (data.success) {
                const stats = data.stats;
                document.getElementById('metricEvents').textContent = stats.total_events;
                document.getElementById('metricLatency').textContent = `${stats.avg_latency_ms}ms`;
                document.getElementById('metricSystems').textContent = stats.unique_systems;
                
                // Update systems display with visual indication
                this.updateSystemsStatus(stats.systems_involved);
            }
        } catch (error) {
            console.warn('Failed to update realtime stats:', error);
        }
    }

    // Update query context information
    async updateQueryContext() {
        try {
            const response = await fetch('/demo5/api/events/query-context');
            const data = await response.json();
            
            if (data.success && data.query_contexts.length > 0) {
                // Update scenario panel with latest query context
                const latestQuery = data.query_contexts[0];
                this.updateScenarioContext(latestQuery);
            }
        } catch (error) {
            console.warn('Failed to update query context:', error);
        }
    }

    // Update systems status display
    updateSystemsStatus(involvedSystems) {
        // Reset all nodes
        document.querySelectorAll('.system-node').forEach(node => {
            node.classList.remove('context-active');
        });
        
        // Highlight currently involved systems
        involvedSystems.forEach(systemName => {
            const nodeElement = this.getNodeElement(systemName);
            if (nodeElement) {
                nodeElement.classList.add('context-active');
            }
        });
    }

    // Update scenario context with query information
    updateScenarioContext(queryContext) {
        if (!queryContext) return;
        
        // Update scenario panel if active
        const panel = document.getElementById('scenarioInfoPanel');
        if (panel.classList.contains('active')) {
            const queryElement = document.getElementById('scenarioQuery');
            if (queryElement && queryContext.query_text) {
                queryElement.textContent = queryContext.query_text;
                queryElement.title = `Category: ${queryContext.query_category}`;
            }
        }
    }
    
    async simulateRandomScenario() {
        if (this.isSimulating) {
            this.showToast('Simulation already in progress', 'info');
            return;
        }
        
        // Always clear previous scenario and animations
        await this.clear();
        
        const btnSimulate = document.getElementById('btnSimulate');
        this.isSimulating = true;
        btnSimulate.disabled = true;
        
        try {            
            // Start immediate visual feedback
            this.startImmediateAnimation();
            
            // Call the new scenario engine
            const response = await fetch('/demo5/api/scenarios/random', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            console.log('Scenario API result:', result);
            console.log('Scenario flow data:', result?.scenario?.flow);
            
            if (result.success) {
                this.currentScenario = result.scenario;
                
                // Show scenario info
                this.displayScenarioInfo(result.scenario);
                
                // Check if we have scenario data with flow
                if (result.scenario && result.scenario.flow) {
                    console.log('Using scenario flow data:', result.scenario.flow);
                    await this.animateScenarioFromData(result.scenario);
                } else if (result.workflow_id) {
                    console.log('Trying to fetch events for workflow:', result.workflow_id);
                    await this.animateScenario(result.workflow_id);
                } else {
                    console.log('No flow data or workflow_id, showing demo');
                    await this.showDemoAnimationWithScenario();
                }
                
                // Display result
                if (result.result) {
                    this.displayScenarioResult(result.result);
                }
                
            } else {
                console.error('Scenario API failed:', result.error);
                
                if (result.error && result.error.includes('seed_demo5.py')) {
                    this.showToast('Database not seeded. Running demo scenario...', 'warning');
                } else {
                    this.showToast('API failed, running demo: ' + (result.error || 'Unknown error'), 'warning');
                }
                
                // Still show some animation as fallback
                await this.showDemoAnimationWithScenario();
            }
        } catch (error) {
            console.error('Simulation error:', error);
            this.showToast('Network error, running demo: ' + error.message, 'warning');
            // Show demo animation as fallback
            await this.showDemoAnimationWithScenario();
        } finally {
            this.isSimulating = false;
            btnSimulate.disabled = false;
        }
    }
    
    displayScenarioInfo(scenario) {
        const panel = document.getElementById('scenarioInfoPanel');
        
        document.getElementById('scenarioTitle').textContent = scenario.name;
        document.getElementById('scenarioQuery').textContent = scenario.query;
        document.getElementById('scenarioCategory').textContent = scenario.category;
        document.getElementById('scenarioAgents').textContent = scenario.agents_count;
        document.getElementById('scenarioSystems').textContent = scenario.systems_count;
        document.getElementById('scenarioLatency').textContent = scenario.total_latency_ms + 'ms';
        
        panel.classList.add('active');
    }
    
    async animateScenario(workflowId) {
        try {
            // Fetch events for this workflow
            const response = await fetch(`/demo5/api/events/recent?correlation_id=${workflowId}`);
            const data = await response.json();
            
            if (data.success && data.events.length > 0) {
                // Animating events
                
                // Clear existing event log and remove placeholder
                this.clearEventLog();
                
                // Reset metrics
                this.eventCount = 0;
                document.getElementById('metricEvents').textContent = '0';
                document.getElementById('metricLatency').textContent = '0ms';
                
                // Animate each event with proper delays
                for (let i = 0; i < data.events.length; i++) {
                    const event = data.events[i];
                    await this.animateEvent(event);
                    
                    // Update metrics in real-time
                    this.eventCount++;
                    document.getElementById('metricEvents').textContent = this.eventCount;
                    document.getElementById('metricLatency').textContent = 
                        Math.round(event.processing_time_ms || 0) + 'ms';
                    
                    // Wait based on the event's delay
                    const delay = event.payload?.delay_ms || 400;
                    await this.sleep(delay);
                }
                
                this.showToast(`Scenario complete! ${data.events.length} events processed`, 'success');
                
                // Clean up all node states after scenario completion
                setTimeout(() => {
                    this.cleanupAllNodeStates();
                }, 2000);
                
                // Auto-open event log if not already open
                if (!this.eventLogSidebar.classList.contains('open')) {
                    this.toggleLog();
                }
                
            } else {
                console.warn('No events found for workflow, falling back to demo');
                this.showToast('No events found, showing demo animation', 'info');
                await this.showDemoAnimation();
            }
        } catch (error) {
            console.error('Error animating scenario:', error);
            this.showToast('Animation error: ' + error.message, 'error');
        }
    }
    
    async animateEvent(event) {
        // Get source and target nodes
        const sourceNode = this.getNodeElement(event.source_system);
        const targetNode = this.getNodeElement(event.target_system);
        
        console.log(`Animating: ${event.source_system} → ${event.target_system}`);
        
        // Highlight components involved in current scenario
        this.highlightScenarioComponents(event);
        
        // Activate source node with enhanced styling
        if (sourceNode) {
            sourceNode.classList.add('active', 'processing', 'scenario-active');
            this.activateConnections();
            this.addNodePulseEffect(sourceNode);
        }
        
        // Animate particle from source to target
        if (sourceNode && targetNode) {
            await this.animateParticle(sourceNode, targetNode);
        }
        
        // Activate target node with enhanced styling
        if (targetNode) {
            targetNode.classList.add('active', 'scenario-active', 'receiving');
            this.addNodePulseEffect(targetNode);
        }
        
        // Add event to log
        this.addEventToLog(event);
        
        // Update real-time statistics
        this.updateRealtimeStats(event);
        
        // Deactivate after animation
        setTimeout(() => {
            if (sourceNode) {
                sourceNode.classList.remove('active', 'processing', 'receiving');
            }
            if (targetNode) {
                targetNode.classList.remove('active', 'receiving');
            }
            this.deactivateConnections();
        }, 1200);
    }
    
    getNodeElement(systemName) {
        // Normalize system name for element ID
        let nodeId = `node-${systemName.replace(/[\s_]/g, '-')}`;
        let element = document.getElementById(nodeId);
        
        // If not found with underscores replaced with dashes, try with underscores preserved
        if (!element) {
            nodeId = `node-${systemName}`;
            element = document.getElementById(nodeId);
        }
        
        if (!element) {
            console.warn(`Node element not found: ${nodeId} for system: ${systemName}`);
            console.log('Available node IDs:', Array.from(document.querySelectorAll('.system-node')).map(n => n.id));
        } else {
            console.log(`✅ Found node element: ${nodeId} for system: ${systemName}`);
        }
        
        return element;
    }
    
    activateConnections() {
        document.querySelectorAll('.connection-line').forEach(line => {
            line.classList.add('active');
        });
    }
    
    deactivateConnections() {
        setTimeout(() => {
            document.querySelectorAll('.connection-line').forEach(line => {
                line.classList.remove('active');
            });
        }, 600);
    }
    
    async animateParticle(sourceNode, targetNode) {
        return new Promise((resolve) => {
            const sourceRect = sourceNode.getBoundingClientRect();
            const targetRect = targetNode.getBoundingClientRect();
            const canvasRect = this.canvas.getBoundingClientRect();
            
            // Create particle
            const particle = document.createElement('div');
            particle.className = 'event-particle';
            particle.style.left = (sourceRect.left - canvasRect.left + sourceRect.width / 2) + 'px';
            particle.style.top = (sourceRect.top - canvasRect.top + sourceRect.height / 2) + 'px';
            this.canvas.appendChild(particle);
            
            // Calculate movement
            const deltaX = targetRect.left - sourceRect.left;
            const deltaY = targetRect.top - sourceRect.top;
            
            // Animate
            setTimeout(() => {
                particle.style.transition = 'all 1s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                particle.style.transform = `translate(${deltaX}px, ${deltaY}px)`;
                particle.style.opacity = '0';
            }, 50);
            
            // Remove particle
            setTimeout(() => {
                particle.remove();
                resolve();
            }, 1100);
        });
    }
    
    addEventToLog(event) {
        // Remove placeholder if it exists (only on first event)
        if (this.eventLogContent.children.length === 1) {
            const firstChild = this.eventLogContent.firstChild;
            if (firstChild && firstChild.className && firstChild.className.includes('text-center')) {
                this.eventLogContent.removeChild(firstChild);
            }
        }
        
        // Parse event data
        const eventInfo = this.parseEventInfo(event);
        
        // Create event entry
        const entry = document.createElement('div');
        entry.className = 'event-entry';
        entry.style.cssText = `
            background: ${eventInfo.bgColor};
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-left: 3px solid ${eventInfo.borderColor};
            border-radius: 12px;
            padding: 16px;
            color: #e2e8f0;
            transition: all 0.2s ease;
        `;
        
        // Add hover effect
        entry.addEventListener('mouseenter', () => {
            entry.style.transform = 'translateX(-4px)';
            entry.style.background = eventInfo.bgColor.replace('0.08', '0.12');
            entry.style.boxShadow = `0 4px 12px ${eventInfo.borderColor}30`;
        });
        entry.addEventListener('mouseleave', () => {
            entry.style.transform = 'translateX(0)';
            entry.style.background = eventInfo.bgColor;
            entry.style.boxShadow = 'none';
        });
        
        entry.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="flex-grow-1">
                    <h6 class="mb-1" style="color: #f1f5f9; font-weight: 600; font-size: 0.9rem;">
                        <i class="bi ${eventInfo.icon} me-2" style="color: ${eventInfo.borderColor};"></i>
                        ${eventInfo.title}
                    </h6>
                    <small style="color: #94a3b8; font-size: 0.75rem;">
                        Step ${event.payload.step || '?'} of ${event.payload.total_steps || '?'} • 
                        ${this.getRelativeTime(event.timestamp)}
                    </small>
                </div>
                <span class="badge" style="background: ${eventInfo.badgeColor}; color: white; font-size: 0.75rem; padding: 4px 10px; border-radius: 12px;">
                    ${eventInfo.badgeText}
                </span>
            </div>
            <p class="mb-2" style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;">
                ${event.payload.description || eventInfo.description}
            </p>
            ${eventInfo.details ? `
                <div style="background: rgba(51, 65, 85, 0.3); padding: 10px 12px; border-radius: 6px; font-size: 0.75rem; color: #94a3b8; border-left: 2px solid ${eventInfo.borderColor}40;">
                    ${eventInfo.details}
                </div>
            ` : ''}
        `;
        
        // Insert at top
        this.eventLogContent.insertBefore(entry, this.eventLogContent.firstChild);
        
        // Limit to 50 entries
        while (this.eventLogContent.children.length > 50) {
            this.eventLogContent.removeChild(this.eventLogContent.lastChild);
        }
    }
    
    parseEventInfo(event) {
        const eventType = event.event_type || 'unknown';
        const source = event.source_system || 'Unknown';
        const target = event.target_system || 'Unknown';
        
        // Default styling
        let info = {
            title: `${source} → ${target}`,
            description: 'Event processed',
            details: '',
            icon: 'bi-arrow-right-circle',
            bgColor: 'rgba(71, 85, 105, 0.08)',
            borderColor: '#64748b',
            badgeColor: '#64748b',
            badgeText: eventType
        };
        
        // Enhanced parsing based on event type
        switch (eventType) {
            case 'user_query':
                info.icon = 'bi-person-check';
                info.bgColor = 'rgba(59, 130, 246, 0.08)';
                info.borderColor = '#3b82f6';
                info.badgeColor = '#3b82f6';
                info.badgeText = 'User Query';
                info.title = 'Engineer Submits Request';
                break;
                
            case 'query_routing':
                info.icon = 'bi-router';
                info.bgColor = 'rgba(139, 92, 246, 0.08)';
                info.borderColor = '#8b5cf6';
                info.badgeColor = '#8b5cf6';
                info.badgeText = 'Routing';
                info.title = 'Gateway Routing Request';
                break;
                
            case 'agent_invocation':
                info.icon = 'bi-cpu';
                info.bgColor = 'rgba(34, 197, 94, 0.08)';
                info.borderColor = '#22c55e';
                info.badgeColor = '#22c55e';
                info.badgeText = 'Agent';
                info.title = `Activating ${target}`;
                info.details = 'AI agent initialized and ready to process request';
                break;
                
            case 'knowledge_search':
                info.icon = 'bi-search';
                info.bgColor = 'rgba(245, 158, 11, 0.08)';
                info.borderColor = '#f59e0b';
                info.badgeColor = '#f59e0b';
                info.badgeText = 'Search';
                info.title = 'Knowledge Base Search';
                break;
                
            case 'vector_search':
                info.icon = 'bi-database-search';
                info.bgColor = 'rgba(236, 72, 153, 0.08)';
                info.borderColor = '#ec4899';
                info.badgeColor = '#ec4899';
                info.badgeText = 'Vector DB';
                info.title = 'Vector Similarity Search';
                info.details = 'Semantic search across knowledge base using embeddings';
                break;
                
            case 'mcp_connection':
                info.icon = 'bi-plug';
                info.bgColor = 'rgba(16, 185, 129, 0.08)';
                info.borderColor = '#10b981';
                info.badgeColor = '#10b981';
                info.badgeText = 'Connection';
                info.title = 'MCP Gateway Connection';
                break;
                
            case 'plm_specification_query':
                info.icon = 'bi-file-earmark-text';
                info.bgColor = 'rgba(139, 92, 246, 0.08)';
                info.borderColor = '#8b5cf6';
                info.badgeColor = '#8b5cf6';
                info.badgeText = 'PLM';
                info.title = 'Retrieving Product Specs';
                info.details = 'Accessing PLM for product specifications and formulations';
                break;
                
            case 'sap_inventory_check':
            case 'sap_material_query':
                info.icon = 'bi-boxes';
                info.bgColor = 'rgba(59, 130, 246, 0.08)';
                info.borderColor = '#3b82f6';
                info.badgeColor = '#3b82f6';
                info.badgeText = 'SAP';
                info.title = 'SAP Material Query';
                info.details = 'Checking inventory levels and material availability';
                break;
                
            case 'lims_test_query':
                info.icon = 'bi-flask';
                info.bgColor = 'rgba(239, 68, 68, 0.08)';
                info.borderColor = '#ef4444';
                info.badgeColor = '#ef4444';
                info.badgeText = 'LIMS';
                info.title = 'Laboratory Test Query';
                info.details = 'Accessing LIMS for test protocols and quality data';
                break;
                
            case 'supplier_availability_check':
                info.icon = 'bi-truck';
                info.bgColor = 'rgba(245, 158, 11, 0.08)';
                info.borderColor = '#f59e0b';
                info.badgeColor = '#f59e0b';
                info.badgeText = 'Supplier';
                info.title = 'Supplier Availability Check';
                info.details = 'Querying approved supplier network for material availability';
                break;
                
            case 'regulatory_standard_check':
                info.icon = 'bi-shield-check';
                info.bgColor = 'rgba(251, 191, 36, 0.08)';
                info.borderColor = '#fbbf24';
                info.badgeColor = '#fbbf24';
                info.badgeText = 'Regulatory';
                info.title = 'Regulatory Compliance Check';
                info.details = 'Verifying compliance with standards and regulations';
                break;
                
            case 'llm_inference':
                info.icon = 'bi-stars';
                info.bgColor = 'rgba(168, 85, 247, 0.08)';
                info.borderColor = '#a855f7';
                info.badgeColor = '#a855f7';
                info.badgeText = 'AI Processing';
                info.title = 'LLM Inference';
                info.details = 'Large Language Model processing request and generating insights';
                break;
                
            case 'llm_response':
                info.icon = 'bi-lightbulb';
                info.bgColor = 'rgba(34, 197, 94, 0.08)';
                info.borderColor = '#22c55e';
                info.badgeColor = '#22c55e';
                info.badgeText = 'AI Result';
                info.title = 'AI Generated Response';
                break;
                
            case 'agent_recommendation_ready':
                info.icon = 'bi-check-circle';
                info.bgColor = 'rgba(34, 197, 94, 0.08)';
                info.borderColor = '#22c55e';
                info.badgeColor = '#22c55e';
                info.badgeText = 'Complete';
                info.title = 'Agent Completed Analysis';
                info.details = 'Recommendation ready for aggregation';
                break;
                
            case 'response_aggregation':
                info.icon = 'bi-collection';
                info.bgColor = 'rgba(139, 92, 246, 0.08)';
                info.borderColor = '#8b5cf6';
                info.badgeColor = '#8b5cf6';
                info.badgeText = 'Aggregation';
                info.title = 'Combining Agent Responses';
                info.details = 'Synthesizing results from multiple agents and systems';
                break;
                
            case 'response_delivery':
                info.icon = 'bi-send-check';
                info.bgColor = 'rgba(34, 197, 94, 0.08)';
                info.borderColor = '#22c55e';
                info.badgeColor = '#22c55e';
                info.badgeText = 'Delivered';
                info.title = 'Response Delivered to Engineer';
                info.details = 'Complete answer delivered to user interface';
                break;
                
            case 'plm_response':
            case 'sap_response':
            case 'lims_response':
            case 'supplier_response':
                info.icon = 'bi-check2-circle';
                info.bgColor = 'rgba(16, 185, 129, 0.08)';
                info.borderColor = '#10b981';
                info.badgeColor = '#10b981';
                info.badgeText = 'Response';
                info.title = `${target} Data Retrieved`;
                break;
        }
        
        return info;
    }
    
    displayScenarioResult(result) {
        // Add a special "result" entry to the event log
        const entry = document.createElement('div');
        entry.className = 'event-entry';
        entry.style.cssText = `
            background: rgba(34, 197, 94, 0.12);
            border: 2px solid #22c55e;
            border-radius: 12px;
            padding: 20px;
            color: #f1f5f9;
            margin-bottom: 20px;
        `;
        
        let resultHtml = '<h5 style="color: #22c55e; font-weight: 700; margin-bottom: 12px;"><i class="bi bi-check-circle-fill me-2"></i>Scenario Result</h5>';
        
        // Format result based on structure
        if (typeof result === 'object') {
            resultHtml += '<div style="font-size: 0.85rem; line-height: 1.6;">';
            for (const [key, value] of Object.entries(result)) {
                resultHtml += `<div style="margin-bottom: 8px;">`;
                resultHtml += `<strong style="color: #a7f3d0;">${this.formatKey(key)}:</strong> `;
                
                if (typeof value === 'object' && value !== null) {
                    resultHtml += `<div style="margin-left: 16px; margin-top: 4px;">`;
                    if (Array.isArray(value)) {
                        value.forEach(item => {
                            if (typeof item === 'object' && item !== null) {
                                resultHtml += `<div style="margin-bottom: 6px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px;">`;
                                for (const [k, v] of Object.entries(item)) {
                                    resultHtml += `<div><em>${k}:</em> ${this.formatValue(v)}</div>`;
                                }
                                resultHtml += `</div>`;
                            } else {
                                resultHtml += `<div>• ${this.formatValue(item)}</div>`;
                            }
                        });
                    } else {
                        for (const [k, v] of Object.entries(value)) {
                            resultHtml += `<div><em>${k}:</em> ${this.formatValue(v)}</div>`;
                        }
                    }
                    resultHtml += `</div>`;
                } else {
                    resultHtml += `<span style="color: #cbd5e1;">${this.formatValue(value)}</span>`;
                }
                
                resultHtml += `</div>`;
            }
            resultHtml += '</div>';
        } else {
            resultHtml += `<p>${result}</p>`;
        }
        
        entry.innerHTML = resultHtml;
        
        // Insert at top
        this.eventLogContent.insertBefore(entry, this.eventLogContent.firstChild);
    }
    
    formatValue(value) {
        if (typeof value === 'object' && value !== null) {
            return JSON.stringify(value, null, 2).replace(/\n/g, '<br>').replace(/  /g, '&nbsp;&nbsp;');
        }
        return value;
    }
    
    formatKey(key) {
        // Convert snake_case or camelCase to Title Case
        return key
            .replace(/_/g, ' ')
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, str => str.toUpperCase())
            .trim();
    }
    
    clearEventLog() {
        // Remove all child elements
        while (this.eventLogContent.firstChild) {
            this.eventLogContent.removeChild(this.eventLogContent.firstChild);
        }
    }
    
    getRelativeTime(timestamp) {
        const now = new Date();
        const eventTime = new Date(timestamp);
        const diffInSeconds = Math.floor((now - eventTime) / 1000);
        
        if (diffInSeconds < 5) return 'Just now';
        if (diffInSeconds < 60) return `${diffInSeconds}s ago`;
        if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
        return eventTime.toLocaleTimeString();
    }
    
    async clear() {
        try {
            await fetch('/demo5/api/events/clear', { method: 'POST' });
            
            // Clear event log
            this.clearEventLog();
            const placeholder = document.createElement('div');
            placeholder.className = 'text-center py-5';
            placeholder.style.color = '#64748b';
            placeholder.innerHTML = `
                <i class="bi bi-inbox" style="font-size: 48px; opacity: 0.3;"></i>
                <p class="mt-3 mb-0">No events yet</p>
                <small style="opacity: 0.7;">Click "Simulate Flow" to start</small>
            `;
            this.eventLogContent.appendChild(placeholder);
            
            // Hide scenario panel and status bar
            document.getElementById('scenarioInfoPanel').classList.remove('active');
            this.hideScenarioStatusBar();
            
            // Clear all visual states
            document.querySelectorAll('.system-node').forEach(node => {
                node.classList.remove('active', 'processing', 'scenario-active', 'scenario-involved', 'receiving', 'context-active');
            });
            
            // Clear connection states
            document.querySelectorAll('.connection-line').forEach(line => {
                line.classList.remove('active');
            });
            
            // Reset metrics
            this.eventCount = 0;
            this.systemsInvolved = new Set();
            document.getElementById('metricEvents').textContent = '0';
            document.getElementById('metricLatency').textContent = '0ms';
            document.getElementById('metricSystems').textContent = '16';
            
            // Reset state
            this.currentScenario = null;
            this.isSimulating = false;
            
        } catch (error) {
            console.error('Clear error:', error);
            this.showToast('Error clearing events', 'error');
        }
    }
    
    toggleLog() {
        this.eventLogSidebar.classList.toggle('open');
    }

    hideScenarioPanel() {
        const panel = document.getElementById('scenarioInfoPanel');
        panel.classList.remove('active');
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast-custom ${type}`;
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi ${type === 'success' ? 'bi-check-circle-fill' : type === 'error' ? 'bi-exclamation-circle-fill' : 'bi-info-circle-fill'} me-2"></i>
                <span>${message}</span>
            </div>
        `;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // Start immediate visual feedback
    startImmediateAnimation() {
        // Highlight all system nodes to show activity
        document.querySelectorAll('.system-node').forEach(node => {
            node.classList.add('scenario-involved');
        });
        
        // Activate connection lines
        document.querySelectorAll('.connection-line').forEach(line => {
            line.classList.add('active');
        });
        
        // Update metrics immediately
        this.eventCount = 0;
        document.getElementById('metricEvents').textContent = '0';
        document.getElementById('metricLatency').textContent = '0ms';
        
        console.log('Started immediate animation feedback');
    }

    // Animate scenario from scenario data (fallback)
    async animateScenarioFromData(scenario) {
        console.log('animateScenarioFromData called with:', scenario);
        
        if (!scenario || !scenario.flow || !Array.isArray(scenario.flow)) {
            console.warn('No valid flow data available:', {
                hasScenario: !!scenario,
                hasFlow: !!(scenario?.flow),
                flowIsArray: Array.isArray(scenario?.flow),
                flowLength: scenario?.flow?.length
            });
            console.log('Falling back to demo animation');
            return this.showDemoAnimation();
        }

        console.log(`Animating ${scenario.flow.length} flow steps`);
        this.clearEventLog();
        
        for (let i = 0; i < scenario.flow.length; i++) {
            const step = scenario.flow[i];
            console.log(`Step ${i + 1}:`, step);
            
            // Create mock event from flow step
            const mockEvent = {
                source_system: step.from,
                target_system: step.to,
                event_type: step.event || 'SYSTEM_EVENT',
                processing_time_ms: step.delay || 500,
                timestamp: new Date().toISOString(),
                payload: {
                    description: step.description || `${step.from} → ${step.to}`,
                    step: i + 1,
                    total_steps: scenario.flow.length,
                    delay_ms: step.delay || 500
                }
            };
            
            await this.animateEvent(mockEvent);
            await this.sleep(step.delay || 600);
        }
        
        console.log('Scenario animation completed');
    }

    // Demo animation as ultimate fallback
    async showDemoAnimation() {
        this.clearEventLog();
        
        const demoFlow = [
            { from: 'UI', to: 'Orchestrator', description: 'User submits formulation request' },
            { from: 'Orchestrator', to: 'FormulationAgent', description: 'Agent analysis started' },
            { from: 'FormulationAgent', to: 'SAP_ERP', description: 'Querying material costs' },
            { from: 'SAP_ERP', to: 'FormulationAgent', description: 'Material data retrieved' },
            { from: 'FormulationAgent', to: 'RAG_Engine', description: 'Knowledge retrieval initiated' },
            { from: 'RAG_Engine', to: 'Vector_DB', description: 'Vector search started' },
            { from: 'Vector_DB', to: 'RAG_Engine', description: 'Similar formulations found' },
            { from: 'FormulationAgent', to: 'LIMS', description: 'Historical test data query' },
            { from: 'LIMS', to: 'FormulationAgent', description: 'Test results retrieved' },
            { from: 'RegulatoryAgent', to: 'Regulatory_DB', description: 'Compliance check' },
            { from: 'Regulatory_DB', to: 'RegulatoryAgent', description: 'Standards validated' },
            { from: 'SupplyChainAgent', to: 'Supplier_Portal', description: 'Supplier availability check' },
            { from: 'Supplier_Portal', to: 'SupplyChainAgent', description: 'Suppliers confirmed' },
            { from: 'FormulationAgent', to: 'Orchestrator', description: 'Analysis complete' },
            { from: 'Orchestrator', to: 'UI', description: 'Recommendations ready' }
        ];

        for (let i = 0; i < demoFlow.length; i++) {
            const step = demoFlow[i];
            
            const mockEvent = {
                source_system: step.from,
                target_system: step.to,
                event_type: 'DEMO_EVENT',
                processing_time_ms: 300 + (i * 50),
                timestamp: new Date().toISOString(),
                payload: {
                    description: step.description,
                    step: i + 1,
                    total_steps: demoFlow.length,
                    delay_ms: 500
                }
            };
            
            await this.animateEvent(mockEvent);
            await this.sleep(500);
        }
        
        this.showToast('Demo animation completed', 'success');
    }

    // Demo animation with complete scenario experience
    async showDemoAnimationWithScenario() {
        // Create a mock scenario
        const mockScenario = {
            name: 'Quality Investigation - QTZT-2025-0234',
            query: 'LIMS flagged batch QTZT-2025-0234 as fail. What\'s the issue?',
            category: 'Two Agent',
            agents: ['FormulationAgent', 'TestProtocolAgent', 'RegulatoryAgent'],
            flow: [
                { from: 'UI', to: 'Orchestrator', description: 'Quality investigation request submitted', delay: 500 },
                { from: 'Orchestrator', to: 'FormulationAgent', description: 'Analyzing batch formulation data', delay: 800 },
                { from: 'FormulationAgent', to: 'SAP_ERP', description: 'Retrieving batch production records', delay: 600 },
                { from: 'SAP_ERP', to: 'FormulationAgent', description: 'Production data: Temperature spike detected', delay: 400 },
                { from: 'FormulationAgent', to: 'LIMS', description: 'Querying detailed test results', delay: 700 },
                { from: 'LIMS', to: 'FormulationAgent', description: 'Viscosity out of spec: 11.8 cSt (target: 11.2)', delay: 500 },
                { from: 'TestProtocolAgent', to: 'PLM', description: 'Checking formulation specifications', delay: 600 },
                { from: 'PLM', to: 'TestProtocolAgent', description: 'Formulation specs retrieved', delay: 400 },
                { from: 'RegulatoryAgent', to: 'Regulatory_DB', description: 'Validating quality requirements', delay: 500 },
                { from: 'Regulatory_DB', to: 'RegulatoryAgent', description: 'API SP standards confirmed', delay: 300 },
                { from: 'FormulationAgent', to: 'Orchestrator', description: 'Root cause analysis complete', delay: 600 },
                { from: 'Orchestrator', to: 'UI', description: 'Investigation results ready', delay: 400 }
            ],
            total_latency_ms: 6400,
            result: {
                root_cause: 'Temperature spike during mixing',
                recommendation: 'Rework batch with temperature control',
                quality_impact: 'Viscosity out of specification',
                corrective_action: 'Review heating control system'
            }
        };

        this.currentScenario = mockScenario;
        
        // Show scenario info
        this.displayScenarioInfo(mockScenario);
        
        // Run the animation
        await this.animateScenarioFromData(mockScenario);
        
        // Display results
        this.displayScenarioResult(mockScenario.result);
        
        this.showToast('Quality investigation scenario completed', 'success');
    }

    // Enhanced component highlighting for current scenario
    highlightScenarioComponents(event) {
        // Clear previous scenario highlights
        document.querySelectorAll('.system-node').forEach(node => {
            node.classList.remove('scenario-involved');
        });

        // Highlight nodes involved in current scenario
        if (this.currentScenario && this.currentScenario.agents) {
            this.currentScenario.agents.forEach(agentName => {
                const nodeElement = this.getNodeElement(agentName);
                if (nodeElement) {
                    nodeElement.classList.add('scenario-involved');
                }
            });
        }

        // Always highlight source and target
        const sourceNode = this.getNodeElement(event.source_system);
        const targetNode = this.getNodeElement(event.target_system);
        if (sourceNode) sourceNode.classList.add('scenario-involved');
        if (targetNode) targetNode.classList.add('scenario-involved');
    }

    // Add pulse effect to nodes
    addNodePulseEffect(node) {
        node.style.animation = 'nodePulse 1.5s ease-in-out';
        setTimeout(() => {
            node.style.animation = '';
        }, 1500);
    }

    // Update real-time statistics
    updateRealtimeStats(event) {
        // Update event count
        this.eventCount++;
        document.getElementById('metricEvents').textContent = this.eventCount;
        
        // Update latency display
        if (event.processing_time_ms) {
            document.getElementById('metricLatency').textContent = `${event.processing_time_ms}ms`;
        }
        
        // Update systems count (unique systems involved)
        if (!this.systemsInvolved) {
            this.systemsInvolved = new Set();
        }
        this.systemsInvolved.add(event.source_system);
        this.systemsInvolved.add(event.target_system);
        document.getElementById('metricSystems').textContent = this.systemsInvolved.size;
    }

    // Enhanced scenario display with more context
    displayScenarioInfo(scenario) {
        // Use status bar instead of blocking panel
        this.showScenarioStatusBar(scenario);
        
        // Also keep the side panel option for detailed view
        const panel = document.getElementById('scenarioInfoPanel');
        
        // Update panel details (but don't show it by default)
        document.getElementById('scenarioTitle').textContent = scenario.name || 'Active Scenario';
        document.getElementById('scenarioQuery').textContent = scenario.query || 'Processing request...';
        document.getElementById('scenarioCategory').textContent = scenario.category || 'General';
        document.getElementById('scenarioAgents').textContent = scenario.agents ? scenario.agents.length : '4';
        document.getElementById('scenarioSystems').textContent = this.countUniqueSystems(scenario) || '16';
        document.getElementById('scenarioLatency').textContent = `${scenario.total_latency_ms || '0'}ms`;
        
        // Add scenario type badge
        this.addScenarioTypeBadge(scenario.category);
        
        // Highlight involved agents immediately
        if (scenario.agents && Array.isArray(scenario.agents)) {
            scenario.agents.forEach(agentName => {
                const nodeElement = this.getNodeElement(agentName);
                if (nodeElement) {
                    nodeElement.classList.add('scenario-involved');
                    // Add slight delay for staggered effect
                    setTimeout(() => {
                        nodeElement.classList.add('scenario-active');
                    }, Math.random() * 1000);
                }
            });
        }
        
        console.log('Scenario info displayed:', scenario);
    }

    // Show scenario status bar (non-blocking)
    showScenarioStatusBar(scenario) {
        console.log('Showing scenario status bar for:', scenario);
        const statusBar = document.getElementById('scenarioStatusBar');
        if (!statusBar) {
            console.error('Status bar element not found');
            return;
        }
        
        // Build status bar content with cleaner design
        const agentCount = scenario.agents ? scenario.agents.length : 0;
        const statusText = `${scenario.name || 'Running Scenario'}`;
        
        statusBar.innerHTML = `
            <div class="scenario-status-content">
                <div class="scenario-title">${statusText}</div>
                <div class="scenario-agents">${agentCount} Agents Active</div>
            </div>
            <button class="info-btn" onclick="eventFlowViz.toggleDetailedPanel()" title="Show detailed scenario info">
                <i class="bi bi-info-circle"></i>
            </button>
        `;
        
        // Show the status bar using CSS class
        statusBar.classList.add('visible');
        console.log('Status bar shown with visible class');
    }

    hideScenarioStatusBar() {
        const statusBar = document.getElementById('scenarioStatusBar');
        if (statusBar) {
            statusBar.classList.remove('visible');
        }
    }

    toggleDetailedPanel() {
        const panel = document.getElementById('scenarioInfoPanel');
        if (panel) {
            panel.classList.toggle('active');
        }
    }

    cleanupAllNodeStates() {
        console.log('🧹 Cleaning up all node states after scenario completion');
        document.querySelectorAll('.system-node').forEach(node => {
            node.classList.remove('active', 'processing', 'receiving', 'scenario-active', 'scenario-involved');
        });
        
        // Also cleanup connection lines
        document.querySelectorAll('.connection-line').forEach(line => {
            line.classList.remove('active');
        });
    }

    // Count unique systems in scenario
    countUniqueSystems(scenario) {
        if (!scenario.flow) return 0;
        const systems = new Set();
        scenario.flow.forEach(step => {
            systems.add(step.from);
            systems.add(step.to);
        });
        return systems.size;
    }

    // Add visual badge for scenario type
    addScenarioTypeBadge(category) {
        const titleElement = document.getElementById('scenarioTitle');
        const existingBadge = titleElement.querySelector('.scenario-badge');
        if (existingBadge) {
            existingBadge.remove();
        }
        
        let badgeColor = '#4299e1';
        let badgeText = 'General';
        
        switch(category) {
            case 'Single Agent':
                badgeColor = '#48bb78';
                badgeText = '1 Agent';
                break;
            case 'Multi Agent':
                badgeColor = '#ed8936';
                badgeText = 'Multi';
                break;
            case 'Complex Flow':
                badgeColor = '#9f7aea';
                badgeText = 'Complex';
                break;
        }
        
        const badge = document.createElement('span');
        badge.className = 'scenario-badge ms-2';
        badge.style.cssText = `
            background: ${badgeColor};
            color: white;
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 12px;
            font-weight: 500;
        `;
        badge.textContent = badgeText;
        titleElement.appendChild(badge);
    }

    // Enhanced event log display
    addEventToLog(event) {
        // Remove placeholder if it exists (only on first event)
        if (this.eventLogContent.children.length === 1) {
            const firstChild = this.eventLogContent.firstChild;
            if (firstChild && firstChild.className && firstChild.className.includes('text-center')) {
                this.eventLogContent.removeChild(firstChild);
            }
        }

        // Parse event data with enhanced information
        const eventInfo = this.parseEventInfoEnhanced(event);
        
        // Create enhanced event entry
        const entry = document.createElement('div');
        entry.className = 'event-entry';
        entry.style.cssText = `
            background: ${eventInfo.bgColor};
            border: 1px solid rgba(148, 163, 184, 0.1);
            border-left: 3px solid ${eventInfo.borderColor};
            border-radius: 12px;
            padding: 16px;
            color: #e2e8f0;
            transition: all 0.2s ease;
            margin-bottom: 12px;
            position: relative;
            overflow: hidden;
        `;
        
        // Add animated progress bar for processing events
        if (event.event_type?.includes('PROCESSING') || event.event_type?.includes('ANALYSIS')) {
            const progressBar = document.createElement('div');
            progressBar.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                height: 2px;
                background: ${eventInfo.borderColor};
                animation: progressLoad 2s ease-in-out;
                width: 100%;
            `;
            entry.appendChild(progressBar);
        }
        
        // Enhanced hover effects
        entry.addEventListener('mouseenter', () => {
            entry.style.transform = 'translateX(-4px) scale(1.02)';
            entry.style.background = eventInfo.bgColor.replace('0.08', '0.15');
            entry.style.boxShadow = `0 6px 20px ${eventInfo.borderColor}40`;
        });
        entry.addEventListener('mouseleave', () => {
            entry.style.transform = 'translateX(0) scale(1)';
            entry.style.background = eventInfo.bgColor;
            entry.style.boxShadow = 'none';
        });

        entry.innerHTML = `
            <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="flex-grow-1">
                    <h6 class="mb-1" style="color: #f1f5f9; font-weight: 600; font-size: 0.9rem;">
                        <i class="bi ${eventInfo.icon} me-2" style="color: ${eventInfo.borderColor};"></i>
                        ${eventInfo.title}
                    </h6>
                    <div class="d-flex align-items-center gap-2">
                        <small style="color: #94a3b8; font-size: 0.75rem;">
                            Step ${event.payload?.step || '?'} of ${event.payload?.total_steps || '?'}
                        </small>
                        <span style="color: #64748b;">•</span>
                        <small style="color: #94a3b8; font-size: 0.75rem;">
                            ${this.getRelativeTime(event.timestamp)}
                        </small>
                        ${event.processing_time_ms ? `
                            <span style="color: #64748b;">•</span>
                            <small style="color: #10b981; font-size: 0.75rem; font-weight: 500;">
                                ${event.processing_time_ms}ms
                            </small>
                        ` : ''}
                    </div>
                </div>
                <div class="d-flex flex-column align-items-end gap-1">
                    <span class="badge" style="background: ${eventInfo.badgeColor}; color: white; font-size: 0.75rem; padding: 4px 10px; border-radius: 12px;">
                        ${eventInfo.badgeText}
                    </span>
                    <small style="color: #64748b; font-size: 0.7rem;">
                        ${event.source_system} → ${event.target_system}
                    </small>
                </div>
            </div>
            <p class="mb-2" style="color: #cbd5e1; font-size: 0.85rem; line-height: 1.5;">
                ${event.payload?.description || eventInfo.description}
            </p>
            ${eventInfo.details ? `
                <div style="background: rgba(51, 65, 85, 0.3); padding: 10px 12px; border-radius: 6px; font-size: 0.75rem; color: #94a3b8; border-left: 2px solid ${eventInfo.borderColor}40;">
                    ${eventInfo.details}
                </div>
            ` : ''}
        `;
        
        // Add entry to log with smooth animation
        entry.style.opacity = '0';
        entry.style.transform = 'translateY(-10px)';
        this.eventLogContent.insertBefore(entry, this.eventLogContent.firstChild);
        
        // Animate in
        setTimeout(() => {
            entry.style.transition = 'all 0.3s ease';
            entry.style.opacity = '1';
            entry.style.transform = 'translateY(0)';
        }, 50);
        
        // Auto-scroll to latest
        this.eventLogContent.scrollTop = 0;
    }

    // Enhanced event info parsing
    parseEventInfoEnhanced(event) {
        const eventType = event.event_type || '';
        let info = {
            title: eventType.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase()),
            icon: 'bi-activity',
            borderColor: '#4299e1',
            bgColor: 'rgba(66, 153, 225, 0.08)',
            badgeColor: '#4299e1',
            badgeText: 'Event',
            description: event.payload?.description || 'System event occurred',
            details: null
        };

        // Enhanced event type classification
        if (eventType.includes('FORMULATION')) {
            info.icon = 'bi-beaker';
            info.borderColor = '#10b981';
            info.bgColor = 'rgba(16, 185, 129, 0.08)';
            info.badgeColor = '#10b981';
            info.badgeText = 'Formulation';
        } else if (eventType.includes('SAP') || eventType.includes('ERP')) {
            info.icon = 'bi-building';
            info.borderColor = '#f59e0b';
            info.bgColor = 'rgba(245, 158, 11, 0.08)';
            info.badgeColor = '#f59e0b';
            info.badgeText = 'SAP';
        } else if (eventType.includes('LIMS') || eventType.includes('TEST')) {
            info.icon = 'bi-microscope';
            info.borderColor = '#8b5cf6';
            info.bgColor = 'rgba(139, 92, 246, 0.08)';
            info.badgeColor = '#8b5cf6';
            info.badgeText = 'LIMS';
        } else if (eventType.includes('REGULATORY')) {
            info.icon = 'bi-shield-check';
            info.borderColor = '#ef4444';
            info.bgColor = 'rgba(239, 68, 68, 0.08)';
            info.badgeColor = '#ef4444';
            info.badgeText = 'Regulatory';
        } else if (eventType.includes('SUPPLIER') || eventType.includes('SUPPLY')) {
            info.icon = 'bi-truck';
            info.borderColor = '#06b6d4';
            info.bgColor = 'rgba(6, 182, 212, 0.08)';
            info.badgeColor = '#06b6d4';
            info.badgeText = 'Supply Chain';
        } else if (eventType.includes('VECTOR') || eventType.includes('RAG')) {
            info.icon = 'bi-database-gear';
            info.borderColor = '#84cc16';
            info.bgColor = 'rgba(132, 204, 22, 0.08)';
            info.badgeColor = '#84cc16';
            info.badgeText = 'AI/RAG';
        } else if (eventType.includes('AGENT')) {
            info.icon = 'bi-robot';
            info.borderColor = '#ec4899';
            info.bgColor = 'rgba(236, 72, 153, 0.08)';
            info.badgeColor = '#ec4899';
            info.badgeText = 'Agent';
        }

        // Add payload details if available
        if (event.payload) {
            const details = [];
            Object.entries(event.payload).forEach(([key, value]) => {
                if (key !== 'description' && key !== 'step' && key !== 'total_steps' && value !== null) {
                    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    details.push(`${formattedKey}: ${this.formatValue(value)}`);
                }
            });
            if (details.length > 0) {
                info.details = details.join('<br>');
            }
        }

        return info;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.visualizer = new EnhancedEventFlowVisualizer();
    console.log('Enhanced Event Flow Visualizer ready');
});
