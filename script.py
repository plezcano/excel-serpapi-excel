import pandas as pd
import logging
from pathlib import Path

# Configurar logging con formato claro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger(__name__)

# Configuración
EXCEL_FILE = "3. SEO_Website_DLS.xlsx"
SHEET_NAME = 0  # 0 = primera hoja, o usa el nombre: "Sheet1"

def leer_excel(ruta: str, hoja=0) -> pd.DataFrame:
    """Lee el Excel y devuelve un DataFrame limpio."""
    log.info(f"=== INICIO ===")
    log.info(f"Abriendo archivo: {ruta}")
    
    if not Path(ruta).exists():
        log.error(f"Archivo no encontrado: {ruta}")
        raise FileNotFoundError(ruta)
    
    df = pd.read_excel(ruta, sheet_name=hoja, header=0)
    log.info(f"Archivo leído correctamente | Filas: {len(df)} | Columnas: {len(df.columns)}")
    log.info(f"Columnas detectadas: {list(df.columns)}")
    
    # Limpieza opcional
    if "keyword" in df.columns:
        antes = len(df)
        df = df.dropna(subset=["keyword"]).reset_index(drop=True)
        log.info(f"Filas eliminadas sin keyword: {antes - len(df)} | Filas finales: {len(df)}")
    
    return df

def imprimir_celdas(df: pd.DataFrame):
    """Imprime cada celda con prompt detallado: fila, columna y valor."""
    log.info(f"--- Imprimiendo {len(df)} filas x {len(df.columns)} columnas ---")
    
    for idx, fila in df.iterrows():
        log.info(f"┌── Fila {idx + 1} ──────────────────────")
        for columna in df.columns:
            valor = fila[columna]
            tipo = type(valor).__name__
            # Marcar valores vacíos o nulos
            if pd.isna(valor):
                log.info(f"│  [{columna}] → (vacío)")
            else:
                log.info(f"│  [{columna}] ({tipo}) → {valor}")
        log.info(f"└────────────────────────────────────")

def main():
    df = leer_excel(EXCEL_FILE, SHEET_NAME)
    imprimir_celdas(df)
    log.info("=== FIN ===")

if __name__ == "__main__":
    main()
