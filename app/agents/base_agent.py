"""
Base Agent Interface
Abstract class defining the standard agent interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all AI agents
    Implements Agentic Canvas framework capabilities
    """
    
    def __init__(self, agent_id: str, agent_type: str, capabilities: List[str] = None):
        """
        Initialize base agent
        
        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (T1, T2, T3, T4)
            capabilities: List of AIA CPT capabilities (PK.*, CG.*, etc.)
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.capabilities = capabilities or []
        self.state = "idle"  # idle, active, error, learning
        self.confidence = 0.0
        self.created_at = datetime.utcnow()
        self.last_action_at = None
        
        logger.info(f"Agent initialized: {self.agent_id} ({self.agent_type})")
    
    # PK: Perception & Knowledge
    @abstractmethod
    def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        PK.OB - Environmental Sensing
        Perceive and process environmental data
        
        Args:
            environment: Current environment state
            
        Returns:
            Processed perception data
        """
        pass
    
    # CG: Cognition & Reasoning
    @abstractmethod
    def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        CG.RS - Reasoning
        CG.DC - Decision Making
        Make decisions based on perception
        
        Args:
            perception: Processed perception data
            
        Returns:
            Decision data
        """
        pass
    
    # AE: Action & Execution
    @abstractmethod
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        AE.TX - Task Execution
        Execute decided actions
        
        Args:
            decision: Decision to execute
            
        Returns:
            Action results
        """
        pass
    
    # IC: Interaction & Collaboration
    def communicate(self, message: Dict[str, Any], target_agent: str = None) -> Dict[str, Any]:
        """
        IC.AC - Agent Communication
        Send message to other agents
        
        Args:
            message: Message content
            target_agent: Target agent ID (None for broadcast)
            
        Returns:
            Communication result
        """
        return {
            'from': self.agent_id,
            'to': target_agent or 'broadcast',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    # LA: Learning & Adaptation
    def learn(self, experience: Dict[str, Any]) -> None:
        """
        LA.SL - Supervised Learning
        Learn from experience
        
        Args:
            experience: Experience data for learning
        """
        # Base implementation - can be overridden
        logger.info(f"Agent {self.agent_id} learning from experience")
    
    # GS: Governance & Safety
    def explain(self, decision: Dict[str, Any]) -> str:
        """
        GS.EX - Explainability
        Explain reasoning behind decision
        
        Args:
            decision: Decision to explain
            
        Returns:
            Human-readable explanation
        """
        return f"Agent {self.agent_id} made decision based on standard reasoning protocols"
    
    # Full agent loop
    def run_cycle(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run complete perception-reasoning-action cycle
        
        Args:
            environment: Current environment state
            
        Returns:
            Cycle results
        """
        try:
            self.state = "active"
            
            # Perceive
            perception = self.perceive(environment)
            
            # Reason
            decision = self.reason(perception)
            
            # Act
            result = self.act(decision)
            
            self.last_action_at = datetime.utcnow()
            self.state = "idle"
            
            return {
                'success': True,
                'perception': perception,
                'decision': decision,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.state = "error"
            logger.error(f"Agent {self.agent_id} error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'capabilities': self.capabilities,
            'state': self.state,
            'confidence': self.confidence,
            'last_action_at': self.last_action_at.isoformat() if self.last_action_at else None
        }