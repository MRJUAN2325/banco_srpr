import streamlit as st
import pandas as pd
import datetime

st.set_page_config(
    page_title="Banco SRPR (BSRPR)",
    page_icon="🏦",
    layout="wide"
)

# Initialize Session State
if "users" not in st.session_state:
    st.session_state.users = {
        "bancospr": {"password": "2325", "name": "Banco srpr (Administrador)", "role": "admin", "balance": 1000}
    }

if "transactions" not in st.session_state:
    st.session_state.transactions = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None

# Custom CSS for modern banking aesthetic
st.markdown("""
    
""", unsafe_allow_html=True)

# ----------------- LOGIN / REGISTER VIEW -----------------
if not st.session_state.logged_in:
    st.title("🏦 Banco SRPR (BSRPR)")
    st.subheader("Acceso a Banca Online - Moneda Oficial: Oincalias")
    
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Crear Cuenta Nueva"])
    
    with tab1:
        with st.form("login_form"):
            username_input = st.text_input("Usuario")
            password_input = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Entrar")
            
            if submit_login:
                if username_input in st.session_state.users and st.session_state.users[username_input]["password"] == password_input:
                    st.session_state.logged_in = True
                    st.session_state.username = username_input
                    st.success("¡Bienvenido de nuevo!")
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos.")
                    
    with tab2:
        with st.form("register_form"):
            new_user = st.text_input("Nuevo Nombre de Usuario")
            new_pass = st.text_input("Contraseña", type="password")
            new_name = st.text_input("Nombre Completo")
            submit_reg = st.form_submit_button("Registrarse")
            
            if submit_reg:
                if not new_user or not new_pass or not new_name:
                    st.warning("Por favor, rellene todos los campos.")
                elif new_user in st.session_state.users:
                    st.error("El nombre de usuario ya existe.")
                else:
                    st.session_state.users[new_user] = {
                        "password": new_pass,
                        "name": new_name,
                        "role": "client",
                        "balance": 10 # Exactamente 10 oincalias de regalo para nuevos usuarios
                    }
                    st.session_state.transactions.append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "sender": "bancospr",
                        "receiver": new_user,
                        "amount": 10,
                        "concept": "Bono de bienvenida Banco SRPR (10 oincalias)"
                    })
                    st.success("¡Cuenta creada con éxito! Se han ingresado 10 oincalias de regalo. Ya puedes iniciar sesión.")

# ----------------- DASHBOARD VIEW -----------------
else:
    user = st.session_state.username
    user_data = st.session_state.users[user]
    
    # Sidebar
    st.sidebar.title(f"Hola, {user_data['name']}")
    st.sidebar.write(f"Rol: **{user_data['role'].upper()}**")
    st.sidebar.markdown("---")
    
    menu = ["Mis Cuentas y Saldo", "Realizar Transferencia", "Historial de Movimientos"]
    if user_data["role"] == "admin":
        menu.append("Panel de Administración BSRPR")
        
    choice = st.sidebar.radio("Navegación", menu)
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()
        
    # --- VISTA: MIS CUENTAS Y SALDO ---
    if choice == "Mis Cuentas y Saldo":
        st.title("💼 Posición Global")
        st.write("Bienvenido al panel de control de **Banco SRPR (BSRPR)**.")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Saldo Disponible", value=f"{int(user_data['balance']):,d} Oincalias")
        with col2:
            st.metric(label="Cuenta Principal", value=f"BSRPR-ES99-{user.upper()}-001")
            
        st.markdown("---")
        st.subheader("Tarjetas Asociadas")
        st.info("💳 Tarjeta de Débito BSRPR Aqua Virtual Activa")

    # --- VISTA: REALIZAR TRANSFERENCIA ---
    elif choice == "Realizar Transferencia":
        st.title("💸 Nueva Transferencia")
        st.write("Envía oincalias de forma inmediata y segura.")
        
        with st.form("transfer_form"):
            recipient = st.selectbox("Cuenta Destinatario", [u for u in st.session_state.users.keys() if u != user])
            amount = st.number_input("Cantidad en Oincalias", min_value=1, max_value=int(user_data["balance"]), step=1, format="%d")
            concept = st.text_input("Concepto", "Pago / Transferencia")
            submit_transfer = st.form_submit_button("Confirmar Transferencia")
            
            if submit_transfer:
                if user_data["balance"] < amount:
                    st.error("Saldo insuficiente.")
                else:
                    st.session_state.users[user]["balance"] -= amount
                    st.session_state.users[recipient]["balance"] += amount
                    st.session_state.transactions.append({
                        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "sender": user,
                        "receiver": recipient,
                        "amount": amount,
                        "concept": concept
                    })
                    st.success(f"¡Transferencia de {amount:,d} oincalias realizada con éxito!")

    # --- VISTA: HISTORIAL DE MOVIMIENTOS ---
    elif choice == "Historial de Movimientos":
        st.title("📊 Historial de Movimientos")
        st.write("Consulta todos tus ingresos y cargos recientes.")
        
        user_txs = [tx for tx in st.session_state.transactions if tx["sender"] == user or tx["receiver"] == user]
        if not user_txs:
            st.info("No hay movimientos registrados.")
        else:
            df_txs = pd.DataFrame(user_txs)
            st.dataframe(df_txs, use_container_width=True)

    # --- VISTA: PANEL DE ADMINISTRACIÓN BSRPR ---
    elif choice == "Panel de Administración BSRPR" and user_data["role"] == "admin":
        st.title("🛡️ Panel de Control Administrador - Banco SRPR")
        st.warning("Estás accediendo a la cuenta administradora global BSRPR. Tienes privilegios de supervisión total sobre los usuarios y el historial.")
        
        tab_admin1, tab_admin2 = st.tabs(["Auditoría de Usuarios", "Historial Global de Transacciones"])
        
        with tab_admin1:
            st.subheader("Usuarios Registrados en la Plataforma")
            users_list = []
            for uname, udata in st.session_state.users.items():
                users_list.append({
                    "Usuario": uname,
                    "Nombre": udata["name"],
                    "Rol": udata["role"],
                    "Saldo (Oincalias)": f"{int(udata['balance']):,d}"
                })
            st.dataframe(pd.DataFrame(users_list), use_container_width=True)
            
        with tab_admin2:
            st.subheader("Historial Completo de Transacciones (Global)")
            if st.session_state.transactions:
                st.dataframe(pd.DataFrame(st.session_state.transactions), use_container_width=True)
            else:
                st.info("No hay transacciones globales registradas.")
