# IntelliWheels - AI Car Marketplace

An AI-powered car marketplace assistant for the Jordanian market. Features a chatbot (Google Gemini), rule-based price estimator, and car image analyzer.

## Features

- **AI Chatbot** - Powered by Google Gemini. Ask anything about cars, specs, comparisons, and the Jordanian market.
- **Price Estimator** - Crisp (rule-based) depreciation logic categorizing cars into Luxury, Premium, and Economic. Prices in JOD.
- **Vision Helper** - Upload a car photo and Gemini Vision identifies the make, model, year, and condition.
- **WhatsApp Integration** - Send chat responses and price estimates via WhatsApp using Twilio.

## Quick Start

`ash
cd IntelliWheels
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
copy .env.example .env       # then add your GEMINI_API_KEY
python manage.py migrate
python manage.py runserver
`

Open http://localhost:8000/

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat/` | POST | Send a message to the AI chatbot |
| `/api/estimate/` | POST | Get a price estimate for a car |
| `/api/makes/` | GET | List all known car makes |
| `/api/models/<make>/` | GET | List models for a make |
| `/api/vision/` | POST | Upload a car image for AI analysis |
| `/api/whatsapp/send/` | POST | Send a message via WhatsApp |

## Environment Variables

| Variable | Description |
|---|---|
| `GEMINI_API_KEY` | Google Gemini API key |
| `GEMINI_MODEL` | Gemini model name (default: gemini-2.0-flash) |
| `GEMINI_VISION_MODEL` | Gemini Vision model (default: gemini-2.0-flash) |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID (optional) |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token (optional) |
| `TWILIO_WHATSAPP_NUMBER` | Twilio WhatsApp sender number |
| `TWILIO_WHATSAPP_TO` | Default WhatsApp recipient number |

## Project Structure

`
IntelliWheels/
  config/           Django settings
  core/             Core app (models, views, templates)
    models/         CarListing, ChatSession, PriceEstimate, VisionAnalysis
    serializers/    REST serializers
    templates/      Frontend HTML
    tools/          WhatsApp Twilio integration
  api/              REST API endpoints
    views/          Chat, Price, Vision, WhatsApp views
  ai_engine/        AI components
    agents/         Car chatbot agent
    llm_client.py   Gemini client
    price_estimator.py   Crisp depreciation logic
    vision_helper.py     Gemini Vision image analysis
`

## Tech Stack

- Django 4.2 + Django REST Framework
- Google Gemini (google-generativeai)
- Twilio (WhatsApp)
- SQLite
- Pillow (image processing)

---
Built for the AI Engineer Course Capstone Project.
