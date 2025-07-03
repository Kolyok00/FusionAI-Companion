"""
WebSocket Manager for GarvisNeuralMind
Handles real-time WebSocket connections for chat and notifications
"""

import asyncio
import json
from typing import Dict, List, Set
from fastapi import WebSocket
from loguru import logger


class WebSocketManager:
    """Manager for WebSocket connections"""
    
    def __init__(self):
        # Store active connections
        self.active_connections: Set[WebSocket] = set()
        self.connection_data: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)
        self.connection_data[websocket] = {
            "connected_at": asyncio.get_event_loop().time(),
            "user_id": None,
            "conversation_id": None
        }
        
        logger.info(f"WebSocket kapcsolat elfogadva. Aktív kapcsolatok: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "welcome",
            "message": "Kapcsolódva a GarvisNeuralMind-hoz!",
            "timestamp": asyncio.get_event_loop().time()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        
        logger.info(f"WebSocket kapcsolat bontva. Aktív kapcsolatok: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            if websocket in self.active_connections:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Hiba üzenet küldése során: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Send a message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message, ensure_ascii=False)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Broadcast hiba: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_to_conversation(self, conversation_id: str, message: dict):
        """Send a message to all clients in a specific conversation"""
        message_json = json.dumps(message, ensure_ascii=False)
        disconnected = []
        
        for connection in self.active_connections:
            connection_info = self.connection_data.get(connection, {})
            if connection_info.get("conversation_id") == conversation_id:
                try:
                    await connection.send_text(message_json)
                except Exception as e:
                    logger.error(f"Conversation broadcast hiba: {e}")
                    disconnected.append(connection)
        
        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_typing_indicator(self, conversation_id: str, is_typing: bool):
        """Send typing indicator to conversation participants"""
        message = {
            "type": "typing",
            "conversation_id": conversation_id,
            "is_typing": is_typing,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.send_to_conversation(conversation_id, message)
    
    async def send_system_notification(self, notification_type: str, data: dict):
        """Send system notification to all connected clients"""
        message = {
            "type": "system_notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await self.broadcast(message)
    
    def set_user_info(self, websocket: WebSocket, user_id: str = None, conversation_id: str = None):
        """Set user information for a WebSocket connection"""
        if websocket in self.connection_data:
            if user_id:
                self.connection_data[websocket]["user_id"] = user_id
            if conversation_id:
                self.connection_data[websocket]["conversation_id"] = conversation_id
    
    def get_connection_info(self, websocket: WebSocket) -> dict:
        """Get information about a WebSocket connection"""
        return self.connection_data.get(websocket, {})
    
    @property
    def connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connections_by_conversation(self, conversation_id: str) -> List[WebSocket]:
        """Get all connections for a specific conversation"""
        connections = []
        for connection, data in self.connection_data.items():
            if data.get("conversation_id") == conversation_id:
                connections.append(connection)
        return connections
    
    def get_connection_stats(self) -> dict:
        """Get statistics about WebSocket connections"""
        stats = {
            "total_connections": self.connection_count,
            "conversations": {},
            "users": set()
        }
        
        for connection, data in self.connection_data.items():
            conv_id = data.get("conversation_id")
            user_id = data.get("user_id")
            
            if conv_id:
                if conv_id not in stats["conversations"]:
                    stats["conversations"][conv_id] = 0
                stats["conversations"][conv_id] += 1
            
            if user_id:
                stats["users"].add(user_id)
        
        stats["unique_users"] = len(stats["users"])
        stats["active_conversations"] = len(stats["conversations"])
        del stats["users"]  # Remove set for JSON serialization
        
        return stats