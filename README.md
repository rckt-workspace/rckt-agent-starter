uvicorn app.main:app --reload



# RCKT Agent Starter

Una plantilla educativa y simple para crear agentes de IA y integrarlos en aplicaciones web.

**Diseñado para personas que quieren aprender a crear agentes sin necesidad de ser ingenieros expertos.**

---

## ¿Qué es RCKT Agent Starter?

Este proyecto es un backend simple que te permite:

1. **Crear un agente de IA** con instrucciones en lenguaje natural
2. **Agregar conocimiento** al agente desde un archivo de texto
3. **Integrar el agente en aplicaciones web** (React, Lovable, etc) mediante una simple API REST
4. **Personalizar el comportamiento** sin escribir código Python

Todo esto usando **FastAPI**, **Python** y **OpenRouter**.

---

## Arquitectura

```
Tu App Web (React, Lovable, etc)
            ↓
    POST /api/chat
            ↓
    FastAPI Backend
            ↓
    Agent Core
            ↓
    Carga AGENT.md (instrucciones)
    + knowledge.md (información)
            ↓
    OpenRouter API
            ↓
    Modelo LLM
            ↓
    Respuesta
```

---

## Requisitos

- **Python 3.10+**
- **pip** (gestor de paquetes Python)
- **OpenRouter API Key** (gratis en https://openrouter.ai)

---

## 1. Instalación

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/rckt/rckt-agent-starter.git
cd rckt-agent-starter
```

### Paso 2: Crear un entorno virtual (recomendado)

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 2. Crear el archivo .env

Copia el archivo `.env.example` a `.env`:

```bash
cp .env.example .env
```

O en Windows:
```bash
copy .env.example .env
```

Luego edita `.env` con tus valores:

```ini
# Application Configuration
APP_NAME=RCKT Agent Starter
APP_ENV=development

# OpenRouter Configuration
# Consigue tu API key en https://openrouter.ai
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Elige un modelo de https://openrouter.ai/keys
AGENT_MODEL=openrouter/auto
AGENT_FALLBACK_MODEL=openrouter/free
AGENT_USE_FALLBACK=true

# Configuración del agente
AGENT_MAX_TOKENS=700

# CORS - dominios desde los que se puede acceder
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

**⚠️ Importante:** Nunca hagas commit de `.env` con secretos reales. Siempre usa `.env.example`.

---

## 3. Ejecutar FastAPI

```bash
uvicorn app.main:app --reload
```

Verás algo como:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

## 4. Probar la API

### Opción A: Usar Swagger UI (recomendado)

Abre en el navegador:
```
http://localhost:8000/docs
```

Verás una interfaz interactiva donde puedes probar todos los endpoints.

### Opción B: Usar curl (línea de comandos)

**Probar /health:**
```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "ok"}
```

**Probar /api/agent:**
```bash
curl http://localhost:8000/api/agent
```

Respuesta:
```json
{
  "name": "RCKT Agent Starter",
  "version": "1.0.0"
}
```

**Probar /api/chat:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, ¿qué servicios ofrece RCKT?"}'
```

Respuesta:
```json
{
  "answer": "RCKT ofrece servicios de desarrollo web, aplicaciones móviles e inteligencia artificial..."
}
```

---

## 5. Personalizar el Comportamiento

### Cambiar instrucciones del agente

Edita el archivo `agent/AGENT.md`:

```markdown
# Tu Asistente

## Objetivo

Tu objetivo aquí...

## Lo que debes hacer

- Punto 1
- Punto 2
```

Cualquier cambio aquí afecta inmediatamente al comportamiento del agente. **No necesitas reiniciar el servidor.**

### Agregar conocimiento

Edita `agent/knowledge.md`:

```markdown
# Información sobre mi empresa

## Servicios

Nuestros servicios son...

## Contacto

Email: ejemplo@empresa.com
```

Este contenido se envía al modelo LLM automáticamente.

### Cambiar modelo o configuración

Modifica las variables en `.env`:

```ini
AGENT_MODEL=openrouter/auto
AGENT_MAX_TOKENS=1000
```

Luego reinicia FastAPI (Ctrl+C y vuelve a ejecutar).

---

## 6. Ejecutar Tests

```bash
pytest tests/
```

O con más detalle:

```bash
pytest tests/ -v
```

Verás algo como:

```
tests/test_health.py::test_health_endpoint PASSED
tests/test_health.py::test_root_endpoint PASSED
tests/test_health.py::test_agent_info_endpoint PASSED
```

---

## 7. Integrar con tu App Web

### Ejemplo en JavaScript/React:

```javascript
async function chatWithAgent(message) {
  const response = await fetch('http://localhost:8000/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();
  return data.answer;
}

// Uso:
const answer = await chatWithAgent('¿Qué es RCKT?');
console.log(answer);
```

### En Lovable:

1. Agrega un componente que haga llamadas POST a `http://localhost:8000/api/chat`
2. Ajusta `CORS_ORIGINS` en `.env` para incluir tu dominio de Lovable
3. Envía el mensaje del usuario y muestra `answer` en la UI

---

## Buenas Prácticas de Seguridad

### 1. Nunca expongas tu API Key

❌ **NO hagas esto:**
```javascript
// PELIGRO: exponer la API key en el frontend
const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
  headers: {
    'Authorization': 'Bearer sk-or-v1-xxx' // ¡NUNCA!
  }
});
```

✅ **Haz esto:**
```javascript
// El frontend llamra a TU backend
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  body: JSON.stringify({ message: 'Hola' })
});
```

El backend maneja la autenticación de OpenRouter de forma segura.

### 2. Protege tu .env

- Nunca hagas commit de `.env` (está en `.gitignore`)
- Nunca compartas `OPENROUTER_API_KEY`
- En producción, usa variables de entorno del servidor (Railway, Vercel, etc)

### 3. Configura CORS correctamente

En `.env`, lista únicamente los dominios que necesitan acceder:

```ini
CORS_ORIGINS=https://tuapp.ejemplo.com,https://www.tuapp.ejemplo.com
```

No uses `*` en producción.

### 4. Valida inputs

El backend ya valida:
- `message` debe tener entre 1 y 2000 caracteres
- Tipo de datos correcto

Pero en el frontend también deberías validar.

---

## Estructura de Archivos

```
rckt-agent-starter/
├── app/                      # Código de la aplicación
│   ├── main.py              # FastAPI principal
│   ├── core/
│   │   └── config.py        # Variables de entorno
│   ├── llm/
│   │   └── openrouter.py    # Cliente OpenRouter
│   ├── schemas/
│   │   └── chat.py          # Modelos de datos
│   ├── agent/
│   │   ├── agent.py         # Lógica del agente
│   │   └── prompt_loader.py # Carga de archivos
│   └── api/
│       ├── health.py        # GET /health
│       └── chat.py          # POST /api/chat
│
├── agent/                    # Configuración del agente
│   ├── AGENT.md             # Instrucciones (editar aquí)
│   └── knowledge.md         # Información (editar aquí)
│
├── tests/                    # Tests
│   └── test_health.py
│
├── requirements.txt          # Dependencias Python
├── .env.example              # Plantilla de variables
├── .env                      # Tus variables (ignorado)
├── .gitignore                # Archivos a ignorar
├── README.md                 # Este archivo
└── CLAUDE.md                 # Notas para futuras sesiones
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'app'"

Asegúrate de ejecutar FastAPI desde la carpeta raíz del proyecto:

```bash
cd rckt-agent-starter
uvicorn app.main:app --reload
```

### Error: "OPENROUTER_API_KEY not configured"

Comprueba que `.env` existe y tiene:
```ini
OPENROUTER_API_KEY=sk-or-v1-xxxxx
```

### Error: "404 Not Found"

Verifica que usas las rutas correctas:
- `/health` (GET)
- `/api/agent` (GET)
- `/api/chat` (POST)

No es `/api/health`, es `/health`.

### El agente da respuestas genéricas

Edita `agent/AGENT.md` con instrucciones más específicas y agrega más información a `agent/knowledge.md`.

---

## Próximos Pasos

1. **Personaliza AGENT.md** con tus instrucciones
2. **Actualiza knowledge.md** con tu información
3. **Integra la API** en tu app web
4. **Prueba en navegador** con http://localhost:8000/docs

---

## Preguntas Frecuentes

**P: ¿Puedo usar un modelo diferente de OpenRouter?**

R: Sí. OpenRouter soporta múltiples modelos. Cambia `AGENT_MODEL` en `.env`.

**P: ¿Cómo agrego más contexto?**

R: Edita `agent/knowledge.md` con más información. Es simple, sin embeddings.

**P: ¿Puedo conectar una base de datos?**

R: Este starter es simple por diseño. Para RAG o bases de datos, consulta otros recursos.

**P: ¿Cómo despliego esto en producción (Render)?**

R: Puedes desplegar todo el proyecto (Frontend + Backend) en un **único Web Service** en Render:

1. Conecta tu repositorio en [Render.com](https://render.com).
2. Selecciona **New Web Service** con entorno **Python**.
3. **Build Command**:
   ```bash
   pip install -r requirements.txt && cd frontend && npm install && npm run build && cd ..
   ```
4. **Start Command**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. En **Environment Variables**, agrega tu `OPENROUTER_API_KEY`.

FastAPI compilará el frontend en React y servirá tanto los endpoints REST como la interfaz visual en una sola URL sin necesidad de configurar CORS.


---

## Licencia

MIT

---

## Contacto

Para dudas o contribuciones: https://rckt.es

¡Feliz creación de agentes! 🚀
