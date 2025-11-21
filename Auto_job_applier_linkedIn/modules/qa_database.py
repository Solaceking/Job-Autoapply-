"""
Q&A Learning Database Module

Stores question-answer pairs in SQLite for learning and reuse.
Uses fuzzy matching to find similar questions.
"""

import sqlite3
import hashlib
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path

LogCallback = Optional[Callable[[str, str], None]]


class QADatabase:
    """SQLite database for storing and retrieving question-answer pairs."""
    
    def __init__(self, db_path: str = "data/questions.db", log_cb: LogCallback = None):
        """
        Initialize Q&A Database.
        
        Args:
            db_path: Path to SQLite database file
            log_cb: Optional logging callback
        """
        self.db_path = db_path
        self.log = log_cb or (lambda level, msg: None)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Create database tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create question_bank table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS question_bank (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    question_normalized TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    job_title TEXT,
                    company TEXT,
                    job_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    times_used INTEGER DEFAULT 1,
                    success_count INTEGER DEFAULT 0,
                    similarity_hash TEXT,
                    UNIQUE(question_normalized)
                )
            ''')
            
            # Create index for faster lookups
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_question_norm 
                ON question_bank(question_normalized)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_similarity_hash 
                ON question_bank(similarity_hash)
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.log('error', f'Failed to initialize Q&A database: {e}')
    
    def _normalize_question(self, question: str) -> str:
        """Normalize question for matching."""
        import re
        # Remove extra whitespace, lowercase
        normalized = re.sub(r'\s+', ' ', question.strip().lower())
        # Remove punctuation
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized
    
    def _calculate_similarity_hash(self, question: str) -> str:
        """Calculate a hash for similarity grouping."""
        # Use first 3-4 significant words
        words = self._normalize_question(question).split()
        significant_words = [w for w in words if len(w) > 3][:4]
        hash_input = ' '.join(sorted(significant_words))
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def _fuzzy_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts (0.0 to 1.0).
        Uses simple word-based Jaccard similarity.
        """
        words1 = set(self._normalize_question(text1).split())
        words2 = set(self._normalize_question(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    def find_similar_question(self, question: str, threshold: float = 0.8) -> Optional[Dict[str, Any]]:
        """
        Find a similar question in the database.
        
        Args:
            question: Question text to search for
            threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            Dict with question data if found, None otherwise
        """
        try:
            normalized = self._normalize_question(question)
            similarity_hash = self._calculate_similarity_hash(question)
            
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # First try exact match
            cursor.execute('''
                SELECT * FROM question_bank 
                WHERE question_normalized = ?
                ORDER BY times_used DESC, last_used DESC
                LIMIT 1
            ''', (normalized,))
            
            row = cursor.fetchone()
            if row:
                conn.close()
                return dict(row)
            
            # Try similarity hash match
            cursor.execute('''
                SELECT * FROM question_bank 
                WHERE similarity_hash = ?
                ORDER BY times_used DESC, last_used DESC
                LIMIT 5
            ''', (similarity_hash,))
            
            candidates = cursor.fetchall()
            conn.close()
            
            # Calculate similarity for each candidate
            best_match = None
            best_score = 0.0
            
            for candidate in candidates:
                score = self._fuzzy_similarity(question, candidate['question'])
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = dict(candidate)
            
            return best_match
            
        except Exception as e:
            self.log('error', f'Error finding similar question: {e}')
            return None
    
    def store_question(self, question: str, answer: str, job_title: str = '', 
                      company: str = '', job_context: str = '') -> bool:
        """
        Store a question-answer pair in the database.
        
        Args:
            question: Question text
            answer: Answer text
            job_title: Optional job title
            company: Optional company name
            job_context: Optional job context
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            normalized = self._normalize_question(question)
            similarity_hash = self._calculate_similarity_hash(question)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Try to insert, or update if exists
            cursor.execute('''
                INSERT INTO question_bank 
                (question, question_normalized, answer, job_title, company, 
                 job_context, similarity_hash, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(question_normalized) DO UPDATE SET
                    answer = excluded.answer,
                    job_title = excluded.job_title,
                    company = excluded.company,
                    job_context = excluded.job_context,
                    times_used = times_used + 1,
                    last_used = excluded.last_used
            ''', (question, normalized, answer, job_title, company, 
                  job_context, similarity_hash, datetime.now()))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.log('error', f'Error storing question: {e}')
            return False
    
    def update_usage(self, question_id: int):
        """Update usage statistics for a question."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE question_bank 
                SET times_used = times_used + 1,
                    last_used = ?
                WHERE id = ?
            ''', (datetime.now(), question_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.log('error', f'Error updating usage: {e}')
    
    def get_all_questions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all questions from database, ordered by usage."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM question_bank 
                ORDER BY times_used DESC, last_used DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            self.log('error', f'Error getting questions: {e}')
            return []
    
    def export_to_csv(self, output_path: str) -> bool:
        """Export Q&A database to CSV file."""
        try:
            import csv
            
            questions = self.get_all_questions(limit=10000)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if not questions:
                    return False
                
                writer = csv.DictWriter(f, fieldnames=questions[0].keys())
                writer.writeheader()
                writer.writerows(questions)
            
            self.log('success', f'Exported {len(questions)} questions to {output_path}')
            return True
            
        except Exception as e:
            self.log('error', f'Error exporting to CSV: {e}')
            return False
