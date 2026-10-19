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

    # --- 3. PROCESAR OCUPACIONES EXISTENTES (Rojo / Amarillo) ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        
        # FullCalendar corta a las 00:00 del día final. Al sumar 1 día exacto, 
        # la barra visual se extiende correctamente cubriendo la última noche de estadía.
        fecha_fin_visual = row['Fecha de Fin'] + timedelta(days=1)
        
        event = {
            "title": f"{row['Departamento']} - {row['Inquilino']} ({estado})",
            "start": row['Fecha de Inicio'].strftime('%Y-%m-%d'),
            "end": fecha_fin_visual.strftime('%Y-%m-%d'),
            "color": colores.get(estado, '#FF4B4B')
        }
        calendar_events.append(event)

    # --- 4. CÁLCULO DE HUECOS "DISPONIBLE" CON CRUCE DE FECHAS ---
    año_actual = datetime.today().year
    fecha_actual = datetime(año_actual, 1, 1)
    fecha_limite_calendario = datetime(año_actual, 12, 31)
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        # Si la fecha actual es anterior al check-in, ese tramo intermedio está disponible.
        # Al usar 'f_ini' directamente, el bloque verde termina EXACTAMENTE el día que entra el nuevo huésped.
        if fecha_actual < f_ini:
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": f_ini.strftime('%Y-%m-%d'),
                "color": '#00CC96'  # Verde
            })
        
        # Avanzamos el puntero al día del checkout real (sin sumarle 1 día extra en el algoritmo).
        # Esto permite que el próximo bloque verde o la siguiente reserva inicien ese mismo día.
        if f_fin > fecha_actual:
            fecha_actual = f_fin
            
    # Rellenamos el espacio sobrante del año
    if fecha_actual < fecha_limite_calendario:
        # Sumamos 1 día al límite final solo para que el casillero del 31 de diciembre quede pintado completo
        fecha_fin_calendario_visual = fecha_limite_calendario + timedelta(days=1)
        calendar_events.append({
            "title": "Disponible",
            "start": fecha_actual.strftime('%Y-%m-%d'),
            "end": fecha_fin_calendario_visual.strftime('%Y-%m-%d'),
            "color": '#00CC96'  # Verde
        })

    # --- 5. CONFIGURACIÓN Y RENDERIZADO ---
    calendar_options = {
        "editable": "false",
        "selectable": "false",
        "headerToolbar": {
            "left": "today prev,next",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek",
        },
        "initialView": "dayGridMonth",
    }

    calendar(events=calendar_events, options=calendar_options)
