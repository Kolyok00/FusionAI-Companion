# GarvisNeuralMind Quick Start Guide

## 🚀 Gyors Indítás

### 1. Telepítés és Konfiguráció

```bash
# 1. Klónozd a repót
git clone https://github.com/felhasznalo/GarvisNeuralMind.git
cd GarvisNeuralMind_v2

# 2. Futtasd a setup scriptet
python scripts/setup.py

# 3. Szerkeszd a .env fájlt
nano .env
# Add meg az API kulcsaidat
```

### 2. API Kulcsok Beszerzése

#### OpenRouter (Ajánlott)
- Regisztrálj: https://openrouter.ai/
- Hozz létre API kulcsot
- Add hozzá az .env fájlhoz: `OPENROUTER_API_KEY=sk-or-...`

#### OpenAI (Opcionális)
- API kulcs: https://platform.openai.com/api-keys
- Add hozzá: `OPENAI_API_KEY=sk-...`

#### Google AI (Opcionális)
- API kulcs: https://makersuite.google.com/app/apikey
- Add hozzá: `GOOGLE_AI_API_KEY=...`

### 3. Alkalmazás Indítása

#### Python módban (Fejlesztéshez)
```bash
python scripts/run.py dev
```

#### Docker módban (Ajánlott production-hoz)
```bash
python scripts/run.py docker
```

### 4. API Tesztelése

#### Web interfész
Nyisd meg a böngészőben: http://localhost:8000/docs

#### Curl paranccsal
```bash
# Alapvető chat üzenet
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Szia! Hogyan működsz?"}'

# Rendszer státusz
curl http://localhost:8000/api/status
```

#### Python kóddal
```python
import requests

# Chat API hívás
response = requests.post(
    "http://localhost:8000/api/chat",
    json={"message": "Magyarázd el, hogy működsz!"}
)
print(response.json())
```

### 5. WebSocket Kapcsolat

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function(event) {
    console.log('Kapcsolódva!');
    
    // Üzenet küldése
    ws.send(JSON.stringify({
        message: "Szia WebSocket!",
        conversation_id: "test-conv-1"
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('AI válasz:', response);
};
```

## 🛠️ Konfigurációs Lehetőségek

### AI Modellek
```yaml
# config/settings.yaml
ai_models:
  openrouter:
    default_model: "deepseek/deepseek-r1"  # Nagyon gyors és okos
  openai:
    default_model: "gpt-4"                 # Drágább de precíz
  google_ai:
    default_model: "gemini-pro"            # Google alternatíva
```

### Memoria Beállítások
```yaml
storage:
  redis:
    host: "localhost"
    port: 6379
  postgresql:
    database: "garvis_neural_mind"
```

## 🚨 Hibaelhárítás

### Gyakori Problémák

#### "Import error" üzenetek
```bash
# Telepítsd a függőségeket
pip install -r requirements.txt
```

#### "API key not found"
```bash
# Ellenőrizd a .env fájlt
cat .env
# API kulcsok formátuma: OPENROUTER_API_KEY=sk-or-...
```

#### "Connection refused"
```bash
# Ellenőrizd hogy fut-e az alkalmazás
python scripts/run.py status

# Ha Docker-t használsz
docker-compose ps
```

### Debug Módba Kapcsolás
```bash
# Részletes logok
export DEBUG=true
python scripts/run.py dev
```

## 📊 Monitoring és Teljesítmény

### Alapvető Metrikák
- API válasz idők: `/api/status`
- Aktív WebSocket kapcsolatok
- Memoria használat
- AI provider állapotok

### Production Monitoring
```bash
# Docker-rel full monitoring stack
docker-compose --profile monitoring up -d

# Grafana: http://localhost:3000 (admin/admin)
# Prometheus: http://localhost:9090
```

## 🔗 API Dokumentáció

### Főbb Endpointok
- `GET /` - Alapvető státusz
- `POST /api/chat` - AI beszélgetés
- `GET /api/memory/conversations` - Beszélgetés történet
- `DELETE /api/memory/conversations/{id}` - Beszélgetés törlése
- `GET /api/status` - Rendszer állapot
- `WebSocket /ws` - Valós idejű kommunikáció

### Swagger UI
Teljes dokumentáció: http://localhost:8000/docs

## 🎯 Következő Lépések

1. **Finomhangolás**: Implementáld a fine-tuning funkcionalitást
2. **Böngészővezérlés**: Add hozzá a browser automation-t
3. **Voice Interface**: Hang alapú interakció
4. **VSCode Integráció**: Kód asszisztens funkciók
5. **Advanced Memory**: Vektor keresés és kontextus

Részletes dokumentáció: [docs/](../docs/)