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
LIMITE_PRUEBA = 10
API_KEY = os.getenv("SERPAPI_KEY")
TOP_RESULTS = 5  # ← Solo guardar las primeras 5 posiciones de cada SERP

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
        log.error("ERROR: SERPAPI_KEY no esta configurada")
        sys.exit(1)
    log.info(f"API key cargada (termina en ...{API_KEY[-4:]})")

def normalizar_estado(estado):
    if pd.isna(estado):
        return estado
    estado_str = str(estado).strip()
    return ESTADOS_USA.get(estado_str.upper(), estado_str)

def leer_excel(ruta: str) -> pd.DataFrame:
    log.info(f"Abriendo archivo: {ruta}")
    if not Path(ruta).exists():
        raise FileNotFoundError(ruta)
    df = pd.read_excel(ruta, header=0)
    df = df[COLUMNAS].dropna(subset=["keyword"]).reset_index(drop=True)
    df["state"] = df["state"].apply(normalizar_estado)
    log.info(f"Total filas en Excel: {len(df)}")
    if LIMITE_PRUEBA:
        df = df.head(LIMITE_PRUEBA)
        log.info(f"MODO PRUEBA: procesando solo las primeras {LIMITE_PRUEBA} filas")
    return df

def construir_location(city, state, country) -> str:
    partes = [str(p).strip() for p in [city, state, country] if pd.notna(p)]
    return ", ".join(partes)

def extraer_top_resultados(organic_results: list, top_n: int) -> list:
    """Extrae solo los campos que nos interesan de cada resultado."""
    extraidos = []
    for r in organic_results[:top_n]:
        extraidos.append({
            "position": r.get("position"),
            "title": r.get("title", ""),
            "link": r.get("link", ""),
            "displayed_link": r.get("displayed_link", ""),
            "snippet": r.get("snippet", "")
        })
    return extraidos

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
            top = extraer_top_resultados(organic, TOP_RESULTS)
            
            log.info(f"[{idx + 1}/{len(df)}] OK | '{keyword}' | top {len(top)} extraidos de {len(organic)}")
            
            resultados.append({
                "keyword": keyword,
                "city": fila["city"],
                "state": fila["state"],
                "country": fila["country"],
                "location": location,
                "status": "ok",
                "top_results": top
            })
        except Exception as e:
            log.error(f"[{idx + 1}/{len(df)}] ERROR | '{keyword}' | {str(e)[:80]}")
            resultados.append({
                "keyword": keyword,
                "location": location,
                "status": "error",
                "error": str(e)
            })
        
        time.sleep(1)
    
    return resultados

def mostrar_muestra(resultados: list):
    """Imprime un vistazo de la primera consulta exitosa para verificar formato."""
    primera_ok = next((r for r in resultados if r["status"] == "ok"), None)
    if not primera_ok:
        log.info("No hay resultados exitosos para mostrar muestra.")
        return
    
    log.info("=== MUESTRA: primera keyword exitosa ===")
    log.info(f"Keyword: {primera_ok['keyword']}")
    log.info(f"Location: {primera_ok['location']}")
    log.info(f"Top {len(primera_ok['top_results'])} resultados:")
    for r in primera_ok["top_results"]:
        log.info(f"  #{r['position']} | {r['title'][:60]}")
        log.info(f"        URL: {r['link'][:80]}")
        time.sleep(0.1)  # pausa pequeña para no saturar logs

def resumen(resultados: list):
    ok = sum(1 for r in resultados if r["status"] == "ok")
    err = sum(1 for r in resultados if r["status"] == "error")
    log.info("=== RESUMEN FINAL ===")
    log.info(f"Consultas exitosas : {ok}")
    log.info(f"Consultas con error: {err}")
    log.info(f"Creditos SerpApi gastados: ~{ok + err}")

def main():
    validar_api_key()
    df = leer_excel(EXCEL_FILE)
    client = serpapi.Client(api_key=API_KEY)
    resultados = procesar(df, client)
    mostrar_muestra(resultados)
    resumen(resultados)

if __name__ == "__main__":
    main()
