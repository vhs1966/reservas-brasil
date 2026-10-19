import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta

def mostrar_calendario(df):
    # 1. Limpieza inicial de datos con fechas válidas
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], errors='coerce')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], errors='coerce')
    df = df.dropna(subset=['Fecha de Inicio', 'Fecha de Fin'])
    
    # 2. FILTRO POR DEPARTAMENTO
    # Extraemos la lista de departamentos únicos para el selector
    lista_deptos = sorted(df['Departamento'].unique().tolist())
    depto_seleccionado = st.selectbox("🏢 Selecciona un Departamento:", lista_deptos)
    
    # Filtramos el DataFrame para quedarnos solo con los datos del departamento elegido
    df_filtrado = df[df['Departamento'] == depto_seleccionado].sort_values(by='Fecha de Inicio')

    calendar_events = []
    
    # Mapeo de colores fijos para Alquilado y Reservado
    colores = {
        'Alquilado': '#FF4B4B',  # Rojo
        'Reservado': '#FFD700',  # Amarillo
    }

    # --- AGREGAR OCUPACIONES EXISTENTES (Rojo / Amarillo) ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        event = {
            "title": f"{row['Departamento']} - {row['Inquilino']} ({estado})",
            "start": row['Fecha de Inicio'].strftime('%Y-%m-%d'),
            "end": row['Fecha de Fin'].strftime('%Y-%m-%d'),
            "color": colores.get(estado, '#FF4B4B') # Rojo por defecto si hay dudas
        }
        calendar_events.append(event)

    # --- CALCULAR AUTOMÁTICAMENTE LOS DÍAS DISPONIBLES (Verde) ---
    # Definimos el rango del calendario: desde hoy hasta fin de año (ej. 31 de Diciembre)
    fecha_inicio_calendario = datetime.today()
    fecha_fin_calendario = datetime(fecha_inicio_calendario.year, 12, 31)
    
    # Ordenamos los rangos ocupados cronológicamente para medir los huecos
    periodos_ocupados = []
    for _, row in df_filtrado.iterrows():
        periodos_ocupados.append((row['Fecha de Inicio'], row['Fecha de Fin']))
    
    # Algoritmo para encontrar ventanas libres
    fecha_actual = fecha_inicio_calendario
    for inicio_p, fin_p in periodos_ocupados:
        # Si la fecha actual es anterior al inicio de una reserva, ese hueco está Disponible
        if fecha_actual < inicio_p:
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": inicio_p.strftime('%Y-%m-%d'),
                "color": '#00CC96'  # Verde
            })
        # Avanzamos nuestra posición al fin de esta ocupación para seguir evaluando
        if fin_p > fecha_actual:
            fecha_actual = fin_p
            
    # Si después de la última reserva analizada queda tiempo hasta fin de año, lo marcamos Disponible
    if fecha_actual < fecha_fin_calendario:
        calendar_events.append({
            "title": "Disponible",
            "start": fecha_actual.strftime('%Y-%m-%d'),
            "end": fecha_fin_calendario.strftime('%Y-%m-%d'),
            "color": '#00CC96'  # Verde
        })

    # 3. Configuración de opciones del calendario
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

    # Renderizamos el calendario con los eventos de ocupación + los huecos verdes automáticos
    calendar(events=calendar_events, options=calendar_options)
