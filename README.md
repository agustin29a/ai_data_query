# 🧠 Sistema NL-to-SQL con RAG

Un sistema completo de consultas en lenguaje natural a SQL que combina **RAG (Retrieval-Augmented Generation)**, **visualización automática de datos** y **gestión de conversaciones**. Construido con FastAPI, React y NestJS.

---

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Reference](#-api-reference)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## 🌟 Descripción General

Este sistema permite a los usuarios realizar consultas en lenguaje natural que se convierten automáticamente en SQL, ejecutan las consultas contra bases de datos PostgreSQL, generan visualizaciones apropiadas y mantienen un historial completo de conversaciones.

### Componentes del Sistema

1. **NL-to-SQL RAG API** (Backend Principal) - FastAPI
2. **Chat Model** (Frontend) - React + TypeScript
3. **Chat Session API** (Servicio de Persistencia) - NestJS + MongoDB

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                    Chat Model (React)                    │
│              Interface de Usuario Interactiva            │
└───────────────────┬─────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐       ┌──────────────────┐
│  NL-to-SQL    │◄─────►│  Chat Session    │
│   RAG API     │       │      API         │
│   (FastAPI)   │       │   (NestJS)       │
└───────┬───────┘       └────────┬─────────┘
        │                        │
        ▼                        ▼
┌───────────────┐       ┌──────────────────┐
│  PostgreSQL   │       │    MongoDB       │
│  (Data Store) │       │ (Conversations)  │
└───────────────┘       └──────────────────┘
        │
        ▼
┌───────────────┐
│  AWS Bedrock  │
│  (LLM Model)  │
└───────────────┘
```

---

## ✨ Características Principales

### 🎯 Core Features

- **💬 Conversión NL-to-SQL con RAG:** Traduce preguntas en lenguaje natural a consultas SQL optimizadas
- **📊 Visualización Automática:** Detecta y genera gráficos apropiados para los resultados
- **🗨️ Gestión de Sesiones:** Mantiene historial completo de conversaciones
- **🛡️ Validación de Seguridad:** Protección contra inyecciones SQL y operaciones peligrosas
- **🎨 Interfaz Moderna:** UI responsive con tema oscuro
- **⚡ Pipeline RAG Optimizado:** Selección inteligente de esquema para mejor rendimiento
- **🤖 Modelo Fine-Tuned:** Detección de gráficos con DistilBERT entrenado

### 📈 Visualizaciones Soportadas

- Gráficos de barras
- Gráficos de líneas
- Gráficos de dispersión
- Gráficos circulares
- Histogramas
- Gráficos de área
- Box plots

---

## 🛠 Tecnologías Utilizadas

### Backend Principal (NL-to-SQL RAG API)
- **FastAPI** - Framework web moderno
- **AWS Bedrock** - Servicio de LLM
- **PostgreSQL** - Base de datos principal
- **DistilBERT** - Modelo de detección de gráficos
- **Matplotlib/Seaborn** - Generación de visualizaciones

### Frontend (Chat Model)
- **React 18** - Biblioteca de UI
- **TypeScript** - Tipado estático
- **Vite** - Build tool
- **Ant Design** - Componentes de UI
- **React Syntax Highlighter** - Resaltado de código SQL

### Servicio de Persistencia (Chat Session API)
- **NestJS** - Framework de Node.js
- **MongoDB** - Base de datos de conversaciones
- **Mongoose** - ODM para MongoDB
- **class-validator** - Validación de datos

---

## 📁 Estructura del Proyecto

```
proyecto-raiz/
├── api_model_fast/              # Backend Principal
│   ├── app/
│   │   ├── main.py
│   │   ├── routes/
│   │   │   ├── rag_api.py
│   │   │   └── health.py
│   │   ├── services/
│   │   │   ├── rag/
│   │   │   │   ├── rag_pipeline.py
│   │   │   │   └── schema_selector.py
│   │   │   ├── bedrock_service.py
│   │   │   ├── chart_detector.py
│   │   │   ├── chart_service.py
│   │   │   └── security_validator.py
│   │   ├── models/
│   │   │   └── modelo_distilbert_mejorado/
│   │   └── config/
│   │       └── config.py
│   └── requirements.txt
│
├── chat_model/                  # Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   ├── Charts/
│   │   │   ├── Sidebar/
│   │   │   └── UI/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.ts
│
└── chat_session/                # Servicio de Persistencia
    ├── src/
    │   ├── main.ts
    │   ├── app.module.ts
    │   └── conversations/
    │       ├── conversations.controller.ts
    │       ├── conversations.service.ts
    │       ├── dto/
    │       ├── schemas/
    │       └── interfaces/
    └── package.json
```

---

## 🚀 Instalación

### Prerrequisitos

- **Node.js** 16+
- **Python** 3.9+
- **PostgreSQL** 12+
- **MongoDB** 4.4+
- **AWS Account** con acceso a Bedrock
- **Docker** (opcional)

### 1️⃣ Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd proyecto-raiz
```

### 2️⃣ Backend Principal (NL-to-SQL RAG API)

```bash
cd api_model_fast

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Volver al directorio raíz
cd ..
```

### 3️⃣ Frontend (Chat Model)

```bash
cd chat_model

# Instalar dependencias
npm install
# o
yarn install

# Volver al directorio raíz
cd ..
```

### 4️⃣ Servicio de Persistencia (Chat Session API)

```bash
cd chat_session

# Instalar dependencias
npm install
# o
yarn install

# Volver al directorio raíz
cd ..
```

---

## ⚙️ Configuración

### Backend Principal (api_model_fast/.env)

```env
DEBUG=False

# PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_username
DB_PASS=your_password

# AWS Bedrock
PROFILE_ARN=your_bedrock_profile_arn
AWS_REGION=us-east-2

# Security
SECRET_KEY=your_secret_key

# Google API (opcional)
GOOGLE_API_KEY=your_google_api_key

# Conversations Service
CONVERSATIONS_URL=http://localhost:3000
```

### Frontend (chat_model/.env)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_SESSIONS_API_BASE_URL=http://localhost:3000
```

### Servicio de Persistencia (chat_session/.env)

```env
MONGODB_URI=mongodb://localhost:27017/chat_sessions
PORT=3000
```

---

## 🎯 Uso

### Iniciar Todos los Servicios

#### 1. Backend Principal

```bash
cd api_model_fast
source venv/bin/activate  # En Windows: venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

#### 2. Servicio de Persistencia

```bash
cd chat_session
npm run start:dev
# o
yarn start:dev
```

#### 3. Frontend

```bash
cd chat_model
npm run dev
# o
yarn dev
```

### Acceder a la Aplicación

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Session API:** http://localhost:3000

---

## 📚 API Reference

### NL-to-SQL RAG API

#### **POST /rag/nl-to-sql**
Convierte pregunta en lenguaje natural a SQL con visualización.

**Request:**
```json
{
  "pregunta": "Muestra las ventas mensuales del último año",
  "id": "optional-conversation-id"
}
```

**Response:**
```json
{
  "pregunta": "Muestra las ventas mensuales del último año",
  "sql_generado": "SELECT DATE_TRUNC('month', fecha) as mes, SUM(monto) as ventas FROM ventas WHERE fecha >= NOW() - INTERVAL '1 year' GROUP BY mes ORDER BY mes",
  "confidence_score": 0.95,
  "resultados": {
    "columns": ["mes", "ventas"],
    "data": [["2023-01-01", 15000], ["2023-02-01", 18000]]
  },
  "chart": {
    "needs_chart": true,
    "chart_type": "line",
    "chart_image": "data:image/png;base64,...",
    "chart_generated": true
  },
  "status": "success"
}
```

### Chat Session API

#### **POST /conversations**
Crear nueva conversación.

```json
{
  "title": "Mi conversación",
  "messages": [
    {
      "isUser": true,
      "content": "Muestra las ventas"
    }
  ]
}
```

#### **POST /conversations/message**
Agregar mensaje a conversación existente.

```json
{
  "_id": "conversation_id",
  "isUser": false,
  "content": {
    "query_sql": "SELECT * FROM ventas",
    "query_result": [...],
    "chart_base64": "..."
  }
}
```

#### **GET /conversations/history/:session_id**
Obtener historial completo de conversación.

#### Más Endpoints

- `GET /conversations` - Listar todas las conversaciones
- `GET /conversations/:id` - Obtener conversación por ID
- `DELETE /conversations/:id` - Eliminar conversación
- `PATCH /conversations/:id` - Actualizar conversación

---

## 🛡️ Seguridad

### Validación SQL
- Filtrado de operaciones peligrosas (DROP, DELETE, UPDATE sin WHERE)
- Detección de patrones de inyección SQL
- Sanitización de consultas generadas

### Rate Limiting
- Protección contra abuso de API
- Límites configurables por endpoint

### CORS
- Orígenes configurables
- Control de métodos permitidos

---

## 🎨 Personalización

### Tema del Frontend

Edita `chat_model/src/config/antd-theme.config.ts`:

```typescript
export const appTheme: ThemeConfig = {
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorBgBase: '#0f0f0f',
    colorBgContainer: '#141414',
    // ... más personalizaciones
  }
};
```

### Modelo de Detección de Gráficos

El modelo DistilBERT fine-tuned se encuentra en:
```
api_model_fast/app/models/modelo_distilbert_mejorado/
```

## 🙏 Agradecimientos

- AWS Bedrock por el servicio de LLM
- La comunidad de FastAPI, React y NestJS

---

**Desarrollado usando FastAPI, React, NestJS y TypeScript**
