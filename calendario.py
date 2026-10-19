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

    # --- 4. CÁLCULO DE HUECOS "DISPONIBLE" ORIGINAL ---
    año_actual = datetime.today().year
    fecha_actual = datetime(año_actual, 1, 1).date()
    fecha_limite_calendario = datetime(año_actual, 12, 31).date()
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        if f_fin < fecha_actual:
            continue
            
        f_ini_ajustada = max(f_ini, fecha_actual)
        
        if fecha_actual < f_ini_ajustada:
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": f_ini_ajustada.strftime('%Y-%m-%d'),
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

    # --- 5. CONFIGURACIÓN Y RENDERIZADO CON DIAS COMPLEMENTARIOS ---
    calendar_options = {
        "editable": "false",
        "selectable": "false",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "multiMonthYear,dayGridMonth,dayGridWeek",
        },
        "initialView": "multiMonthYear",
        # SOLUCIÓN: Forza a que se muestren siempre los números de los días de los meses vecinos
        "showNonCurrentDates": "true",
    }

    calendar(events=calendar_events, options=calendar_options)
