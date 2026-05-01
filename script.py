import sys
sys.stdout.reconfigure(line_buffering=True)

import pandas as pd
import logging
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('payloads_log.txt', mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
log = logging.getLogger(__name__)

EXCEL_FILE = "3. SEO_Website_DLS.xlsx"
COLUMNAS = ["keyword", "city", "state", "country"]

def leer_excel(ruta: str) -> pd.DataFrame:
    log.info(f"Abriendo archivo: {ruta}")
    if not Path(ruta).exists():
        raise FileNotFoundError(ruta)
    df = pd.read_excel(ruta, header=0)
    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    df = df[COLUMNAS].dropna(subset=["keyword"]).reset_index(drop=True)
    log.info(f"Filas a procesar: {len(df)}")
    return df

def construir_location(city, state, country) -> str:
    partes = [str(p).strip() for p in [city, state, country] if pd.notna(p)]
    return ", ".join(partes)

def construir_payload(keyword: str, location: str) -> dict:
    return {
        "engine": "google",
        "q": keyword,
        "location": location,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us"
    }

def simular_envio(df: pd.DataFrame):
    log.info("=== SIMULACION DE ENVIO A SERPAPI ===")
    
    for idx, fila in df.iterrows():
        keyword = fila["keyword"]
        location = construir_location(fila["city"], fila["state"], fila["country"])
        payload = construir_payload(keyword, location)
        
        # UNA sola línea por fila — payload completo en formato compacto
        log.info(f"[{idx + 1}/{len(df)}] q='{payload['q']}' | location='{payload['location']}' | hl={payload['hl']} | gl={payload['gl']} | engine={payload['engine']} | domain={payload['google_domain']}")
        
        # Pausa pequeña cada 100 filas para no saturar Railway
        if (idx + 1) % 100 == 0:
            time.sleep(0.5)
    
    log.info("=== Lectura completa ===")

def main():
    df = leer_excel(EXCEL_FILE)
    simular_envio(df)

if __name__ == "__main__":
    main()
