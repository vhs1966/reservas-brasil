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
    import json
    # Cargamos el diccionario de forma nativa e independiente
    credenciales_json = '''{
  "type": "service_account",
  "project_id": "reservasbrasil",
  "private_key_id": "8a9dc35bc6afc57cf3cc808e8b0eb3b2fc19f5b6",
  "private_key": "-----BEGIN PRIVATE KEY-----\\newogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIsCiAgInByb2plY3RfaWQiOiAicmVzZXJ2YXNicmFzaWwiLAogICJwcml2YXRlX2tleV9pZCI6ICI4YTlkYzM1YmM2YWZjNTdjZjNjYzgwOGU4YjBlYjNiMmZjMTlmNWI2IiwKICAicHJpdmF0ZV9rZXkiOiAiLS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0tXG5NSUlFdlFJQkFEQU5CZ2txaGtpRzl3MEJBUUVGQUFTQ0JLY3dnZ1NqQWdFQUFvSUJBUUN3ZUUrTnFNTjdFdzNFXG5nNTRSWnVTQjlmTk1aWFhwa1djMzB4a0hsdHdabVB0cm56dkZHd0Y2aEhFeDBxMU9JYlJvVldDMUZTQjVHckNuXG5ZV3k3MjBmZEEwZ3hXcDNSNXo3ZUpsSDAzblZEdnljQkh0NDYyejlVZ1FoenMva0Mxa3ZOM3JuZDB5UUR3bHVUXG5MTmxEU1doRGR5TGoyeXJsazdDcHNETFZva2lscG5DUzJlZ3FvOFFkWHBYRit5Vjd5MU01T1k5TFZZNGIvY2RSXG41bklUWW5tM3c3Q3pJSmJhWWUwNHNPQ3VXWkNKemp0ZFc2V0dNZ2Zwd1gwZ2hqenA0bHlHbVgxL0NTZVRxclFjXG5hODF0UCtRUE5jT2taRDhIbnd6T3VkU2dxeFptOHZuVGdKNGUxQ3RnOTZIbmlBRGFBczhGejU0aXM0VDloU0dzXG4vaDZYbjMyMUFnTUJBQUVDZ2dFQUF0eVJNdW10ZTF2SVBVR0NndDVyN0JxQmZEcFA0MHJDYnpxVU53Nmk3OEZUXG5sbVNiSWJWMCtocXFzN0xieElGUGZXdnZ4by96YVIraTNlK3J4WVhFcVE2MmgxT1Z1ODF4cWxpZXA2N0Frek9MXG53RUhjeFJCQXRqblI0N0NVMmtCczBNeDIvcFUyQ2diemRsdGp0U1c4Rm5DWW9UUkVnazg1WDBVMUVPWUZoUVRpXG5ocVNkeG9EaS9tZlAyaXd4Vy9xazhuM1o1UzVJTDkxbUl5eFJ0SGRhNGsrUGFjNWlPZ2FqbHdwcFYza3c3aFpJXG41RGFCMTlsOFI1ZGxuQ0VPNlJQZkJrdzR5SlZBVDdkV2dEa0tMRFRkUUU4ZWJZVnFvNVBNT3VSMWJDbzdtM3dtXG5JdWRBVE03S3I5Y0NCUTBEa1NHc3JOdk5BOENTT3VSektSd29kUFpNOFFLQmdRRFpOTXJidXp1eHZFUWtQNWFSXG5iY081dnRpSXNNd25Na0g3c3JzQmtaOTlEaFEzMHhxYkxuN3lWbEx5bW4rM1RFNWtJeHNES3ZoRENYTVpHWmZkXG5hVUdseVNWZTMzY053ZEFuTStsL2dOZzNHVlh5ZDNYVUhIU3lZS09DQTMrNURXcFgyYXJ4YkdOMW12Z2tOc2tZXG5KSzlBRG00YmE2OU12WWc1UVI1ck8rUEJtUUtCZ1FEUC9QU2dSQWtJVkorMm5oS1JCN05xMTdLb3BqazFaeDB5XG5oUDlVb2szbFBQY2hBcmtrRWVPY0luUEcvUmFjNTVrN1hSOVU2dFBTeXN2NW5OOHJRdjZMRDdqK2g3dWRZWFl0XG5YTmJhajgrMmRpdHRTeGt6b3RjRDJYcHBDSHdwNEhQL2pIT3ZqaEpkeFY0T0hlODA1OE1pOU81enJLTTRTN2hvXG5tTTVsWnQ5bWZRS0JnR3UvRW5wWnNNMEVOVkU5OGZVR1hEZENBcXdiOThuaDFuV0RQZDBUWGVodEdYNXZ6Qno2XG52YUo5Uy94b3c3NHJyaDlpZ3IzWmpQbkVNRUpkUGNacHRsVUZLUEtkSzdPNVZ3WjdhL01CK1QrcjQ4UzVtY3UwXG5xZmJxbFhHalJyS0hneDg5TE4xQ0JUeUx1VmhOalFmYStzeHQzQlRpSUQyVEw0WW5WVzJnY2VUUkFvR0FHWU0yXG40cDNWMmM2L2xLQUpPUDhQMUJCSFd3YWd4OXN4S3F4RHdiYnpCU2FZVGRWT3Jvei9OWHpJWk9WUXE4aUE5RlkwXG43SzZ0Y3hMck9HQTB3OUxBOUgvbU9scWQrZTBsbU9UbGVnUGYvOHE1QXZ3T1NGWTJOOE9xajAyNkpVemlEYnZGXG55UWdOV3JGR0cwY3l1M09lYlNCTVM2WW1rMVkrZFo0ZzJ6Rm1QK1VDZ1lFQXpCWUtnZytOMWpnMGpvUzg4MGd3XG41bTlMTXVJNm4vQnA0OTRzUmJYMFA3QVlWZUNCbjQzK0UvYndDcHRkRlVXb1U2OEtXVEF2STFyOEVIVk0xb1BjXG5RbCtReFh3YnI3VUNQY3Z3MUtOTldPTjhnQi9rZnNjSXNTWlRtRTBYMUdiTThnZktzN1hVM0J1enlRL2VtdnMwXG5SSThkSjdjaE5qeTArV2FtRWVzT0RzMD1cbi0tLS0tRU5EIFBSSVZBVEUgS0VZLS0tLS1cbiIsCiAgImNsaWVudF9lbWFpbCI6ICJyZXNlcnZhcy1hcHBAcmVzZXJ2YXNicmFzaWwuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLAogICJjbGllbnRfaWQiOiAiMTA1OTI1OTA1MjcxNzM2NDc0NzU0IiwKICAiYXV0aF91cmkiOiAiaHR0cHM6Ly9hY2NvdW50cy5nb29nbGUuY29tL28vb2F1dGgyL2F1dGgiLAogICJ0b2tlbl91cmkiOiAiaHR0cHM6Ly9vYXV0aDIuZ29vZ2xlYXBpcy5jb20vdG9rZW4iLAogICJhdXRoX3Byb3ZpZGVyX3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vb2F1dGgyL3YxL2NlcnRzIiwKICAiY2xpZW50X3g1MDlfY2VydF91cmwiOiAiaHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vcm9ib3QvdjEvbWV0YWRhdGEveDUwOS9yZXNlcnZhcy1hcHAlNDByZXNlcnZhc2JyYXNpbC5pYW0uZ3NlcnZpY2VhY2NvdW50LmNvbSIsCiAgInVuaXZlcnNlX2RvbWFpbiI6ICJnb29nbGVhcGlzLmNvbSIKfQo=\\n",
  "client_email": "reservas-app@://gserviceaccount.com",
  "client_id": "105925905271736474754",
  "auth_uri": "https://google.com",
  "token_uri": "https://googleapis.com",
  "auth_provider_x509_cert_url": "https://googleapis.com",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/reservas-app%40://gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'''
    info_claves = json.loads(credenciales_json.strip())
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
