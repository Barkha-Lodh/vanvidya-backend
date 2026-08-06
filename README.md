# ⚙️ VanVidya – Backend (API & Data Layer)

Backend service powering the VanVidya Android app — handles plant/mushroom data, 
disease detection logic, and AI-enriched content.

🔗 Frontend repo: [VanVidya-Frontend](https://github.com/Barkha-Lodh/vanvidya-frontend)

## 🛠️ Tech Stack
- **Framework:** Django REST Framework
- **Database:** PostgreSQL
- **APIs integrated:** Google Gemini API, Groq API, Wikipedia API

## ✨ Features
- 🔗 Provides REST endpoints for plant/mushroom disease and toxicity data
- 💧 Generates personalized care tips (watering, sunlight, soil) based on plant type
- ☀️ Cross-references sensor-based light data to recommend suitable plants
- 🤖 Enriches responses with AI-generated facts using Gemini and Groq APIs
- 📲 Serves data consumed by the Android frontend app

## ⚙️ How It Works (Backend Perspective)
1. 📥 Receives species identification data from the frontend (via Plant.id API results)
2. 🔍 Looks up disease/toxicity and care information in PostgreSQL
3. 🤖 Calls Gemini/Groq APIs to generate additional AI facts
4. 📤 Returns a structured response to the frontend app

## 🔌 API Endpoints
*(List your key endpoints here, e.g. /api/plant-info/, /api/care-tips/, etc.)*
