import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Configuración de la página (Layout wide para aprovechar el espacio)
st.set_page_config(page_title="BR Control de Reservas", layout="wide")

# Estilos personalizados para compactar la interfaz y mejorar visualización móvil
st.markdown("""
    <style>
    .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 1.5rem !important; margin-bottom: 0.5rem; }
    h2 { font-size: 1.2rem !important; margin-top: 1rem; }
    .stNumberInput, .stTextInput, .stDateInput, .stSelectbox { margin-bottom: -10px; }
    div[data-testid="stForm"] { padding: 10px; border-radius: 10px; }
    /* Ajuste para que los inputs se vean bien en pantallas pequeñas */
    input { font-size: 14px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CONEXIÓN A GOOGLE SHEETS ---
def conectar_gsheets():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        client = gspread.authorize(creds)
        spreadsheet_id = "1ch4-13lpkAZRdN3cuj5QJTLAKs5bUIW8K3ckbzbVhZw" # REEMPLAZA CON TU ID REAL
        sheet = client.open_by_key(spreadsheet_id).get_worksheet(0)
        return sheet
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

def obtener_datos(sheet):
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame()

# --- INTERFAZ ---
st.title("🇧🇷 Control de Reservas")

sheet = conectar_gsheets()

# Formulario de Carga Compacto
with st.form("form_reserva", clear_on_submit=True):
    # Fila 1: Departamento y Estado
    c1, c2 = st.columns(2)
    with c1:
        depto = st.selectbox("Departamento", ["Robles", "Naciones", "Costa"])
    with c2:
        estado = st.selectbox("Estado", ["Alquilado", "Disponible", "Reservado"])

    # Fila 2: Fechas una al lado de la otra
    f1, f2 = st.columns(2)
    with f1:
        fecha_inicio = st.date_input("Inicio", datetime.now())
    with f2:
        fecha_fin = st.date_input("Fin", datetime.now())

    # Fila 3: Inquilino y Teléfono
    i1, i2 = st.columns(2)
    with i1:
        inquilino = st.text_input("Inquilino")
    with i2:
        telefono = st.text_input("Teléfono")
        
    # Fila 4: Precio en Reales (R$)
    p1, p2 = st.columns([1, 1])
    with p1:
        precio = st.number_input("Precio por Día (R$)", min_value=0.0, step=10.0, format="%.2f")
    
    # Cálculos Automáticos
    dias_estadia = (fecha_fin - fecha_inicio).days
    if dias_estadia < 0: dias_estadia = 0
    total_reserva = dias_estadia * precio
    
    with p2:
        st.markdown(f"**Total: R$ {total_reserva:.2f}**")
        st.markdown(f"**Total: R$ {total_reserva:,.2f}** ({dias_estadia} días)")
    
    submit = st.form_submit_button("Confirmar y Guardar")

       if submit:
        if not inquilino.strip() or not telefono.strip():
            st.warning("Completa los campos.")
        elif sheet is None:
            st.error("Error de conexión con Google Sheets.")
        else:
            nueva_fila = [
                depto,
                fecha_inicio.strftime("%d/%m/%Y"),
                fecha_fin.strftime("%d/%m/%Y"),
                estado,
                inquilino.strip(),
                telefono.strip(),
                dias_estadia,
                precio,
                total_reserva,
            ]

            try:
                resultado = sheet.append_row(
                    nueva_fila,
                    value_input_option="USER_ENTERED"
                )
                st.success(
                    f"Reserva enviada a Google Sheets. Respuesta: {resultado}"
                )
            except Exception as e:
                st.exception(e)

            elif not sheet:
                st.error("Error de conexión.")
        else:
            st.warning("Completa los campos.")

# Tabla de Reservas
st.subheader("📋 Historial")
df = obtener_datos(sheet)
if not df.empty:
    # Mostramos la tabla compacta
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Sin datos.")
