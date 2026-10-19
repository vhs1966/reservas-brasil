import streamlit as st
import pandas as pd
from streamlit_calendar import calendar

def mostrar_calendario(df):
    # Convertimos las fechas a formato datetime para asegurar consistencia
    # Ajusta los nombres de las columnas si en tu Google Sheet son distintos
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'])
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'])

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
