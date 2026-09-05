import re
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TDT Tv Live", layout="wide", page_icon="📺")

# ==========================================
# CÓDIGO DE GOOGLE ANALYTICS
# ==========================================
GA_ID = "G-88B6BJLQGB"

ga_code = f"""
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""
components.html(ga_code, height=0, width=0)
# ==========================================

@st.cache_data(ttl=300)
def cargar_datos():
    canales_base = [
        {
            "nombre": "Todo Noticias (TN)", 
            "categoria": "Noticias", 
            "url_stream": "https://api.vodgc.net/player/v2/embed/playerId/HKA9Y71614802794/contentId/1363280", 
            "tipo": "iframe_directo"
        },
        {
            "nombre": "C5N (En vivo)", 
            "categoria": "Noticias", 
            "url_stream": "https://www.youtube.com/watch?v=j6oh4Kqz3UM", 
            "tipo": "youtube"
        },
        {
            "nombre": "La Nación +", 
            "categoria": "Noticias", 
            "url_stream": "https://www.youtube.com/embed/FEWZjXJ7M0c?si=bd5d9K4LEQAYdksX", 
            "tipo": "youtube"
        },
        {
            "nombre": "Crónica TV", 
            "categoria": "Noticias", 
            "url_stream": "https://www.youtube.com/watch?v=hw4uHyct4vg", 
            "tipo": "youtube"
        }
    ]
    
    for m3u_filename in ["tv.m3u", "ar.m3u"]:
        try:
            with open(m3u_filename, "r", encoding="utf-8", errors="ignore") as f:
                nombre = "Canal M3U"
                user_agent = ""
                for linea in f:
                    linea = linea.strip()
                    if linea.startswith('#EXTINF:'):
                        partes = linea.split(',')
                        nombre = partes[-1].strip() if len(partes) > 1 else "Canal M3U"
                    elif linea.startswith('#EXTVLCOPT:http-user-agent='):
                        user_agent = linea.split('=', 1)[1].strip()
                    elif linea.startswith('http://') or linea.startswith('https://') or "<iframe" in linea:
                        tipo = "youtube" if ("youtube.com" in linea or "youtu.be" in linea) else "hls"
                        canales_base.append({
                            "nombre": nombre, 
                            "categoria": "General", 
                            "url_stream": linea, 
                            "tipo": tipo,
                            "user_agent": user_agent
                        })
                        user_agent = ""
            break
        except Exception:
            pass

    return pd.DataFrame(canales_base)

df = cargar_datos()

st.title("📺 TDT TV Digital")

if not df.empty:
    busqueda = st.text_input("🔍 Buscar canal...", placeholder="Ej: TV Pública, América, Telefe, TN, Crónica, La Nación...")

    df_filtrado = df.copy()
    if busqueda:
        df_filtrado = df_filtrado[df_filtrado["nombre"].str.contains(busqueda, case=False, na=False)]

    col_reproductor, col_lista = st.columns([2, 1])

    with col_lista:
        st.subheader(f"Canales ({len(df_filtrado)})")
        opciones = {row['nombre']: (row['url_stream'], row.get('tipo', 'hls')) for _, row in df_filtrado.iterrows()}
        canal_seleccionado = st.radio("Selecciona una señal:", list(opciones.keys()), index=0 if len(opciones) > 0 else None)

    with col_reproductor:
        if canal_seleccionado:
            url_stream, tipo = opciones[canal_seleccionado]
            st.subheader(f"🔴 En vivo: {canal_seleccionado}")
            
            if tipo == "iframe_tvp" or tipo == "iframe_directo":
                iframe_html = f"""
                <iframe width="100%" height="450" 
                src="{url_stream}" 
                title="{canal_seleccionado}" 
                frameborder="0" 
                referrerpolicy="no-referrer-when-downgrade"
                allow="autoplay; fullscreen; encrypted-media; picture-in-picture" 
                allowfullscreen 
                style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                </iframe>
                """
                components.html(iframe_html, height=460)

            elif tipo == "youtube" or "youtube.com" in url_stream or "youtu.be" in url_stream:
                video_id = ""
                match = re.search(r'(?:v=|\/embed\/|\/watch\?v=|\/v\/|https:\/\/youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url_stream)
                if match:
                    video_id = match.group(1)

                if video_id:
                    iframe_html = f"""
                    <iframe width="100%" height="450" 
                    src="https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1" 
                    title="{canal_seleccionado}" 
                    frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    referrerpolicy="strict-origin-when-cross-origin" 
                    allowfullscreen 
                    style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                    </iframe>
                    """
                    components.html(iframe_html, height=460)
                    st.link_button("🔴 Abrir directo en YouTube", f"https://www.youtube.com/watch?v={video_id}", use_container_width=True)
                else:
                    st.error("No se pudo obtener el ID del video de YouTube.")
            
            else:
                player_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
                    <style>
                        body {{ margin: 0; background-color: #000; display: flex; justify-content: center; align-items: center; height: 100vh; }}
                        video {{ width: 100%; max-height: 480px; border-radius: 12px; }}
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
                components.html(player_html, height=460)
                st.caption(f"**URL Directa:** `{url_stream}`")