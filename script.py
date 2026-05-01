import pandas as pd
import logging
from pathlib import Path

# Logging que escribe a archivo Y a consola
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('payloads_log.txt', mode='w', encoding='utf-8'),
        logging.StreamHandler()
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
    log.info(f"Filas a procesar: {len(df)}\n")
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
    log.info("=== SIMULACION DE ENVIO A SERPAPI ===\n")
    for idx, fila in df.iterrows():
        keyword = fila["keyword"]
        location = construir_location(fila["city"], fila["state"], fila["country"])
        payload = construir_payload(keyword, location)
        
        log.info(f"[{idx + 1}/{len(df)}] Payload:")
        for clave, valor in payload.items():
            log.info(f"    {clave:15} -> {valor}")
        log.info("")

def main():
    df = leer_excel(EXCEL_FILE)
    simular_envio(df)
    log.info("=== Lectura completa ===")

if __name__ == "__main__":
    main()
