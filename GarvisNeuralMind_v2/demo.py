#!/usr/bin/env python3
"""
GarvisNeuralMind Demo Script
Bemutatja a GarvisNeuralMind API funkcionalitását
"""

import asyncio
import json
import time
from pathlib import Path
import requests
import websockets

# API Base URL
BASE_URL = "http://localhost:8000"


def test_basic_api():
    """Alapvető API funkciók tesztelése"""
    print("🔍 Alapvető API tesztelés...")
    
    try:
        # 1. Alapvető státusz
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.json()}")
        
        # 2. Rendszer állapot
        response = requests.get(f"{BASE_URL}/api/status")
        print(f"📊 System status: {response.json()}")
        
        # 3. Chat API teszt
        chat_data = {
            "message": "Szia! Mit tudsz csinálni?",
            "conversation_id": "demo-conversation"
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        chat_result = response.json()
        print(f"💬 Chat response: {chat_result['response'][:100]}...")
        
        # 4. Beszélgetések lekérdezése
        response = requests.get(f"{BASE_URL}/api/memory/conversations")
        conversations = response.json()
        print(f"🧠 Conversations count: {len(conversations)}")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Nem lehet kapcsolódni az API-hoz!")
        print("💡 Indítsd el az alkalmazást: python scripts/run.py dev")
        return False
    except Exception as e:
        print(f"❌ API teszt hiba: {e}")
        return False


async def test_websocket():
    """WebSocket kapcsolat tesztelése"""
    print("\n🔌 WebSocket tesztelés...")
    
    try:
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket kapcsolat létrehozva")
            
            # Üzenet küldése
            message = {
                "message": "WebSocket teszt üzenet",
                "conversation_id": "websocket-demo"
            }
            await websocket.send(json.dumps(message))
            print("📤 Üzenet elküldve")
            
            # Válasz fogadása
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Válasz érkezett: {data.get('response', 'No response')[:100]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ WebSocket teszt hiba: {e}")
        return False


def interactive_chat():
    """Interaktív chat interfész"""
    print("\n💬 Interaktív Chat Mód")
    print("Írj 'quit' a kilépéshez")
    print("-" * 40)
    
    conversation_id = f"interactive-{int(time.time())}"
    
    while True:
        try:
            user_input = input("\n👤 Te: ")
            if user_input.lower() in ['quit', 'exit', 'kilépés']:
                break
            
            if not user_input.strip():
                continue
            
            # API hívás
            chat_data = {
                "message": user_input,
                "conversation_id": conversation_id
            }
            
            print("🤖 GarvisNeuralMind: ", end="", flush=True)
            response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
            
            if response.status_code == 200:
                result = response.json()
                print(result['response'])
                print(f"   (Model: {result['model_used']})")
            else:
                print(f"Hiba történt: {response.status_code}")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Hiba: {e}")
    
    print("\n👋 Chat befejezve!")


def performance_test():
    """Teljesítmény teszt"""
    print("\n⚡ Teljesítmény teszt...")
    
    messages = [
        "Mi a neve ennek a rendszernek?",
        "Hogyan működik az AI?",
        "Milyen funkciókat támogatsz?",
        "Mi a különbség a különböző AI modellek között?",
        "Köszönöm a válaszokat!"
    ]
    
    start_time = time.time()
    
    for i, message in enumerate(messages, 1):
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": message, "conversation_id": "perf-test"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {i}/5: {len(result['response'])} karakteres válasz")
            else:
                print(f"❌ {i}/5: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {i}/5: {e}")
    
    total_time = time.time() - start_time
    print(f"📊 Összesen {total_time:.2f} másodperc, átlag: {total_time/len(messages):.2f}s/üzenet")


def main():
    """Fő demo funkció"""
    print("🚀 GarvisNeuralMind Demo Script")
    print("=" * 50)
    
    # 1. Alapvető API teszt
    if not test_basic_api():
        return
    
    # 2. WebSocket teszt
    print("\n" + "=" * 50)
    asyncio.run(test_websocket())
    
    # 3. Teljesítmény teszt
    print("\n" + "=" * 50)
    performance_test()
    
    # 4. Interaktív mód választás
    print("\n" + "=" * 50)
    print("🎯 Demo opciók:")
    print("1. Interaktív chat")
    print("2. Exit")
    
    choice = input("\nVálaszd (1-2): ").strip()
    
    if choice == "1":
        interactive_chat()
    
    print("\n🎉 Demo befejezve!")
    print("📖 További dokumentáció: docs/quick-start.md")
    print("🌐 API dokumentáció: http://localhost:8000/docs")


if __name__ == "__main__":
    main()