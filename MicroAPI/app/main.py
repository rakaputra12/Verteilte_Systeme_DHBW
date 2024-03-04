# Importieren der benötigten Module
from fastapi import FastAPI,HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
from dotenv import load_dotenv
import os

'''
Laden der Umgebungsvariablen aus der .env-Datei, aber bei der Ausführung
auf dem Kubernetes wird durch Configmap und Secrets ersetzt.
'''
load_dotenv()

# Abrufen von Umgebungsvariablen
COUCHDB_URL = os.environ.get('COUCHDB_URL')
DB_NAME = os.environ.get('DB_NAME')
COUCHDB_USERNAME = os.environ.get('COUCHDB_USERNAME')
COUCHDB_PASSWORD = os.environ.get('COUCHDB_PASSWORD')

# Initialisieren der FastAPI-App
app=FastAPI()

# Aktivieren von CORS für den Zugriff von der Frontend-Anwendung
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API-Endpunkt zum Abrufen von Daten basierend auf Parametern
@app.post("/api/v1/get_data")
def get_data(month: int = Query(..., description="Month (integer)", gt=1, lt=13),
                                day: int = Query(..., description="Day (integer)", gt=1, lt=32)):
    try:
         # Funktion für die Ausführung einer CouchDB-Mango-Abfrage
        def couchdb_mango_query(month, day):
            url = f"{COUCHDB_URL}/{DB_NAME}/_find"
            auth = (COUCHDB_USERNAME, COUCHDB_PASSWORD)

            query = {
                "selector": {"month": str(month-1), "day": str(day)},
                "fields": ["first", "name", "prof", "year", "month", "day"],
                "sort": [{"year": "asc"}]
            }

            headers = {"Content-Type": "application/json"}
            
            timeout = httpx.Timeout(2.0)

            # HTTP-Anfrage an die CouchDB senden
            response = httpx.post(url, auth=auth, json=query, headers=headers, timeout=timeout)

            # Überprüfen des HTTP-Statuscodes und Verarbeiten der Antwort
            if response.status_code == 200:
                result = response.json()
                if 'docs' in result:
                    return result['docs']
                else:
                    return []
            else:
                raise HTTPException(status_code=response.status_code, detail="Invalid credentials")
            
        # Überprüfen des HTTP-Statuscodes und Verarbeiten der Antwort
        results = couchdb_mango_query(month, day)

        formatted_results = [
            {
                "name": f"{doc.get('first', '')} {doc.get('name', '')}",
                "profession": doc.get("prof", ""),
                "born": f"{doc.get('day', '')}.{int(doc.get('month', '')) + 1}.{doc.get('year', '')}"
            }
            for doc in results
        ]

        # Überprüfen, ob Daten vorhanden sind, sonst HTTP 204 No Content zurückgeben
        if not formatted_results:
            raise HTTPException(status_code=204, detail="No content")
        return formatted_results
    except HTTPException as e:
        # HTTP-Fehler direkt weiterleiten
        raise e 
    except Exception as e:
        print(f"Exception occurred: {e}") 
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Einfacher Gesundheitsüberprüfungs-Endpunkt
@app.get("/health")
def health():
    return {"status": "UP"}