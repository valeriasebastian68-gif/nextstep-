import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os

# 1. Configuración de conexión (Esto usa tus Secrets de GitHub)
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def scraping_pronabec():
    print("🚀 Iniciando búsqueda en Pronabec (Becas Perú)...")
    
    # URL de la sección de becas de Pronabec
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    try:
        response = requests.get(target_url, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Buscamos los títulos de las becas
        # Buscamos en etiquetas h3 y enlaces que suelen tener los nombres
        oportunidades = soup.find_all(['h3', 'a'])
        
        encontrados = 0
        for op in oportunidades:
            titulo = op.get_text().strip()
            link = op.get('href', 'https://www.pronabec.gob.pe')
            
            # 3. FILTRO INTELIGENTE:
            # Solo guardamos si el texto es largo y NO tiene palabras de relleno
            palabras_basura = ["derechos reservados", "ver más", "contáctenos", "inicio", "gob.pe"]
            
            if len(titulo) > 15 and not any(basura in titulo.lower() for basura in palabras_basura):
                # Si el link es relativo, lo completamos
                if link.startswith('/'):
                    link = f"https://www.pronabec.gob.pe{link}"
                
                # Preparamos el dato para la tabla
                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": link
                }
                
                # 4. Guardado en Supabase (usando upsert para no repetir links)
                try:
                    supabase.table("oportunidades").upsert(data).execute()
                    print(f"✅ Beca guardada: {titulo}")
                    encontrados += 1
                except Exception as e:
                    print(f"⚠️ Error al guardar: {e}")
        
        if encontrados == 0:
            print("📊 Análisis: No se encontraron becas nuevas con los filtros actuales.")
        else:
            print(f"🎉 ¡Éxito! Se procesaron {encontrados} registros.")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == "__main__":
    scraping_pronabec()
