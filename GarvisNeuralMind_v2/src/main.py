#!/usr/bin/env python3
"""
GarvisNeuralMind - AI-alapú asszisztens rendszer
Főprogram - FastAPI alapú REST API és WebSocket szerver
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import yaml

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from core.config import Settings
from core.ai_manager import AIManager
from core.memory_manager import MemoryManager
from core.websocket_manager import WebSocketManager

# Pydantic models for API
class ChatMessage(BaseModel):
    message: str
    model: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    model_used: str
    conversation_id: str
    timestamp: str

class SystemStatus(BaseModel):
    status: str
    version: str
    uptime: float
    active_connections: int
    memory_usage: Dict[str, Any]

# Initialize FastAPI app
app = FastAPI(
    title="GarvisNeuralMind API",
    description="AI-alapú asszisztens rendszer - REST API és WebSocket interfész",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global managers
settings: Settings = None
ai_manager: AIManager = None
memory_manager: MemoryManager = None
websocket_manager: WebSocketManager = None

@app.on_event("startup")
async def startup_event():
    """Alkalmazás indítási események"""
    global settings, ai_manager, memory_manager, websocket_manager
    
    logger.info("🚀 GarvisNeuralMind indítása...")
    
    try:
        # Configuration loading
        settings = Settings()
        logger.info("✅ Konfiguráció betöltve")
        
        # Initialize managers
        ai_manager = AIManager(settings)
        memory_manager = MemoryManager(settings)
        websocket_manager = WebSocketManager()
        
        # Initialize components
        await ai_manager.initialize()
        await memory_manager.initialize()
        
        logger.info("✅ GarvisNeuralMind sikeresen elindult!")
        
    except Exception as e:
        logger.error(f"❌ Hiba az indítás során: {e}")
        raise e

@app.on_event("shutdown")
async def shutdown_event():
    """Alkalmazás leállítási események"""
    logger.info("🛑 GarvisNeuralMind leállítása...")
    
    if memory_manager:
        await memory_manager.close()
    if ai_manager:
        await ai_manager.close()
    
    logger.info("✅ GarvisNeuralMind sikeresen leállt")

# API Endpoints

@app.get("/", response_model=Dict[str, str])
async def root():
    """Gyökér endpoint - API állapot"""
    return {
        "message": "GarvisNeuralMind API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """AI beszélgetési interfész"""
    try:
        response = await ai_manager.process_message(
            message=chat_message.message,
            model=chat_message.model,
            conversation_id=chat_message.conversation_id
        )
        
        # Save to memory
        await memory_manager.save_conversation(
            conversation_id=response["conversation_id"],
            user_message=chat_message.message,
            ai_response=response["response"],
            model_used=response["model_used"]
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat hiba: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/conversations", response_model=List[Dict[str, Any]])
async def get_conversations(limit: int = 10):
    """Beszélgetések lekérdezése"""
    try:
        conversations = await memory_manager.get_conversations(limit=limit)
        return conversations
    except Exception as e:
        logger.error(f"Memory hiba: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Beszélgetés törlése"""
    try:
        result = await memory_manager.delete_conversation(conversation_id)
        return {"success": result, "conversation_id": conversation_id}
    except Exception as e:
        logger.error(f"Delete hiba: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status", response_model=SystemStatus)
async def system_status():
    """Rendszerállapot lekérdezése"""
    try:
        status_data = {
            "status": "running",
            "version": "2.0.0",
            "uptime": getattr(app, "start_time", 0),
            "active_connections": websocket_manager.connection_count if websocket_manager else 0,
            "memory_usage": await memory_manager.get_memory_stats() if memory_manager else {}
        }
        return SystemStatus(**status_data)
    except Exception as e:
        logger.error(f"Status hiba: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket kapcsolat kezelése"""
    await websocket_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Process message through AI manager
            try:
                message_data = yaml.safe_load(data)
                response = await ai_manager.process_message(
                    message=message_data.get("message", ""),
                    model=message_data.get("model"),
                    conversation_id=message_data.get("conversation_id")
                )
                
                await websocket.send_text(yaml.dump(response))
                
            except Exception as e:
                error_response = {"error": str(e), "type": "processing_error"}
                await websocket.send_text(yaml.dump(error_response))
                
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

# Fine-tuning endpoints (placeholder for future implementation)
@app.post("/api/fine-tune/start")
async def start_fine_tuning(model_config: Dict[str, Any]):
    """Fine-tuning folyamat indítása"""
    # TODO: Implement fine-tuning functionality
    return {"message": "Fine-tuning funkcionalitás fejlesztés alatt", "config": model_config}

@app.get("/api/fine-tune/status/{job_id}")
async def get_fine_tuning_status(job_id: str):
    """Fine-tuning állapot lekérdezése"""
    # TODO: Implement fine-tuning status tracking
    return {"job_id": job_id, "status": "not_implemented"}

if __name__ == "__main__":
    # Setup logging
    logger.add("logs/garvis.log", rotation="1 day", retention="7 days", level="INFO")
    
    # Start the server
    config_path = Path(__file__).parent.parent / "config" / "settings.yaml"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )