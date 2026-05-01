import pandas as pd

print("inicio")

# Leer Excel
df = pd.read_excel("3. SEO_Website_DLS.xlsx", header=0)

# Eliminar filas sin keyword
df = df.dropna(subset=["keyword"])

# Resetear índice
df = df.reset_index(drop=True)

# Mostrar info
print("filas limpias:", df.shape)
print(df.head())

print("fin")
