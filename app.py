import streamlit as st
import pandas as pd
from streamlit_calendar import calendar
from datetime import datetime, timedelta

def mostrar_calendario(df):
    # --- 1. CONFIGURACIÓN SEGURA DE FORMATO DE FECHAS ---
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], dayfirst=True, errors='coerce', format='mixed')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], dayfirst=True, errors='coerce', format='mixed')
    
    # Eliminamos las horas para mantener la consistencia interna
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
    año_actual = 2027
    fecha_actual = datetime(año_actual, 1, 1).date()
    fecha_limite_calendario = datetime(año_actual, 12, 31).date()
    
    for _, row in df_filtrado.iterrows():
        f_ini = row['Fecha de Inicio']
        f_fin = row['Fecha de Fin']
        
        if f_fin < fecha_actual:
            continue
            
        f_ini_ajustada = max(f_ini, fecha_actual)
        
        if fecha_actual < f_ini_ajustada:
            fecha_fin_verde_visual = f_ini_ajustada + timedelta(days=1)
            
            calendar_events.append({
                "title": "Disponible",
                "start": fecha_actual.strftime('%Y-%m-%d'),
                "end": fecha_fin_verde_visual.strftime('%Y-%m-%d'),
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

    # --- 5. CONFIGURACIÓN DE ESTILOS CSS ---
    st.markdown(
        """
        <style>
        .fc-multimonth-day {
            min-height: 42px !important;
        }
        .fc-event {
            margin-top: 1px !important;
            margin-bottom: 1px !important;
            padding: 0px 2px !important;
            font-size: 9px !important;
            line-height: 11px !important;
        }
        .fc-more-link {
            color: #0046BF !important;
            font-weight: bold !important;
            font-size: 9px !important;
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
        "dayMaxEvents": 2,
    }

    # Renderizamos el calendario
    calendar(events=calendar_events, options=calendar_options)

    # --- 6. FORMATEAR TABLA VISUAL (NUEVO: DD/MM/AAAA) ---
    # Creamos una copia de la tabla filtrada para cambiar el formato visual sin romper el calendario
    df_tabla_visual = df_filtrado.copy()
    
    # Transformamos el formato de visualización a Día/Mes/Año de forma prolija
    df_tabla_visual['Fecha de Inicio'] = pd.to_datetime(df_tabla_visual['Fecha de Inicio']).dt.strftime('%d/%m/%Y')
    df_tabla_visual['Fecha de Fin'] = pd.to_datetime(df_tabla_visual['Fecha de Fin']).dt.strftime('%d/%m/%Y')

    # Si tu listado impreso abajo usa st.dataframe o st.table, podés mostrar esta nueva variable:
    st.subheader("📋 Listado de Reservas Seleccionadas")
    st.dataframe(df_tabla_visual, use_container_width=True)
