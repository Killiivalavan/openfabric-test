import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union


class MemoryManager:
    """
    Manages both short-term (session) and long-term (persistent) memory storage
    for creative generations in the application.
    
    This class handles:
    - Short-term memory during a session
    - Long-term memory using SQLite database
    - Querying and retrieving past creations
    """
    
    def __init__(self, db_path: str = "datastore/memory.db"):
        """
        Initialize the memory manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.session_memory = {}  # In-memory storage for current session
        
        # Ensure datastore directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Initialize database
        self._init_db()
        
    def _init_db(self):
        """Initialize the SQLite database with required tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Creations table - stores all generated content
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS creations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_prompt TEXT NOT NULL,
                enhanced_prompt TEXT NOT NULL,
                image_path TEXT,
                model_path TEXT,
                metadata TEXT,
                tags TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
            logging.info(f"Memory database initialized at {self.db_path}")
        except Exception as e:
            logging.error(f"Error initializing memory database: {str(e)}")
    
    def store_creation(self, 
                       user_prompt: str, 
                       enhanced_prompt: str, 
                       image_path: Optional[str] = None,
                       model_path: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       tags: Optional[List[str]] = None) -> int:
        """
        Store a creation in both short-term and long-term memory.
        
        Args:
            user_prompt: Original user prompt
            enhanced_prompt: Enhanced prompt used for generation
            image_path: Path to the generated image
            model_path: Path to the generated 3D model
            metadata: Additional metadata about the creation
            tags: List of tags for searching
            
        Returns:
            int: ID of the stored creation
        """
        # Format timestamp
        timestamp = datetime.now().isoformat()
        
        # Prepare data for storage
        creation_data = {
            "timestamp": timestamp,
            "user_prompt": user_prompt,
            "enhanced_prompt": enhanced_prompt,
            "image_path": image_path,
            "model_path": model_path,
            "metadata": json.dumps(metadata) if metadata else None,
            "tags": json.dumps(tags) if tags else None
        }
        
        # Store in session memory
        session_id = str(int(time.time()))
        self.session_memory[session_id] = creation_data
        
        try:
            # Store in long-term memory (SQLite)
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO creations 
            (timestamp, user_prompt, enhanced_prompt, image_path, model_path, metadata, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                user_prompt,
                enhanced_prompt,
                image_path,
                model_path,
                creation_data["metadata"],
                creation_data["tags"]
            ))
            
            creation_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logging.info(f"Creation stored with ID: {creation_id}")
            return creation_id
            
        except Exception as e:
            logging.error(f"Error storing creation in long-term memory: {str(e)}")
            return -1
    
    def get_creation_by_id(self, creation_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a creation by its ID from long-term memory.
        
        Args:
            creation_id: The ID of the creation to retrieve
            
        Returns:
            Dict containing the creation data, or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM creations WHERE id = ?
            ''', (creation_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                column_names = [description[0] for description in cursor.description]
                creation = dict(zip(column_names, row))
                
                # Parse JSON fields
                if creation["metadata"]:
                    creation["metadata"] = json.loads(creation["metadata"])
                if creation["tags"]:
                    creation["tags"] = json.loads(creation["tags"])
                    
                return creation
            return None
            
        except Exception as e:
            logging.error(f"Error retrieving creation {creation_id}: {str(e)}")
            return None
    
    def search_creations(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for creations by keyword in prompts or tags.
        
        Args:
            query: Search term
            limit: Maximum number of results to return
            
        Returns:
            List of matching creation dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return results as dictionaries
            cursor = conn.cursor()
            
            # Search in user_prompt, enhanced_prompt, and tags
            cursor.execute('''
            SELECT * FROM creations 
            WHERE user_prompt LIKE ? OR enhanced_prompt LIKE ? OR tags LIKE ?
            ORDER BY timestamp DESC LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
            
            results = cursor.fetchall()
            conn.close()
            
            # Convert Row objects to dictionaries and parse JSON fields
            creations = []
            for row in results:
                creation = dict(row)
                if creation["metadata"]:
                    creation["metadata"] = json.loads(creation["metadata"])
                if creation["tags"]:
                    creation["tags"] = json.loads(creation["tags"])
                creations.append(creation)
                
            return creations
            
        except Exception as e:
            logging.error(f"Error searching creations: {str(e)}")
            return []
    
    def get_recent_creations(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most recent creations.
        
        Args:
            limit: Maximum number of results to return
            
        Returns:
            List of recent creation dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
            SELECT * FROM creations ORDER BY timestamp DESC LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            # Convert Row objects to dictionaries and parse JSON fields
            creations = []
            for row in results:
                creation = dict(row)
                if creation["metadata"]:
                    creation["metadata"] = json.loads(creation["metadata"])
                if creation["tags"]:
                    creation["tags"] = json.loads(creation["tags"])
                creations.append(creation)
                
            return creations
            
        except Exception as e:
            logging.error(f"Error retrieving recent creations: {str(e)}")
            return []
    
    def get_memory_context(self, query: Optional[str] = None, limit: int = 3) -> str:
        """
        Get a formatted context string from memory to use in prompt enhancement.
        
        Args:
            query: Optional search term to find relevant past creations
            limit: Maximum number of past creations to include
            
        Returns:
            String containing formatted context from memory
        """
        creations = []
        
        if query:
            creations = self.search_creations(query, limit)
        else:
            creations = self.get_recent_creations(limit)
            
        if not creations:
            return ""
            
        context_parts = []
        for creation in creations:
            context_parts.append(f"Previous creation: '{creation['user_prompt']}' - Enhanced as: '{creation['enhanced_prompt']}'")
            
        return "\n".join(context_parts) 