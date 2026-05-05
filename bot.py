def buscar_voluntariados():
    print("🚀 Iniciando búsqueda en Pronabec (Becas Perú)...")
    # Usamos la sección de becas vigentes de Pronabec
    sitio = "https://www.pronabec.gob.pe/becas-vigentes/"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        respuesta = requests.get(sitio, headers=headers, timeout=15)
        soup = BeautifulSoup(respuesta.text, 'html.parser')
        
        # Buscamos los títulos de las becas
        elementos = soup.find_all('h3') 
        print(f"📊 Análisis técnico: Se detectaron {len(elementos)} posibles becas.")

        for item in elementos:
            titulo = item.get_text().strip()
            link_tag = item.find('a') or item.find_parent('a')
            link = link_tag['href'] if link_tag else sitio

            if len(titulo) > 5:
                data = {
                    "titulo": titulo,
                    "entidad": "PRONABEC",
                    "link": link
                }
                supabase.table("oportunidades").upsert(data, on_conflict='link').execute()
                print(f"✅ Becas encontradas: {titulo}")

    except Exception as e:
        print(f"❌ Error: {e}")
