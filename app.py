import streamlit as st
import pandas as pd
import gspread
import streamlit.components.v1 as components
import json

st.set_page_config(page_title="TDT Argentina Live", layout="wide", page_icon="📺")

# Carga de datos
@st.cache_data(ttl=300)
def cargar_datos():
    # Intenta leer credenciales desde Streamlit Secrets (para el deploy web) o archivo local
    if "gcp_service_account" in st.secrets:
        client = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    else:
        client = gspread.oauth(
            credentials_filename="credentials.json",
            authorized_user_filename="authorized_user.json"
        )
    sheet = client.open("TDT_Argentina").sheet1
    return pd.DataFrame(sheet.get_all_records())

try:
    df = cargar_datos()
except Exception as e:
    st.error(f"Error al cargar datos de Google Sheets: {e}")
    st.stop()

# Interfaz personalizada CSS/HTML
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stTextInput input { border-radius: 20px; padding: 10px 15px; }
</style>
""", unsafe_allow_html=True)

st.title("📺 Argentina TV Digital")

# Buscador rápido
busqueda = st.text_input("🔍 Buscar canal...", placeholder="Ej: A24, América, Santa Fe...")

df_filtrado = df[df["estado"] == "Activo"]
if busqueda:
    df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(busqueda, case=False, na=False)]

col_reproductor, col_lista = st.columns([2, 1])

with col_lista:
    st.subheader(f"Canales ({len(df_filtrado)})")
    
    # Lista desplegable de selección rápida
    opciones = {row['nombre']: row['url_stream'] for _, row in df_filtrado.iterrows()}
    canal_seleccionado = st.radio("Selecciona una señal:", list(opciones.keys()), index=0 if len(opciones) > 0 else None)

with col_reproductor:
    if canal_seleccionado:
        url_stream = opciones[canal_seleccionado]
        st.subheader(f"🔴 En vivo: {canal_seleccionado}")
        
        # Player HTML5 custom con HLS.js
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