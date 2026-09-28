import json
import os
from datetime import datetime
import streamlit as st

DATA_FILE = "banco_srpr.json"


def cargar_datos():
  # Estructura base obligatoria con el Banco Central garantizado
  datos_por_defecto = {
      "usuarios": {
          "banco central de la srpr": {
              "pin": "2325",
              "oinkalias": 1000,
              "creado": str(datetime.now().date()),
          }
      },
      "favores": [],
      "transacciones": [{
          "fecha": str(datetime.now().date()),
          "descripcion": (
              "Fundación del Banco Central de la SRPR con fondos imperiales"
          ),
          "monto": 1000,
      }],
  }

  if not os.path.exists(DATA_FILE):
    guardar_datos(datos_por_defecto)
    return datos_por_defecto

  try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
      # Asegurar formato base por si faltaban claves
      if "usuarios" not in data:
        data["usuarios"] = {}
      if "favores" not in data:
        data["favores"] = []
      if "transacciones" not in data:
        data["transacciones"] = []

      # Forzar que la cuenta del Banco Central exista siempre y tenga el PIN 2325
      data["usuarios"]["banco central de la srpr"] = {
          "pin": "2325",
          "oinkalias": data["usuarios"]
          .get("banco central de la srpr", {})
          .get("oinkalias", 1000),
          "creado": data["usuarios"]
          .get("banco central de la srpr", {})
          .get("creado", str(datetime.now().date())),
      }
      guardar_datos(data)
      return data
  except Exception:
    guardar_datos(datos_por_defecto)
    return datos_por_defecto


def guardar_datos(datos):
  with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(datos, f, ensure_ascii=False, indent=4)


db = cargar_datos()

st.set_page_config(
    page_title="Banco Central - SRPR", page_icon="🏛️", layout="wide"
)

if "usuario_actual" not in st.session_state:
  st.session_state.usuario_actual = None

# ==========================================
# PANTALLA DE ACCESO (SI NO HAY SESIÓN)
# ==========================================
if not st.session_state.usuario_actual:
  st.title("🏛️ Banco Central de la SRPR")
  st.markdown(
      "*Segunda República de Pamplona Románica — Identifícate, ciudadano.*"
  )
  st.markdown("---")

  col_acc1, col_acc2 = st.columns(2)

  with col_acc1:
    st.subheader("🔐 Iniciar Sesión")
    with st.form("form_login"):
      usuario_input = (
          st.text_input("Nombre de cuenta (minúsculas)")
          .strip()
          .lower()
      )
      pin_input = st.text_input("PIN de seguridad", type="password").strip()
      btn_login = st.form_submit_button("Entrar al Imperio")

      if btn_login:
        if not usuario_input or not pin_input:
          st.error("Por favor, rellena todos los campos.")
        elif usuario_input not in db["usuarios"]:
          st.error(
              f"La cuenta '{usuario_input}' no existe en la República."
              " ¡Asegúrate de escribirla en minúsculas!"
          )
        elif db["usuarios"][usuario_input]["pin"] != pin_input:
          st.error("PIN incorrecto.")
        else:
          st.session_state.usuario_actual = usuario_input
          st.rerun()

  with col_acc2:
    st.subheader("📝 Crear Cuenta Nueva")
    with st.form("form_registro"):
      nuevo_nombre = (
          st.text_input("Nuevo Alias (minúsculas)").strip().lower()
      )
      nuevo_pin = st.text_input("Nuevo PIN", type="password").strip()
      btn_registro = st.form_submit_button("Registrarse (+10 🐖 gratis)")

      if btn_registro:
        if not nuevo_nombre or not nuevo_pin:
          st.error("Rellena todos los campos.")
        elif nuevo_nombre in db["usuarios"]:
          st.error(
              f"El usuario '{nuevo_nombre}' ya existe. Prueba a iniciar"
              " sesión."
          )
        else:
          db["usuarios"][nuevo_nombre] = {
              "pin": nuevo_pin,
              "oinkalias": 10,
              "creado": str(datetime.now().date()),
          }
          guardar_datos(db)
          st.success(
              "¡Cuenta creada con éxito! Ya puedes iniciar sesión en el panel"
              " de la izquierda."
          )

# ==========================================
# PANEL PRINCIPAL (CON SESIÓN INICIADA)
# ==========================================
else:
  user = st.session_state.usuario_actual
  saldo_actual = db["usuarios"][user]["oinkalias"]
  es_admin = user == "banco central de la srpr"

  # Cabecera de Estado Superior
  col_head1, col_head2, col_head3 = st.columns([3, 1, 1])
  with col_head1:
    st.title("🏛️ Banco Central de la SRPR")
    if es_admin:
      st.markdown(
          "🛡️ *Modo Administrador Imperial / Tesorería del Estado activo.*"
      )
  with col_head2:
    st.markdown(f"👤 **{user}**")
    st.markdown(f"🐖 **{saldo_actual} Oinkalias**")
  with col_head3:
    if st.button("Cerrar Sesión"):
      st.session_state.usuario_actual = None
      st.rerun()

  st.markdown("---")

  # Pestañas
  if es_admin:
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤝 Mercado de Favores",
        "🛡️ Panel de Administrador",
        "📜 Historial",
        "⚙️ Ajustes de Cuenta",
    ])
  else:
    tab1, tab2, tab3 = st.tabs(
        ["🤝 Mercado de Favores", "📜 Historial", "⚙️ Ajustes de Cuenta"]
    )

  # --- PESTAÑA 1: MERCADO DE FAVORES ---
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
            "Descripción del favor (ej: Préstame el compás)"
        )
        pago_oinkalias = st.number_input(
            "Oinkalias ofrecidas",
            min_value=1,
            max_value=int(saldo_actual) if saldo_actual > 0 else 1,
            step=1,
        )
        enviar_favor = st.form_submit_button("Enviar Solicitud")

        if enviar_favor:
          if not destinatario:
            st.error("No hay más usuarios registrados para asignar favores.")
          elif db["usuarios"][user]["oinkalias"] < pago_oinkalias:
            st.error("No tienes suficientes oinkalias.")
          else:
            db["usuarios"][user]["oinkalias"] -= int(pago_oinkalias)
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
            st.success("¡Favor enviado! Oinkalias retenidas en garantía.")
            st.rerun()

    with col2:
      st.subheader("📥 Gestión de Favores")
      mis_favores_enviados = [
          f for f in db["favores"] if f["solicitante"] == user
      ]
      mis_favores_recibidos = [
          f for f in db["favores"] if f["destinatario"] == user
      ]

      st.markdown("### Tus solicitudes enviadas:")
      if not mis_favores_enviados:
        st.info("Ninguna solicitud activa.")
      for f in mis_favores_enviados:
        st.markdown(
            f"**Para:** {f['destinatario']} | **Qué:** {f['descripcion']} |"
            f" **{f['monto']} 🐖** | Estado: `{f['estado']}`"
        )
        if f["estado"] == "Pendiente" and st.button(
            f"Cancelar #{f['id']}", key=f"cancel_{f['id']}"
        ):
          db["usuarios"][user]["oinkalias"] += f["monto"]
          db["favores"] = [x for x in db["favores"] if x["id"] != f["id"]]
          guardar_datos(db)
          st.success("Cancelado y oinkalias devueltas.")
          st.rerun()

      st.markdown("### Favores que te han pedido:")
      if not mis_favores_recibidos:
        st.info("Nadie te ha pedido nada.")
      for f in mis_favores_recibidos:
        st.markdown(
            f"**De:** {f['solicitante']} | **Qué:** {f['descripcion']} |"
            f" **{f['monto']} 🐖** | Estado: `{f['estado']}`"
        )
        if f["estado"] == "Pendiente":
          if st.button(
              f"Marcar Terminado (Cobrar) #{f['id']}", key=f"term_{f['id']}"
          ):
            db["usuarios"][user]["oinkalias"] += f["monto"]
            db["transacciones"].append({
                "fecha": str(datetime.now().date()),
                "descripcion": (
                    f"Favor completado: '{f['descripcion']}' (De"
                    f" {f['solicitante']} a {f['destinatario']})"
                ),
                "monto": f["monto"],
            })
            for item in db["favores"]:
              if item["id"] == f["id"]:
                item["estado"] = "Completado"
            guardar_datos(db)
            st.success("¡Completado! Oinkalias cobradas con éxito.")
            st.rerun()

  # --- PESTAÑA DE ADMINISTRADOR ---
  if es_admin:
    with tab2:
      st.header("🛡️ Panel de Administrador Imperial")
      st.markdown(
          "Supervisión global de todos los favores y transacciones del"
          " territorio de la SRPR."
      )

      if db["favores"]:
        st.markdown("### Listado Completo de Favores en Curso y Finalizados:")
        for f in db["favores"]:
          color_estado = "🟢" if f["estado"] == "Completado" else "🟡"
          st.markdown(
              f"{color_estado} **ID #{f['id']}** | **De:** `{f['solicitante']}`"
              f" ➔ **Para:** `{f['destinatario']}` | **Favor:**"
              f" *{f['descripcion']}* | **Recompensa:** `{f['monto']} 🐖` |"
              f" **Estado:** `{f['estado']}`"
          )
      else:
        st.info(
            "No hay ningún favor registrado en los archivos de la República."
        )

      st.markdown("---")
      st.subheader("👥 Ciudadanos Registrados en la SRPR")
      for ciudadano, info in db["usuarios"].items():
        st.markdown(
            f"- 👤 **{ciudadano}** | Saldo: `{info['oinkalias']} 🐖` | Miembro"
            f" desde: {info['creado']}"
        )

  # --- PESTAÑA DE HISTORIAL ---
  target_tab_historial = tab3 if es_admin else tab2
  with target_tab_historial:
    st.header("📜 Historial de Transacciones")
    st.markdown("Registro oficial de movimientos y favores de la República.")

    if db["transacciones"]:
      for t in reversed(db["transacciones"]):
        fecha_t = t.get("fecha", "Fecha desconocida")
        desc_t = t.get("descripcion", "Movimiento sin descripción")
        monto_t = t.get("monto", 0)
        st.markdown(f"📅 **{fecha_t}** — {desc_t} `(+{monto_t} 🐖)`")
    else:
      st.info("Aún no hay transacciones registradas en el imperio.")

  # --- PESTAÑA DE AJUSTES ---
  target_tab_ajustes = tab4 if es_admin else tab3
  with target_tab_ajustes:
    st.header("⚙️ Ajustes de Cuenta")
    st.write(f"**Usuario:** {user}")
    st.write(f"**Fecha de alta:** {db['usuarios'][user]['creado']}")
    nuevo_pin_cambio = st.text_input(
        "Nuevo PIN de seguridad", type="password"
    ).strip()
    if st.button("Actualizar PIN"):
      if nuevo_pin_cambio:
        db["usuarios"][user]["pin"] = nuevo_pin_cambio
        guardar_datos(db)
        st.success("PIN actualizado correctamente.")
      else:
        st.error("Introduce un PIN válido.")
