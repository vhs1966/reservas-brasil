import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import base64
import json

st.set_page_config(page_title="Reservas Brasil", page_icon="🇧🇷", layout="centered")
st.title("🇧🇷 Control de Reservas - Brasil")

# Conexión ultra segura y blindada por Base64
@st.cache_data(ttl=2)
def cargar_datos():
    # El programa lee el diccionario seguro de la cajita de secretos de forma oficial
    info_claves = dict(st.secrets["gcp_service_account"])
    gc = gspread.service_account_from_dict(info_claves)
    sh = gc.open('Reservas Brasil')
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    return worksheet, pd.DataFrame(data)

try:
    worksheet, df = cargar_datos()
except Exception as e:
    st.error(f"⛔ Error de conexión real: {e}")
    df = pd.DataFrame()

# ----------------- FORMULARIO DE CARGA -----------------
st.subheader("➕ Cargar Nueva Reserva")
with st.form("nueva_reserva", clear_on_submit=True):
    depto = st.selectbox("Seleccioná el Departamento", ["Costa", "Robles", "Naciones"])
    
    col1, col2 = st.columns(2)
    with col1:
        f_inicio = st.date_input("Fecha de Inicio", datetime.now(), format="DD/MM/YYYY")
    with col2:
        f_fin = st.date_input("Fecha de Fin", datetime.now(), format="DD/MM/YYYY")
        
    estado = st.selectbox("Estado", ["Alquilado", "Reservado", "Disponible"])
    inquilino = st.text_input("Nombre del Inquilino")
    telefono = st.text_input("Teléfono de Contacto")
    precio_dia = st.number_input("Precio por Día ($)", min_value=0.0, step=10.0, value=0.0)
    
    boton_guardar = st.form_submit_button("Guardar Reserva")

    if boton_guardar:
        if f_fin < f_inicio:
            st.error("⛔ Error: La fecha de fin no puede ser anterior a la de inicio.")
        elif inquilino == "":
            st.error("⛔ Error: El nombre del inquilino es obligatorio.")
        else:
            dias_estadia = (f_fin - f_inicio).days
            if dias_estadia == 0:
                dias_estadia = 1
                
            total_pagar = dias_estadia * precio_dia
            
            f_inicio_str = f_inicio.strftime("%d/%m/%Y")
            f_fin_str = f_fin.strftime("%d/%m/%Y")
            
            nueva_fila = [
                depto, 
                f_inicio_str, 
                f_fin_str, 
                estado, 
                inquilino, 
                str(telefono), 
                int(dias_estadia), 
                float(precio_dia), 
                float(total_pagar)
            ]
            
            if not df.empty or len(df) == 0:
                worksheet.append_row(nueva_fila)
                st.success(f"✅ ¡Reserva guardada! {dias_estadia} días calculados. Total: ${total_pagar}")
                st.rerun()
            else:
                st.error("No se pudo guardar. Intente nuevamente.")

# ----------------- VISTA DE TABLA PARA AGENTES -----------------
st.subheader("📋 Reservas Registradas")
if not df.empty:
    columnas_validas = [c for c in ["Departamento", "Fecha de Inicio", "Fecha de Fin", "Estado", "Inquilino", "Total"] if c in df.columns]
    st.dataframe(df[columnas_validas], use_container_width=True, hide_index=True)
else:
    st.info("No hay reservas registradas todavía.")
