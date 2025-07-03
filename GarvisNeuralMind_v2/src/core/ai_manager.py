"""
AI Manager for GarvisNeuralMind
Handles communication with various AI model providers (OpenRouter, OpenAI, Google AI)
"""

import asyncio
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
import httpx
from loguru import logger

from .config import Settings


class AIManager:
    """Manager for AI model interactions"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = None
        self.default_model = "gpt-3.5-turbo"  # Fallback model
        
        # Model configurations
        self.model_configs = {
            "openrouter": {
                "base_url": "https://openrouter.ai/api/v1",
                "api_key": settings.openrouter_api_key,
                "default_model": "deepseek/deepseek-r1"
            },
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "api_key": settings.openai_api_key,
                "default_model": "gpt-4"
            },
            "google": {
                "api_key": settings.google_ai_api_key,
                "default_model": "gemini-pro"
            }
        }
    
    async def initialize(self):
        """Initialize AI manager and test connections"""
        logger.info("🤖 AI Manager inicializálása...")
        
        # Create HTTP client
        self.client = httpx.AsyncClient(timeout=30.0)
        
        # Test available providers
        available_providers = []
        
        for provider, config in self.model_configs.items():
            if config.get("api_key"):
                try:
                    await self._test_provider(provider)
                    available_providers.append(provider)
                    logger.info(f"✅ {provider} provider elérhető")
                except Exception as e:
                    logger.warning(f"⚠️ {provider} provider nem elérhető: {e}")
        
        if available_providers:
            logger.info(f"🎯 Elérhető AI providers: {', '.join(available_providers)}")
        else:
            logger.error("❌ Egyik AI provider sem elérhető!")
    
    async def close(self):
        """Close connections and cleanup"""
        if self.client:
            await self.client.aclose()
    
    async def process_message(
        self, 
        message: str, 
        model: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a message through AI models"""
        
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # Determine which provider to use
        provider, model_name = self._resolve_model(model)
        
        try:
            if provider == "openrouter":
                response = await self._call_openrouter(message, model_name)
            elif provider == "openai":
                response = await self._call_openai(message, model_name)
            elif provider == "google":
                response = await self._call_google_ai(message, model_name)
            else:
                response = await self._fallback_response(message)
            
            return {
                "response": response,
                "model_used": f"{provider}:{model_name}",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI hiba: {e}")
            return {
                "response": f"Sajnálom, hiba történt az AI válasz generálása során: {str(e)}",
                "model_used": "error",
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
    
    def _resolve_model(self, model: Optional[str]) -> tuple[str, str]:
        """Resolve provider and model from model string"""
        
        if not model:
            # Use first available provider
            for provider, config in self.model_configs.items():
                if config.get("api_key"):
                    return provider, config["default_model"]
        
        # Parse provider:model format
        if ":" in model:
            provider, model_name = model.split(":", 1)
            if provider in self.model_configs and self.model_configs[provider].get("api_key"):
                return provider, model_name
        
        # Check if it's just a model name for a provider
        for provider, config in self.model_configs.items():
            if config.get("api_key") and model in config.get("models", [model]):
                return provider, model
        
        # Fallback to first available
        for provider, config in self.model_configs.items():
            if config.get("api_key"):
                return provider, config["default_model"]
        
        return "fallback", "local"
    
    async def _test_provider(self, provider: str):
        """Test if a provider is available"""
        if provider == "openrouter":
            return await self._test_openrouter()
        elif provider == "openai":
            return await self._test_openai()
        elif provider == "google":
            return await self._test_google_ai()
        return False
    
    async def _test_openrouter(self) -> bool:
        """Test OpenRouter connection"""
        config = self.model_configs["openrouter"]
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        response = await self.client.get(
            f"{config['base_url']}/models",
            headers=headers
        )
        return response.status_code == 200
    
    async def _test_openai(self) -> bool:
        """Test OpenAI connection"""
        config = self.model_configs["openai"]
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        response = await self.client.get(
            f"{config['base_url']}/models",
            headers=headers
        )
        return response.status_code == 200
    
    async def _test_google_ai(self) -> bool:
        """Test Google AI connection"""
        # Simple check - if we have API key, assume it works
        return bool(self.model_configs["google"]["api_key"])
    
    async def _call_openrouter(self, message: str, model: str) -> str:
        """Call OpenRouter API"""
        config = self.model_configs["openrouter"]
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "max_tokens": 1000
        }
        
        response = await self.client.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter API hiba: {response.status_code}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def _call_openai(self, message: str, model: str) -> str:
        """Call OpenAI API"""
        config = self.model_configs["openai"]
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "max_tokens": 1000
        }
        
        response = await self.client.post(
            f"{config['base_url']}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenAI API hiba: {response.status_code}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
    
    async def _call_google_ai(self, message: str, model: str) -> str:
        """Call Google AI API (placeholder)"""
        # TODO: Implement Google AI Gemini API
        return f"Google AI válasz (fejlesztés alatt): {message[:50]}..."
    
    async def _fallback_response(self, message: str) -> str:
        """Fallback response when no AI providers are available"""
        return f"Helyi válasz (AI szolgáltatók nem elérhetők): Üzenetét megkaptam: '{message[:100]}...'"