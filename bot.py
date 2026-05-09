import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os
import re

# 1. Configuración de conexión segura
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def analizar_contenido(texto, titulo):
    """Lógica de archivador: Categoriza por edad, departamento y tipo"""
    texto = texto.lower()
    
    # --- BUSCAR EDADES ---
    # Busca patrones como "18 años", "hasta los 22", etc.
    edad = re.search(r'(\d{1,2})\s*años', texto)
    rango_edad = f"Hasta {edad.group(1)} años" if edad else "Ver bases"

    # --- BUSCAR DEPARTAMENTO ---
    regiones = ["Lima", "Cusco", "Arequipa", "Piura", "Puno", "Trujillo", "Iquitos"]
    dep = next((r for r in regiones if r.lower() in texto), "Nacional")

    # --- CATEGORIZACIÓN ---
    t = titulo.upper()
    if "18" in t or "TALENTO" in t: cat = "Pregrado / Beca 18"
    elif "MAESTRÍA" in t or "DOCTORADO" in t: cat = "Posgrado"
    elif "INTERNACIONAL" in t: cat = "Internacional"
    else: cat = "General"

    return dep, rango_edad, cat

def scraping_pronabec():
    print("🚀 Iniciando Escaneo Inteligente NextStep...")
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    try:
        # Identificarnos como un navegador real para evitar bloqueos
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'}
        response = requests.get(target_url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"❌ Error de acceso: La página devolvió código {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        enlaces = soup.find_all('a')
        
        count = 0
        for b in enlaces:
            titulo = b.get_text().strip()
            link = b.get('href', '')

            # Solo procesar si el texto parece una beca real
            if "BECA" in titulo.upper() and len(titulo) > 10 and len(titulo) < 100:
                if link.startswith('/'): link = f"https://www.pronabec.gob.pe{link}"
                
                # Extraemos info básica del texto del enlace
                departamento, edad, categoria = analizar_contenido(titulo, titulo)
                
                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": link,
                    "departamento": departamento,
                    "categorias": [categoria],
                    "fecha_limite": "Consultar en link" # Más seguro por ahora
                }
                
                try:
                    supabase.table("oportunidades").upsert(data).execute()
                    print(f"✅ Archivado: {titulo} | {categoria} | {departamento}")
                    count += 1
                except Exception as e:
                    print(f"⚠️ Error al guardar en tabla: {e}")

        print(f"\n✨ ¡Éxito! Se archivaron {count} becas correctamente.")

    except Exception as e:
        print(f"💥 Error crítico: {e}")

if __name__ == "__main__":
    scraping_pronabec()
