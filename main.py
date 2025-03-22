import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import atividades_app  # importa o módulo com a página de atividades

# Configuração inicial da página
st.set_page_config(
    page_title="Organizador de Estudos",
    page_icon="🎓",
    layout="wide"
)

# Inicializa o Firebase (apenas uma vez)
if not firebase_admin._apps:
    cred = credentials.Certificate("sopa.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Gerenciamento de navegação usando session_state
if 'pagina' not in st.session_state:
    st.session_state['pagina'] = 'inicio'

def mudar_pagina(p):
    st.session_state['pagina'] = p

# Sidebar personalizada com botões e emojis
st.sidebar.title("Navegação")
if st.sidebar.button("🏠 Início"):
    mudar_pagina("inicio")
if st.sidebar.button("📝 Atividades"):
    mudar_pagina("atividades")
if st.sidebar.button("🎓 Períodos"):
    mudar_pagina("periodos")

# Renderiza o conteúdo conforme a página selecionada
if st.session_state['pagina'] == "inicio":
    st.title("Oiiiii amorzinhoo")
    st.write("Eu te amo mais que tudo nesse mundo! ❤️")
elif st.session_state['pagina'] == "atividades":
    atividades_app.app(db)
elif st.session_state['pagina'] == "periodos":
    st.title("Página de Períodos - Em breve")
    st.write("Aqui você poderera gerenciar os períodos, cadastrar matérias e registrar provas.")
