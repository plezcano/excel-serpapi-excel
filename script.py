import pandas as pd
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
log = logging.getLogger(__name__)

# Configuración
EXCEL_FILE = "3. SEO_Website_DLS.xlsx"
COLUMNAS = ["keyword", "city", "state", "country"]

def leer_excel(ruta: str) -> pd.DataFrame:
    """Lee el Excel y devuelve solo las columnas necesarias."""
    log.info(f"Abriendo archivo: {ruta}")
    
    if not Path(ruta).exists():
        log.error(f"Archivo no encontrado: {ruta}")
        raise FileNotFoundError(ruta)
    
    df = pd.read_excel(ruta, header=0)
    
    # Validar columnas
    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        log.error(f"Faltan columnas en el Excel: {faltantes}")
        raise ValueError(f"Columnas faltantes: {faltantes}")
    
    df = df[COLUMNAS].dropna(subset=["keyword"]).reset_index(drop=True)
    log.info(f"Filas a procesar: {len(df)}\n")
    return df

def construir_location(city, state, country) -> str:
    """Arma el string de location: 'City, State, Country'."""
    partes = [str(p).strip() for p in [city, state, country] if pd.notna(p)]
    return ", ".join(partes)

def construir_payload(keyword: str, location: str) -> dict:
    """Arma el diccionario que se enviaría a SerpApi."""
    return {
        "engine": "google",
        "q": keyword,
        "location": location,
        "google_domain": "google.com",
        "hl": "en",
        "gl": "us"
    }

def simular_envio(df: pd.DataFrame):
    """Recorre cada fila e imprime el payload que se enviaría a SerpApi."""
    log.info("=== SIMULACIÓN DE ENVÍO A SERPAPI (sin llamar a la API) ===\n")
    
    for idx, fila in df.iterrows():
        keyword = fila["keyword"]
        location = construir_location(fila["city"], fila["state"], fila["country"])
        payload = construir_payload(keyword, location)
        
        log.info(f"[{idx + 1}/{len(df)}] Payload que se enviaría:")
        for clave, valor in payload.items():
            log.info(f"    {clave:15} → {valor}")
        log.info("")  # línea en blanco entre filas

def main():
    df = leer_excel(EXCEL_FILE)
    simular_envio(df)
    log.info("=== Lectura completa. Listos para conectar a la API en la Parte 2. ===")

if __name__ == "__main__":
    main()
