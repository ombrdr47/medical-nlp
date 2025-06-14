FROM python:3.10-slim
WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential python3-dev gcc g++ libatlas-base-dev libblas-dev liblapack-dev libffi-dev pkg-config \
 && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel cython

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY medical-nlp-streamlit.py .

EXPOSE 8501
CMD ["streamlit","run","medical-nlp-streamlit.py","--server.port","8501","--server.headless","true"]
