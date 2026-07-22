FROM python:3.12-slim

# psycopg2-binary ships its own libpq, so no build deps needed.
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Fly routes public traffic to this internal port (see fly.toml).
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8080}"]
