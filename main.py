import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import atividades_app
import periodos_app
import periodo
import materia

st.set_page_config(page_title="Site Da Sopinha", page_icon="🎓", layout="wide")

senha_correta = st.secrets["auth"]["senha"]

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Área Protegida")
    senha = st.text_input("Digite a senha para acessar o site:", type="password")
    if senha == senha_correta:
        st.session_state['autenticado'] = True
        st.success("Senha correta! Bem-vindo(a) 💖")
        st.rerun()
    elif senha:
        st.error("Senha incorreta. Tente novamente.")
    st.stop()

# Inicializa Firebase uma única vez
if not firebase_admin._apps:
    cred = credentials.Certificate({
        "type": st.secrets["firebase"]["type"],
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": st.secrets["firebase"]["auth_uri"],
        "token_uri": st.secrets["firebase"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["firebase"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"],
        "universe_domain": st.secrets["firebase"]["universe_domain"]
    })
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Define a página padrão
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

def mudar_pagina(p):
    st.session_state['pagina'] = p

# Sidebar de navegação
st.sidebar.title("Navegação")
if st.sidebar.button("🏠 Início"):
    mudar_pagina("inicio")
if st.sidebar.button("📝 Atividades"):
    mudar_pagina("atividades")
if st.sidebar.button("🎓 Períodos"):
    mudar_pagina("periodos")

# Lógica de renderização por página
pagina = st.session_state['pagina']

if pagina == "inicio":
    st.title("Site da mais linda desse mundo ❤️")
    st.image("nos.png", use_container_width=True)

elif pagina == "atividades":
    atividades_app.app(db)

elif pagina == "periodos":
    periodos_app.app(db)

elif pagina == "periodo_detalhe" and "periodo_ativo" in st.session_state:
    periodo.app(db, st.session_state["periodo_ativo"])

elif pagina == "materia_detalhe" and "periodo_ativo" in st.session_state and "materia_ativa" in st.session_state:
    materia.app(db, st.session_state["periodo_ativo"], st.session_state["materia_ativa"])
