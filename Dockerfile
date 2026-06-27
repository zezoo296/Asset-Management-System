FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/app
ENV ALEMBIC_CONFIG=/app/alembic.ini

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && cd /app/app && uvicorn main:app --host 0.0.0.0 --port 8000"]
