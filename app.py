import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from calendario import mostrar_calendario

# Configuración de la página
st.set_page_config(
    page_title="BR Control de Reservas",
    layout="wide",
)

# Estilos
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    h1 {
        font-size: 1.5rem !important;
        margin-bottom: 0.5rem;
    }
    h2 {
        font-size: 1.2rem !important;
        margin-top: 1rem;
    }
    .stNumberInput, .stTextInput, .stDateInput, .stSelectbox {
        margin-bottom: -10px;
    }
    div[data-testid="stForm"] {
        padding: 10px;
        border-radius: 10px;
    }
    input {
        font-size: 14px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Conexión a Google Sheets
def conectar_gsheets():
    try:
        scope = ["https://googleapis.com"]
        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope,
        )
        client = gspread.authorize(creds)

        spreadsheet_id = "1ch4-13lpkAZRdN3cuj5QJTLAKs5bUIW8K3ckbzbVhZw"
        return client.open_by_key(spreadsheet_id).get_worksheet(0)

    except Exception as e:
        st.error(f"Error de conexión con Google Sheets: {e}")
        return None


def obtener_datos(sheet):
    if sheet is None:
        return pd.DataFrame()

    try:
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"No se pudo leer el historial: {e}")
        return pd.DataFrame()


# Interfaz
st.title("🇧🇷 Control de Reservas")

sheet = conectar_gsheets()

with st.form("form_reserva", clear_on_submit=True):
    # Departamento y estado
    c1, c2 = st.columns(2)

    with c1:
        depto = st.selectbox(
            "Departamento",
            ["Robles", "Naciones", "Costa"],
        )

    with c2:
        estado = st.selectbox(
            "Estado",
            ["Alquilado", "Disponible", "Reservado"],
        )

    # Fechas
    f1, f2 = st.columns(2)

    with f1:
        # CORRECCIÓN FORMULARIO: Agregamos format="DD/MM/YYYY" para cambiar el orden visual en pantalla
        fecha_inicio = st.date_input("Inicio", value=datetime.now().date(), format="DD/MM/YYYY")

    with f2:
        # CORRECCIÓN FORMULARIO: Agregamos format="DD/MM/YYYY" para cambiar el orden visual en pantalla
        fecha_fin = st.date_input("Fin", value=datetime.now().date(), format="DD/MM/YYYY")

    # Inquilino y teléfono
    i1, i2 = st.columns(2)

    with i1:
        inquilino = st.text_input("Inquilino")

    with i2:
        telefono = st.text_input("Teléfono")

    # Precio y total
    p1, p2 = st.columns(2)

    with p1:
        precio = st.number_input(
            "Precio por Día (R$)",
            min_value=0.0,
            step=10.0,
            format="%.2f",
        )

    dias_estadia = max((fecha_fin - fecha_inicio).days, 0)
    total_reserva = dias_estadia * precio

    with p2:
        st.markdown(f"**Total: R$ {total_reserva:,.2f}** ({dias_estadia} días)")

    submit = st.form_submit_button("Confirmar y Guardar")


if submit:
    if not inquilino.strip() or not telefono.strip():
        st.warning("Completá el nombre del inquilino y el teléfono.")
    elif dias_estadia <= 0:
        st.warning("La fecha de fin debe ser posterior a la fecha de inicio.")
    elif sheet is None:
        st.error("No hay conexión con Google Sheets. Revisá la configuración.")
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
            respuesta = sheet.append_row(
                nueva_fila,
                value_input_option="USER_ENTERED",
            )
            st.success(f"Reserva guardada. Respuesta de Google Sheets: {respuesta}")
        except Exception as e:
            st.error(f"No se pudo guardar la reserva: {e}")


# Historial
st.subheader("📋 Historial")

df = obtener_datos(sheet)

# Dejamos que el calendario procese el DataFrame puro con su lógica interna
mostrar_calendario(df)

if not df.empty:
    # --- CONVERSIÓN ESTRICTA A TEXTO PARA LA TABLA DEL HISTORIAL ---
    # Pasamos las columnas a formato de tiempo para ordenarlas cronológicamente
    df['Fecha de Inicio'] = pd.to_datetime(df['Fecha de Inicio'], dayfirst=True, errors='coerce')
    df['Fecha de Fin'] = pd.to_datetime(df['Fecha de Fin'], dayfirst=True, errors='coerce')
    
    # Transformamos a texto fijo para que Streamlit no de vuelta los valores en la tabla de abajo
    df['Fecha de Inicio'] = df['Fecha de Inicio'].dt.strftime('%d/%m/%Y')
    df['Fecha de Fin'] = df['Fecha de Fin'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Sin datos.")
