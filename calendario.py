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

    # Definimos los límites estrictos del año actual en pantalla (2027)
    año_pantalla = 2027
    limite_inferior = datetime(año_pantalla, 1, 1).date()
    limite_superior = datetime(año_pantalla, 12, 31).date()

    # --- 3. PROCESAR OCUPACIONES EXISTENTES CON RECORTE SEGURO ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        
        f_inicio_real = row['Fecha de Inicio']
        f_fin_real = row['Fecha de Fin']
        
        # Si la reserva termina antes de este año o empieza después, la salteamos
        if f_fin_real < limite_inferior or f_inicio_real > limite_superior:
            continue
            
        # LA VUELTA TÉCNICA: Si la reserva empezó el año pasado, hacemos que visualmente 
        # arranque el 25 de diciembre. Así FullCalendar pinta obligatoriamente los días grises de la primera hilera.
        if f_inicio_real < limite_inferior:
            f_inicio_visual = datetime(año_pantalla - 1, 12, 25).date()
        else:
            f_inicio_visual = f_inicio_real
            
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
            # Estiramos +1 día el verde en el Check-In para armar el cruce del "+2 more" nativo
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

    # --- 5. CONFIGURACIÓN Y RENDERIZADO ORIGINAL ---
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
