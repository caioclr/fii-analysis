from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes_fii import router as fii_router
from src.api.routes_settings import router as settings_router
from src.database.connection import init_db

# Inicializa o banco SQLite se necessário
init_db()

app = FastAPI(
    title="Analisys - FII Intelligence & Valuation Terminal API",
    description="API REST de alto desempenho para Screener de FIIs, Auditoria Fundamentalista, Séries B3 e Simulação de Valuation.",
    version="2.0.0"
)

# Configuração de CORS para permitir requisições do frontend Vite e locais
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5533",
        "http://127.0.0.1:5533",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rotas
app.include_router(fii_router)
app.include_router(settings_router)

@app.get("/api/health")
def healthcheck():
    return {
        "status": "healthy",
        "system": "Analisys FII Terminal",
        "version": "2.0.0"
    }

import os
from fastapi.staticfiles import StaticFiles

# Se a pasta frontend/dist existir, serve o frontend SPA compilado na raiz
dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

