import json
import os
from datetime import datetime
import pandas as pd
import streamlit as st

DATA_FILE = "banco_srpr.json"


def cargar_datos():
  if not os.path.exists(DATA_FILE):
    datos_iniciales = {
        "usuarios": {
            "Juan": {
                "pin": "1234",
                "oinkalias": 20,
                "creado": str(datetime.now().date()),
            }
        },
        "favores": [],
        "transacciones": [{
            "fecha": str(datetime.now().date()),
            "monto_total": 5,
            "tipo": "inicio",
        }],
    }
    guardar_datos(datos_iniciales)
    return datos_iniciales
  try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      return json.load(f)
  except Exception:
    # Si el archivo se corrompe por algún motivo, lo reiniciamos limpio
    return {
        "usuarios": {
            "Juan": {
                "pin": "1234",
                "oinkalias": 20,
                "creado": str(datetime.now().date()),
            }
        },
        "favores": [],
        "transacciones": [],
    }


def guardar_datos(datos):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=4)


# Cargar base de datos del imperio
db = cargar_datos()

st.set_page_config(
    page_title="Banco Central - SRPR", page_icon="🏛️", layout="wide"
)

st.title("🏛️ Banco Central de la SRPR")
st.markdown(
    "*Segunda República de Pamplona Románica — Sistema Económico y de"
    " Favores*"
)

# Sidebar: Gestión de Sesión / Cuentas
st.sidebar.header("🔐 Acceso Imperial")
opcion_sesion = st.sidebar.radio(
    "Selecciona una opción:", ["Iniciar Sesión", "Crear Cuenta Nueva"]
)

if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

if opcion_sesion == "Crear Cuenta Nueva":
  st.sidebar.subheader("Registro de Ciudadano")
  nuevo_nombre = st.sidebar.text_input(
      "Nombre de la cuenta / Alias"
  ).strip()  # .strip() elimina espacios accidentales
  nuevo_pin = st.sidebar.text_input(
      "PIN de seguridad", type="password"
  ).strip()

  if st.sidebar.button("Registrarse en la República"):
    if not nuevo_nombre or not nuevo_pin:
      st.sidebar.error("Rellena todos los campos, cojones.")
    elif nuevo_nombre in db["usuarios"]:
      st.sidebar.error(
          f"¡El usuario '{nuevo_nombre}' ya existe! Prueba a iniciar sesión."
      )
    else:
      db["usuarios"][nuevo_nombre] = {
          "pin": nuevo_pin,
          "oinkalias": 10,  # 10 oinkalias de inicio gratis
          "creado": str(datetime.now().date()),
      }
      guardar_datos(db)
      st.sidebar.success(
          f"¡Cuenta creada con éxito, {nuevo_nombre}! Has recibido tus 10 🐖"
          " oinkalias iniciales."
      )

elif opcion_sesion == "Iniciar Sesión":
  st.sidebar.subheader("Login de Cuenta")
  usuario_input = st.sidebar.text_input("Nombre de cuenta").strip()
  pin_input = st.sidebar.text_input("PIN", type="password").strip()

  if st.sidebar.button("Entrar"):
    if usuario_input not in db["usuarios"]:
      st.sidebar.error("Ese nombre de cuenta no existe en la República.")
    elif db["usuarios"][usuario_input]["pin"] != pin_input:
      st.sidebar.error("PIN incorrecto, espía de los enemigos.")
    else:
      st.session_state.usuario_actual = usuario_input
      st.sidebar.success(f"Bienvenido de nuevo, {usuario_input}.")
      st.rerun()

# Si hay sesión iniciada, mostrar el panel principal del banco
if st.session_state.usuario_actual:
  user = st.session_state.usuario_actual
  saldo_actual = db["usuarios"][user]["oinkalias"]

  st.sidebar.markdown("---")
  st.sidebar.write(f"👤 **Conectado como:** `{user}`")
  st.sidebar.write(f"🐖 **Saldo:** `{saldo_actual} Oinkalias`")
  if st.sidebar.button("Cerrar Sesión"):
    st.session_state.usuario_actual = None
    st.rerun()

  # Pestañas principales
  tab1, tab2, tab3 = st.tabs(
      ["🤝 Mercado de Favores", "📊 Economía & Gráficos", "⚙️ Ajustes de Cuenta"]
  )

  with tab1:
    st.header("Mercado de Favores Imperiales")

    col1, col2 = st.columns(2)

    with col1:
      st.subheader("➕ Pedir un Favor")
      with st.form("form_favor"):
        destinatario = st.selectbox(
            "¿A quién le pides el favor?",
            [u for u in db["usuarios"] if u != user],
        )
        descripcion_favor = st.text_area(
            "Descripción del favor (ej: Préstame el compás a tercera hora)"
        )
        pago_oinkalias = st.number_input(
            "Oinkalias ofrecidas como recompensa",
            min_value=1,
            max_value=int(saldo_actual) if saldo_actual > 0 else 1,
            step=1,
        )
        enviar_favor = st.form_submit_button("Enviar Solicitud de Favor")

        if enviar_favor:
          if not destinatario:
            st.error("No hay más usuarios registrados para pedir favores.")
          elif db["usuarios"][user]["oinkalias"] < pago_oinkalias:
            st.error("No tienes suficientes oinkalias, ¡estás en bancarrota!")
          else:
            db["usuarios"][user]["oinkalias"] -= pago_oinkalias

            nuevo_favor = {
                "id": len(db["favores"]) + 1,
                "solicitante": user,
                "destinatario": destinatario,
                "descripcion": descripcion_favor,
                "monto": int(pago_oinkalias),
                "estado": "Pendiente",
                "fecha": str(datetime.now().date()),
            }
            db["favores"].append(nuevo_favor)
            guardar_datos(db)
            st.success(
                "¡Favor enviado con éxito! Oinkalias retenidas en garantía."
            )
            st.rerun()

    with col2:
      st.subheader("📥 Gestión de Favores")

      mis_favores_enviados = [
          f for f in db["favores"] if f["solicitante"] == user
      ]
      mis_favores_recibidos = [
          f for f in db["favores"] if f["destinatario"] == user
      ]

      st.markdown("### Favores que tú has solicitado:")
      if not mis_favores_enviados:
        st.info("No has solicitado ningún favor.")
      for f in mis_favores_enviados:
        st.markdown(
            f"**Para:** {f['destinatario']} | **Qué:** {f['descripcion']} |"
            f" **Recompensa:** {f['monto']} 🐖 | **Estado:** `{f['estado']}`"
        )
        if f["estado"] == "Pendiente" and st.button(
            f"Cancelar Favor #{f['id']}", key=f"cancel_{f['id']}"
        ):
          db["usuarios"][user]["oinkalias"] += f["monto"]
          db["favores"] = [x for x in db["favores"] if x["id"] != f["id"]]
          guardar_datos(db)
          st.success("Favor cancelado y oinkalias devueltas.")
          st.rerun()

      st.markdown("### Favores que te han solicitado a ti:")
      if not mis_favores_recibidos:
        st.info("Nadie te ha pedido favores todavía.")
      for f in mis_favores_recibidos:
        st.markdown(
            f"**De:** {f['solicitante']} | **Qué:** {f['descripcion']} |"
            f" **Recompensa:** {f['monto']} 🐖 | **Estado:** `{f['estado']}`"
        )
        if f["estado"] == "Pendiente":
          if st.button(
              f"Marcar como Terminado (Aceptar) #{f['id']}",
              key=f"term_{f['id']}",
          ):
            db["usuarios"][user]["oinkalias"] += f["monto"]
            db["transacciones"].append({
                "fecha": str(datetime.now().date()),
                "monto_total": f["monto"],
                "tipo": "favor_completado",
            })
            for item in db["favores"]:
              if item["id"] == f["id"]:
                item["estado"] = "Completado"
            guardar_datos(db)
            st.success(
                "¡Favor completado! Las oinkalias han sido ingresadas en tu"
                " cuenta."
            )
            st.rerun()

  with tab2:
    st.header("📊 Macroeconómica de la SRPR")
    st.markdown("Flujo de riqueza diario basado en los favores realizados.")

    if db["transacciones"]:
      df_trans = pd.DataFrame(db["transacciones"])
      df_grouped = df_trans.groupby("fecha")["monto_total"].sum().reset_index()
      df_grouped.columns = ["Fecha", "Volumen de Oinkalias Movidas"]

      st.line_chart(df_grouped.set_index("Fecha"))

      total_movido = sum([t["monto_total"] for t in db["transacciones"]])
      if total_movido >= 10:
        st.success(
            "🟢 **Economía Próspera:** Los números están en verde. La República"
            " fluye con fuerza."
        )
      else:
        st.warning(
            "🔴 **Alerta Económica:** Poco movimiento de favores. La economía"
            " se estanca."
        )
    else:
      st.info("Aún no hay suficientes datos macroeconómicos registrados.")

  with tab3:
    st.header("⚙️ Ajustes de Cuenta")
    st.write(f"**Usuario:** {user}")
    st.write(f"**Fecha de alta en la SRPR:** {db['usuarios'][user]['creado']}")
    nuevo_pin_cambio = st.text_input(
        "Cambiar PIN de seguridad", type="password"
    ).strip()
    if st.button("Actualizar PIN"):
      if nuevo_pin_cambio:
        db["usuarios"][user]["pin"] = nuevo_pin_cambio
        guardar_datos(db)
        st.success("PIN actualizado correctamente.")
      else:
        st.error("Introduce un PIN válido.")

else:
  st.warning(
      "⚠️ Por favor, inicia sesión o crea una cuenta en la barra lateral"
      " izquierda para acceder al Banco Central de la SRPR."
  )
