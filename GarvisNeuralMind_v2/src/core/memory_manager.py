"""
Memory Manager for GarvisNeuralMind
Handles conversation storage and retrieval using Redis, PostgreSQL, and Pinecone
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from loguru import logger

from .config import Settings


class MemoryManager:
    """Manager for conversation memory and storage"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_client = None
        self.postgres_connection = None
        self.pinecone_index = None
        self.in_memory_storage = {}  # Fallback storage
    
    async def initialize(self):
        """Initialize memory storage backends"""
        logger.info("🧠 Memory Manager inicializálása...")
        
        # Try to initialize Redis
        if self.settings.memory_persistence:
            try:
                await self._init_redis()
                logger.info("✅ Redis memória tároló inicializálva")
            except Exception as e:
                logger.warning(f"⚠️ Redis nem elérhető: {e}")
        
        # Try to initialize PostgreSQL
        try:
            await self._init_postgres()
            logger.info("✅ PostgreSQL adatbázis inicializálva")
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL nem elérhető: {e}")
        
        # Try to initialize Pinecone
        try:
            await self._init_pinecone()
            logger.info("✅ Pinecone vektor adatbázis inicializálva")
        except Exception as e:
            logger.warning(f"⚠️ Pinecone nem elérhető: {e}")
        
        logger.info("🎯 Memory Manager sikeresen inicializálva")
    
    async def close(self):
        """Close all connections"""
        if self.redis_client:
            try:
                await self.redis_client.close()
            except:
                pass
        
        if self.postgres_connection:
            try:
                await self.postgres_connection.close()
            except:
                pass
    
    async def save_conversation(
        self,
        conversation_id: str,
        user_message: str,
        ai_response: str,
        model_used: str
    ):
        """Save a conversation turn to storage"""
        
        conversation_data = {
            "conversation_id": conversation_id,
            "user_message": user_message,
            "ai_response": ai_response,
            "model_used": model_used,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to Redis (temporary storage)
        if self.redis_client:
            try:
                await self._save_to_redis(conversation_id, conversation_data)
            except Exception as e:
                logger.error(f"Redis mentési hiba: {e}")
        
        # Save to PostgreSQL (persistent storage)
        if self.postgres_connection:
            try:
                await self._save_to_postgres(conversation_data)
            except Exception as e:
                logger.error(f"PostgreSQL mentési hiba: {e}")
        
        # Save to Pinecone (vector search)
        if self.pinecone_index:
            try:
                await self._save_to_pinecone(conversation_data)
            except Exception as e:
                logger.error(f"Pinecone mentési hiba: {e}")
        
        # Fallback to in-memory storage
        if conversation_id not in self.in_memory_storage:
            self.in_memory_storage[conversation_id] = []
        self.in_memory_storage[conversation_id].append(conversation_data)
        
        logger.debug(f"Beszélgetés mentve: {conversation_id}")
    
    async def get_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations"""
        
        # Try PostgreSQL first
        if self.postgres_connection:
            try:
                return await self._get_from_postgres(limit)
            except Exception as e:
                logger.error(f"PostgreSQL lekérdezési hiba: {e}")
        
        # Try Redis
        if self.redis_client:
            try:
                return await self._get_from_redis(limit)
            except Exception as e:
                logger.error(f"Redis lekérdezési hiba: {e}")
        
        # Fallback to in-memory
        conversations = []
        for conv_id, messages in list(self.in_memory_storage.items())[-limit:]:
            if messages:
                conversations.append({
                    "conversation_id": conv_id,
                    "last_message": messages[-1],
                    "message_count": len(messages)
                })
        
        return conversations[:limit]
    
    async def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation from all storage backends"""
        success = True
        
        # Delete from Redis
        if self.redis_client:
            try:
                await self._delete_from_redis(conversation_id)
            except Exception as e:
                logger.error(f"Redis törlési hiba: {e}")
                success = False
        
        # Delete from PostgreSQL
        if self.postgres_connection:
            try:
                await self._delete_from_postgres(conversation_id)
            except Exception as e:
                logger.error(f"PostgreSQL törlési hiba: {e}")
                success = False
        
        # Delete from in-memory
        if conversation_id in self.in_memory_storage:
            del self.in_memory_storage[conversation_id]
        
        return success
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        stats = {
            "in_memory_conversations": len(self.in_memory_storage),
            "redis_connected": bool(self.redis_client),
            "postgres_connected": bool(self.postgres_connection),
            "pinecone_connected": bool(self.pinecone_index)
        }
        
        # Add more detailed stats if available
        if self.redis_client:
            try:
                stats["redis_keys"] = await self._get_redis_key_count()
            except:
                stats["redis_keys"] = "unknown"
        
        return stats
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        try:
            import redis.asyncio as redis
            
            self.redis_client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                password=self.settings.redis_password,
                db=self.settings.redis_db,
                decode_responses=True
            )
            
            # Test connection
            await self.redis_client.ping()
            
        except ImportError:
            logger.warning("Redis library nincs telepítve")
            raise Exception("Redis library not available")
        except Exception as e:
            raise Exception(f"Redis kapcsolódási hiba: {e}")
    
    async def _init_postgres(self):
        """Initialize PostgreSQL connection"""
        # Placeholder - would implement with asyncpg or sqlalchemy
        logger.info("PostgreSQL inicializálás (placeholder)")
    
    async def _init_pinecone(self):
        """Initialize Pinecone connection"""
        # Placeholder - would implement with pinecone library
        logger.info("Pinecone inicializálás (placeholder)")
    
    async def _save_to_redis(self, conversation_id: str, data: Dict[str, Any]):
        """Save conversation to Redis"""
        key = f"conversation:{conversation_id}"
        await self.redis_client.lpush(key, json.dumps(data))
        await self.redis_client.expire(key, 86400)  # 24 hours
    
    async def _save_to_postgres(self, data: Dict[str, Any]):
        """Save conversation to PostgreSQL"""
        # Placeholder for PostgreSQL implementation
        pass
    
    async def _save_to_pinecone(self, data: Dict[str, Any]):
        """Save conversation to Pinecone for vector search"""
        # Placeholder for Pinecone implementation
        pass
    
    async def _get_from_redis(self, limit: int) -> List[Dict[str, Any]]:
        """Get conversations from Redis"""
        keys = await self.redis_client.keys("conversation:*")
        conversations = []
        
        for key in keys[-limit:]:
            messages = await self.redis_client.lrange(key, 0, -1)
            if messages:
                conv_id = key.split(":", 1)[1]
                last_message = json.loads(messages[0])
                conversations.append({
                    "conversation_id": conv_id,
                    "last_message": last_message,
                    "message_count": len(messages)
                })
        
        return conversations
    
    async def _get_from_postgres(self, limit: int) -> List[Dict[str, Any]]:
        """Get conversations from PostgreSQL"""
        # Placeholder for PostgreSQL implementation
        return []
    
    async def _delete_from_redis(self, conversation_id: str):
        """Delete conversation from Redis"""
        key = f"conversation:{conversation_id}"
        await self.redis_client.delete(key)
    
    async def _delete_from_postgres(self, conversation_id: str):
        """Delete conversation from PostgreSQL"""
        # Placeholder for PostgreSQL implementation
        pass
    
    async def _get_redis_key_count(self) -> int:
        """Get number of Redis keys"""
        keys = await self.redis_client.keys("conversation:*")
        return len(keys)