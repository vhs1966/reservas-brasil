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

    # --- 3. PROCESAR OCUPACIONES EXISTENTES (Rojo / Amarillo con Horas fijas) ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        
        # Seteamos las reservas para que ocupen desde las 14:00 (Check-In) hasta las 10:00 del día de salida (Check-Out)
        start_str = row['Fecha de Inicio'].strftime('%Y-%m-%d') + 'T14:00:00'
        end_str = (row['Fecha de Fin'] + timedelta(days=1)).strftime('%Y-%m-%d') + 'T10:00:00'
        
        event = {
            "title": f"{row['Inquilino']} ({estado})",
            "start": start_str,
            "end": end_str,
            "color": colores.get(estado, '#FF4B4B')
        }
        calendar_events.append(event)

    # --- 4. CÁLCULO DE HUECOS "DISPONIBLE" CON HORAS DE CORTE (Verde) ---
    año_actual = datetime.today().year
    fecha_actual = datetime(año_actual, 1, 1)
    fecha_limite_calendario = datetime(año_actual, 12, 31)
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        if fecha_actual < f_ini:
            # El bloque disponible termina el día del Check-In a las 14:00 hs
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d') + 'T10:00:00',
                "end": f_ini.strftime('%Y-%m-%d') + 'T14:00:00',
                "color": '#00CC96'  # Verde
            })
        
        if f_fin > fecha_actual:
            fecha_actual = f_fin
            
    if fecha_actual < fecha_limite_calendario:
        fecha_fin_calendario_visual = fecha_limite_calendario + timedelta(days=1)
        calendar_events.append({
            "title": "Disponible",
            "start": fecha_actual.strftime('%Y-%m-%d') + 'T10:00:00',
            "end": fecha_fin_calendario_visual.strftime('%Y-%m-%d') + 'T10:00:00',
            "color": '#00CC96'  # Verde
        })

    # --- 5. CONFIGURACIÓN Y RENDERIZADO ---
    calendar_options = {
        "editable": "false",
        "selectable": "false",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "multiMonthYear,dayGridMonth,dayGridWeek",
        },
        "initialView": "multiMonthYear",
    }

    calendar(events=calendar_events, options=calendar_options)
