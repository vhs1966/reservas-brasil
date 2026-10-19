import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

def mostrar_calendario(df):
    # 1. Convertimos las fechas a formato datetime de forma segura (con errors='coerce')
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], errors='coerce')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], errors='coerce')

    # 2. FILTRADO: Eliminamos cualquier fila que se haya quedado sin una fecha de inicio o de fin válida
    df = df.dropna(subset=['Fecha de Inicio', 'Fecha de Fin'])

    calendar_events = []
    
    # Mapeo de colores según el estado
    colores = {
        'Alquilado': '#FF4B4B',  # Rojo
        'Reservado': '#FFD700',  # Amarillo
        'Disponible': '#00CC96'  # Verde
    }

    # Procesamos cada fila para crear los eventos del calendario
    for _, row in df.iterrows():
        event = {
            "title": f"{row['Departamento']} - {row['Inquilino']}",
            "start": row['Fecha de Inicio'].strftime('%Y-%m-%d'),
            "end": row['Fecha de Fin'].strftime('%Y-%m-%d'),
            "color": colores.get(row['Estado'], '#00CC96') # Verde por defecto
        }
        calendar_events.append(event)

    # Configuración de opciones del calendario
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

    # Renderizamos el calendario
    calendar(events=calendar_events, options=calendar_options)
