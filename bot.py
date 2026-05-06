import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Conexión a Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def buscar_becas_pronabec():
    print("🚀 Iniciando búsqueda en Pronabec (Becas Perú)...")
    sitio = "https://www.pronabec.gob.pe/becas-vigentes/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        respuesta = requests.get(sitio, headers=headers, timeout=15)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Buscamos los títulos de las becas en etiquetas h3
        becas = soup.find_all('h3') 
        print(f"📊 Análisis técnico: Se detectaron {len(becas)} posibles becas.")

        for b en becas:
            titulo = b.get_text().strip()
            # Buscamos el link de la beca
            link_tag = b.find('a') or b.find_parent('a')
            link = link_tag['href'] if link_tag else sitio

            if len(titulo) > 5:
                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": link
                }
                
                try:
                    # Guardamos en Supabase
                    supabase.table("oportunidades").upsert(data, on_conflict='link').execute()
                    print(f"✅ Beca guardada: {titulo}")
                except Exception as db_err:
                    print(f"⚠️ Error al guardar en DB: {db_err}")

    except Exception as e:
        print(f"❌ Error en el robot: {e}")

if __name__ == "__main__":
    buscar_becas_pronabec()
