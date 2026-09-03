# RCKT Agent Starter - Guía para Claude

## Filosofía del Proyecto

Este es un proyecto **educativo y simple**, diseñado para enseñar a personas no técnicas cómo crear y personalizar agentes de IA simples.

**NO es un starter empresarial** y no busca escalar de formas complejas.

## Objetivos de Diseño

1. **Simplicidad**: El código debe ser fácil de entender y modificar
2. **Educativo**: Cualquiera (no solo ingenieros) debe poder personalizar el comportamiento
3. **Modular pero no sobreinginerizado**: Separación clara de responsabilidades sin abstracciones innecesarias
4. **Reutilizable**: Plantilla clara para otros proyectos

## Reglas Fundamentales

### Lo que SI está permitido

- FastAPI y endpoints REST simples
- OpenRouter como proveedor LLM
- Configuración mediante variables de entorno
- Modelos Pydantic para validación
- Tests básicos unitarios
- Logging simple
- Documentación clara

### Lo que NO debe agregarse JAMÁS

- **RAG** (Retrieval Augmented Generation)
- **Embeddings** o vector stores
- **pgvector, Pinecone, Chroma, o cualquier BD vectorial**
- **PostgreSQL, MongoDB, Redis o cualquier BD compleja**
- **LangChain, LangGraph o frameworks de agentes**
- **CrewAI, Autogen o frameworks multi-agente**
- **MCP (Model Context Protocol)**
- **WebSockets o streaming**
- **Celery, colas o background jobs**
- **Microservicios**
- **Autenticación (OAuth, JWT, etc)**
- **Dashboards o interfaces web en el backend**
- **Multiple agentes o orquestación de agentes**
- **Supabase, Firebase o backends serverless complejos**

Document analysis in this starter uses direct context injection.
Do not introduce RAG, embeddings or vector databases unless explicitly requested.

La razón: Agregar cualquiera de estos haría el proyecto menos educativo, más difícil de mantener, y no se alinea con el objetivo de ser un starter simple.


## Cómo Personalizar el Comportamiento

El diseño permite cambiar el comportamiento del agente SIN modificar Python:

### 1. Cambiar instrucciones del agente
Editar: `agent/AGENT.md`

Este archivo contiene las instrucciones en lenguaje natural que el agente debe seguir. Puede ser editado por personas no técnicas.

### 2. Agregar o cambiar conocimiento
Editar: `agent/knowledge.md`

Este archivo contiene información que el agente puede usar para responder preguntas. Simple, sin RAG.

### 3. Cambiar modelo o configuración de OpenRouter
Variables de entorno en `.env`:

```
AGENT_MODEL=openrouter/auto
AGENT_FALLBACK_MODEL=openrouter/free
AGENT_USE_FALLBACK=true
AGENT_MAX_TOKENS=700
```

No hay nombres de modelos repartidos por el código.

## Estructura del Código

```
app/
├── main.py              # Aplicación FastAPI principal
├── core/config.py       # Configuración desde variables de entorno
├── llm/openrouter.py    # Cliente encapsulado de OpenRouter
├── schemas/chat.py      # Modelos Pydantic
├── agent/
│   ├── agent.py         # Lógica principal del agente
│   └── prompt_loader.py # Carga AGENT.md y knowledge.md
├── documents/
│   ├── parser.py        # Extracción en memoria (.pdf, .docx, .txt, .md, .csv)
│   └── validators.py    # Validación de formato, MIME y tamaño
├── api/
│   ├── health.py        # GET /health
│   └── chat.py          # POST /api/chat, POST /api/chat/document, GET /api/agent
```

Cada módulo tiene una responsabilidad clara.

## Consideraciones de Seguridad

- **NUNCA exponer OPENROUTER_API_KEY al frontend**
- La API key se usa únicamente en el backend
- CORS debe configurarse correctamente para permitir solo dominios conocidos
- No almacenar secretos en el código (usar .env)
- `.env` debe estar en `.gitignore`

## Pruebas

Las pruebas deben ser simples y unitarias:
- No hacer llamadas reales a OpenRouter en tests básicos
- Usar TestClient de FastAPI para endpoints

## Changelog y Decisiones

Cuando hagas cambios, actualiza esta sección para futuras sesiones:

- **v1.0.0 (2026-09-01)**: Versión inicial del starter
- **v1.1.0 (2026-09-02)**: Soporte de Document Analysis en memoria con inyección directa de contexto y chat frontend en React/TypeScript
