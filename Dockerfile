FROM python:3.11-slim

WORKDIR /app

# 1. Copy requirements FIRST so Docker caches dependencies.
# This makes future builds take seconds, not minutes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the rest of the app code
COPY . .

# 3. RUN COMMAND (Shell Form)
# Crucial: Do NOT use brackets [ ] or quotes " " around the command.
# This allows $PORT to be read correctly as a number.
CMD uvicorn main:app --host 0.0.0.0 --port $PORT