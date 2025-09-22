import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

class ChatPersistence:
    """Handles saving and loading of chat conversations with SQLite backend"""
    
    def __init__(self, db_path: str = "data/chat_history.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._ensure_data_directory()
        self._initialize_database()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _initialize_database(self):
        """Initialize the SQLite database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create conversations table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT UNIQUE NOT NULL,
                        title TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        message_count INTEGER DEFAULT 0,
                        model_used TEXT
                    )
                """)
                
                # Create messages table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        conversation_id TEXT NOT NULL,
                        message_id TEXT,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id)
                    )
                """)
                
                # Create indexes for better performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
                    ON messages(conversation_id)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_conversations_created_at 
                    ON conversations(created_at)
                """)
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise
    
    def save_conversation(self, conversation_id: str, messages: List[Dict], 
                         model_used: str = None) -> bool:
        """
        Save a complete conversation to the database
        
        Args:
            conversation_id: Unique identifier for the conversation
            messages: List of message dictionaries
            model_used: AI model used for the conversation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Generate conversation title from first user message
                title = self._generate_conversation_title(messages)
                
                # Insert or update conversation record
                cursor.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (conversation_id, title, updated_at, message_count, model_used)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    title,
                    datetime.now().isoformat(),
                    len(messages),
                    model_used
                ))
                
                # Clear existing messages for this conversation
                cursor.execute("""
                    DELETE FROM messages WHERE conversation_id = ?
                """, (conversation_id,))
                
                # Insert all messages
                for msg in messages:
                    cursor.execute("""
                        INSERT INTO messages 
                        (conversation_id, message_id, role, content, timestamp)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        conversation_id,
                        msg.get("message_id", ""),
                        msg["role"],
                        msg["content"],
                        msg.get("timestamp", "")
                    ))
                
                conn.commit()
                self.logger.info(f"Conversation {conversation_id} saved successfully")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[List[Dict]]:
        """
        Load a conversation from the database
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message dictionaries or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT message_id, role, content, timestamp
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY id ASC
                """, (conversation_id,))
                
                rows = cursor.fetchall()
                
                if not rows:
                    self.logger.warning(f"No messages found for conversation {conversation_id}")
                    return None
                
                messages = []
                for row in rows:
                    messages.append({
                        "message_id": row[0],
                        "role": row[1],
                        "content": row[2],
                        "timestamp": row[3]
                    })
                
                self.logger.info(f"Loaded {len(messages)} messages for conversation {conversation_id}")
                return messages
                
        except sqlite3.Error as e:
            self.logger.error(f"Error loading conversation: {e}")
            return None
    
    def get_conversation_list(self, limit: int = 50) -> List[str]:
        """
        Get a list of available conversation IDs
        
        Args:
            limit: Maximum number of conversations to return
            
        Returns:
            List of conversation IDs sorted by most recent
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT conversation_id, title, updated_at, message_count
                    FROM conversations
                    ORDER BY updated_at DESC
                    LIMIT ?
                """, (limit,))
                
                rows = cursor.fetchall()
                
                # Return formatted conversation list
                conversations = []
                for row in rows:
                    conv_id, title, updated_at, msg_count = row
                    # Format: "Title (10 messages) - 2024-01-15"
                    date_str = updated_at.split('T')[0] if 'T' in updated_at else updated_at[:10]
                    formatted = f"{title} ({msg_count} messages) - {date_str}"
                    conversations.append(conv_id)
                
                return conversations
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting conversation list: {e}")
            return []
    
    def get_conversation_info(self, conversation_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific conversation
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary with conversation metadata or None if not found
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT conversation_id, title, created_at, updated_at, 
                           message_count, model_used
                    FROM conversations
                    WHERE conversation_id = ?
                """, (conversation_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                return {
                    "conversation_id": row[0],
                    "title": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                    "message_count": row[4],
                    "model_used": row[5]
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting conversation info: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete messages first (foreign key constraint)
                cursor.execute("""
                    DELETE FROM messages WHERE conversation_id = ?
                """, (conversation_id,))
                
                # Delete conversation
                cursor.execute("""
                    DELETE FROM conversations WHERE conversation_id = ?
                """, (conversation_id,))
                
                conn.commit()
                self.logger.info(f"Conversation {conversation_id} deleted successfully")
                return True
                
        except sqlite3.Error as e:
            self.logger.error(f"Error deleting conversation: {e}")
            return False
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search conversations by content
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching conversation dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT DISTINCT c.conversation_id, c.title, c.updated_at, 
                           c.message_count, m.content
                    FROM conversations c
                    JOIN messages m ON c.conversation_id = m.conversation_id
                    WHERE m.content LIKE ?
                    ORDER BY c.updated_at DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
                
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append({
                        "conversation_id": row[0],
                        "title": row[1],
                        "updated_at": row[2],
                        "message_count": row[3],
                        "preview": row[4][:100] + "..." if len(row[4]) > 100 else row[4]
                    })
                
                return results
                
        except sqlite3.Error as e:
            self.logger.error(f"Error searching conversations: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics
        
        Returns:
            Dictionary with various statistics
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total conversations
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total_conversations = cursor.fetchone()[0]
                
                # Total messages
                cursor.execute("SELECT COUNT(*) FROM messages")
                total_messages = cursor.fetchone()[0]
                
                # Average messages per conversation
                avg_messages = total_messages / max(total_conversations, 1)
                
                # Most active day
                cursor.execute("""
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM conversations
                    GROUP BY DATE(created_at)
                    ORDER BY count DESC
                    LIMIT 1
                """)
                most_active_day = cursor.fetchone()
                
                # Model usage
                cursor.execute("""
                    SELECT model_used, COUNT(*) as count
                    FROM conversations
                    WHERE model_used IS NOT NULL
                    GROUP BY model_used
                    ORDER BY count DESC
                """)
                model_usage = dict(cursor.fetchall())
                
                return {
                    "total_conversations": total_conversations,
                    "total_messages": total_messages,
                    "avg_messages_per_conversation": round(avg_messages, 2),
                    "most_active_day": most_active_day,
                    "model_usage": model_usage
                }
                
        except sqlite3.Error as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}
    
    def _generate_conversation_title(self, messages: List[Dict]) -> str:
        """
        Generate a descriptive title for the conversation
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Generated title string
        """
        # Find first user message
        first_user_msg = None
        for msg in messages:
            if msg["role"] == "user":
                first_user_msg = msg["content"]
                break
        
        if not first_user_msg:
            return f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        # Create title from first user message (limit to 50 chars)
        title = first_user_msg.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        
        return title
    
    def cleanup_old_conversations(self, days_old: int = 30) -> int:
        """
        Delete conversations older than specified days
        
        Args:
            days_old: Number of days to keep conversations
            
        Returns:
            Number of conversations deleted
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Find old conversations
                cursor.execute("""
                    SELECT conversation_id FROM conversations
                    WHERE created_at < datetime('now', '-{} days')
                """.format(days_old))
                
                old_conversations = cursor.fetchall()
                
                # Delete old conversations
                for (conv_id,) in old_conversations:
                    self.delete_conversation(conv_id)
                
                self.logger.info(f"Cleaned up {len(old_conversations)} old conversations")
                return len(old_conversations)
                
        except sqlite3.Error as e:
            self.logger.error(f"Error cleaning up old conversations: {e}")
            return 0
    
    def export_conversation_to_json(self, conversation_id: str) -> Optional[str]:
        """
        Export a conversation to JSON format
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            JSON string or None if error
        """
        try:
            messages = self.load_conversation(conversation_id)
            info = self.get_conversation_info(conversation_id)
            
            if not messages or not info:
                return None
            
            export_data = {
                "conversation_info": info,
                "messages": messages,
                "exported_at": datetime.now().isoformat()
            }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
            
        except Exception as e:
            self.logger.error(f"Error exporting conversation to JSON: {e}")
            return None