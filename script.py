df = pd.read_excel("3. SEO_Website_DLS.xlsx")

df = df.dropna(subset=["keyword"])  # solo filas con keyword

print(df.shape)
print(df.head())
