# 🏥 Medical NLP Pipeline

An AI system for **medical transcription**, **NLP-based summarization**, **sentiment & intent analysis**, and **SOAP‐note generation**, built with **FastAPI** (backend) and **Streamlit** (frontend). Packaged via **Docker Compose** for one-command setup.

---

## 🔗 Live Demo

▶️ [View the live app here](http://3.84.120.27:8501/)

---


## 🚀 Quickstart

### 1. Clone & Configure

```bash
git clone https://github.com/YOUR_USERNAME/medical-nlp.git
cd medical-nlp
````

Copy the example environment file and edit if needed:

```bash
cp .env.example .env
# .env contents:
# API_BASE_URL=http://localhost:8000/api/v1
# WS_URL=ws://localhost:8000/ws/transcribe-stream
```

### 2. Run with Docker Compose

```bash
docker-compose up -d --build
```

* **API** →  `http://localhost:8000/docs`
* **UI**  →  `http://localhost:8501`

### 3. (Optional) Run Locally Without Docker

```bash
# Backend
cd api
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn medical_nlp_api:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd ../streamlit
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run medical_nlp_streamlit.py
```

---

## 🚨 Usage

### API Endpoints

* **Health Check**
  `GET /`
  *Response:*

  ```json
  { "status": "healthy", "service": "Medical NLP Pipeline API", "version": "1.0.0", "timestamp": "..." }
  ```

* **Analyze Conversation (Sync)**
  `POST /api/v1/analyze`
  *Body:*

  ```json
  {
    "conversation_text": "Doctor: … Patient: …",
    "patient_id": "PAT-12345",
    "encounter_date": "2025-06-11T10:00:00",
    "settings": { "include_confidence_scores": true }
  }
  ```

  *Response:* full `AnalysisResponse` JSON (entities, summary, sentiment, SOAP, metrics)

* **Analyze Conversation (Async)**
  `POST /api/v1/analyze/async`
  *Same body as `/analyze`*
  *Response:*

  ```json
  { "job_id": "…", "status": "pending", "message": "Job submitted", "result_url": "/api/v1/jobs/{job_id}" }
  ```

* **Get Job Status**
  `GET /api/v1/jobs/{job_id}`
  *Response:* status + result when complete

* **Extract Entities**
  `POST /api/v1/entities/extract`
  *Body:* `{ "text": "…" }`
  *Response:* `{ "entities": […], "count": N }`

* **Sentiment & Intent**
  `POST /api/v1/sentiment/analyze`
  *Body:* `{ "text": "…" }`
  *Response:*

  ```json
  {
    "text": "...",
    "sentiment": "Anxious",
    "confidence": 0.85,
    "intent": "Seeking reassurance",
    "intent_confidence": 0.80,
    "emotional_indicators": ["anxious:worried"]
  }
  ```

* **Generate SOAP Note**
  `POST /api/v1/soap/generate`
  *Same body as `/analyze`*
  *Response:* `SOAPResponse` JSON

* **Model Info**
  `GET /api/v1/models/info`
  *Response:* metadata about loaded NER, sentiment, summarizer, and SOAP models

* **WebSocket (Real-time Entities)**
  `WebSocket /ws/transcribe-stream`
  *Send:* plain text
  *Receive:* JSON messages of extracted entities or errors

---

## 📷 Screenshots

1. **Streamlit UI**
   ![Streamlit UI](./docs/streamlit_screenshot.png)

2. **FastAPI Swagger Docs** (`/docs`)
   ![Swagger UI](./docs/swagger_screenshot.png)

3. **Sample JSON Response**
   ![API Response](./docs/api_response_screenshot.png)

*(Place your actual screenshots under `docs/` and update paths above.)*

---

## ⚙️ Methodology

1. **NER & Keywords**

   * spaCy / custom BioBERT NER for Symptoms, Diagnoses, Treatments
   * KeyBERT for keyword extraction

2. **Summarization**

   * HuggingFace `facebook/bart-large-cnn`

3. **Sentiment & Intent**

   * `emilyalsentzer/Bio_ClinicalBERT-med-sentiment`
   * Fine-tuned BERT head for intent classes

4. **SOAP-Note Generation**

   * Rule-based + T5-based prompt engineering

---