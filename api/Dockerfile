FROM python:3.10-slim

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential python3-dev gcc g++ libatlas-base-dev libblas-dev liblapack-dev libffi-dev pkg-config \
 && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel cython

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_sm

COPY medical_nlp_pipeline.py medical_nlp_api.py ./

EXPOSE 8000
CMD ["uvicorn", "medical_nlp_api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
