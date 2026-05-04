import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client

# Conexión a tu nuevo almacén de NextStep
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def buscar_voluntariados():
    print("🚀 Iniciando búsqueda de oportunidades...")
    # Iremos a una página de voluntariados en Perú
    sitio = "https://proa.pe/programas_todos"
    respuesta = requests.get(sitio, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    
    # Buscamos los nombres de los proyectos
    titulos = soup.find_all('h5')
    
    for t in titulos:
        nombre = t.get_text().strip()
        
        # Esta es la información que irá a tus columnas de Supabase
        nueva_oportunidad = {
            "titulo": nombre,
            "entidad": "Proa.pe",
            "categoria": "Voluntariado",
            "departamento": "Todo el Perú",
            "descripcion": "Encuentra más detalles en la web oficial de Proa."
        }
        
        # Lo guardamos en la tabla
        try:
            supabase.table("oportunidades").insert(nueva_oportunidad).execute()
            print(f"✅ Guardado con éxito: {nombre}")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")

if __name__ == "__main__":
    buscar_voluntariados()
                print(f"✅ Guardado: {titulo}")
            except Exception as e:
                print(f"❌ Error al guardar {titulo}: {e}")

if __name__ == "__main__":
    buscar_y_guardar()
