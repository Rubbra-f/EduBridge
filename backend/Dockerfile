FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY requirements-api.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api_server.py ./api_server.py
COPY cdacdm ./cdacdm
COPY configs ./configs
COPY artifacts/model ./artifacts/model
COPY artifacts/assessment ./artifacts/assessment
EXPOSE 8000
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]

COPY assessment_content.py ./assessment_content.py
COPY content ./content
