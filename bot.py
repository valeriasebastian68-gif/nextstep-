import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
import os

# 1. Configuración de conexión
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def scraping_pronabec():
    print("🚀 Buscando exclusivamente Becas y Créditos...")
    
    # Esta es la URL donde Pronabec lista sus convocatorias
    target_url = "https://www.pronabec.gob.pe/becas-propias/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(target_url, headers=headers, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. EL CAMBIO CLAVE: Buscamos dentro de los contenedores de las becas
        # Pronabec suele usar h3 para los nombres de las becas en sus tarjetas
        oportunidades = soup.find_all(['h3', 'h2', 'a'])
        
        encontrados = 0
        for op in oportunidades:
            titulo = op.get_text().strip()
            link = op.get('href', '')

            # --- FILTRO DE CALIDAD "NEXTSTEP" ---
            # Solo guardamos si es una BECA o un CRÉDITO real
            es_beca_real = "BECA" in titulo.upper() or "CRÉDITO" in titulo.upper() or "CREDITO" in titulo.upper()
            
            # Lista negra para evitar textos legales o de menú
            palabras_basura = ["derechos", "teléfono", "central", "aliados", "política", "atención"]
            es_basura = any(basura in titulo.lower() for basura in palabras_basura)

            if es_beca_real and not es_basura and len(titulo) > 5:
                # Limpiar el link
                if link.startswith('/'):
                    link = f"https://www.pronabec.gob.pe{link}"
                elif not link.startswith('http'):
                    link = "https://www.pronabec.gob.pe/becas-propias/"

                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": link
                }
                
                try:
                    supabase.table("oportunidades").upsert(data).execute()
                    print(f"✅ BECA ENCONTRADA: {titulo}")
                    encontrados += 1
                except Exception as e:
                    print(f"⚠️ Error en DB: {e}")
        
        if encontrados == 0:
            print("⚠️ El bot no detectó palabras clave (BECA/CRÉDITO). Revisando estructura...")
            # Intento secundario si la página cambió de formato
            for link_alt in soup.find_all('a', href=True):
                txt = link_alt.get_text().strip()
                if "BECA" in txt.upper() and len(txt) < 100:
                    print(f"🎯 Hallazgo alternativo: {txt}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scraping_pronabec()
