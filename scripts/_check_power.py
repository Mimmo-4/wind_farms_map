import pandas as pd
df = pd.read_csv(r"data/wind_farms.csv")
fin = df[df["Country"] == "Finland"]
print("Finland unique Rated Power values:")
print(sorted(fin["Rated Power"].dropna().unique()))
