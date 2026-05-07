import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os

# 1. Configuración de conexión (Usa tus Secrets de GitHub)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def scraping_pronabec():
    print("🚀 Iniciando búsqueda de becas reales en Pronabec...")
    
    # URL específica de becas propias
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    try:
        response = requests.get(target_url, timeout=15)
        response.encoding = 'utf-8' # Para que no salgan símbolos raros
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Buscamos los títulos que suelen estar en etiquetas h3 o enlaces de tarjetas
        elementos = soup.find_all(['h3', 'a'])
        
        encontrados = 0
        for el in elementos:
            titulo = el.get_text().strip()
            link = el.get('href', '')

            # --- FILTRO ANTIRRUIDO (Data Cleaning) ---
            # Solo aceptamos textos que parezcan nombres de becas
            palabras_basura = [
                "derechos reservados", "teléfono", "central", "aliados", 
                "it looks like", "ver más", "contáctenos", "normas", 
                "política", "atención", "612-8230", "©", "gob.pe"
            ]

            # Requisitos: 
            # 1. Más de 15 letras.
            # 2. Que NO contenga palabras de la lista negra.
            # 3. Que contenga la palabra "BECA" o sea un nombre propio largo.
            es_basura = any(basura in titulo.lower() for basura in palabras_basura)
            
            if len(titulo) > 15 and not es_basura:
                # Completar link si es necesario
                if link.startswith('/'):
                    full_link = f"https://www.pronabec.gob.pe{link}"
                elif link.startswith('http'):
                    full_link = link
                else:
                    full_link = "https://www.pronabec.gob.pe/becas-propias/"

                # Preparar datos para Supabase
                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": full_link
                }
                
                try:
                    # El 'upsert' evitará que se dupliquen si el 'link' es el mismo
                    supabase.table("oportunidades").upsert(data).execute()
                    print(f"✅ Oportunidad válida guardada: {titulo}")
                    encontrados += 1
                except Exception as e:
                    print(f"⚠️ Error al guardar en DB: {e}")
        
        print(f"\n--- Finalizado: Se agregaron {encontrados} registros válidos ---")

    except Exception as e:
        print(f"❌ Error crítico en el bot: {e}")

if __name__ == "__main__":
    scraping_pronabec()
