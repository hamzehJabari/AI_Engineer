# IntelliWheels - AI Car Marketplace

An AI-powered car marketplace assistant for the Jordanian market. Features multi-agent orchestration with CrewAI, a chatbot (Google Gemini), rule-based price estimator, car image analyzer, and WhatsApp integration.

## Features

- **AI Chatbot Agent** - Powered by Google Gemini via CrewAI. Ask anything about cars, specs, comparisons, and the Jordanian market.
- **Vision Analysis Agent** - Upload a car photo and the CrewAI vision agent identifies the make, model, year, and condition using Gemini Vision.
- **Price Estimator** - Crisp (rule-based) depreciation logic categorizing cars into Luxury, Premium, and Economic. Prices in JOD.
- **Multi-Agent Orchestration** - CrewAI crews and flows coordinate the car chat agent and vision agent with routing logic.
- **WhatsApp Integration** - Send chat responses and price estimates via WhatsApp using Twilio.
- **Swagger / OpenAPI Docs** - Interactive API documentation with Swagger UI, ReDoc, and downloadable OpenAPI 3.0 schema.

## Architecture

```
Browser (HTML/JS)
    │
    ▼
Django REST Framework (api/views/)
    │
    ├── ChatView ──► CarChatbotAgent ──► GeminiClient ──► Gemini API
    │                    or
    │                CarChatbotCrewAgent ──► CarChatCrew (CrewAI) ──► Gemini
    │
    ├── PriceEstimateView ──► estimate_price() (crisp logic, no AI)
    │
    ├── VisionAnalyzeView ──► analyze_car_image() ──► GeminiClient ──► Gemini Vision
    │                             or
    │                         analyze_car_image_crew() ──► VisionAnalysisCrew (CrewAI)
    │
    └── WhatsAppSendView ──► Twilio API
```

## Quick Start

```bash
cd Marketplace_AI
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # then add your GEMINI_API_KEY
python manage.py migrate
python manage.py runserver
```

Open http://localhost:8000/

## API Documentation

| URL | Description |
|---|---|
| `/api/docs/` | **Swagger UI** - Interactive API explorer |
| `/api/redoc/` | **ReDoc** - Clean, readable API reference |
| `/api/schema/` | **OpenAPI 3.0 Schema** - Downloadable JSON/YAML schema |

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat/` | POST | Send a message to the AI chatbot agent |
| `/api/estimate/` | POST | Get a price estimate for a car |
| `/api/makes/` | GET | List all known car makes |
| `/api/models/<make>/` | GET | List models for a make |
| `/api/vision/` | POST | Upload a car image for AI vision agent analysis |
| `/api/whatsapp/send/` | POST | Send a message via WhatsApp |

## Project Structure

```
Marketplace_AI/
├── ai_engine/                  AI components
│   ├── agents/                 Agent classes (direct + CrewAI wrappers)
│   │   └── car_chatbot.py      CarChatbotAgent + CarChatbotCrewAgent
│   ├── crews/                  CrewAI crew definitions
│   │   ├── car_chat_crew/      Car advisor crew
│   │   │   ├── config/         agents.yaml + tasks.yaml
│   │   │   └── crew.py         CarChatCrew (CrewBase)
│   │   └── vision_crew/        Vision analyst crew
│   │       ├── config/         agents.yaml + tasks.yaml
│   │       └── crew.py         VisionAnalysisCrew (CrewBase)
│   ├── flows/                  CrewAI flow orchestration
│   │   └── car_marketplace/    Multi-agent flow
│   │       ├── schema.py       Pydantic state model
│   │       └── flow.py         CarMarketplaceFlow (routing + orchestration)
│   ├── prompts/                Prompt engineering (.md files)
│   │   ├── car_chatbot_system.md
│   │   └── vision_analysis.md
│   ├── tools/                  LLM configuration
│   │   └── __init__.py         gemini_llm + gemini_vision_llm (CrewAI LLM)
│   ├── llm_client.py           Low-level Gemini SDK wrapper (GeminiClient)
│   ├── price_estimator.py      Crisp depreciation logic (no AI)
│   └── vision_helper.py        Vision analysis (direct + crew)
├── api/                        REST API endpoints
│   └── views/                  Chat, Price, Vision, WhatsApp views
├── core/                       Django core app
│   ├── models/                 Database models (ORM)
│   ├── serializers/            Input validation
│   ├── templates/              Frontend HTML
│   └── tools/                  WhatsApp Twilio integration
└── config/                     Django settings
```

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name (default: gemini-2.5-flash) |
| `GEMINI_VISION_MODEL` | Gemini Vision model (default: gemini-2.5-flash) |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (optional) |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (optional) |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp sender number |
| `TWILIO_WHATSAPP_TO` | Default WhatsApp recipient number |

## Tech Stack

- Django 4.2 + Django REST Framework
- CrewAI (multi-agent orchestration)
- Google Gemini (google-genai SDK) — text + vision
- drf-spectacular (Swagger / OpenAPI 3.0)
- Twilio (WhatsApp)
- SQLite
- Pillow (image processing)

---
Built for the AI Engineer Course Capstone Project.
