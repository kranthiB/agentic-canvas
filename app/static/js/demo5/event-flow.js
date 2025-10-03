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
        
        // Initialized successfully
    }
    
    async simulateRandomScenario() {
        if (this.isSimulating) {
            this.showToast('Simulation already in progress', 'info');
            return;
        }
        
        const btnSimulate = document.getElementById('btnSimulate');
        this.isSimulating = true;
        btnSimulate.disabled = true;
        
        try {
            this.showToast('Picking a realistic scenario...', 'info');
            
            // Call the new scenario engine
            const response = await fetch('/demo5/api/scenarios/random', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentScenario = result.scenario;
                
                // Show scenario info
                this.displayScenarioInfo(result.scenario);
                
                this.showToast(`Scenario: ${result.scenario.name}`, 'success');
                
                // Animate the flow
                await this.animateScenario(result.workflow_id);
                
                // Display result
                this.displayScenarioResult(result.result);
                
            } else {
                this.showToast('Simulation failed: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Simulation error:', error);
            this.showToast('Simulation error: ' + error.message, 'error');
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
                
                // Auto-open event log if not already open
                if (!this.eventLogSidebar.classList.contains('open')) {
                    this.toggleLog();
                }
                
            } else {
                this.showToast('No events found for scenario', 'info');
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
        
        // Activate source node
        if (sourceNode) {
            sourceNode.classList.add('active', 'processing');
            this.activateConnections();
        }
        
        // Animate particle from source to target
        if (sourceNode && targetNode) {
            await this.animateParticle(sourceNode, targetNode);
        }
        
        // Activate target node
        if (targetNode) {
            targetNode.classList.add('active');
        }
        
        // Add event to log
        this.addEventToLog(event);
        
        // Deactivate after animation
        setTimeout(() => {
            if (sourceNode) {
                sourceNode.classList.remove('active', 'processing');
            }
            if (targetNode) {
                targetNode.classList.remove('active');
            }
            this.deactivateConnections();
        }, 800);
    }
    
    getNodeElement(systemName) {
        // Normalize system name for element ID
        const nodeId = `node-${systemName.replace(/[\s_]/g, '-')}`;
        const element = document.getElementById(nodeId);
        
        if (!element) {
            console.warn(`Node element not found: ${nodeId} for system: ${systemName}`);
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
            
            // Hide scenario panel
            document.getElementById('scenarioInfoPanel').classList.remove('active');
            
            // Reset metrics
            this.eventCount = 0;
            document.getElementById('metricEvents').textContent = '0';
            document.getElementById('metricLatency').textContent = '0ms';
            
            this.showToast('Event history cleared', 'info');
        } catch (error) {
            console.error('Clear error:', error);
            this.showToast('Error clearing events', 'error');
        }
    }
    
    toggleLog() {
        this.eventLogSidebar.classList.toggle('open');
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
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    window.visualizer = new EnhancedEventFlowVisualizer();
    console.log('Enhanced Event Flow Visualizer ready');
});
