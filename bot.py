def extraer_fecha(texto):
    # PATRÓN 1: Busca fechas tipo 30/05/2026
    patron_num = r'\d{2}[/-]\d{2}[/-]\d{4}'
    # PATRÓN 2: Busca fechas tipo "30 de mayo"
    patron_texto = r'\d{1,2}\s+de\s+[a-z]+'
    
    res_num = re.search(patron_num, texto)
    res_txt = re.search(patron_texto, texto.lower())
    
    if res_num: return res_num.group(0)
    if res_txt: return res_txt.group(0).capitalize()
    return "Verificar en link"

def categorizar_beca(titulo):
    t = titulo.upper()
    # Categorías más precisas para Perú
    if any(x in t for x in ["MAESTRÍA", "POSGRADO", "DOCTORADO", "COBERTURA"]):
        return "Posgrado"
    if any(x in t for x in ["BECA 18", "TALENTO", "EXCELENCIA", "CONTINUIDAD", "DOCENTE"]):
        return "Pregrado / Nacional"
    if any(x in t for x in ["ALIANZA", "EXTRANJERO", "INTERNACIONAL", "HUNGRÍA"]):
        return "Internacional"
    return "Beca General"

if __name__ == "__main__":
    scraping_pronabec()
