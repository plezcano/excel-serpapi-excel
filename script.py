import pandas as pd

print("inicio")

df = pd.read_excel("3. SEO_Website_DLS.xlsx")

print("filas:", df.shape)

df = df.dropna(subset=["keyword"])

print("filas limpias:", df.shape)

print(df.head())

print("fin")
