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
    
    # Paleta de colores limpia (Agregamos Naranja para el recambio)
    colores = {
        'Alquilado': '#FF4B4B',  # Rojo
        'Reservado': '#FFD700',  # Amarillo
        'Recambio': '#FF8C00',   # Naranja para Check-out / Check-in simultáneo
    }

    # Creamos un diccionario rápido para saber qué días exactos entra alguien
    dias_de_checkin = set(df_filtrado['Fecha de Inicio'].dt.strftime('%Y-%m-%d').tolist())

    # --- 3. PROCESAR OCUPACIONES EXISTENTES (Rojo / Amarillo) ---
    for _, row in df_filtrado.iterrows():
        estado = str(row['Estado']).strip().capitalize()
        
        f_ini_str = row['Fecha de Inicio'].strftime('%Y-%m-%d')
        f_fin_real = row['Fecha de Fin']
        
        # Validamos si el día de salida de este huésped coincide con el ingreso de otro
        f_fin_str = f_fin_real.strftime('%Y-%m-%d')
        
        if f_fin_str in dias_de_checkin:
            # Si coincide, la ocupación actual termina UN DÍA ANTES para cederle el casillero al "Recambio"
            fecha_fin_visual = f_fin_real
        else:
            # Si NO coincide, sumamos 1 día normal para que cubra la barra visual completa
            fecha_fin_visual = f_fin_real + timedelta(days=1)
        
        event = {
            "title": f"{row['Inquilino']} ({estado})",
            "start": f_ini_str,
            "end": fecha_fin_visual.strftime('%Y-%m-%d'),
            "color": colores.get(estado, '#FF4B4B')
        }
        calendar_events.append(event)
        
        # Si ese día de salida era un recambio, creamos el bloque naranja independiente de 1 solo día
        if f_fin_str in dias_de_checkin:
            dia_siguiente_recambio = f_fin_real + timedelta(days=1)
            calendar_events.append({
                "title": "🔄 Recambio",
                "start": f_fin_str,
                "end": dia_siguiente_recambio.strftime('%Y-%m-%d'),
                "color": colores['Recambio']
            })

    # --- 4. CÁLCULO DE HUECOS VERDES SIN SOLAPAR LOS RECAMBIOS ---
    año_actual = datetime.today().year
    fecha_actual = datetime(año_actual, 1, 1)
    fecha_limite_calendario = datetime(año_actual, 12, 31)
    
    # Creamos una lista de todos los días que están ocupados por reservas o recambios
    dias_ocupados_totales = set()
    for _, row in df_filtrado.iterrows():
        current = row['Fecha de Inicio']
        while current <= row['Fecha de Fin']:
            dias_ocupados_totales.add(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)

    # Armamos bloques verdes continuos agrupando los días que quedaron verdaderamente libres
    bloque_verde_inicio = None
    
    current_date = fecha_actual
    while current_date <= fecha_limite_calendario:
        date_str = current_date.strftime('%Y-%m-%d')
        
        if date_str not in dias_ocupados_totales:
            if bloque_verde_inicio is None:
                bloque_verde_inicio = current_date
        else:
            if bloque_verde_inicio is None:
                # Si el día de hoy es el checkout de una reserva y no hay checkin inmediato, arranca disponible HOY
                # Pero revisamos si la reserva anterior terminó ayer
                pass
            if bloque_verde_inicio is not None:
                calendar_events.append({
                    "title": "Disponible",
                    "start": bloque_verde_inicio.strftime('%Y-%m-%d'),
                    "end": current_date.strftime('%Y-%m-%d'),
                    "color": '#00CC96'
                })
                bloque_verde_inicio = None
                
        current_date += timedelta(days=1)
        
    if bloque_verde_inicio is not None:
        calendar_events.append({
            "title": "Disponible",
            "start": bloque_verde_inicio.strftime('%Y-%m-%d'),
            "end": (fecha_limite_calendario + timedelta(days=1)).strftime('%Y-%m-%d'),
            "color": '#00CC96'
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
