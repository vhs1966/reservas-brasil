import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta

def mostrar_calendario(df):
    # --- 1. CONFIGURACIÓN SEGURA DE FORMATO DE FECHAS ---
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], dayfirst=True, errors='coerce', format='mixed')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], dayfirst=True, errors='coerce', format='mixed')
    
    # Eliminamos la hora para que la tabla de historial quede limpia
    df['Fecha de Inicio'] = df['Fecha de Inicio'].dt.date
    df['Fecha de Fin'] = df['Fecha de Fin'].dt.date

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

    # Ajustamos el límite inferior a diciembre del año anterior para que el algoritmo procese todo
    limite_inferior = datetime(2026, 12, 1).date()
    limite_superior = datetime(2027, 12, 31).date()

    # --- 3. PROCESAR OCUPACIONES EXISTENTES ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        
        f_inicio_real = row['Fecha de Inicio']
        f_fin_real = row['Fecha de Fin']
        
        if f_fin_real < limite_inferior or f_inicio_real > limite_superior:
            continue
            
        f_inicio_visual = max(f_inicio_real, limite_inferior)
        f_fin_visual = min(f_fin_real, limite_superior) + timedelta(days=1)
        
        event = {
            "title": f"{row['Departamento']} - {row['Inquilino']} ({estado})",
            "start": f_inicio_visual.strftime('%Y-%m-%d'),
            "end": f_fin_visual.strftime('%Y-%m-%d'),
            "color": colores.get(estado, '#FF4B4B')
        }
        calendar_events.append(event)

    # --- 4. CÁLCULO DE HUECOS "DISPONIBLE" (VERDE) ---
    fecha_actual = limite_inferior
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        if f_fin < limite_inferior:
            continue
            
        f_ini_ajustada = max(f_ini, limite_inferior)
        
        if fecha_actual < f_ini_ajustada:
            fecha_fin_verde_visual = f_ini_ajustada + timedelta(days=1)
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": fecha_fin_verde_visual.strftime('%Y-%m-%d'),
                "color": '#00CC96'
            })
        
        if f_fin > fecha_actual:
            fecha_actual = f_fin
            
    if fecha_actual < limite_superior:
        fecha_fin_calendario_visual = limite_superior + timedelta(days=1)
        calendar_events.append({
            "title": "Disponible",
            "start": fecha_actual.strftime('%Y-%m-%d'),
            "end": fecha_fin_calendario_visual.strftime('%Y-%m-%d'),
            "color": '#00CC96'
        })

    # --- 5. CONFIGURACIÓN DE TEXTO Y ESTILOS (AZUL) ---
    st.markdown(
        """
        <style>
        .fc-more-link {
            color: #007BFF !important;
            font-weight: bold !important;
            text-decoration: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

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
        # CAMBIO SEGURO: Forzamos de forma nativa al calendario a arrancar su vista visual en diciembre de 2026
        "initialDate": "2026-12-01",
    }

    calendar(events=calendar_events, options=calendar_options)
