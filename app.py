import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="TDT Argentina Live", layout="wide", page_icon="📺")

@st.cache_data(ttl=300)
def cargar_datos():
    canales_base = [
        {
            "nombre": "El Nueve (En vivo)", 
            "categoria": "General", 
            "url_stream": "https://www.youtube.com/watch?v=tR3k8XmK8s0", 
            "tipo": "youtube"
        },
        {
            "nombre": "América TV (En vivo)", 
            "categoria": "General", 
            "url_stream": "https://vmf.edge-apps.net/embed/live.php?streamname=americahls-100056&autoplay=true", 
            "tipo": "iframe_directo"
        },
        {
            "nombre": "Telefe (En vivo)", 
            "categoria": "General", 
            "url_stream": "https://mdstrm.com/live-stream/6a024684fd4ca6a938f3a118", 
            "tipo": "iframe_directo"
        },
        {
            "nombre": "TV Pública (En vivo)", 
            "categoria": "General", 
            "url_stream": "https://g3.vxral-slo.transport.edge-access.net/b16/ngrp:c7_vivo01_dai_source-20001_all/playlist.m3u8", 
            "tipo": "hls"
        },
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
            "nombre": "A24", 
            "categoria": "Noticias", 
            "url_stream": "https://www.youtube.com/watch?v=O1R1L-xKkXo", 
            "tipo": "youtube"
        },
        {
            "nombre": "La Nación +", 
            "categoria": "Noticias", 
            "url_stream": "https://www.youtube.com/watch?v=eYkP3N19K9s", 
            "tipo": "youtube"
        },
        {
            "nombre": "Crónica TV", 
            "categoria": "Noticias", 
            "url_stream": "https://www.youtube.com/watch?v=rR3k8XmK8s0", 
            "tipo": "youtube"
        }
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
    busqueda = st.text_input("🔍 Buscar canal...", placeholder="Ej: TV Pública, América, Telefe, TN...")

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
            
            # Reproductor iframe directo (América TV, Telefe, TN)
            if tipo == "iframe_directo":
                iframe_html = f"""
                <iframe width="100%" height="450" 
                src="{url_stream}" 
                title="{canal_seleccionado}" 
                frameborder="0" 
                referrerpolicy="no-referrer"
                allow="autoplay; fullscreen; encrypted-media; picture-in-picture" 
                allowfullscreen 
                style="border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                </iframe>
                """
                components.html(iframe_html, height=460)

            # Reproductor de YouTube
            elif tipo == "youtube" or "youtube.com" in url_stream or "youtu.be" in url_stream:
                video_id = ""
                if "v=" in url_stream:
                    video_id = url_stream.split("v=")[1].split("&")[0]
                elif "youtu.be/" in url_stream:
                    video_id = url_stream.split("youtu.be/")[1].split("?")[0]
                elif "embed/" in url_stream:
                    video_id = url_stream.split("embed/")[1].split("?")[0]

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
            
            # Reproductor HLS (.m3u8)
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