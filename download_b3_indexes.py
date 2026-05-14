import brdata as br


print(br.b3.download_index("IBOV"))

print("---")
print(br.b3.download_index("IBOV", theoretical=False))
