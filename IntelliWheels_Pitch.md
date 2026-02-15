# 🚗 IntelliWheels

## AI-Powered Car Marketplace Assistant for Jordan

`Gemini 2.5` · `Django REST` · `Twilio WhatsApp` · `Crisp Logic` · `Vision AI`

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
| 🤖 | **AI Chatbot** | Google Gemini 2.5 Flash — Ask anything about cars: specs, comparisons, recommendations. Jordanian market focus with JOD pricing. |
| 📊 | **Price Estimator** | Crisp (rule-based) logic — 15 makes, 70+ models. Three depreciation tiers: Luxury (12%), Premium (10%), Economic (7%). |
| 👁️ | **Vision Helper** | Gemini Vision API — Upload any car photo and instantly identify make, model, year, and visible condition. |
| 📲 | **WhatsApp Share** | Twilio API — Send chat replies and price estimates directly to WhatsApp for on-the-go access. |

---

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| Backend | Django 4.2 + REST Framework |
| LLM | Google Gemini 2.5 Flash |
| LLM SDK | google-genai (new official SDK) |
| Vision | Gemini Vision API |
| Price Logic | Crisp / rule-based (custom) |
| Messaging | Twilio WhatsApp Sandbox |
| Database | SQLite 3 |
| Frontend | HTML / CSS / JavaScript |
| Config | python-dotenv (.env) |

### Why These Choices?

- **Django + DRF** — Battle-tested framework with admin, ORM, serializer validation
- **Gemini 2.5 Flash** — Fast, multimodal, free tier suitable for development
- **google-genai SDK** — New official SDK replacing deprecated google-generativeai
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
└──┬──────────┬──────────┬──────────┬─────────────┘
   ▼          ▼          ▼          ▼
┌──────┐  ┌───────┐  ┌───────┐  ┌─────────┐
│🤖 Car│  │📊Crisp│  │👁️Gemini│ │📲Twilio │
│Chatbot│  │Logic  │  │Vision │  │WhatsApp │
└──┬───┘  └───┬───┘  └───┬───┘  └────┬────┘
   ▼          ▼          ▼           ▼
┌─────────────────────┐  ┌───────────────────────┐
│🗄️ SQLite — Records  │  │🧠 Gemini API (genai)  │
└─────────────────────┘  └───────────────────────┘
```

### Data Flows

- **Chat:** User → ChatView → CarChatbotAgent → GeminiClient → Gemini API → ChatMessage → JSON
- **Price:** User → PriceEstimateView → `estimate_price()` crisp logic → PriceEstimate → JSON
- **Vision:** Image → VisionView → `analyze_car_image()` → Gemini Vision → VisionAnalysis → JSON
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
{ "message": "For 15,000 JOD...", "model_used": "gemini-2.5-flash" }
```

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

## LLM Integration & Agent

### GeminiClient Architecture

| Property | Value |
|---|---|
| SDK | google-genai (new official SDK) |
| Model | gemini-2.5-flash |
| Pattern | Singleton instance (one client, all requests) |
| Methods | `chat()` + `analyze_image()` |

### Key Features

- **System instructions** — Jordanian market specialization via GenerateContentConfig
- **Multi-turn** — Full conversation history with Content/Part objects
- **Vision** — `Part.from_bytes()` for image analysis
- **Mock mode** — Works without API key (returns setup instructions)
- **Rate limit handling** — 429 errors → friendly message, no crashes

### CarChatbotAgent — System Prompt Capabilities

- Car specs & comparisons
- Budget recommendations (JOD)
- Category explanations (Luxury/Premium/Economic)
- Price guidance → redirect to estimator
- Maintenance & import tips for Jordan
- Politely redirects non-car questions

### Session Management

- Each conversation → unique ChatSession
- Every message saved as ChatMessage
- Full history sent to Gemini for context
- Frontend tracks `session_id` for continuity

---

## Vision Analysis & WhatsApp

### 👁️ Gemini Vision Helper

| Property | Value |
|---|---|
| Input | Car photo (JPEG/PNG/WebP) |
| Output | Make, Model, Year, Condition |
| Method | `Part.from_bytes()` → Gemini Vision |
| Prompt | Structured JSON output format |

**Response Parsing:**
- Parse JSON from Gemini response
- Strip markdown code fences if present
- Fallback: raw text → condition field
- All results saved to VisionAnalysis model

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
- ✅ Core LLM logic (Gemini via google-genai SDK)
- ✅ Agent capabilities (CarChatbotAgent)
- ✅ WhatsApp connection (Twilio API)
- ✅ Debugging & error handling (logging + fallbacks)
- ✅ Performance & safety checks (validation + rate limits)
- ✅ Technical documentation (TECHNICAL_DOCUMENTATION.docx)
- ✅ Final pitch presentation (this deck)

### Bonus Features

- ✅ Computer Vision (Gemini Vision API)
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

**IntelliWheels — AI Car Marketplace for Jordan**

| 7 | 70+ | 4 | 5 |
|---|---|---|---|
| API Endpoints | Car Models | AI Features | DB Models |

> AI Engineer Course — Capstone Project — February 2026

**❓ Questions?**
