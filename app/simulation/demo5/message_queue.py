"""
In-Memory Message Queue for Event-Driven Communication
Demo version of pub/sub messaging system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from uuid import uuid4
from collections import defaultdict
from queue import Queue
import threading
import time


@dataclass
class Message:
    """
    A message represents a unit of communication between systems. Each message
    has a destination (topic), a payload (the actual data), and metadata for
    tracking and debugging.
    """
    message_id: str = field(default_factory=lambda: str(uuid4()))
    topic: str = ""  # Where this message is being sent
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # For tracking related messages
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    
    # Processing metadata
    retry_count: int = 0
    max_retries: int = 3
    processed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization"""
        return {
            'message_id': self.message_id,
            'topic': self.topic,
            'payload': self.payload,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'retry_count': self.retry_count,
            'processed': self.processed
        }


class InMemoryMessageQueue:
    """
    An in-memory message queue that mimics the behavior of enterprise message
    brokers like Kafka or RabbitMQ. Messages are organized into topics, and
    consumers can subscribe to specific topics they care about.
    
    This is like having multiple post office boxes. When you subscribe to a topic,
    you're saying "I want to receive all mail sent to this mailbox." The queue
    handles delivering messages to all interested subscribers.
    
    In production, you'd replace this with actual Kafka or RabbitMQ, but the
    code using the queue would barely change - that's the power of good abstraction!
    """
    
    def __init__(self):
        # Storage for messages by topic
        # Each topic has its own queue of messages waiting to be processed
        self.topics: Dict[str, Queue] = defaultdict(Queue)
        
        # Subscribers are callback functions that get called when messages arrive
        # Multiple systems can subscribe to the same topic
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Message history for debugging and replay
        self.message_history: List[Message] = []
        
        # Worker threads that process messages in the background
        self.workers: Dict[str, threading.Thread] = {}
        self.running = False
        
        # Statistics for monitoring
        self.stats = {
            'messages_published': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'active_topics': set()
        }
    
    def publish(self, topic: str, payload: Dict[str, Any], correlation_id: Optional[str] = None) -> str:
        """
        Publish a message to a topic. This is like dropping a letter in a mailbox.
        All subscribers to this topic will receive the message.
        
        Returns the message ID for tracking
        """
        message = Message(
            topic=topic,
            payload=payload,
            correlation_id=correlation_id
        )
        
        # Add to topic queue
        self.topics[topic].put(message)
        
        # Add to history
        self.message_history.append(message)
        
        # Update statistics
        self.stats['messages_published'] += 1
        self.stats['active_topics'].add(topic)
        
        # Immediately notify subscribers (in real systems, this happens async)
        self._notify_subscribers(topic, message)
        
        return message.message_id
    
    def subscribe(self, topic: str, callback: Callable[[Message], None]):
        """
        Subscribe to a topic. Your callback function will be called whenever
        a message is published to this topic.
        
        This is like telling the post office "call me whenever mail arrives
        for this address." The callback is your phone number.
        """
        self.subscribers[topic].append(callback)
        
        # If we have a worker thread for this topic, make sure it's running
        if topic not in self.workers and self.running:
            self._start_worker(topic)
    
    def _notify_subscribers(self, topic: str, message: Message):
        """
        Notify all subscribers that a new message has arrived. This happens
        immediately in our demo, but in production it might be async.
        """
        if topic in self.subscribers:
            for callback in self.subscribers[topic]:
                try:
                    # Call the subscriber's callback function
                    callback(message)
                except Exception as e:
                    print(f"Error notifying subscriber for topic {topic}: {e}")
                    self.stats['messages_failed'] += 1
    
    def _start_worker(self, topic: str):
        """
        Start a background worker thread to process messages for a topic.
        In production, these would be separate processes or containers.
        """
        def worker():
            while self.running:
                try:
                    # Get a message from the queue (wait up to 1 second)
                    message = self.topics[topic].get(timeout=1.0)
                    
                    # Process it
                    self._notify_subscribers(topic, message)
                    message.processed = True
                    self.stats['messages_processed'] += 1
                    
                except Exception:
                    # Timeout or error - just continue
                    pass
        
        # Start the worker thread
        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        self.workers[topic] = thread
    
    def start(self):
        """Start all worker threads for message processing"""
        self.running = True
        for topic in self.subscribers.keys():
            if topic not in self.workers:
                self._start_worker(topic)
    
    def stop(self):
        """Stop all worker threads gracefully"""
        self.running = False
        # Wait for workers to finish
        for worker in self.workers.values():
            worker.join(timeout=2.0)
        self.workers.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about message queue performance"""
        return {
            'messages_published': self.stats['messages_published'],
            'messages_processed': self.stats['messages_processed'],
            'messages_failed': self.stats['messages_failed'],
            'active_topics': len(self.stats['active_topics']),
            'pending_messages': sum(q.qsize() for q in self.topics.values()),
            'active_subscribers': sum(len(subs) for subs in self.subscribers.values())
        }
    
    def get_recent_messages(self, topic: Optional[str] = None, limit: int = 50) -> List[Message]:
        """
        Get recent messages for monitoring and debugging. If topic is specified,
        only return messages for that topic.
        """
        messages = self.message_history
        
        if topic:
            messages = [m for m in messages if m.topic == topic]
        
        return messages[-limit:]
    
    def clear_history(self):
        """Clear message history (useful for demo resets)"""
        self.message_history.clear()
        self.stats['messages_published'] = 0
        self.stats['messages_processed'] = 0
        self.stats['messages_failed'] = 0


# Create a global singleton instance
message_queue = InMemoryMessageQueue()
