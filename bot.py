import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Conexión a tu almacén de NextStep
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def buscar_voluntariados():
    print("🚀 Iniciando búsqueda de oportunidades...")
    sitio = "https://proa.pe/programas_todos"
    
    try:
        respuesta = requests.get(sitio, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # En Proa, los proyectos suelen estar en etiquetas h5 o dentro de cards
        proyectos = soup.find_all('div', class_='card-body') # Ajustado para captar más info

        for p in proyectos:
            try:
                # Extraemos el título y el link
                titulo_tag = p.find('h5')
                link_tag = p.find('a')
                
                if titulo_tag and link_tag:
                    titulo = titulo_tag.get_text().strip()
                    link = link_tag['href']
                    
                    # Si el link es relativo, le agregamos el dominio
                    if not link.startswith('http'):
                        link = f"https://proa.pe{link}"

                    data = {
                        "titulo": titulo,
                        "entidad": "Proa Perú",
                        "link": link
                    }

                    # Guardado en tu base de datos de 2 años
                    supabase.table("oportunidades").upsert(data, on_conflict='link').execute()
                    print(f"✅ Guardado: {titulo}")

            except Exception as e:
                continue # Si falla uno, que siga con el siguiente

    except Exception as e:
        print(f"❌ Error en la conexión: {e}")

# Ejecutamos la función
if __name__ == "__main__":
    buscar_voluntariados()
