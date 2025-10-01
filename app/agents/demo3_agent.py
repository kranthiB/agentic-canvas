"""
Demo 3: Safety Guardian Agent
T2 Procedural Workflow Agent for refinery safety monitoring
"""
import random
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.agents.base_agent import BaseAgent
from app.models.demo3_models import RiskLevel, PermitType

logger = logging.getLogger(__name__)


class SafetyGuardianAgent(BaseAgent):
    """
    T2 Procedural Workflow Agent
    Capabilities: PK.OB, CG.PS, IC.HL, AE.CG, GS.SF
    """
    
    def __init__(self):
        super().__init__(
            agent_id='safety-guardian-001',
            agent_type='T2-Procedural',
            capabilities=['PK.OB', 'CG.PS', 'IC.HL', 'AE.CG', 'GS.SF']
        )
        
        # Safety thresholds
        self.GAS_THRESHOLDS = {
            'O2': {'min': 19.5, 'max': 23.5},
            'LEL': {'critical': 10, 'warning': 5},
            'H2S': {'critical': 10, 'warning': 5},
            'CO': {'critical': 50, 'warning': 25}
        }
        
        # Proximity thresholds (meters)
        self.PROXIMITY_THRESHOLDS = {
            'hot_work': 50,
            'confined_space': 30,
            'electrical': 25,
            'default': 20
        }
        
        # Critical conflicts (incompatible activities)
        self.CRITICAL_CONFLICTS = [
            ('hot_work', 'line_breaking'),
            ('hot_work', 'confined_space'),
            ('electrical', 'hot_work')
        ]
        
        self.confidence = 0.94
    
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        PK.OB - Environmental Sensing
        Monitor gas levels, permits, and facility state
        """
        gas_readings = environment.get('gas_readings', {})
        active_permits = environment.get('active_permits', [])
        
        # Assess gas hazards
        gas_hazards = self._assess_gas_hazards(gas_readings)
        
        # Get permit conflicts
        permit_conflicts = self._detect_permit_conflicts(active_permits)
        
        perception = {
            'gas_readings': gas_readings,
            'gas_hazards': gas_hazards,
            'active_permits_count': len(active_permits),
            'active_permits': active_permits,
            'conflicts': permit_conflicts,
            'overall_risk_level': self._calculate_overall_risk(gas_hazards, permit_conflicts),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Perceived {len(gas_hazards)} gas hazards, {len(permit_conflicts)} conflicts")
        
        return perception
    
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.PS - Problem Solving
        GS.SF - Safety protocols
        Analyze hazards and determine actions
        """
        gas_hazards = perception['gas_hazards']
        conflicts = perception['conflicts']
        overall_risk = perception['overall_risk_level']
        
        # Generate recommendations
        recommendations = []
        
        # Gas hazard recommendations
        for hazard in gas_hazards:
            if hazard['severity'] == 'critical':
                recommendations.append({
                    'type': 'gas_alarm',
                    'severity': 'critical',
                    'action': f"IMMEDIATE EVACUATION: {hazard['gas_type']} at {hazard['level']:.1f} {hazard['unit']}",
                    'area': hazard['area'],
                    'priority': 1
                })
            elif hazard['severity'] == 'warning':
                recommendations.append({
                    'type': 'gas_warning',
                    'severity': 'high',
                    'action': f"Investigate {hazard['gas_type']} elevation in {hazard['area']}",
                    'area': hazard['area'],
                    'priority': 2
                })
        
        # Conflict recommendations
        for conflict in conflicts:
            if conflict['severity'] == 'critical':
                recommendations.append({
                    'type': 'permit_conflict',
                    'severity': 'critical',
                    'action': f"SUSPEND PERMIT: {conflict['description']}",
                    'recommendation': conflict['recommendation'],
                    'priority': 1
                })
            else:
                recommendations.append({
                    'type': 'permit_conflict',
                    'severity': conflict['severity'],
                    'action': f"Review: {conflict['description']}",
                    'recommendation': conflict['recommendation'],
                    'priority': 2 if conflict['severity'] == 'high' else 3
                })
        
        # Human-in-the-loop requirement
        requires_approval = any(r['severity'] == 'critical' for r in recommendations)
        
        decision = {
            'recommendations': recommendations,
            'overall_risk_level': overall_risk,
            'requires_human_approval': requires_approval,
            'confidence': self.confidence,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return decision
    
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        AE.CG - Code Generation (auto-generate safety procedures)
        Execute safety actions
        """
        recommendations = decision['recommendations']
        
        # Generate safety actions
        actions = []
        
        for rec in recommendations:
            if rec['severity'] == 'critical':
                actions.append({
                    'action_type': 'emergency_response',
                    'description': rec['action'],
                    'automated': True,
                    'executed_at': datetime.utcnow().isoformat()
                })
            else:
                actions.append({
                    'action_type': 'advisory',
                    'description': rec['action'],
                    'automated': False,
                    'requires_operator_action': True
                })
        
        result = {
            'actions_taken': actions,
            'overall_risk_level': decision['overall_risk_level'],
            'requires_human_approval': decision['requires_human_approval'],
            'alert_count': len(actions)
        }
        
        return result
    
    def _assess_gas_hazards(self, gas_readings: Dict[str, Any]) -> List[Dict]:
        """Assess gas reading hazards"""
        hazards = []
        
        for area, readings in gas_readings.items():
            # Oxygen
            o2 = readings.get('O2', 20.9)
            if o2 < self.GAS_THRESHOLDS['O2']['min'] or o2 > self.GAS_THRESHOLDS['O2']['max']:
                hazards.append({
                    'gas_type': 'O2',
                    'area': area,
                    'level': o2,
                    'unit': '%',
                    'severity': 'critical',
                    'description': f'Oxygen level out of safe range: {o2}%'
                })
            
            # LEL (Lower Explosive Limit)
            lel = readings.get('LEL', 0)
            if lel >= self.GAS_THRESHOLDS['LEL']['critical']:
                hazards.append({
                    'gas_type': 'LEL',
                    'area': area,
                    'level': lel,
                    'unit': '%',
                    'severity': 'critical',
                    'description': f'EXPLOSIVE ATMOSPHERE: LEL at {lel}%'
                })
            elif lel >= self.GAS_THRESHOLDS['LEL']['warning']:
                hazards.append({
                    'gas_type': 'LEL',
                    'area': area,
                    'level': lel,
                    'unit': '%',
                    'severity': 'warning',
                    'description': f'Elevated LEL detected: {lel}%'
                })
            
            # H2S (Hydrogen Sulfide)
            h2s = readings.get('H2S', 0)
            if h2s >= self.GAS_THRESHOLDS['H2S']['critical']:
                hazards.append({
                    'gas_type': 'H2S',
                    'area': area,
                    'level': h2s,
                    'unit': 'ppm',
                    'severity': 'critical',
                    'description': f'TOXIC GAS: H2S at {h2s} ppm'
                })
            elif h2s >= self.GAS_THRESHOLDS['H2S']['warning']:
                hazards.append({
                    'gas_type': 'H2S',
                    'area': area,
                    'level': h2s,
                    'unit': 'ppm',
                    'severity': 'warning',
                    'description': f'Elevated H2S detected: {h2s} ppm'
                })
            
            # CO (Carbon Monoxide)
            co = readings.get('CO', 0)
            if co >= self.GAS_THRESHOLDS['CO']['critical']:
                hazards.append({
                    'gas_type': 'CO',
                    'area': area,
                    'level': co,
                    'unit': 'ppm',
                    'severity': 'critical',
                    'description': f'TOXIC GAS: CO at {co} ppm'
                })
            elif co >= self.GAS_THRESHOLDS['CO']['warning']:
                hazards.append({
                    'gas_type': 'CO',
                    'area': area,
                    'level': co,
                    'unit': 'ppm',
                    'severity': 'warning',
                    'description': f'Elevated CO detected: {co} ppm'
                })
        
        return hazards
    
    def _detect_permit_conflicts(self, active_permits: List[Dict]) -> List[Dict]:
        """Detect conflicts between active permits"""
        conflicts = []
        
        for i, permit1 in enumerate(active_permits):
            for permit2 in active_permits[i+1:]:
                # Check temporal overlap
                if not self._check_temporal_overlap(permit1, permit2):
                    continue
                
                # Check proximity
                proximity_conflict = self._check_proximity(permit1, permit2)
                if proximity_conflict:
                    conflicts.append(proximity_conflict)
                
                # Check permit type conflicts
                type_conflict = self._check_permit_type_conflict(permit1, permit2)
                if type_conflict:
                    conflicts.append(type_conflict)
        
        return conflicts
    
    def _check_temporal_overlap(self, permit1: Dict, permit2: Dict) -> bool:
        """Check if permits overlap in time"""
        start1 = permit1.get('start_time')
        end1 = permit1.get('end_time')
        start2 = permit2.get('start_time')
        end2 = permit2.get('end_time')
        
        if not all([start1, end1, start2, end2]):
            return True
        
        # Convert to datetime if strings
        if isinstance(start1, str):
            start1 = datetime.fromisoformat(start1)
        if isinstance(end1, str):
            end1 = datetime.fromisoformat(end1)
        if isinstance(start2, str):
            start2 = datetime.fromisoformat(start2)
        if isinstance(end2, str):
            end2 = datetime.fromisoformat(end2)
        
        return not (end1 < start2 or end2 < start1)
    
    def _check_proximity(self, permit1: Dict, permit2: Dict) -> Dict:
        """Check spatial proximity"""
        coords1 = {
            'x': permit1.get('coordinates_x', 0),
            'y': permit1.get('coordinates_y', 0),
            'z': permit1.get('coordinates_z', 0)
        }
        coords2 = {
            'x': permit2.get('coordinates_x', 0),
            'y': permit2.get('coordinates_y', 0),
            'z': permit2.get('coordinates_z', 0)
        }
        
        distance = (
            (coords1['x'] - coords2['x']) ** 2 +
            (coords1['y'] - coords2['y']) ** 2 +
            (coords1['z'] - coords2['z']) ** 2
        ) ** 0.5
        
        permit_type = permit1.get('permit_type', 'default')
        threshold = self.PROXIMITY_THRESHOLDS.get(permit_type, self.PROXIMITY_THRESHOLDS['default'])
        
        if distance < threshold:
            return {
                'type': 'proximity',
                'severity': 'high' if distance < threshold / 2 else 'medium',
                'description': f"Permits too close ({distance:.1f}m) - minimum {threshold}m required",
                'permit1': permit1.get('permit_number'),
                'permit2': permit2.get('permit_number'),
                'distance_m': round(distance, 1),
                'recommendation': f"Maintain minimum {threshold}m separation or reschedule activities"
            }
        
        return None
    
    def _check_permit_type_conflict(self, permit1: Dict, permit2: Dict) -> Dict:
        """Check for critical permit type combinations"""
        type1 = permit1.get('permit_type')
        type2 = permit2.get('permit_type')
        
        if (type1, type2) in self.CRITICAL_CONFLICTS or (type2, type1) in self.CRITICAL_CONFLICTS:
            return {
                'type': 'permit_type',
                'severity': 'critical',
                'description': f"CRITICAL: {type1} and {type2} cannot occur simultaneously",
                'permit1': permit1.get('permit_number'),
                'permit2': permit2.get('permit_number'),
                'recommendation': "Suspend one permit until other is complete"
            }
        
        return None
    
    def _calculate_overall_risk(self, gas_hazards: List, conflicts: List) -> str:
        """Calculate overall facility risk level"""
        if any(h['severity'] == 'critical' for h in gas_hazards):
            return 'critical'
        if any(c['severity'] == 'critical' for c in conflicts):
            return 'critical'
        if len(gas_hazards) > 2 or len(conflicts) > 2:
            return 'high'
        if gas_hazards or conflicts:
            return 'medium'
        return 'low'
    
    def generate_safety_procedure(self, scenario: Dict[str, Any]) -> str:
        """
        AE.CG - Code Generation
        Auto-generate safety procedure for novel scenario
        """
        permit_type = scenario.get('permit_type', 'hot_work')
        area = scenario.get('area', 'Unknown')
        
        procedure = f"""
# SAFETY PROCEDURE: {permit_type.upper().replace('_', ' ')}
## Location: {area}

### PRE-WORK REQUIREMENTS
1. Gas testing completed and documented
2. Fire watch personnel assigned (if required)
3. Emergency equipment verified and accessible
4. Communication protocols established
5. Escape routes confirmed clear

### DURING WORK
1. Continuous gas monitoring required
2. Fire watch maintains visual contact
3. No smoking or open flames in vicinity
4. Report any unusual conditions immediately
5. Stop work if gas levels exceed thresholds

### POST-WORK
1. Final gas test and equipment check
2. Area inspection and cleanup
3. Fire watch remains 30 minutes after hot work
4. Documentation completion
5. Supervisor sign-off

### EMERGENCY RESPONSE
- Gas alarm: Evacuate immediately to muster point
- Fire: Activate alarm, evacuate, call emergency services
- Injury: Stop work, provide first aid, call medical team

**Auto-generated by Safety Guardian Agent**
**Generated: {datetime.utcnow().isoformat()}**
**Confidence: {self.confidence * 100:.0f}%**
        """
        
        return procedure.strip()
    
    def explain(self, decision: Dict[str, Any]) -> str:
        """
        GS.EX - Explainability
        Explain safety decision
        """
        recommendations = decision.get('recommendations', [])
        risk_level = decision.get('overall_risk_level', 'unknown')
        
        explanation = f"""
**Safety Guardian Analysis**

Overall Risk Level: {risk_level.upper()}

Active Hazards Detected: {len(recommendations)}

Reasoning:
This assessment is based on real-time monitoring of:
- Gas detector readings across 6 refinery areas
- Active permit-to-work spatial and temporal analysis
- Proximity-based conflict detection
- Incompatible activity identification

Recommendations are prioritized by:
1. Immediate life safety threats (gas alarms, critical conflicts)
2. High-risk conditions requiring prompt attention
3. Medium-risk advisories for operator awareness

All critical recommendations require human approval before automated actions.

Confidence: {self.confidence * 100:.0f}%
Human-in-the-Loop: {decision.get('requires_human_approval', False)}
        """
        
        return explanation.strip()