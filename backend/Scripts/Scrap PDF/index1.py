import tabula

# Read the PDF file into a pandas DataFrame
df = tabula.read_pdf("example1.pdf")
df = df.dropna(axis="columns")
print(df)
# convert PDF into CSV
# tabula.convert_into("example1.pdf", "output.csv", output_format="csv", pages='all')
