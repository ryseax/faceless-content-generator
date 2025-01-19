# Verwenden eines Basis-Images
FROM python:3.10-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
ENV OPENAI_API_KEY=PLACEHOLDER_API_KEY
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Flask auf Port 8080 starten
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "flask_API:app"]
