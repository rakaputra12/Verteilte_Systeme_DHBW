# Verwenden das offizielle Python 3.9 slim-Image als Basisimage
FROM python:3.9-slim

# Setzen das Arbeitsverzeichnis innerhalb des Containers auf /app und Kopieren den Inhalt in den Container
WORKDIR /app
COPY . /app

# Installiere die Python-Abhängigkeiten, die in requirements.txt aufgelistet sind
RUN pip install -r requirements.txt

# Belichte Port 8000, um die Kommunikation mit dem Webserver im Container zu ermöglichen
EXPOSE 8000

# Befehl, der beim Starten des Containers ausgeführt wird
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
