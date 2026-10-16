import streamlit as st
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(
    page_title="Control de Reservas - Brasil",
    page_icon="🇧🇷",
    layout="centered",
)

st.title("🇧🇷 Control de Reservas - Brasil")

# Encabezados que tendrá la hoja de Google Sheets.
ENCABEZADOS = [
    "Departamento",
    "Fecha de inicio",
    "Fecha de fin",
    "Estado",
    "Nombre del huésped",
    "Teléfono de contacto",
    "Precio por día (R$)",
]


@st.cache_resource
def conectar_google_sheets():
    """Conecta con Google Sheets y devuelve la hoja de trabajo."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    credenciales = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]),
        scopes=scopes,
    )

    cliente = gspread.authorize(credenciales)

    # Reemplaza este texto por el ID de la hoja, no por su nombre.
    archivo = cliente.open_by_key("1ch4-13lpkAZRdN3cuj5QJTLAKs5bUIW8K3ckbzbVhZw")

    # Si la pestaña se llama distinto, cambia "Reservas".
    try:
        hoja = archivo.worksheet("Reservas")
    except gspread.WorksheetNotFound:
        hoja = archivo.add_worksheet(title="Reservas", rows=1000, cols=len(ENCABEZADOS))

    # Agrega los encabezados si la pestaña está vacía.
    if not hoja.row_values(1):
        hoja.append_row(ENCABEZADOS)

    return hoja


# Intenta conectar antes de mostrar el formulario.
try:
    worksheet = conectar_google_sheets()
    error_conexion = None
except Exception as e:
    worksheet = None
    error_conexion = str(e)

if error_conexion:
    st.error(
        "No se pudo conectar con Google Sheets. "
        "Revisa el ID de la hoja, las credenciales y los permisos de la cuenta de servicio."
    )
    with st.expander("Ver detalle del error"):
        st.code(error_conexion)

st.subheader("➕ Cargar Nueva Reserva")

with st.form("formulario_reserva", clear_on_submit=True):
    departamento = st.selectbox(
        "Seleccioná el Departamento",
        ["Costa", "Centro", "Norte", "Sur"],
    )

    col1, col2 = st.columns(2)
    with col1:
        fecha_inicio = st.date_input("Fecha de inicio", value=date.today())
    with col2:
        fecha_fin = st.date_input("Fecha de fin", value=date.today())

    estado = st.selectbox(
        "Estado",
        ["Alquilado", "Disponible", "Pendiente"],
    )

    nombre = st.text_input("Nombre del huésped")
    telefono = st.text_input("Teléfono de contacto")
    precio = st.number_input(
        "Precio por día (R$)",
        min_value=0.0,
        step=10.0,
        format="%.2f",
    )

    enviado = st.form_submit_button("Guardar Reserva")

if enviado:
    if worksheet is None:
        st.error("No se puede guardar la reserva porque no hay conexión con Google Sheets.")
    elif fecha_fin < fecha_inicio:
        st.error("La fecha de fin no puede ser anterior a la fecha de inicio.")
    elif not nombre.strip():
        st.error("Ingresá el nombre del huésped.")
    else:
        nueva_reserva = [
            departamento,
            fecha_inicio.strftime("%d/%m/%Y"),
            fecha_fin.strftime("%d/%m/%Y"),
            estado,
            nombre.strip(),
            telefono.strip(),
            precio,
        ]

        try:
            worksheet.append_row(nueva_reserva, value_input_option="USER_ENTERED")
            st.success("Reserva guardada correctamente.")
            st.rerun()
        except Exception as e:
            st.error(f"No se pudo guardar la reserva: {e}")

st.subheader("📋 Reservas Registradas")

if worksheet is not None:
    try:
        registros = worksheet.get_all_records()

        if registros:
            df = pd.DataFrame(registros)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay reservas registradas todavía.")
    except Exception as e:
        st.error(f"No se pudieron cargar las reservas: {e}")
else:
    st.info("Las reservas aparecerán aquí cuando se restablezca la conexión.")
