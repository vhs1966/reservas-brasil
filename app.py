import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="BR Control de Reservas - Brasil", layout="wide")

# Estilos personalizados para móviles
st.markdown("""
    <style>
    .main {
        padding: 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    /* Optimización para inputs en móviles */
    input, select {
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🇧🇷 BR Control de Reservas - Brasil")

# Inicialización del estado de la sesión para simular una base de datos local
if 'reservas' not in st.session_state:
    st.session_state.reservas = pd.DataFrame(columns=[
        "Departamento", "Fecha Inicio", "Fecha Fin", "Estado", "Inquilino", "Teléfono", "Precio/Día"
    ])

# Formulario de Carga
st.header("➕ Cargar Nueva Reserva")

with st.form("form_reserva", clear_on_submit=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        depto = st.selectbox("Selecciona el Departamento", ["Costa", "Centro", "Norte", "Sur"])
        fecha_inicio = st.date_input("Fecha de Inicio", datetime.now())
        estado = st.selectbox("Estado", ["Alquilado", "Reservado", "Disponible", "Mantenimiento"])
        
    with col2:
        fecha_fin = st.date_input("Fecha de Fin", datetime.now())
        inquilino = st.text_input("Nombre del Inquilino")
        telefono = st.text_input("Teléfono de Contacto")
        
    precio = st.number_input("Precio por Día ($)", min_value=0.0, step=10.0, format="%.2f")
    
    submit = st.form_submit_button("Guardar Reserva")

    if submit:
        if inquilino and telefono:
            nueva_reserva = {
                "Departamento": depto,
                "Fecha Inicio": fecha_inicio.strftime('%d/%m/%Y'),
                "Fecha Fin": fecha_fin.strftime('%d/%m/%Y'),
                "Estado": estado,
                "Inquilino": inquilino,
                "Teléfono": telefono,
                "Precio/Día": precio
            }
            st.session_state.reservas = pd.concat([st.session_state.reservas, pd.DataFrame([nueva_reserva])], ignore_index=True)
            st.success("✅ Reserva guardada con éxito")
        else:
            st.error("⚠️ Por favor, completa los campos obligatorios (Inquilino y Teléfono)")

# Tabla de Reservas
st.header("📋 Reservas Registradas")

if not st.session_state.reservas.empty:
    # Contenedor con scroll horizontal para móviles
    st.dataframe(st.session_state.reservas, use_container_width=True)
    
    # Botón para limpiar (opcional)
    if st.button("Limpiar Todas las Reservas"):
        st.session_state.reservas = pd.DataFrame(columns=st.session_state.reservas.columns)
        st.rerun()
else:
    st.info("No hay reservas registradas todavía.")
