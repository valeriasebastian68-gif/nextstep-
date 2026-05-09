import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import re # Para buscar fechas

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def extraer_fecha(texto):
    # Busca formatos como 30/05/2026 o 30-05-2026
    patron = r'\d{2}[/-]\d{2}[/-]\d{4}'
    resultado = re.search(patron, texto)
    return resultado.group(0) if resultado else "Por definir"

def categorizar_beca(titulo):
    t = titulo.upper()
    if "POSGRADO" in t or "MAESTRÍA" in t or "DOCTORADO" in t:
        return "Posgrado"
    if "MOVILIDAD" in t or "INTERCAMBIO" in t:
        return "Internacional"
    if "TALENTO" in t or "18" in t or "DOCENTE" in t:
        return "Pregrado / Nacional"
    return "General"

def scraping_pronabec():
    print("🧠 Ejecutando NextStep: Categorización y Fechas...")
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        elementos = soup.find_all(['h3', 'a', 'p']) # Agregamos 'p' para buscar fechas en párrafos
        
        encontrados = 0
        for el in elementos:
            titulo = el.get_text().strip()
            link = el.get('href', '')

            if ("BECA" in titulo.upper() or "CRÉDITO" in titulo.upper()) and len(titulo) < 100:
                # Intentamos buscar una fecha cerca del título
                fecha = extraer_fecha(el.parent.get_text()) 
                categoria = categorizar_beca(titulo)
                
                if link.startswith('/'):
                    link = f"https://www.pronabec.gob.pe{link}"

                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": link,
                    "fecha_limite": fecha,
                    "categorias": [categoria] # Lo enviamos como lista para tu columna text[]
                }
                
                try:
                    supabase.table("oportunidades").upsert(data).execute()
                    print(f"📍 {categoria} | {titulo} | Cierra: {fecha}")
                    encontrados += 1
                except Exception as e:
                    print(f"⚠️ Error DB: {e}")
        
        print(f"\n✅ Proceso terminado. {encontrados} becas categorizadas.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scraping_pronabec()
