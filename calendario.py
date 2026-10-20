import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta

def mostrar_calendario(df):
    # --- 1. CONFIGURACIÓN SEGURA DE FORMATO DE FECHAS ---
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], dayfirst=True, errors='coerce', format='mixed')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], dayfirst=True, errors='coerce', format='mixed')
    
    # Limpiamos las horas de las columnas
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

    # --- 4. CÁLCULO DE HUECOS "DISPONIBLE" ARREGLADO PARA FIN DE AÑO ---
    año_actual = 2027  # Año de la pantalla actual
    
    # Buscamos si el departamento ya viene ocupado desde diciembre del año anterior
    reserva_previa = df_filtrado[df_filtrado['Fecha de Inicio'] < datetime(año_actual, 1, 1).date()]
    
    if not reserva_previa.empty:
        # Si ya venía ocupado (ej. hasta el 9 de enero), el cálculo disponible arranca el día del checkout real
        ultima_fecha_previa = reserva_previa['Fecha de Fin'].max()
        fecha_actual = max(datetime(año_actual, 1, 1).date(), ultima_fecha_previa)
    else:
        # Si no había nada a fin de año, arrancamos libres el 1 de enero
        fecha_actual = datetime(año_actual, 1, 1).date()
        
    fecha_limite_calendario = datetime(año_actual, 12, 31).date()
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        # Ignoramos la reserva previa porque ya la contemplamos en el punto de partida
        if f_fin <= fecha_actual:
            continue
            
        if fecha_actual < f_ini:
            # Estiramos el bloque verde +1 día para forzar el cruce exacto en el check-in (ej. día 18)
            fecha_fin_verde_visual = f_ini + timedelta(days=1)
            
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": fecha_fin_verde_visual.strftime('%Y-%m-%d'),
                "color": '#00CC96'  # Verde
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

    # --- 5. CONFIGURACIÓN DE TEXTO Y ESTILOS (AZUL FRANCIA) ---
    st.markdown(
        """
        <style>
        .fc-more-link {
            color: #0046BF !important;
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
        "showNonCurrentDates": "true",
        "moreLinkText": "Res.", 
    }

    calendar(events=calendar_events, options=calendar_options)
