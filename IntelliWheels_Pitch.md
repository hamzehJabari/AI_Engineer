# 🚗 IntelliWheels

## AI-Powered Car Marketplace Assistant for Jordan

`CrewAI Flows` · `Gemini 2.0` · `Django REST` · `Twilio WhatsApp` · `Multi-Agent Orchestration`

> AI Engineer Course — Capstone Project — February 2026

---

## The Problem

Car buyers in Jordan face multiple challenges:

| | Challenge | Description |
|---|---|---|
| 💰 | **Price Opacity** | No standardized reference for used car valuations in JOD. Sellers set arbitrary prices — buyers can't verify. |
| 🔍 | **Information Fragmentation** | Specs, comparisons, and advice scattered across forums, Facebook groups, and word of mouth. |
| 📷 | **No Visual Identification** | Buyers see a car on the street and can't quickly identify what it is, what year, or what it's worth. |
| 📱 | **Accessibility Gap** | Technical car data isn't easily accessible to non-technical users, especially on mobile devices. |

---

## The Solution: IntelliWheels

4 AI-powered features in one platform:

| | Feature | Description |
|---|---|---|
| 🤖 | **AI Chatbot** | CrewAI multi-agent system powered by Gemini 2.0 Flash — Car advisor agent handles specs, comparisons, recommendations with Jordanian market focus (JOD pricing). |
| 📊 | **Price Estimator** | Crisp (rule-based) logic — 15 makes, 70+ models. Three depreciation tiers: Luxury (12%), Premium (10%), Economic (7%). |
| 👁️ | **Vision Helper** | CrewAI vision analyst agent + Gemini Vision API — Upload any car photo for instant AI identification of make, model, year, and condition. |
| 📲 | **WhatsApp Share** | Twilio API — Send chat replies and price estimates directly to WhatsApp for on-the-go access. |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Backend | Django 4.2 + REST Framework |
| Orchestration | **CrewAI Flows** (@start/@router/@listen) |
| Agents | **2 CrewAI Agents** (Car Advisor + Vision Analyst) |
| LLM | Google Gemini 2.0 Flash |
| LLM SDK | google-genai (new official SDK) + CrewAI LLM wrapper |
| Vision | CrewAI Vision Agent + Gemini Vision API |
| Price Logic | Crisp / rule-based (custom) |
| Messaging | Twilio WhatsApp Sandbox |
| Database | SQLite 3 |
| Frontend | HTML / CSS / JavaScript |
| Config | YAML (agents/tasks) + python-dotenv (.env) |

### Why These Choices?

- **CrewAI Flows** — Advanced multi-agent orchestration with @start/@router/@listen decorators for intelligent request routing
- **Django + DRF** — Battle-tested framework with admin, ORM, serializer validation
- **Gemini 2.0 Flash** — Fast, multimodal, production-ready with free tier
- **google-genai SDK** — New official SDK replacing deprecated google-generativeai
- **YAML Configuration** — Declarative agent/task configs following CrewAI best practices
- **Crisp logic** — Deterministic pricing — no hallucinated numbers
- **Twilio** — Industry-standard WhatsApp API with sandbox for prototyping

---

## System Architecture

```
┌─────────────────────────────────────────────────┐
│       🌐 Browser — Dark Cyberpunk UI            │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│    🚀 Django REST Framework — 7 API Endpoints   │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│   🔀 CarMarketplaceFlow — @start/@router        │
│        (Request Classification & Routing)       │
└──┬──────────────────────────┬──────────────┬────┘
   ▼                          ▼              ▼
┌─────────┐            ┌──────────┐    ┌─────────┐
│🤖 Chat  │            │👁️ Vision │    │📊 Crisp │
│  Crew   │            │  Crew    │    │ Logic   │
│(Advisor)│            │(Analyst) │    └────┬────┘
└────┬────┘            └────┬─────┘         │
     │                      │               │
     └──────────┬───────────┘               │
                ▼                           ▼
      ┌──────────────────┐    ┌─────────────────────┐
      │🧠 Gemini 2.0 API │    │🗄️ SQLite + WhatsApp │
      └──────────────────┘    └─────────────────────┘
```

### Data Flows

- **Chat:** User → ChatView → CarMarketplaceFlow → @router("chat") → CarChatCrew → Gemini 2.0 → ChatMessage → JSON
- **Price:** User → PriceEstimateView → `estimate_price()` crisp logic → PriceEstimate → JSON
- **Vision:** Image → VisionView → CarMarketplaceFlow → @router("vision") → VisionAnalysisCrew → Gemini Vision → VisionAnalysis → JSON
- **Combined:** User + Image → Flow → @router("chat_and_vision") → Both Crews (parallel) → Merged output → JSON
- **WhatsApp:** Click share → WhatsAppView → `send_whatsapp_message()` → Twilio API → Delivered

---

## API Design — 7 Endpoints

| Endpoint | Method | Description | Input |
|---|---|---|---|
| `/api/chat/` | POST | AI chatbot conversation | message, session_id (opt) |
| `/api/estimate/` | POST | Crisp logic price estimate | make, model, year, mileage |
| `/api/makes/` | GET | List all 15 car makes | — |
| `/api/models/<make>/` | GET | List models for a make | make (URL param) |
| `/api/vision/` | POST | Car image AI analysis | image (file upload) |
| `/api/whatsapp/send/` | POST | Send via WhatsApp | message, to (opt) |
| `/health/` | GET | Health check | — |

### Example: POST /api/estimate/

```json
// Request
{ "make": "toyota", "model": "camry", "year": 2020, "mileage_km": 80000 }

// Response
{ "depreciated_price_jod": 16213, "depreciation_pct": 35.1 }
```

### Example: POST /api/chat/

```json
// Request
{ "message": "Best car under 15K JOD?" }

// Response
{ "message": "For 15,000 JOD...", "model_used": "crewai-car-advisor" }
```

---

## CrewAI Flow Architecture

### Multi-Agent Orchestration Pattern

IntelliWheels uses **CrewAI Flows** to intelligently route requests to specialized AI agents:

```python
@start()
def classify_request(self):
    """Determine request type: chat, vision, or both"""
    # Returns: "chat" | "vision" | "chat_and_vision"

@router(classify_request)
def route_to_crew(self):
    """Route to appropriate crew based on classification"""
    return self.state.request_type

@listen("chat")
def run_chat_crew(self):
    """Execute CarChatCrew for text queries"""
    CarChatCrew().crew().kickoff(inputs={...})

@listen("vision")
def run_vision_crew(self):
    """Execute VisionAnalysisCrew for image analysis"""
    VisionAnalysisCrew().crew().kickoff(inputs={...})
```

### Two Specialized Crews

| | Crew | Agent | Config | Purpose |
|---|---|---|---|---|
| 🤖 | **CarChatCrew** | car_advisor | agents.yaml + tasks.yaml | Answers car questions, comparisons, recommendations for Jordanian market |
| 👁️ | **VisionAnalysisCrew** | vision_analyst | agents.yaml + tasks.yaml | Identifies car from photos, extracts make/model/year/condition |

### Why CrewAI Flows?

- **Intelligent Routing** — @router automatically selects the right agent(s)
- **Parallel Execution** — Can run both crews simultaneously for combined requests
- **State Management** — CarMarketplaceState (Pydantic) tracks context across steps
- **Declarative Config** — YAML-based agent/task definitions (no hardcoded prompts in code)
- **Course Pattern** — Follows agents_htu best practices (@start/@listen/@router)

---

## Crisp Price Estimator

> Deterministic, rule-based — no hallucinated prices

### Formula

```
Value = Base Price × (1 − rate)^age − Mileage Penalty
```

### Depreciation Categories

| Category | Rate | Examples |
|---|---|---|
| **LUXURY** | 12%/yr | S-Class, 7-Series, Cayenne |
| **PREMIUM** | 10%/yr | C-Class, 3-Series, A4 |
| **ECONOMIC** | 7%/yr | Camry, Elantra, Civic |

### Mileage Penalties

- \> 100,000 km → extra 5% deduction
- \> 200,000 km → extra 10% deduction
- Floor: never below 5% of base price

### Coverage

| 15 | 70+ | 3 |
|---|---|---|
| Car Makes | Models | Categories |

### Example Calculation

**Toyota Camry 2020 · 80,000 km**

| Step | Value |
|---|---|
| Category | Economic (7%/yr) |
| Base | 25,000 JOD |
| Age | 6 years → factor: 0.6485 |
| After age | 16,213 JOD |
| Mileage | under 100K → no penalty |
| **Final** | **16,213 JOD (35.1% depreciation)** |

---

## LLM Integration & Multi-Agent System

### Multi-Agent Architecture

**CarMarketplaceFlow (Orchestration Layer)**
| Decorator | Purpose |
|---|---|
| @start() | Classify request (chat/vision/both) based on inputs |
| @router() | Route to appropriate crew(s) |
| @listen("chat") | Execute CarChatCrew |
| @listen("vision") | Execute VisionAnalysisCrew |
| or_() | Merge results from parallel crew executions |

**GeminiClient (LLM Layer)**
| Property | Value |
|---|---|
| SDK | google-genai (new official SDK) |
| Model | gemini-2.0-flash |
| Pattern | Singleton instance (one client, all requests) |
| Methods | `chat()` + `analyze_image()` |

### Key Features

- **System instructions** — Jordanian market specialization via GenerateContentConfig
- **Multi-turn** — Full conversation history with Content/Part objects
- **Vision** — `Part.from_bytes()` for image analysis
- **Mock mode** — Works without API key (returns setup instructions)
- **Rate limit handling** — 429 errors → friendly message, no crashes

### CrewAI Agents — Capabilities

**1. Car Advisor Agent (CarChatCrew)**
- Configured via YAML (agents.yaml + tasks.yaml)
- Car specs & comparisons
- Budget recommendations (JOD)
- Category explanations (Luxury/Premium/Economic)
- Price guidance → redirect to estimator
- Maintenance & import tips for Jordan
- Politely redirects non-car questions

**2. Vision Analyst Agent (VisionAnalysisCrew)**
- Configured via YAML (agents.yaml + tasks.yaml)
- Receives raw Gemini Vision output
- Structures and validates JSON output
- Extracts: make, model, year, color, condition, body style
- Generates human-readable condition summary

### Session Management

- Each conversation → unique ChatSession
- Every message saved as ChatMessage
- Full history sent to Gemini for context
- Frontend tracks `session_id` for continuity

---

## Vision Analysis & WhatsApp

### 👁️ CrewAI Vision Analysis Pipeline

| Property | Value |
|---|---|
| Input | Car photo (JPEG/PNG/WebP) |
| Step 1 | Gemini Vision API (`Part.from_bytes()`) |
| Step 2 | VisionAnalysisCrew processes raw output |
| Output | Structured JSON: Make, Model, Year, Color, Condition, Body Style |
| Config | YAML-based agent (vision_analyst) |

**Processing Pipeline:**
1. Image uploaded → Gemini Vision generates raw description
2. VisionAnalysisCrew agent receives raw description
3. Agent extracts and structures: make, model, year, condition
4. JSON parsing with fallback for malformed responses
5. All results saved to VisionAnalysis model

**Advantages of CrewAI Approach:**
- Separation of concerns (vision → structured extraction)
- Consistent JSON output via agent task configuration
- Easy to iterate on extraction logic via YAML
- Agent can handle ambiguous or partial vision outputs

### 📲 Twilio WhatsApp Integration

| Property | Value |
|---|---|
| Provider | Twilio WhatsApp Sandbox |
| Pattern | Follows agents_htu-main project |
| Sender | +14155238886 (sandbox) |
| Recipient | Configurable via .env |

**Features:**
- Auto-add `whatsapp:` prefix to numbers
- Share chat responses with one click
- Share price estimates with one click
- Error 63007 handling (invalid sender)
- Toast notifications for send status

---

## Database Schema — 5 Models

| | Model | Fields |
|---|---|---|
| 🚗 | **CarListing** | make, model, year, mileage_km, fuel_type, transmission, category, color, prices, description, is_sold |
| 💬 | **ChatSession** | started_at, ended_at, summary ← has many ChatMessages |
| 💬 | **ChatMessage** | session (FK), role (user/assistant), content, created_at |
| 📊 | **PriceEstimate** | make, model, year, mileage_km, category, original_price_jod, depreciated_price, breakdown (JSON) |
| 👁️ | **VisionAnalysis** | image (file), detected_make, detected_model, detected_year, condition_summary, raw_response |

> SQLite database · Django ORM · All records persisted and inspectable via `/admin/`

---

## Safety & Performance

| | Feature | Details |
|---|---|---|
| 🔒 | **Input Validation** | DRF serializers validate all inputs. Image MIME whitelist. Year 1980–2026. Message max 5000 chars. |
| ⚡ | **Rate Limit Handling** | Gemini 429/RESOURCE_EXHAUSTED caught → friendly message. No crashes on quota exhaustion. |
| 📋 | **Structured Logging** | 3 loggers (core, api, ai_engine). app.log + errors.log. Verbose format with PID/thread. |
| 🛡️ | **CORS & CSRF** | CORS restricted in production. CSRF middleware active. Auth validators enabled. |
| 🔄 | **Graceful Fallbacks** | Mock responses (no API key). Vision JSON parse fallback. Floor price (5% of base). |
| 📦 | **Data Persistence** | All chats, estimates, and vision results saved. Django Admin for full data inspection. |

---

## Capstone Requirements ✓

### Core Requirements

- ✅ Use case design (car marketplace for Jordan)
- ✅ Django project + API endpoints (7 endpoints)
- ✅ Core LLM logic (Gemini 2.0 via google-genai SDK)
- ✅ Multi-agent system (2 CrewAI agents + Flow orchestration)
- ✅ Agent capabilities (Car Advisor + Vision Analyst)
- ✅ WhatsApp connection (Twilio API)
- ✅ Debugging & error handling (logging + fallbacks)
- ✅ Performance & safety checks (validation + rate limits)
- ✅ Technical documentation (TECHNICAL_DOCUMENTATION.docx)
- ✅ Final pitch presentation (this deck)

### Bonus Features

- ✅ **CrewAI Flow orchestration** (@start/@router/@listen pattern)
- ✅ **YAML-based agent configuration** (agents.yaml + tasks.yaml)
- ✅ **Multi-agent collaboration** (chat + vision crews can run in parallel)
- ✅ Computer Vision (CrewAI Vision Agent + Gemini Vision API)
- ✅ Crisp logic estimator (rule-based, 70+ models)
- ✅ Modern UI (dark cyberpunk theme)
- ✅ Session management (multi-turn conversations)
- ✅ Django Admin (all 5 models registered)
- ✅ .env configuration (load_dotenv override)
- ✅ .gitignore + .env.example + README.md
- ✅ Mock fallback mode (works without API key)
- ✅ Health check endpoint (/health/)

---

## Live Demo

Open **localhost:8000**

| Step | Action |
|---|---|
| 💬 **1. Chat** | "What's the best car for a family of 5 under 20K JOD?" |
| 💰 **2. Price Estimator** | Toyota → Camry → 2020 → 80,000 km |
| 📷 **3. Vision** | Upload any car photo → instant AI identification |
| 📲 **4. WhatsApp** | Click "Send via WhatsApp" → check your phone |

> All features are live and connected to real APIs

---

## 🚗✨ Thank You!

**IntelliWheels — Multi-Agent AI Car Marketplace for Jordan**

| 7 | 2 | 70+ | 4 | 5 |
|---|---|---|---|---|
| API Endpoints | CrewAI Agents | Car Models | AI Features | DB Models |

> AI Engineer Course — Capstone Project — February 2026

**❓ Questions?**
