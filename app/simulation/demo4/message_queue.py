"""
Message Queue - Inter-agent communication for EV charging network
"""
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class Message:
    """Message for inter-agent communication"""
    
    def __init__(
        self,
        topic: str,
        payload: Dict[str, Any],
        sender: str,
        correlation_id: Optional[str] = None,
        priority: int = 5
    ):
        self.topic = topic
        self.payload = payload
        self.sender = sender
        self.correlation_id = correlation_id
        self.priority = priority
        self.timestamp = datetime.utcnow()
        self.message_id = f"{sender}-{datetime.utcnow().timestamp()}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'topic': self.topic,
            'payload': self.payload,
            'sender': self.sender,
            'correlation_id': self.correlation_id,
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat()
        }


class MessageQueue:
    """Message queue for asynchronous agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.message_history: List[Message] = []
        self.pending_messages: List[Message] = []
    
    def publish(
        self,
        topic: str,
        payload: Dict[str, Any],
        sender: str = "system",
        correlation_id: Optional[str] = None,
        priority: int = 5
    ):
        """Publish a message to a topic"""
        message = Message(
            topic=topic,
            payload=payload,
            sender=sender,
            correlation_id=correlation_id,
            priority=priority
        )
        
        self.message_history.append(message)
        
        # Notify subscribers
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in subscriber callback: {e}")
        
        # Notify wildcard subscribers
        if '*' in self.subscribers:
            for callback in self.subscribers['*']:
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in wildcard subscriber: {e}")
        
        logger.debug(f"Published message on topic '{topic}' from {sender}")
    
    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to a topic"""
        self.subscribers[topic].append(callback)
        logger.debug(f"New subscriber to topic '{topic}'")
    
    def unsubscribe(self, topic: str, callback: Callable):
        """Unsubscribe from a topic"""
        if topic in self.subscribers and callback in self.subscribers[topic]:
            self.subscribers[topic].remove(callback)
            logger.debug(f"Unsubscribed from topic '{topic}'")
    
    def get_messages_by_correlation(self, correlation_id: str) -> List[Message]:
        """Get all messages for a correlation ID"""
        return [m for m in self.message_history if m.correlation_id == correlation_id]
    
    def get_recent_messages(self, limit: int = 50) -> List[Message]:
        """Get recent messages"""
        return self.message_history[-limit:]
    
    def clear_history(self):
        """Clear message history"""
        self.message_history.clear()
        self.pending_messages.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get message queue statistics"""
        return {
            'total_messages': len(self.message_history),
            'topics': len(self.subscribers),
            'subscribers': sum(len(subs) for subs in self.subscribers.values()),
            'pending_messages': len(self.pending_messages)
        }


# Global message queue instance
message_queue = MessageQueue()
