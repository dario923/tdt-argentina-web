import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import re

st.set_page_config(page_title="TDT Argentina Live", layout="wide", page_icon="📺")

# Carga y procesamiento del archivo tv.m3u local
@st.cache_data(ttl=300)
def cargar_datos():
    canales = []
    
    # Intenta abrir el archivo tv.m3u
    try:
        with open("tv.m3u", "r", encoding="utf-8", errors="ignore") as f:
            lineas = f.readlines()
    except Exception as e:
        st.error(f"Error al cargar el archivo tv.m3u: {e}")
        return pd.DataFrame()

    canal = {}
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith('#EXTINF:'):
            # Extraer Metadatos
            match_id = re.search(r'tvg-id="(.*?)"', linea)
            match_logo = re.search(r'tvg-logo="(.*?)"', linea)
            match_group = re.search(r'group-title="(.*?)"', linea)
            
            tvg_id = match_id.group(1) if match_id else ""
            logo = match_logo.group(1) if match_logo else ""
            categoria = match_group.group(1) if match_group else "General"
            
            # Extraer Nombre del Canal
            partes = linea.split(',')
            nombre = partes[-1].strip() if len(partes) > 1 else "Canal sin nombre"
            
            canal = {
                "id": tvg_id,
                "nombre": nombre,
                "categoria": categoria,
                "logo": logo,
                "url_stream": "",
                "estado": "Activo"
            }
        elif linea.startswith('http://') or linea.startswith('https://'):
            if canal:
                canal["url_stream"] = linea
                canales.append(canal)
                canal = {}
                
    return pd.DataFrame(canales)

df = cargar_datos()

st.title("📺 Argentina TV Digital")

if not df.empty:
    # Filtro por categoría opcional
    categorias = ["Todas"] + sorted(list(df["categoria"].unique()))
    cat_seleccionada = st.selectbox("📂 Filtrar por categoría:", categorias)

    # Buscador rápido
    busqueda = st.text_input("🔍 Buscar canal...", placeholder="Ej: A24, América, Santa Fe...")

    df_filtrado = df.copy()
    if cat_seleccionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["categoria"] == cat_seleccionada]
    if busqueda:
        df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(busqueda, case=False, na=False)]

    col_reproductor, col_lista = st.columns([2, 1])

    with col_lista:
        st.subheader(f"Canales ({len(df_filtrado)})")
        opciones = {row['nombre']: row['url_stream'] for _, row in df_filtrado.iterrows()}
        canal_seleccionado = st.radio("Selecciona una señal:", list(opciones.keys()), index=0 if len(opciones) > 0 else None)

    with col_reproductor:
        if canal_seleccionado:
            url_stream = opciones[canal_seleccionado]
            st.subheader(f"🔴 En vivo: {canal_seleccionado}")
            
            player_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
                <style>
                    body {{ margin: 0; background-color: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                    video {{ width: 100%; max-height: 480px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
                </style>
            </head>
            <body>
                <video id="video" controls autoplay muted></video>
                <script>
                    var video = document.getElementById('video');
                    var videoSrc = '{url_stream}';
                    if (Hls.isSupported()) {{
                        var hls = new Hls();
                        hls.loadSource(videoSrc);
                        hls.attachMedia(video);
                    }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                        video.src = videoSrc;
                    }}
                </script>
            </body>
            </html>
            """
            components.html(player_html, height=420)
            st.caption(f"**URL Directa:** `{url_stream}`")
else:
    st.warning("No se encontraron canales en el archivo `tv.m3u`. Asegúrate de que esté subido al repositorio.")