// Scenario 1: Mumbai Permit Crisis - Interactive Implementation

// Mock data for Mumbai CNG stations
const mumbaiCngSites = [
    { id: 'CNG-001', name: 'Nariman Point CNG Station', lat: 18.9254, lng: 72.8243, investment: 3.5, daysDelayed: 105 },
    { id: 'CNG-002', name: 'Andheri SEEPZ CNG Hub', lat: 19.1136, lng: 72.8697, investment: 3.2, daysDelayed: 108 },
    { id: 'CNG-003', name: 'Bandra West CNG Center', lat: 19.0596, lng: 72.8295, investment: 3.8, daysDelayed: 102 },
    { id: 'CNG-004', name: 'Powai Tech Park CNG Station', lat: 19.1197, lng: 72.9059, investment: 3.4, daysDelayed: 106 },
    { id: 'CNG-005', name: 'BKC CNG Refueling Center', lat: 19.0608, lng: 72.8683, investment: 4.2, daysDelayed: 110 },
    { id: 'CNG-006', name: 'Malad Industrial CNG Hub', lat: 19.1865, lng: 72.8486, investment: 3.1, daysDelayed: 103 },
    { id: 'CNG-007', name: 'Goregaon East CNG Station', lat: 19.1653, lng: 72.8526, investment: 3.0, daysDelayed: 101 },
    { id: 'CNG-008', name: 'Vikhroli CNG Center', lat: 19.1076, lng: 72.9248, investment: 2.9, daysDelayed: 107 },
    { id: 'CNG-009', name: 'Thane West CNG Hub', lat: 19.2183, lng: 72.9781, investment: 3.3, daysDelayed: 104 },
    { id: 'CNG-010', name: 'Navi Mumbai CNG Station', lat: 19.0330, lng: 73.0297, investment: 3.7, daysDelayed: 109 },
    { id: 'CNG-011', name: 'Lower Parel CNG Center', lat: 18.9968, lng: 72.8288, investment: 4.0, daysDelayed: 111 },
    { id: 'CNG-012', name: 'Worli CNG Refueling Station', lat: 19.0176, lng: 72.8169, investment: 4.1, daysDelayed: 105 },
    { id: 'CNG-013', name: 'Kurla Complex CNG Hub', lat: 19.0728, lng: 72.8826, investment: 3.4, daysDelayed: 102 },
    { id: 'CNG-014', name: 'Mulund CNG Station', lat: 19.1722, lng: 72.9577, investment: 3.0, daysDelayed: 106 },
    { id: 'CNG-015', name: 'Borivali CNG Center', lat: 19.2307, lng: 72.8567, investment: 3.1, daysDelayed: 103 }
];

// MGL (Mahanagar Gas Limited) competitor sites
const mglCompetitorSites = [
    { name: 'MGL - Dadar CNG Station', lat: 19.0176, lng: 72.8461 },
    { name: 'MGL - Churchgate CNG Hub', lat: 18.9322, lng: 72.8264 },
    { name: 'MGL - Andheri CNG Center', lat: 19.1136, lng: 72.8697 },
    { name: 'MGL - Bandra CNG Station', lat: 19.0596, lng: 72.8295 },
    { name: 'MGL - BKC CNG Hub', lat: 19.0608, lng: 72.8683 },
    { name: 'MGL - Powai CNG Center', lat: 19.1197, lng: 72.9059 },
    { name: 'MGL - Thane CNG Station', lat: 19.2183, lng: 72.9781 },
    { name: 'MGL - Navi Mumbai CNG Hub', lat: 19.0330, lng: 73.0297 },
    { name: 'MGL - Worli CNG Center', lat: 19.0150, lng: 72.8170 },
    { name: 'MGL - Malad CNG Station', lat: 19.1850, lng: 72.8480 },
    { name: 'MGL - Goregaon CNG Hub', lat: 19.1640, lng: 72.8520 },
    { name: 'MGL - Vikhroli CNG Center', lat: 19.1070, lng: 72.9240 }
];

// Action plan items for CNG infrastructure
const actionPlanItems = [
    {
        id: 1,
        title: 'Escalate to PESO & Fire Department',
        priority: 'high',
        details: 'Direct engagement with PESO (Petroleum & Explosives Safety Organisation) and Mumbai Fire Brigade for safety clearances',
        expectedOutcome: 'Expedited safety approvals for CNG infrastructure',
        timelineImprovement: '35 days',
        cost: '₹3L'
    },
    {
        id: 2,
        title: 'Environmental Clearance Fast-track',
        priority: 'high',
        details: 'Accelerate pollution control board clearances for CNG dispensing units',
        expectedOutcome: 'Environmental compliance certificates',
        timelineImprovement: '28 days',
        cost: '₹5L'
    },
    {
        id: 3,
        title: 'Gas Pipeline Coordination',
        priority: 'medium',
        details: 'Coordinate with MGL (Mahanagar Gas Limited) for pipeline connections',
        expectedOutcome: 'Assured gas supply infrastructure',
        timelineImprovement: '20 days',
        cost: '₹4L'
    },
    {
        id: 4,
        title: 'Safety Compliance Audit',
        priority: 'medium',
        details: 'Pre-approval safety audits for all pressure vessel installations',
        expectedOutcome: 'Safety certification readiness',
        timelineImprovement: '25 days',
        cost: '₹6L'
    },
    {
        id: 5,
        title: 'Fleet Operator Partnerships',
        priority: 'low',
        details: 'Engage commercial fleet operators as anchor customers',
        expectedOutcome: 'Guaranteed initial demand',
        timelineImprovement: '12 days',
        cost: '₹2L'
    }
];

// Event flow timeline for CNG infrastructure crisis
const eventTimeline = [
    { timestamp: '09:42:00', agent: 'orchestrator', text: 'Crisis detected: 15 Mumbai CNG stations delayed >90 days' },
    { timestamp: '09:42:02', agent: 'orchestrator', text: 'Initiating multi-agent CNG infrastructure response workflow' },
    { timestamp: '09:42:05', agent: 'permit', text: 'Analyzing PESO and Fire Department permit bottleneck...' },
    { timestamp: '09:42:15', agent: 'permit', text: 'Root cause identified: Complex safety clearance process across 6 departments' },
    { timestamp: '09:42:20', agent: 'permit', text: 'Average delay: 145 days (vs 60 days standard for CNG)' },
    { timestamp: '09:42:30', agent: 'financial', text: 'Calculating CNG infrastructure investment impact...' },
    { timestamp: '09:42:40', agent: 'financial', text: 'At-risk investment: ₹42 Crores across 15 CNG stations' },
    { timestamp: '09:42:45', agent: 'financial', text: 'Lost revenue projection: ₹15.2 Cr/year if unresolved' },
    { timestamp: '09:43:00', agent: 'market', text: 'Analyzing CNG market competitive landscape...' },
    { timestamp: '09:43:10', agent: 'market', text: 'MGL: 12 operational CNG stations within 3km radius' },
    { timestamp: '09:43:15', agent: 'market', text: 'Market share risk: Could lose 18% in Mumbai CNG segment' },
    { timestamp: '09:43:30', agent: 'orchestrator', text: 'Generating 5-point CNG action plan...' },
    { timestamp: '09:43:45', agent: 'orchestrator', text: 'Action plan complete. Estimated timeline reduction: 85 days' },
    { timestamp: '09:43:50', agent: 'orchestrator', text: 'Total investment required: ₹20 Lakh | ROI: 28x' },
    { timestamp: '09:44:00', agent: 'orchestrator', text: 'CNG crisis response strategy ready for CEO approval' }
];

// Execution steps for CNG infrastructure
const executionSteps = [
    { id: 1, text: 'Budget Release: ₹20 Lakh allocated for CNG permits', delay: 1000 },
    { id: 2, text: 'Safety Consultant Engagement: PESO specialists contracted', delay: 1500 },
    { id: 3, text: 'PESO Meeting: Scheduled safety review for Monday', delay: 2000 },
    { id: 4, text: 'Environmental Clearance: PCB applications submitted', delay: 1200 },
    { id: 5, text: 'MGL Coordination: Pipeline connection agreements signed', delay: 1000 },
    { id: 6, text: 'Safety Monitoring: CNG compliance tracking activated', delay: 1500 }
];

// Global variables
let map;
let mumbaiCngMarkers = [];
let mglCompetitorMarkers = [];
let eventFlowInterval;
let currentEventIndex = 0;

// Initialize map on load
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    populateMumbaiCngSitesList();
    setupEventListeners();
    
    // Don't show quick start guide
    // setTimeout(() => {
    //     showQuickStartGuide();
    // }, 1000);
});

// Show quick start guide
function showQuickStartGuide() {
    document.getElementById('quickStartGuide').style.display = 'flex';
}

// Hide quick start guide
function hideQuickStartGuide() {
    document.getElementById('quickStartGuide').style.display = 'none';
}

// Initialize Leaflet map
function initializeMap() {
    // Create map centered on Mumbai
    map = L.map('networkMap', {
        zoomControl: false // We'll use custom controls
    }).setView([19.0760, 72.8777], 11);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);

    // Add Mumbai CNG stations (blocked - red markers)
    mumbaiCngSites.forEach(site => {
        const marker = L.circleMarker([site.lat, site.lng], {
            radius: 10,
            fillColor: '#dc2626',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.9,
            className: 'mumbai-site-marker'
        }).addTo(map);

        // Popup content
        const popupContent = `
            <div class="site-popup">
                <div class="popup-header">
                    <h4>${site.name}</h4>
                    <span class="popup-badge" style="background: rgba(220, 38, 38, 0.2); color: #dc2626; border: 1px solid #dc2626;">
                        BLOCKED
                    </span>
                </div>
                <div class="popup-info">
                    <div class="info-row">
                        <span class="info-label">Station ID</span>
                        <span class="info-value">${site.id}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Investment</span>
                        <span class="info-value">₹${site.investment} Cr</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Days Delayed</span>
                        <span class="info-value" style="color: #dc2626;">${site.daysDelayed} days</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Bottleneck</span>
                        <span class="info-value">PESO Safety Permits</span>
                    </div>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent, { maxWidth: 300 });
        mumbaiCngMarkers.push(marker);
    });

    // Add MGL competitor sites (yellow markers)
    mglCompetitorSites.forEach(site => {
        const marker = L.circleMarker([site.lat, site.lng], {
            radius: 8,
            fillColor: '#f59e0b',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);

        const popupContent = `
            <div class="site-popup">
                <div class="popup-header">
                    <h4 style="font-size: 15px;">${site.name}</h4>
                    <span class="popup-badge" style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b;">
                        COMPETITOR
                    </span>
                </div>
                <div class="popup-info">
                    <div class="info-row">
                        <span class="info-label">Operator</span>
                        <span class="info-value">MGL (Mahanagar Gas)</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Status</span>
                        <span class="info-value" style="color: #10b981;">Operational</span>
                    </div>
                </div>
            </div>
        `;

        marker.bindPopup(popupContent, { maxWidth: 300 });
        mglCompetitorMarkers.push(marker);
    });
    
    // Force map to resize and fit container properly
    setTimeout(() => {
        if (map) {
            map.invalidateSize();
        }
    }, 100);
}

// Populate Mumbai CNG stations list in sidebar
function populateMumbaiCngSitesList() {
    const listContainer = document.getElementById('mumbaiSitesList');
    
    mumbaiCngSites.forEach(site => {
        const siteItem = document.createElement('div');
        siteItem.className = 'detail-item';
        siteItem.style.marginBottom = '10px';
        siteItem.style.cursor = 'pointer';
        siteItem.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; gap: 12px;">
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 700; font-size: 14px; color: var(--text-primary); margin-bottom: 2px;">${site.id}</div>
                    <div style="font-size: 13px; color: var(--text-secondary);">${site.name}</div>
                </div>
                <span style="font-size: 11px; color: #dc2626; font-weight: 700; background: rgba(220, 38, 38, 0.1); padding: 3px 8px; border-radius: 8px; flex-shrink: 0;">
                    ${site.daysDelayed} days
                </span>
            </div>
        `;
        
        // Click to zoom to site
        siteItem.addEventListener('click', () => {
            map.setView([site.lat, site.lng], 15);
            // Find and open popup
            mumbaiCngMarkers.forEach(marker => {
                const markerLatLng = marker.getLatLng();
                if (markerLatLng.lat === site.lat && markerLatLng.lng === site.lng) {
                    marker.openPopup();
                }
            });
        });
        
        listContainer.appendChild(siteItem);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Quick start guide buttons
    document.getElementById('btnCloseGuide').addEventListener('click', hideQuickStartGuide);
    document.getElementById('btnStartDemo').addEventListener('click', () => {
        hideQuickStartGuide();
        // Scroll to investigate button and highlight it
        const investigateBtn = document.getElementById('btnInvestigate');
        investigateBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        investigateBtn.style.animation = 'buttonPulse 1s ease 3';
    });
    
    // Investigate button - handled in modal section below
    
    // Show alert modal
    function showAlertModal() {
        console.log('showAlertModal called'); // Debug
        const modal = document.getElementById('crisisAlertModal');
        console.log('Modal element:', modal); // Debug
        
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            
            // Focus the modal for accessibility
            setTimeout(() => {
                const closeBtn = document.getElementById('btnCloseModal');
                if (closeBtn) {
                    closeBtn.focus();
                }
            }, 100);
            
            console.log('Alert modal opened successfully');
        } else {
            console.error('Crisis alert modal not found!');
        }
    }
    
    // Hide alert modal
    function hideAlertModal() {
        const modal = document.getElementById('crisisAlertModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto'; // Restore scroll
        }
    }
    
    // Handle investigate crisis - close modal and continue with existing logic
    function investigateCrisis() {
        hideAlertModal();
        // Continue with existing investigation logic
        startInvestigation();
    }
    
    // Show alert modal button
    const btnShowAlert = document.getElementById('btnShowAlert');
    if (btnShowAlert) {
        btnShowAlert.addEventListener('click', showAlertModal);
        console.log('Alert button listener attached');
    } else {
        console.error('btnShowAlert not found!');
    }
    
    // Close modal button
    const btnCloseModal = document.getElementById('btnCloseModal');
    if (btnCloseModal) {
        btnCloseModal.addEventListener('click', hideAlertModal);
    }
    
    // Investigate crisis button - close modal and proceed
    const btnInvestigate = document.getElementById('btnInvestigate');
    if (btnInvestigate) {
        btnInvestigate.addEventListener('click', investigateCrisis);
    }
    
    // Dismiss alert button - just close modal
    const btnDismissAlert = document.getElementById('btnDismissAlert');
    if (btnDismissAlert) {
        btnDismissAlert.addEventListener('click', hideAlertModal);
    }
    
    // Close modal with ESC key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            hideAlertModal();
        }
    });
    
    // Close modal when clicking backdrop
    const modalElement = document.getElementById('crisisAlertModal');
    if (modalElement) {
        modalElement.addEventListener('click', (event) => {
            if (event.target.classList.contains('modal-backdrop') || event.target.id === 'crisisAlertModal') {
                hideAlertModal();
            }
        });
    }
    
    // Map controls
    document.getElementById('btnZoomIn').addEventListener('click', () => map.zoomIn());
    document.getElementById('btnZoomOut').addEventListener('click', () => map.zoomOut());
    document.getElementById('btnResetView').addEventListener('click', () => {
        map.setView([19.0760, 72.8777], 11);
    });
    
    document.getElementById('btnFullscreen').addEventListener('click', toggleFullscreen);
    
    // Approval modal buttons
    document.getElementById('btnRequestApproval').addEventListener('click', showApprovalModal);
    document.getElementById('btnApproveAction').addEventListener('click', executeActionPlan);
    document.getElementById('btnRejectAction').addEventListener('click', () => {
        document.getElementById('approvalModal').style.display = 'none';
    });
    
    // Close execution overlay
    document.getElementById('btnCloseExecution').addEventListener('click', () => {
        document.getElementById('executionOverlay').style.display = 'none';
        // Show success message
        alert('CNG action plan executed successfully! Crisis resolution in progress.');
    });
}

// Start investigation - show event flow
function startInvestigation() {
    // Show loading
    const loadingOverlay = document.getElementById('mapLoadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
    
    setTimeout(() => {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
        
        // Create and show modal overlay for event flow
        showEventFlowModal();
        
        // Start event stream
        startEventStream();
    }, 2000);
}

// Show event flow as modal
function showEventFlowModal() {
    // Create modal overlay
    const modalOverlay = document.createElement('div');
    modalOverlay.className = 'event-flow-modal-overlay';
    modalOverlay.id = 'eventFlowModalOverlay';
    
    // Move the event flow panel into the modal
    const eventFlowPanel = document.getElementById('eventFlowPanel');
    modalOverlay.appendChild(eventFlowPanel);
    eventFlowPanel.style.display = 'flex';
    
    // Add to body
    document.body.appendChild(modalOverlay);
    
    // Show with animation
    setTimeout(() => {
        modalOverlay.classList.add('show');
    }, 10);
}

// Close event flow panel
function closeEventFlow() {
    const modalOverlay = document.getElementById('eventFlowModalOverlay');
    if (modalOverlay) {
        modalOverlay.classList.remove('show');
        setTimeout(() => {
            modalOverlay.remove();
        }, 300);
    } else {
        // Fallback for old method
        const eventFlowPanel = document.getElementById('eventFlowPanel');
        if (eventFlowPanel) {
            eventFlowPanel.style.display = 'none';
        }
    }
}

// Show event flow completion
function showEventFlowCompletion() {
    const eventStream = document.getElementById('eventStream');
    const progressText = document.getElementById('progressText');
    const progressFill = document.getElementById('progressFill');
    
    // Update progress to completed
    if (progressText && progressFill) {
        progressText.textContent = `Complete! (${eventTimeline.length}/${eventTimeline.length})`;
        progressText.style.color = '#22c55e';
        progressFill.style.width = '100%';
        progressFill.style.background = 'linear-gradient(90deg, #22c55e, #16a34a)';
    }
    
    // Add completion section with button in the same panel
    const completionDiv = document.createElement('div');
    completionDiv.className = 'event-flow-complete';
    completionDiv.innerHTML = `
        <div class="completion-text">Analysis Complete</div>
        <div class="completion-summary">All ${eventTimeline.length} agents have completed their investigation</div>
        <div class="event-flow-actions">
            <button class="btn-view-actions" onclick="showRecommendedActions()">
                <i class="fas fa-lightbulb"></i>
                View Recommended Actions
            </button>
        </div>
    `;
    
    eventStream.appendChild(completionDiv);
    
    // Scroll to bottom to show completion
    setTimeout(() => {
        eventStream.scrollTop = eventStream.scrollHeight;
    }, 100);
}



// Start event stream animation
function startEventStream() {
    const eventStream = document.getElementById('eventStream');
    eventStream.innerHTML = ''; // Clear existing events
    currentEventIndex = 0;
    
    // Show progress indicator
    const eventProgress = document.getElementById('eventProgress');
    const progressText = document.getElementById('progressText');
    const progressFill = document.getElementById('progressFill');
    
    if (eventProgress) {
        eventProgress.style.display = 'flex';
        progressText.textContent = `Processing... (0/${eventTimeline.length})`;
        progressFill.style.width = '0%';
    }
    
    eventFlowInterval = setInterval(() => {
        if (currentEventIndex < eventTimeline.length) {
            const event = eventTimeline[currentEventIndex];
            addEventToStream(event);
            currentEventIndex++;
            
            // Update progress
            if (progressText && progressFill) {
                progressText.textContent = `Processing... (${currentEventIndex}/${eventTimeline.length})`;
                progressFill.style.width = `${(currentEventIndex / eventTimeline.length) * 100}%`;
            }
        } else {
            clearInterval(eventFlowInterval);
            // Show completion indicator
            showEventFlowCompletion();
        }
    }, 1000); // Add event every second
}

// Add event to stream
function addEventToStream(event) {
    const eventStream = document.getElementById('eventStream');
    
    const eventItem = document.createElement('div');
    eventItem.className = `event-item agent-${event.agent}`;
    eventItem.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 4px; flex: 1;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="event-agent">${getAgentName(event.agent)}</span>
                <span class="event-timestamp">${event.timestamp}</span>
            </div>
            <div class="event-action">${event.text}</div>
        </div>
    `;
    
    eventStream.appendChild(eventItem);
    
    // Auto-scroll to bottom
    eventStream.scrollTop = eventStream.scrollHeight;
}

// Get agent display name
function getAgentName(agentType) {
    const names = {
        orchestrator: '🤖 Orchestrator',
        permit: '📋 Permit Agent',
        financial: '💰 Financial Agent',
        market: '📊 Market Intelligence'
    };
    return names[agentType] || agentType;
}

// Show action plan
function showActionPlan() {
    const actionPlanPanel = document.getElementById('actionPlanPanel');
    const actionPlanList = document.getElementById('actionPlanList');
    
    actionPlanList.innerHTML = '';
    
    actionPlanItems.forEach(item => {
        const actionItem = document.createElement('div');
        actionItem.className = `action-item priority-${item.priority}`;
        actionItem.innerHTML = `
            <div class="action-title">
                <span>${item.title}</span>
                <span class="priority-badge">${item.priority}</span>
            </div>
            <div class="action-details">${item.details}</div>
            <div class="action-metrics">
                <div class="action-metric">
                    <div class="action-metric-label">Timeline</div>
                    <div class="action-metric-value">-${item.timelineImprovement}</div>
                </div>
                <div class="action-metric">
                    <div class="action-metric-label">Cost</div>
                    <div class="action-metric-value">${item.cost}</div>
                </div>
                <div class="action-metric">
                    <div class="action-metric-label">Outcome</div>
                    <div class="action-metric-value" style="font-size: 11px; line-height: 1.3;">${item.expectedOutcome}</div>
                </div>
            </div>
        `;
        actionPlanList.appendChild(actionItem);
    });
    
    actionPlanPanel.style.display = 'block';
    actionPlanPanel.style.animation = 'slideUp 0.5s ease';
}

// Show approval modal
function showApprovalModal() {
    document.getElementById('approvalModal').style.display = 'flex';
}

// Execute action plan
function executeActionPlan() {
    // Hide approval modal
    document.getElementById('approvalModal').style.display = 'none';
    
    // Show execution overlay
    const executionOverlay = document.getElementById('executionOverlay');
    executionOverlay.style.display = 'flex';
    
    // Populate execution steps
    const executionStepsContainer = document.getElementById('executionSteps');
    executionStepsContainer.innerHTML = '';
    
    executionSteps.forEach((step, index) => {
        const stepEl = document.createElement('div');
        stepEl.className = 'execution-step';
        stepEl.id = `execStep${step.id}`;
        stepEl.innerHTML = `
            <div class="step-icon-exec">
                <i class="fas fa-circle-notch fa-spin"></i>
            </div>
            <div class="step-text-exec">${step.text}</div>
        `;
        executionStepsContainer.appendChild(stepEl);
    });
    
    // Animate execution steps
    let totalDelay = 0;
    executionSteps.forEach((step, index) => {
        totalDelay += step.delay;
        
        setTimeout(() => {
            const stepEl = document.getElementById(`execStep${step.id}`);
            stepEl.classList.add('completed');
            stepEl.querySelector('.step-icon-exec').innerHTML = '<i class="fas fa-check"></i>';
            
            // If last step, show close button
            if (index === executionSteps.length - 1) {
                setTimeout(() => {
                    document.getElementById('btnCloseExecution').style.display = 'inline-flex';
                }, 500);
            }
        }, totalDelay);
    });
}

// Toggle fullscreen
function toggleFullscreen() {
    const mapWrapper = document.querySelector('.map-wrapper');
    
    if (!document.fullscreenElement) {
        mapWrapper.requestFullscreen().catch(err => {
            console.error('Error attempting to enable fullscreen:', err);
        });
    } else {
        document.exitFullscreen();
    }
}

// Resize map to fit container
function resizeMap() {
    if (map) {
        setTimeout(() => {
            map.invalidateSize();
        }, 250);
    }
}

// Add resize listener and force initial resize
window.addEventListener('resize', resizeMap);
document.addEventListener('fullscreenchange', resizeMap);

// Force resize on initial load
window.addEventListener('load', () => {
    setTimeout(resizeMap, 500);
    console.log('Page loaded, initializing alert system...');
    
    // Debug check
    const alertBtn = document.getElementById('btnShowAlert');
    const modal = document.getElementById('crisisAlertModal');
    console.log('Alert button found:', !!alertBtn);
    console.log('Modal found:', !!modal);
});

// Force resize when returning from fullscreen or modal
document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
        resizeMap();
    }
});

// Show recommended actions modal
function showRecommendedActions() {
    // Close event flow first
    closeEventFlow();
    
    // Show recommended actions modal
    const modal = document.getElementById('recommendedActionsModal');
    if (modal) {
        modal.style.display = 'flex';
        populateAffectedSites();
        initializeActionsCarousel();
    }
}

// Close recommended actions modal
function closeRecommendedActions() {
    const modal = document.getElementById('recommendedActionsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Actions carousel functionality
let currentActionIndex = 0;
const totalActions = 3;

function navigateAction(direction) {
    const carousel = document.getElementById('actionsCarousel');
    const counter = document.getElementById('actionCounter');
    const prevBtn = document.getElementById('prevAction');
    const nextBtn = document.getElementById('nextAction');
    
    if (!carousel) return;
    
    // Update index
    currentActionIndex += direction;
    
    // Handle wrapping
    if (currentActionIndex < 0) {
        currentActionIndex = totalActions - 1;
    } else if (currentActionIndex >= totalActions) {
        currentActionIndex = 0;
    }
    
    // Update active card
    const cards = carousel.querySelectorAll('.action-card');
    cards.forEach((card, index) => {
        card.classList.toggle('active', index === currentActionIndex);
    });
    
    // Update counter
    if (counter) {
        counter.textContent = `${currentActionIndex + 1} / ${totalActions}`;
    }
    
    // Update button states
    if (prevBtn && nextBtn) {
        prevBtn.disabled = false;
        nextBtn.disabled = false;
        
        // Optional: disable buttons at ends (uncomment if you don't want wrapping)
        // prevBtn.disabled = currentActionIndex === 0;
        // nextBtn.disabled = currentActionIndex === totalActions - 1;
    }
}

// Initialize actions carousel
function initializeActionsCarousel() {
    currentActionIndex = 0;
    const counter = document.getElementById('actionCounter');
    if (counter) {
        counter.textContent = `1 / ${totalActions}`;
    }
}

// Populate affected sites from sidebar data
function populateAffectedSites() {
    const affectedSitesList = document.getElementById('affectedSitesList');
    if (!affectedSitesList) return;
    
    // Get sites from the sidebar
    const sidebarSites = document.querySelectorAll('#mumbaiSitesList .site-item');
    let sitesHTML = '';
    
    if (sidebarSites.length > 0) {
        sidebarSites.forEach(site => {
            const siteName = site.querySelector('.site-name')?.textContent || 'Unknown Site';
            const siteDetails = site.querySelector('.site-details')?.textContent || '';
            const statusElement = site.querySelector('.site-status');
            const status = statusElement?.textContent || 'Unknown';
            const statusClass = status.toLowerCase().includes('high') ? 'status-high' : 'status-medium';
            
            sitesHTML += `
                <div class="site-card">
                    <div class="site-header">
                        <div class="site-name">${siteName}</div>
                        <div class="site-status ${statusClass}">${status}</div>
                    </div>
                    <div class="site-details">${siteDetails}</div>
                </div>
            `;
        });
    } else {
        // Fallback data if sidebar is not populated
        sitesHTML = `
            <div class="site-card">
                <div class="site-header">
                    <div class="site-name">MUM-001 - Nariman Point</div>
                    <div class="site-status status-high">92 days</div>
                </div>
                <div class="site-details">Investment: ₹2.2 Cr | Priority: High Risk</div>
            </div>
            <div class="site-card">
                <div class="site-header">
                    <div class="site-name">MUM-002 - Bandra Kurla</div>
                    <div class="site-status status-high">85 days</div>
                </div>
                <div class="site-details">Investment: ₹1.8 Cr | Priority: High Risk</div>
            </div>
            <div class="site-card">
                <div class="site-header">
                    <div class="site-name">MUM-003 - Andheri East</div>
                    <div class="site-status status-high">78 days</div>
                </div>
                <div class="site-details">Investment: ₹1.5 Cr | Priority: Medium Risk</div>
            </div>
        `;
    }
    
    affectedSitesList.innerHTML = sitesHTML;
}

// Request CEO Approval function
function requestCEOApproval() {
    // Show custom confirmation modal instead of browser confirm
    showCustomConfirmation();
}

// Show custom confirmation modal
function showCustomConfirmation() {
    const confirmationOverlay = document.createElement('div');
    confirmationOverlay.className = 'custom-confirmation-overlay';
    confirmationOverlay.id = 'customConfirmationOverlay';
    
    confirmationOverlay.innerHTML = `
        <div class="custom-confirmation-content">
            <div class="custom-confirmation-header">
                <div class="confirmation-icon">
                    <i class="fas fa-exclamation-circle"></i>
                </div>
                <h2 class="confirmation-title">Request CEO Approval</h2>
                <p class="confirmation-subtitle">Are you sure you want to submit this crisis response plan for executive approval?</p>
            </div>
            
            <div class="custom-confirmation-body">
                <div class="confirmation-details">
                    <div class="detail-item">
                        <i class="fas fa-chart-line"></i>
                        <span>Total Investment: <strong>₹20 Lakh</strong></span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-clock"></i>
                        <span>Expected Timeline: <strong>85 days</strong></span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>CNG Stations Affected: <strong>15 locations</strong></span>
                    </div>
                    <div class="detail-item">
                        <i class="fas fa-percentage"></i>
                        <span>Expected ROI: <strong>28%</strong></span>
                    </div>
                </div>
            </div>
            
            <div class="custom-confirmation-actions">
                <button class="btn-cancel-approval" onclick="closeCustomConfirmation()">
                    <i class="fas fa-times"></i>
                    Cancel
                </button>
                <button class="btn-confirm-approval" onclick="proceedWithApproval()">
                    <i class="fas fa-check"></i>
                    Submit Request
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(confirmationOverlay);
    
    // Show with animation
    setTimeout(() => {
        confirmationOverlay.classList.add('show');
    }, 10);
}

// Close custom confirmation
function closeCustomConfirmation() {
    const modal = document.getElementById('customConfirmationOverlay');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Proceed with approval after confirmation
function proceedWithApproval() {
    closeCustomConfirmation();
    closeRecommendedActions();
    showApprovalProcessSteps();
}

// Show approval process steps
function showApprovalProcessSteps() {
    const processOverlay = document.createElement('div');
    processOverlay.className = 'approval-process-overlay';
    processOverlay.id = 'approvalProcessOverlay';
    
    processOverlay.innerHTML = `
        <div class="approval-process-content">
            <div class="approval-process-header">
                <div class="process-icon">
                    <i class="fas fa-cogs"></i>
                </div>
                <h2 class="process-title">Processing Request</h2>
                <p class="process-subtitle">Executing approval workflow...</p>
            </div>
            
            <div class="approval-process-body">
                <div class="process-steps" id="processSteps">
                    <div class="process-step" data-step="1">
                        <div class="step-icon">
                            <i class="fas fa-file-alt"></i>
                        </div>
                        <div class="step-content">
                            <div class="step-title">Validating Request</div>
                            <div class="step-description">Checking all required data and documents</div>
                        </div>
                        <div class="step-status">
                            <i class="fas fa-spinner fa-spin"></i>
                        </div>
                    </div>
                    
                    <div class="process-step" data-step="2">
                        <div class="step-icon">
                            <i class="fas fa-shield-alt"></i>
                        </div>
                        <div class="step-content">
                            <div class="step-title">Security Review</div>
                            <div class="step-description">Performing security and compliance checks</div>
                        </div>
                        <div class="step-status">
                            <i class="fas fa-clock"></i>
                        </div>
                    </div>
                    
                    <div class="process-step" data-step="3">
                        <div class="step-icon">
                            <i class="fas fa-calculator"></i>
                        </div>
                        <div class="step-content">
                            <div class="step-title">Financial Analysis</div>
                            <div class="step-description">Analyzing investment and ROI projections</div>
                        </div>
                        <div class="step-status">
                            <i class="fas fa-clock"></i>
                        </div>
                    </div>
                    
                    <div class="process-step" data-step="4">
                        <div class="step-icon">
                            <i class="fas fa-envelope"></i>
                        </div>
                        <div class="step-content">
                            <div class="step-title">Generating Request</div>
                            <div class="step-description">Creating executive summary and documentation</div>
                        </div>
                        <div class="step-status">
                            <i class="fas fa-clock"></i>
                        </div>
                    </div>
                    
                    <div class="process-step" data-step="5">
                        <div class="step-icon">
                            <i class="fas fa-paper-plane"></i>
                        </div>
                        <div class="step-content">
                            <div class="step-title">Sending to CEO</div>
                            <div class="step-description">Submitting request to executive dashboard</div>
                        </div>
                        <div class="step-status">
                            <i class="fas fa-clock"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(processOverlay);
    
    // Show with animation
    setTimeout(() => {
        processOverlay.classList.add('show');
        executeProcessSteps();
    }, 10);
}

// Execute process steps with animation
function executeProcessSteps() {
    const steps = document.querySelectorAll('.process-step');
    let currentStep = 0;
    
    function processNextStep() {
        if (currentStep < steps.length) {
            const step = steps[currentStep];
            const statusIcon = step.querySelector('.step-status i');
            
            // Update status to processing
            statusIcon.className = 'fas fa-spinner fa-spin';
            step.classList.add('processing');
            
            // Complete step after delay
            setTimeout(() => {
                statusIcon.className = 'fas fa-check-circle';
                step.classList.remove('processing');
                step.classList.add('completed');
                
                currentStep++;
                
                if (currentStep < steps.length) {
                    // Process next step
                    setTimeout(() => {
                        processNextStep();
                    }, 300);
                } else {
                    // All steps completed, show success
                    setTimeout(() => {
                        closeApprovalProcess();
                        showApprovalRequestConfirmation();
                    }, 800);
                }
            }, 1500 + Math.random() * 1000); // Random delay between 1.5-2.5 seconds
        }
    }
    
    processNextStep();
}

// Close approval process modal
function closeApprovalProcess() {
    const modal = document.getElementById('approvalProcessOverlay');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Show approval request confirmation
function showApprovalRequestConfirmation() {
    // Create confirmation modal
    const confirmationOverlay = document.createElement('div');
    confirmationOverlay.className = 'approval-confirmation-overlay';
    confirmationOverlay.id = 'approvalConfirmationOverlay';
    
    confirmationOverlay.innerHTML = `
        <div class="approval-confirmation-content">
            <div class="approval-confirmation-header">
                <div class="approval-icon">
                    <i class="fas fa-paper-plane"></i>
                </div>
                <h2 class="approval-title">Request Sent Successfully!</h2>
                <p class="approval-subtitle">CEO approval request has been submitted</p>
            </div>
            
            <div class="approval-confirmation-body">
                <div class="approval-details">
                    <div class="approval-detail">
                        <strong>Request ID:</strong> REQ-${Date.now()}
                    </div>
                    <div class="approval-detail">
                        <strong>Priority:</strong> Critical
                    </div>
                    <div class="approval-detail">
                        <strong>Expected Response:</strong> Within 24 hours
                    </div>
                    <div class="approval-detail">
                        <strong>Total Investment:</strong> ₹20 Lakh
                    </div>
                </div>
            </div>
            
            <div class="approval-confirmation-actions">
                <button class="btn-close-approval" onclick="closeApprovalConfirmation()">
                    <i class="fas fa-check"></i>
                    OK
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(confirmationOverlay);
    
    // Show with animation
    setTimeout(() => {
        confirmationOverlay.classList.add('show');
    }, 10);
}

// Close approval confirmation
function closeApprovalConfirmation() {
    const modal = document.getElementById('approvalConfirmationOverlay');
    if (modal) {
        modal.classList.remove('show');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

// Event listener for close event flow button
document.addEventListener('DOMContentLoaded', function() {
    const btnCloseEventFlow = document.getElementById('btnCloseEventFlow');
    if (btnCloseEventFlow) {
        btnCloseEventFlow.addEventListener('click', closeEventFlow);
    }
    
    // Close modal when clicking outside
    const modal = document.getElementById('recommendedActionsModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeRecommendedActions();
            }
        });
    }
    
    // Add click handler for CEO approval button
    document.addEventListener('click', function(e) {
        if (e.target.closest('.btn-approve-all')) {
            requestCEOApproval();
        }
    });
});
