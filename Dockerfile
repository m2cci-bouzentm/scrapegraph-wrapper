FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && find /usr/local/lib/python3.12/site-packages/scrapegraphai -name "*.py" \
       -exec sed -i 's/from langchain_community.chat_models import ChatOllama/from langchain_ollama import ChatOllama/' {} + \
    && playwright install --with-deps chromium

COPY app.py .

EXPOSE 8091

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8091"]
