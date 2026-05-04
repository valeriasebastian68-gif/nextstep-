import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Configuración de conexión con Secrets de GitHub
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def buscar_voluntariados():
    print("🚀 Iniciando búsqueda de oportunidades en Proa...")
    sitio = "https://proa.pe/programas_todos"
    
    try:
        # Simulamos un navegador para evitar bloqueos
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        respuesta = requests.get(sitio, headers=headers, timeout=10)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Intentamos capturar los títulos de los voluntariados
        elementos = soup.find_all('h5')
        print(f"📊 Análisis técnico: Se detectaron {len(elementos)} posibles registros.")

        for item in elementos:
            titulo = item.get_text().strip()
            
            # Buscamos el link (normalmente está en el elemento padre o abuelo)
            link_tag = item.find_parent('a') or (item.find_parent().find('a') if item.find_parent() else None)
            link = link_tag['href'] if link_tag and link_tag.has_attr('href') else "#"

            # Limpiamos el link
            if link != "#" and not link.startswith('http'):
                link = f"https://proa.pe{link}"

            if len(titulo) > 2:
                data = {
                    "titulo": titulo,
                    "entidad": "Proa Perú",
                    "link": link
                }

                try:
                    # Guardamos en Supabase (si el link existe, lo actualiza)
                    supabase.table("oportunidades").upsert(data, on_conflict='link').execute()
                    print(f"✅ Éxito: {titulo}")
                except Exception as db_err:
                    print(f"⚠️ No se pudo guardar '{titulo}': {db_err}")

    except Exception as e:
        print(f"❌ Error crítico en el robot: {e}")

if __name__ == "__main__":
    buscar_voluntariados()
