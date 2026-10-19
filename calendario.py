import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta

def mostrar_calendario(df):
    # --- 1. CONFIGURACIÓN SEGURA DE FORMATO DE FECHAS ---
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], dayfirst=True, errors='coerce', format='mixed')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], dayfirst=True, errors='coerce', format='mixed')
    
    # --- 2. OBTENER DEPARTAMENTOS Y FILTRAR ---
    lista_deptos = sorted(df['Departamento'].dropna().unique().tolist())
    depto_seleccionado = st.selectbox("🏢 Selecciona un Departamento:", lista_deptos)
    
    df_filtrado = df[df['Departamento'] == depto_seleccionado].copy()
    df_filtrado = df_filtrado.dropna(subset=['Fecha de Inicio', 'Fecha de Fin'])
    df_filtrado = df_filtrado.sort_values(by='Fecha de Inicio')

    calendar_events = []
    
    colores = {
        'Alquilado': '#FF4B4B',  # Rojo
        'Reservado': '#FFD700',  # Amarillo
    }

    # --- 3. PROCESAR OCUPACIONES EXISTENTES ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        fecha_fin_visual = row['Fecha de Fin'] + timedelta(days=1)
        
        event = {
            "title": f"{row['Departamento']} - {row['Inquilino']} ({estado})",
            "start": row['Fecha de Inicio'].strftime('%Y-%m-%d'),
            "end": fecha_fin_visual.strftime('%Y-%m-%d'),
            "color": colores.get(estado, '#FF4B4B')
        }
        calendar_events.append(event)

    # --- 4. CÁLCULO DE HUECOS "DISPONIBLE" (VERDE) ---
    año_actual = datetime.today().year
    fecha_actual = datetime(año_actual, 1, 1)
    fecha_limite_calendario = datetime(año_actual, 12, 31)
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        if fecha_actual < f_ini:
            fecha_fin_verde_visual = f_ini + timedelta(days=1)
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": fecha_fin_verde_visual.strftime('%Y-%m-%d'),
                "color": '#00CC96'
            })
        
        if f_fin > fecha_actual:
            fecha_actual = f_fin
            
    if fecha_actual < fecha_limite_calendario:
        fecha_fin_calendario_visual = fecha_limite_calendario + timedelta(days=1)
        calendar_events.append({
            "title": "Disponible",
            "start": fecha_actual.strftime('%Y-%m-%d'),
            "end": fecha_fin_calendario_visual.strftime('%Y-%m-%d'),
            "color": '#00CC96'
        })

    # --- 5. CONFIGURACIÓN Y RENDERIZADO (ESTILO INYECTADO DIRECTAMENTE) ---
    calendar_options = {
        "editable": "false",
        "selectable": "false",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "multiMonthYear,dayGridMonth,dayGridWeek",
        },
        "initialView": "multiMonthYear",
        "moreLinkText": "Res.",
        # El truco: Inyectamos estilos directamente en el núcleo del FullCalendar
        "themeSystem": "standard",
        "eventSourceSuccess": "js:function() { document.querySelectorAll('.fc-more-link').forEach(el => { el.style.color = '#0046BF'; el.style.fontWeight = 'bold'; }); }",
    }

    # Como la inyección por JS puede fallar si la librería es restrictiva, 
    # la alternativa más limpia y nativa que soporta FullCalendar es pasar variables CSS en un custom stylesheet inyectado por Streamlit Components.
    # Para asegurar el tiro, mantenemos una inyección general optimizada:
    st.components.v1.html(
        """
        <script>
        parent.document.querySelectorAll('iframe').forEach(iframe => {
            var doc = iframe.contentDocument || iframe.contentWindow.document;
            var style = doc.createElement('style');
            style.innerHTML = `
                .fc-more-link, .fc-more-link * { 
                    color: #0046BF !important; 
                    font-weight: bold !important; 
                }
            `;
            doc.head.appendChild(style);
        });
        </script>
        """,
        height=0
    )

    calendar(events=calendar_events, options=calendar_options)
