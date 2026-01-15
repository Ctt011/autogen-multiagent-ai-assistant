"""
Conversation memory management for the AI Assistant.

Provides persistent storage and retrieval of conversation history using SQLite.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from contextlib import contextmanager

from .logger import logger


class ConversationMemory:
    """Manages conversation history with persistent SQLite storage."""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize conversation memory.

        Args:
            db_path: Path to SQLite database file. Defaults to data/conversations.db
        """
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "conversations.db"
        else:
            db_path = Path(db_path)

        # Create data directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.db_path = str(db_path)
        self._initialize_database()
        logger.info(f"Conversation memory initialized at {self.db_path}")

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    agent_name TEXT
                )
            """)

            # Create index for faster session queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_timestamp
                ON conversations(session_id, timestamp)
            """)

            logger.info("Database initialized successfully")

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        agent_name: Optional[str] = None,
    ):
        """
        Save a message to conversation history.

        Args:
            session_id: Unique identifier for the conversation session
            role: Message role ('user' or 'assistant')
            content: Message content
            agent_name: Name of the agent that generated the message (for assistant)
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO conversations (session_id, timestamp, role, content, agent_name)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        datetime.now().isoformat(),
                        role,
                        content,
                        agent_name,
                    ),
                )
                logger.debug(f"Saved {role} message to session {session_id}")

        except Exception as e:
            logger.error(f"Failed to save message: {e}")

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Retrieve conversation history for a session.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve (most recent first)

        Returns:
            List of message dictionaries with keys: timestamp, role, content, agent_name
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                query = """
                    SELECT timestamp, role, content, agent_name
                    FROM conversations
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                """

                if limit:
                    query += f" LIMIT {limit}"

                cursor.execute(query, (session_id,))
                rows = cursor.fetchall()

                # Convert to list of dicts and reverse (to get chronological order)
                messages = [
                    {
                        "timestamp": row["timestamp"],
                        "role": row["role"],
                        "content": row["content"],
                        "agent_name": row["agent_name"],
                    }
                    for row in rows
                ]
                messages.reverse()

                logger.debug(f"Retrieved {len(messages)} messages from session {session_id}")
                return messages

        except Exception as e:
            logger.error(f"Failed to retrieve session history: {e}")
            return []

    def get_recent_sessions(self, days: int = 7) -> List[Dict[str, str]]:
        """
        Get list of recent conversation sessions.

        Args:
            days: Number of days to look back

        Returns:
            List of session info with session_id, first_message_time, message_count
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT
                        session_id,
                        MIN(timestamp) as first_message,
                        COUNT(*) as message_count
                    FROM conversations
                    WHERE timestamp >= ?
                    GROUP BY session_id
                    ORDER BY first_message DESC
                    """,
                    (cutoff.isoformat(),),
                )

                sessions = [
                    {
                        "session_id": row["session_id"],
                        "first_message": row["first_message"],
                        "message_count": row["message_count"],
                    }
                    for row in cursor.fetchall()
                ]

                logger.debug(f"Found {len(sessions)} recent sessions")
                return sessions

        except Exception as e:
            logger.error(f"Failed to retrieve recent sessions: {e}")
            return []

    def get_context_for_llm(
        self, session_id: str, max_messages: int = 10
    ) -> str:
        """
        Format recent conversation history for LLM context.

        Args:
            session_id: Session identifier
            max_messages: Maximum number of recent messages to include

        Returns:
            Formatted conversation history string
        """
        messages = self.get_session_history(session_id, limit=max_messages)

        if not messages:
            return ""

        context_parts = ["Previous conversation history:\n"]

        for msg in messages:
            role = msg["role"].capitalize()
            content = msg["content"]
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M")

            if msg["agent_name"]:
                context_parts.append(f"[{timestamp}] {role} ({msg['agent_name']}): {content}")
            else:
                context_parts.append(f"[{timestamp}] {role}: {content}")

        return "\n".join(context_parts)

    def cleanup_old_conversations(self, days: int = 30):
        """
        Delete conversations older than specified days.

        Args:
            days: Delete conversations older than this many days
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)

            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM conversations WHERE timestamp < ?",
                    (cutoff.isoformat(),),
                )
                deleted_count = cursor.rowcount

                logger.info(f"Cleaned up {deleted_count} old conversation messages")

        except Exception as e:
            logger.error(f"Failed to cleanup old conversations: {e}")

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about stored conversations.

        Returns:
            Dictionary with total_messages, total_sessions, oldest_message_age_days
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Total messages
                cursor.execute("SELECT COUNT(*) as count FROM conversations")
                total_messages = cursor.fetchone()["count"]

                # Total unique sessions
                cursor.execute("SELECT COUNT(DISTINCT session_id) as count FROM conversations")
                total_sessions = cursor.fetchone()["count"]

                # Oldest message
                cursor.execute("SELECT MIN(timestamp) as oldest FROM conversations")
                oldest = cursor.fetchone()["oldest"]

                oldest_age_days = 0
                if oldest:
                    oldest_date = datetime.fromisoformat(oldest)
                    oldest_age_days = (datetime.now() - oldest_date).days

                return {
                    "total_messages": total_messages,
                    "total_sessions": total_sessions,
                    "oldest_message_age_days": oldest_age_days,
                }

        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                "total_messages": 0,
                "total_sessions": 0,
                "oldest_message_age_days": 0,
            }
