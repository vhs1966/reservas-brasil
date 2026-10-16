import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="BR Control de Reservas - Brasil", layout="wide")

# Estilos personalizados para móviles
st.markdown("""
    <style>
    .main { padding: 1rem; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    input, select { font-size: 16px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_gsheets():
    try:
        # Usa las credenciales de st.secrets (Configuradas en Streamlit Cloud)
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        
        # ID de tu hoja (el que sacamos de la URL)
        spreadsheet_id = "1ch4-13lpkAZRdN3cuj5QJTLAKs5bUIW8K3ckbzbVhZw" # REEMPLAZA CON TU ID REAL
        sheet = client.open_by_key(spreadsheet_id).get_worksheet(0) # Abre la primera pestaña
        return sheet
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# Cargar datos desde Google Sheets
def obtener_datos(sheet):
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

# --- INTERFAZ ---
st.title("🇧🇷 BR Control de Reservas - Brasil")

sheet = conectar_gsheets()

# Formulario de Carga
st.header("➕ Cargar Nueva Reserva")

with st.form("form_reserva", clear_on_submit=True):
    col1, col2 = st.columns([1, 1])
    
    with col1:
        depto = st.selectbox("Selecciona el Departamento", ["Robles", "Naciones", "Costa"])
        fecha_inicio = st.date_input("Fecha de Inicio", datetime.now())
        estado = st.selectbox("Estado", ["Alquilado", "Disponible", "Reservado"])
        
    with col2:
        fecha_fin = st.date_input("Fecha de Fin", datetime.now())
        inquilino = st.text_input("Nombre del Inquilino")
        telefono = st.text_input("Teléfono de Contacto")
        
    precio = st.number_input("Precio por Día ($)", min_value=0.0, step=10.0, format="%.2f")
    
    # Cálculos Automáticos
    dias_estadia = (fecha_fin - fecha_inicio).days
    if dias_estadia < 0: dias_estadia = 0
    total_reserva = dias_estadia * precio
    
    st.info(f"📊 **Resumen:** {dias_estadia} días de estadía | **Total:** ${total_reserva:,.2f}")
    
    submit = st.form_submit_button("Guardar Reserva")

    if submit:
        if inquilino and telefono and sheet:
            nueva_fila = [
                depto,
                fecha_inicio.strftime('%d/%m/%Y'),
                fecha_fin.strftime('%d/%m/%Y'),
                estado,
                inquilino,
                telefono,
                dias_estadia,
                precio,
                total_reserva
            ]
            try:
                sheet.append_row(nueva_fila)
                st.success("✅ Reserva guardada con éxito en Google Sheets")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        elif not sheet:
            st.error("No hay conexión con la planilla.")
        else:
            st.error("⚠️ Por favor, completa los campos obligatorios.")

# Tabla de Reservas
st.header("📋 Reservas Registradas")

df = obtener_datos(sheet)
if not df.empty:
    st.dataframe(df, use_container_width=True)
else:
    st.info("No hay datos disponibles en la planilla.")
