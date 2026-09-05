import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="TDT Argentina Live", layout="wide", page_icon="📺")

@st.cache_data(ttl=300)
def cargar_datos():
    canales_base = [
        {"nombre": "Todo Noticias (TN)", "categoria": "Noticias", "url_stream": "https://www.youtube.com/watch?v=gS_J3k5uRUk", "tipo": "youtube"},
        {"nombre": "C5N", "categoria": "Noticias", "url_stream": "https://www.youtube.com/watch?v=d_kS3xXkM9s", "tipo": "youtube"},
        {"nombre": "A24", "categoria": "Noticias", "url_stream": "https://www.youtube.com/watch?v=O1R1L-xKkXo", "tipo": "youtube"},
        {"nombre": "La Nación +", "categoria": "Noticias", "url_stream": "https://www.youtube.com/watch?v=eYkP3N19K9s", "tipo": "youtube"},
        {"nombre": "TV Pública", "categoria": "General", "url_stream": "https://www.youtube.com/watch?v=uJ3k8XmK8s0", "tipo": "youtube"},
        {"nombre": "América TV", "categoria": "General", "url_stream": "https://www.youtube.com/watch?v=eR3k8XmK8s0", "tipo": "youtube"},
        {"nombre": "Crónica TV", "categoria": "Noticias", "url_stream": "https://www.youtube.com/watch?v=rR3k8XmK8s0", "tipo": "youtube"},
        {"nombre": "El Nueve", "categoria": "General", "url_stream": "https://www.youtube.com/watch?v=tR3k8XmK8s0", "tipo": "youtube"}
    ]
    
    try:
        with open("tv.m3u", "r", encoding="utf-8", errors="ignore") as f:
            nombre = "Canal M3U"
            for linea in f:
                linea = linea.strip()
                if linea.startswith('#EXTINF:'):
                    partes = linea.split(',')
                    nombre = partes[-1].strip() if len(partes) > 1 else "Canal M3U"
                elif linea.startswith('http://') or linea.startswith('https://'):
                    tipo = "youtube" if ("youtube.com" in linea or "youtu.be" in linea) else "hls"
                    canales_base.append({"nombre": nombre, "categoria": "General", "url_stream": linea, "tipo": tipo})
    except Exception:
        pass

    return pd.DataFrame(canales_base)

df = cargar_datos()

st.title("📺 Argentina TV Digital")

if not df.empty:
    busqueda = st.text_input("🔍 Buscar canal...", placeholder="Ej: TN, C5N, América...")

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
            
            # Canales vía YouTube
            if "youtube.com" in url_stream or "youtu.be" in url_stream:
                video_id = ""
                if "v=" in url_stream:
                    video_id = url_stream.split("v=")[1].split("&")[0]
                elif "youtu.be/" in url_stream:
                    video_id = url_stream.split("youtu.be/")[1].split("?")[0]
                
                url_embed = f"https://www.youtube-nocookie.com/embed/{video_id}?autoplay=1&mute=1&rel=0&modestbranding=1"
                
                st.markdown(
                    f"""
                    <iframe width="100%" height="400" src="{url_embed}" 
                    title="{canal_seleccionado}" frameborder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                    allowfullscreen style="border-radius: 12px;"></iframe>
                    """,
                    unsafe_allow_html=True
                )
                
                st.info("💡 Si la transmisión indica restricciones de reproducción por derechos del canal, puedes abrir la señal directamente:")
                st.link_button("🔴 Abrir emisión oficial en vivo", f"https://www.youtube.com/watch?v={video_id}", use_container_width=True)
            
            # Canales con señal HLS (.m3u8) directa
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
                components.html(player_html, height=420)
                st.caption(f"**URL Directa:** `{url_stream}`")