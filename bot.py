import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import re

# 1. Conexión a Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def extraer_fecha(texto):
    # Busca fechas numéricas o con texto (ej. 15 de mayo)
    patron_num = r'\d{2}[/-]\d{2}[/-]\d{4}'
    patron_texto = r'\d{1,2}\s+de\s+[a-z]+'
    res_num = re.search(patron_num, texto)
    res_txt = re.search(patron_texto, texto.lower())
    if res_num: return res_num.group(0)
    if res_txt: return res_txt.group(0).capitalize()
    return "Consultar cronograma"

def categorizar(titulo):
    t = titulo.upper()
    if any(x in t for x in ["18", "TALENTO", "CONTINUIDAD", "DOCENTE"]): return "Pregrado / Nacional"
    if any(x in t for x in ["MAESTRÍA", "POSGRADO", "DOCTORADO"]): return "Posgrado"
    if any(x in t for x in ["EXTRANJERO", "INTERNACIONAL", "HUNGRÍA"]): return "Internacional"
    return "Beca General"

def scraping_pronabec():
    print("🚀 NextStep: Escaneando Pronabec...")
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # BUSCADOR DIRECTO: Filtramos todos los enlaces que tengan la palabra BECA
        enlaces = soup.find_all('a')
        
        encontrados = 0
        for b in enlaces:
            texto = b.get_text().strip()
            link = b.get('href', '')
            
            # Solo procesamos si dice BECA y no es un texto gigante
            if "BECA" in texto.upper() and len(texto) < 100:
                # El bot mira el texto que rodea al enlace para buscar la fecha
                contexto = b.parent.get_text()
                fecha = extraer_fecha(contexto)
                cat = categorizar(texto)
                
                if link.startswith('/'):
                    link = f"https://www.pronabec.gob.pe{link}"
                
                data = {
                    "titulo": texto,
                    "entidad": "PRONABEC",
                    "link": link,
                    "fecha_limite": fecha,
                    "categorias": [cat]
                }
                
                try:
                    supabase.table("oportunidades").upsert(data).execute()
                    print(f"✅ Guardada: {texto} ({fecha})")
                    encontrados += 1
                except Exception as e:
                    print(f"⚠️ Error DB: {e}")

        print(f"\n✨ ¡Listo! Se encontraron {encontrados} oportunidades.")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    scraping_pronabec()
