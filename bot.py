import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import re

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def profundizar_busqueda(link_beca):
    """Entra al link de la beca para sacar datos específicos"""
    try:
        res = requests.get(link_beca, timeout=10)
        soup_interno = BeautifulSoup(res.text, 'html.parser')
        texto_sucio = soup_interno.get_text().lower()
        
        # 1. Buscar Departamento
        regiones = ["lima", "cusco", "arequipa", "puno", "piura", "la libertad", "junín"]
        dep = next((r.capitalize() for r in regiones if r in texto_sucio), "Nacional")
        
        # 2. Buscar Fecha Limite mejorada
        fecha = re.search(r'\d{1,2}\s+de\s+[a-z]+', texto_sucio)
        fecha_final = fecha.group(0).capitalize() if fecha else "Ver en web"
        
        return dep, fecha_final
    except:
        return "Nacional", "Consultar link"

def scraping_pronabec():
    print("📂 Archivador NextStep: Organizando Pronabec...")
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    enlaces = soup.find_all('a')
    for b in enlaces:
        titulo = b.get_text().strip()
        link = b.get('href', '')
        
        if "BECA" in titulo.upper() and len(titulo) < 100:
            if link.startswith('/'): link = f"https://www.pronabec.gob.pe{link}"
            
            # EL BOT ENTRA AL LINK PARA DETALLAR
            print(f"🔎 Analizando detalles de: {titulo}...")
            departamento, fecha_limite = profundizar_busqueda(link)
            
            data = {
                "titulo": titulo,
                "entidad": "PRONABEC",
                "link": link,
                "fecha_limite": fecha_limite,
                "departamento": departamento,
                "categorias": ["Pregrado"] if "18" in titulo or "Talento" in titulo else ["General"]
            }
            
            supabase.table("oportunidades").upsert(data).execute()

if __name__ == "__main__":
    scraping_pronabec()
