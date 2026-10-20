import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta

def mostrar_calendario(df):
    # --- 1. CONFIGURACIÓN SEGURA DE FORMATO DE FECHAS ---
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], dayfirst=True, errors='coerce', format='mixed')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], dayfirst=True, errors='coerce', format='mixed')
    
    # Eliminamos las horas para mantener la consistencia en el historial
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
        # Sumamos 1 día al cierre para la visualización (cubre la última noche reservada)
        fecha_fin_visual = row['Fecha de Fin'] + timedelta(days=1)
        
        event = {
            "title": f"{row['Departamento']} - {row['Inquilino']} ({estado})",
            "start": row['Fecha de Inicio'].strftime('%Y-%m-%d'),
            "end": fecha_fin_visual.strftime('%Y-%m-%d'),
            "color": colores.get(estado, '#FF4B4B')
        }
        calendar_events.append(event)

    # --- 4. CÁLCULO DE HUECOS VERDES OPTIMIZADO (SIN SOLAPAMIENTO EN ENERO) ---
    año_actual = 2027  # Año principal de la pantalla
    fecha_limite_calendario = datetime(año_actual, 12, 31).date()
    
    # Verificamos si este departamento específico viene ocupado desde Diciembre del año anterior
    reserva_fin_de_ano = df_filtrado[df_filtrado['Fecha de Inicio'] < datetime(año_actual, 1, 1).date()]
    
    if not reserva_fin_de_ano.empty:
        # Si venía ocupado, el primer bloque disponible arrancará el día del checkout real (+1 día de margen para el cruce)
        ultima_fecha_fin = reserva_fin_de_ano['Fecha de Fin'].max()
        fecha_actual = max(datetime(año_actual, 1, 1).date(), ultima_fecha_fin)
    else:
        # Si empezaba el año libre, arrancamos el bloque verde desde el 1 de Enero normal
        fecha_actual = datetime(año_actual, 1, 1).date()
        
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        # Ignoramos registros obsoletos que cierran antes o en el mismo punto de nuestro puntero actual
        if f_fin <= fecha_actual:
            continue
            
        if fecha_actual < f_ini:
            # Sincronizamos el cruce de recambio sumando 1 día exacto al bloque verde
            fecha_fin_verde_visual = f_ini + timedelta(days=1)
            
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": fecha_fin_verde_visual.strftime('%Y-%m-%d'),
                "color": '#00CC96'  # Verde
            })
        
        if f_fin > fecha_actual:
            fecha_actual = f_fin
            
    # Rellenamos el tramo final hasta el cierre del año
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
            color: #0046BF !important;       /* Azul Francia fuerte */
            font-weight: bold !important;    /* Negrita destacada */
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
