with open("verification.txt", "r", encoding="utf-16le") as f:
    text = f.read()
with open("verification_utf8.txt", "w", encoding="utf-8") as fw:
    fw.write(text)
