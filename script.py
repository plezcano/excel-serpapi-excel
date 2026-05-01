import sys
sys.stdout.reconfigure(line_buffering=True)

import os
import pandas as pd
import logging
import time
import serpapi
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger(__name__)

# === CONFIGURACION ===
EXCEL_FILE = "3. SEO_Website_DLS.xlsx"
COLUMNAS = ["keyword", "city", "state", "country"]
LIMITE_PRUEBA = 10  # ← Solo 10 keywords. Pon None cuando quieras procesar todas.
API_KEY = os.getenv("SERPAPI_KEY")

# Diccionario de estados USA
ESTADOS_USA = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
    "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
    "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
    "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
    "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming"
}

def validar_api_key():
    if not API_KEY:
        log.error("ERROR: SERPAPI_KEY no esta configurada en variables de entorno")
        sys.exit(1)
    log.info(f"API key cargada (termina en ...{API_KEY[-4:]})")

def normalizar_estado(estado):
    """Convierte 'CA' a 'California'. Si ya está completo, lo deja igual."""
    if pd.isna(estado):
        return estado
    estado_str = str(estado).strip()
    return ESTADOS_USA.get(estado_str.upper(), estado_str)

def leer_excel(ruta: str) -> pd.DataFrame:
    log.info(f"Abriendo archivo: {ruta}")
    if not Path(ruta).exists():
        raise FileNotFoundError(ruta)
    df = pd.read_excel(ruta, header=0)
    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    df = df[COLUMNAS].dropna(subset=["keyword"]).reset_index(drop=True)
    
    # Normalizar estados (CA -> California)
    df["state"] = df["state"].apply(normalizar_estado)
    
    log.info(f"Total filas en Excel: {len(df)}")
    
    if LIMITE_PRUEBA:
        df = df.head(LIMITE_PRUEBA)
        log.info(f"MODO PRUEBA: procesando solo las primeras {LIMITE_PRUEBA} filas")
    
    return df

def construir_location(city, state, country) -> str:
    partes = [str(p).strip() for p in [city, state, country] if pd.notna(p)]
    return ", ".join(partes)

def consultar_serp(client, keyword: str, location: str) -> dict:
    return client.search({
        "engine": "google",
        "q": keyword,
        "location": location,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us"
    })

def procesar(df: pd.DataFrame, client) -> list:
    resultados = []
    log.info(f"=== INICIANDO {len(df)} CONSULTAS A SERPAPI ===")
    
    for idx, fila in df.iterrows():
        keyword = fila["keyword"]
        location = construir_location(fila["city"], fila["state"], fila["country"])
        
        try:
            respuesta = consultar_serp(client, keyword, location)
            organic = respuesta.get("organic_results", [])
            log.info(f"[{idx + 1}/{len(df)}] OK | '{keyword}' @ {location} | {len(organic)} resultados")
            
            resultados.append({
                "keyword": keyword,
                "location": location,
                "status": "ok",
                "num_results": len(organic),
                "organic_results": organic
            })
        except Exception as e:
            log.error(f"[{idx + 1}/{len(df)}] ERROR | '{keyword}' @ {location} | {str(e)[:100]}")
            resultados.append({
                "keyword": keyword,
                "location": location,
                "status": "error",
                "error": str(e)
            })
        
        time.sleep(1)
    
    return resultados

def resumen(resultados: list):
    ok = sum(1 for r in resultados if r["status"] == "ok")
    err = sum(1 for r in resultados if r["status"] == "error")
    total_organicos = sum(r.get("num_results", 0) for r in resultados if r["status"] == "ok")
    
    log.info("=== RESUMEN FINAL ===")
    log.info(f"Consultas exitosas : {ok}")
    log.info(f"Consultas con error: {err}")
    log.info(f"Total resultados organicos obtenidos: {total_organicos}")
    log.info(f"Creditos SerpApi gastados: ~{ok + err}")

def main():
    validar_api_key()
    df = leer_excel(EXCEL_FILE)
    client = serpapi.Client(api_key=API_KEY)
    resultados = procesar(df, client)
    resumen(resultados)

if __name__ == "__main__":
    main()
