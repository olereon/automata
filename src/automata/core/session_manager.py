"""
Session management module for handling browser sessions.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import base64
from cryptography.fernet import Fernet
import hashlib

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages browser sessions including save, restore, and lifecycle management."""

    def __init__(self, session_dir: Optional[str] = None, encryption_key: Optional[str] = None):
        """
        Initialize the session manager.

        Args:
            session_dir: Directory to store session files
            encryption_key: Key for encrypting session data
        """
        self.session_dir = Path(session_dir) if session_dir else Path.home() / ".automata" / "sessions"
        self.session_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize encryption
        self.encryption_key = encryption_key
        self.cipher_suite = None
        if encryption_key:
            # Derive a proper key from the provided key
            key = hashlib.sha256(encryption_key.encode()).digest()
            self.cipher_suite = Fernet(base64.urlsafe_b64encode(key))
        
        # Session expiry settings (default: 30 days)
        self.default_expiry_days = 30

    def _encrypt_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypt session data if encryption is enabled.

        Args:
            data: Session data to encrypt

        Returns:
            Encrypted session data
        """
        if not self.cipher_suite:
            return data
        
        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            
            # Encrypt the JSON string
            encrypted_data = self.cipher_suite.encrypt(json_data.encode())
            
            # Return encrypted data
            return {
                "encrypted": True,
                "data": encrypted_data.decode()
            }
        except Exception as e:
            logger.error(f"Error encrypting session data: {e}")
            return data

    def _decrypt_data(self, encrypted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypt session data if encryption is enabled.

        Args:
            encrypted_data: Encrypted session data

        Returns:
            Decrypted session data
        """
        if not self.cipher_suite or not encrypted_data.get("encrypted"):
            return encrypted_data
        
        try:
            # Decrypt the data
            decrypted_data = self.cipher_suite.decrypt(encrypted_data["data"].encode())
            
            # Parse JSON
            return json.loads(decrypted_data)
        except Exception as e:
            logger.error(f"Error decrypting session data: {e}")
            return encrypted_data

    def _get_session_path(self, session_id: str) -> Path:
        """
        Get the file path for a session.

        Args:
            session_id: ID of the session

        Returns:
            Path to the session file
        """
        return self.session_dir / f"{session_id}.json"

    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """
        Check if a session has expired.

        Args:
            session_data: Session data

        Returns:
            True if session has expired, False otherwise
        """
        if "created_at" not in session_data:
            return False
        
        try:
            created_at = datetime.fromisoformat(session_data["created_at"])
            expiry_days = session_data.get("expiry_days", self.default_expiry_days)
            expiry_date = created_at + timedelta(days=expiry_days)
            
            return datetime.now() > expiry_date
        except Exception as e:
            logger.error(f"Error checking session expiry: {e}")
            return False

    async def save_session(self, browser_manager, session_id: str,
                          include_storage: bool = True,
                          expiry_days: Optional[int] = None) -> str:
        """
        Save a browser session.

        Args:
            browser_manager: BrowserManager instance
            session_id: ID for the session
            include_storage: Whether to include localStorage and sessionStorage
            expiry_days: Number of days until session expires

        Returns:
            Path to the saved session file
        """
        logger.info(f"DEBUG: SessionManager.save_session called with session_id: {session_id}")
        logger.info(f"DEBUG: SessionManager.save_session - include_storage: {include_storage}, expiry_days: {expiry_days}")
        
        try:
            # Save session using browser manager
            logger.info(f"DEBUG: SessionManager: Calling browser_manager.save_session...")
            session_path_str = await browser_manager.save_session(session_id, include_storage)
            logger.info(f"DEBUG: SessionManager: browser_manager.save_session returned: {session_path_str}")
            
            # Load the session data to add metadata
            logger.info(f"DEBUG: SessionManager: Loading session data to add metadata...")
            session_path = Path(session_path_str)
            with open(session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            logger.info(f"DEBUG: SessionManager: Session data loaded successfully")
            
            # Add metadata
            logger.info(f"DEBUG: SessionManager: Adding metadata...")
            session_data["expiry_days"] = expiry_days or self.default_expiry_days
            session_data["metadata"] = {
                "saved_at": datetime.now().isoformat(),
                "version": "1.0"
            }
            logger.info(f"DEBUG: SessionManager: Metadata added successfully")
            
            # Encrypt data if encryption is enabled
            logger.info(f"DEBUG: SessionManager: Encrypting data...")
            encrypted_data = self._encrypt_data(session_data)
            logger.info(f"DEBUG: SessionManager: Data encrypted successfully")
            
            # Save the updated session data
            logger.info(f"DEBUG: SessionManager: Saving updated session data...")
            with open(session_path, "w", encoding="utf-8") as f:
                json.dump(encrypted_data, f, indent=2, default=str)
            logger.info(f"DEBUG: SessionManager: Updated session data saved successfully")
            
            logger.info(f"DEBUG: SessionManager: Session save process completed: {session_path}")
            return str(session_path)
        
        except Exception as e:
            logger.error(f"DEBUG: SessionManager: Error during session save process: {e}")
            logger.error(f"DEBUG: SessionManager: Error type: {type(e).__name__}")
            import traceback
            logger.error(f"DEBUG: SessionManager: Traceback: {traceback.format_exc()}")
            raise

    async def load_session(self, browser_manager, session_id: str, 
                          include_storage: bool = True) -> bool:
        """
        Load a browser session.

        Args:
            browser_manager: BrowserManager instance
            session_id: ID of the session to load
            include_storage: Whether to load localStorage and sessionStorage

        Returns:
            True if session was loaded successfully, False otherwise
        """
        try:
            session_path = self._get_session_path(session_id)
            
            if not session_path.exists():
                logger.warning(f"Session file not found: {session_path}")
                return False
            
            # Load session data
            with open(session_path, "r", encoding="utf-8") as f:
                encrypted_data = json.load(f)
            
            # Decrypt data if encryption is enabled
            session_data = self._decrypt_data(encrypted_data)
            
            # Check if session has expired
            if self._is_session_expired(session_data):
                logger.warning(f"Session has expired: {session_id}")
                return False
            
            # Load session using browser manager
            return await browser_manager.load_session(session_id, include_storage)
        
        except Exception as e:
            logger.error(f"Error loading session: {e}")
            return False

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a saved session.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if session was deleted successfully, False otherwise
        """
        try:
            session_path = self._get_session_path(session_id)
            
            if session_path.exists():
                session_path.unlink()
                logger.info(f"Session deleted: {session_path}")
                return True
            else:
                logger.warning(f"Session file not found: {session_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return False

    async def list_sessions(self, include_expired: bool = False) -> List[Dict[str, Any]]:
        """
        List all saved sessions.

        Args:
            include_expired: Whether to include expired sessions

        Returns:
            List of session information
        """
        sessions = []
        
        try:
            for session_file in self.session_dir.glob("*.json"):
                try:
                    with open(session_file, "r", encoding="utf-8") as f:
                        encrypted_data = json.load(f)
                    
                    # Decrypt data if encryption is enabled
                    session_data = self._decrypt_data(encrypted_data)
                    
                    # Check if session has expired
                    is_expired = self._is_session_expired(session_data)
                    
                    # Skip expired sessions if not requested
                    if is_expired and not include_expired:
                        continue
                    
                    # Create session info
                    session_info = {
                        "session_id": session_data.get("session_id"),
                        "created_at": session_data.get("created_at"),
                        "path": str(session_file),
                        "cookie_count": len(session_data.get("cookies", [])),
                        "has_local_storage": "local_storage" in session_data,
                        "has_session_storage": "session_storage" in session_data,
                        "is_expired": is_expired,
                        "expiry_days": session_data.get("expiry_days", self.default_expiry_days)
                    }
                    
                    # Add metadata if available
                    if "metadata" in session_data:
                        session_info["metadata"] = session_data["metadata"]
                    
                    sessions.append(session_info)
                
                except Exception as e:
                    logger.error(f"Error reading session file {session_file}: {e}")
            
            logger.info(f"Found {len(sessions)} sessions")
            return sessions
        
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return []

    async def cleanup_expired_sessions(self) -> int:
        """
        Delete all expired sessions.

        Returns:
            Number of sessions deleted
        """
        try:
            sessions = await self.list_sessions(include_expired=True)
            deleted_count = 0
            
            for session in sessions:
                if session.get("is_expired", False):
                    if await self.delete_session(session["session_id"]):
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} expired sessions")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            return 0

    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a session without loading it.

        Args:
            session_id: ID of the session

        Returns:
            Session information or None if session doesn't exist
        """
        try:
            session_path = self._get_session_path(session_id)
            
            if not session_path.exists():
                return None
            
            # Load session data
            with open(session_path, "r", encoding="utf-8") as f:
                encrypted_data = json.load(f)
            
            # Decrypt data if encryption is enabled
            session_data = self._decrypt_data(encrypted_data)
            
            # Create session info
            session_info = {
                "session_id": session_data.get("session_id"),
                "created_at": session_data.get("created_at"),
                "path": str(session_path),
                "cookie_count": len(session_data.get("cookies", [])),
                "has_local_storage": "local_storage" in session_data,
                "has_session_storage": "session_storage" in session_data,
                "is_expired": self._is_session_expired(session_data),
                "expiry_days": session_data.get("expiry_days", self.default_expiry_days)
            }
            
            # Add metadata if available
            if "metadata" in session_data:
                session_info["metadata"] = session_data["metadata"]
            
            return session_info
        
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return None