import streamlit as st
from streamlit_quill import st_quill
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from xhtml2pdf import pisa
import io

def app(db):
    col_1, col_2 = st.columns([1, .1])
    with col_1:
        st.title("📝 Resumos")
    with col_2:
        st.markdown("######")
        if st.button("➕ Novo Resumo"):
            st.session_state["abrir_criador"] = True
    st.markdown("---")

    # Cache de períodos e matérias
    periodos_ref = db.collection("periodo")

    if "periodos_docs" not in st.session_state:
        st.session_state["periodos_docs"] = list(periodos_ref.stream())

    periodos_docs = st.session_state["periodos_docs"]

    # Garante que materias_dict está presente e sincronizado
    if "materias_dict" not in st.session_state:
        materias_dict = {}
        for doc in periodos_docs:
            materias_ref = periodos_ref.document(doc.id).collection("materias")
            materias_dict[doc.id] = [m.id for m in materias_ref.stream()]
        st.session_state["materias_dict"] = materias_dict

    materias_dict = st.session_state["materias_dict"]

    periodos_options = [doc.id for doc in periodos_docs]

    # Filtros
    with st.expander("🔍 Filtros", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_nome = st.text_input("Nome do Resumo", key="filtro_nome")
        with col2:
            filtro_periodo = st.selectbox("Período", ["Todos"] + periodos_options, key="filtro_periodo")
        with col3:
            if filtro_periodo != "Todos":
                filtro_materia = st.selectbox("Matéria", ["Todas"] + materias_dict[filtro_periodo], key="filtro_materia")
            else:
                filtro_materia = "Todas"

    # Consulta otimizada de resumos
    resumos_ref = db.collection("resumos")
    query = resumos_ref

    if filtro_periodo != "Todos":
        query = query.where("periodo", "==", filtro_periodo)
    if filtro_materia != "Todas":
        query = query.where("materia", "==", filtro_materia)

    resumos_docs = list(query.stream())
    resumos = [doc.to_dict() | {"id": doc.id} for doc in resumos_docs]

    if filtro_nome:
        resumos = [r for r in resumos if filtro_nome.lower() in r["nome"].lower()]

    st.markdown("---")
    st.subheader("📚 Lista de Resumos")

    if not resumos:
        st.info("Nenhum resumo encontrado com os filtros aplicados.")
    else:
        for resumo in resumos:
            with st.container():
                col1, col2, col3, col4 = st.columns([5, .5, .39, .2])
                with col1:
                    st.markdown(f"**{resumo['nome']}**")
                    st.markdown(f"Período: `{resumo['periodo']}` | Matéria: `{resumo['materia']}`")
                with col2:
                    if st.button("👁️ Visualizar", key=f"ver_{resumo['id']}"):
                        st.session_state["pagina"] = "ver_resumo"
                        st.session_state["resumo_id"] = resumo["id"]
                        st.rerun()
                with col3:
                    if st.button("✏️ Editar", key=f"edit_{resumo['id']}"):
                        st.session_state["pagina"] = "editar_resumo"
                        st.session_state["resumo_id"] = resumo["id"]
                        st.rerun()
                with col4:
                    if st.button("🗑️", key=f"del_{resumo['id']}"):
                        st.session_state["resumo_a_excluir"] = resumo["id"]
                        st.session_state["abrir_confirmacao"] = True

    if st.session_state.get("abrir_confirmacao"):
        confirmar_exclusao(db)

    if st.session_state.get("abrir_criador"):
        criar_resumo(db)

@st.dialog("❌ Confirmar Exclusão")
def confirmar_exclusao(db):
    st.warning("Tem certeza que deseja excluir este resumo?")
    if st.button("Excluir", type="primary"):
        db.collection("resumos").document(st.session_state["resumo_a_excluir"]).delete()
        del st.session_state["abrir_confirmacao"]
        del st.session_state["resumo_a_excluir"]
        st.rerun()

@st.dialog("➕ Criar Novo Resumo")
def criar_resumo(db):
    periodos_ref = db.collection("periodo")
    periodos_docs = list(periodos_ref.stream())
    periodos_options = [doc.id for doc in periodos_docs]

    nome = st.text_input("Nome do Resumo", key="novo_resumo_nome")
    periodo = st.selectbox("Período", periodos_options, key="novo_resumo_periodo")

    materias_ref = periodos_ref.document(periodo).collection("materias")
    materias_options = [m.id for m in materias_ref.stream()]
    materia = st.selectbox("Matéria", materias_options, key="novo_resumo_materia")

    if st.button("Criar", key="botao_criar_resumo"):
        if not nome.strip():
            st.error("O nome do resumo é obrigatório.")
            return

        resumo_ref = db.collection("resumos").document()
        resumo_ref.set({
            "nome": nome,
            "periodo": periodo,
            "materia": materia,
            "conteudo": "",
            "criado_em": datetime.now().isoformat(),
        })
        st.success("Resumo criado com sucesso! ✅")
        st.session_state["pagina"] = "editar_resumo"
        st.session_state["resumo_id"] = resumo_ref.id
        st.session_state["abrir_criador"] = False
        st.rerun()

def editar_resumo(db, resumo_id):
    resumo_ref = db.collection("resumos").document(resumo_id)
    doc = resumo_ref.get()
    if not doc.exists:
        st.error("Resumo não encontrado.")
        return

    resumo = doc.to_dict()

    st.markdown("""
        <style>
        .main .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"📝 Editando: {resumo['nome']}")

    conteudo = st_quill(value=resumo.get("conteudo", ""), html=True, key="quill_editor")

    col1, col2 = st.columns([0.1, 1])
    with col1:
        if st.button("💾 Salvar Resumo"):
            if conteudo and conteudo.strip():
                resumo_ref.update({"conteudo": conteudo})
                st.success("Resumo salvo com sucesso! ✅")
            else:
                st.warning("O conteúdo está vazio.")

    with col2:
        if st.button("👁️ Visualizar"):
            if conteudo and conteudo.strip():
                resumo_ref.update({"conteudo": conteudo})
            st.session_state["pagina"] = "ver_resumo"
            st.session_state["resumo_id"] = resumo_id
            st.rerun()

def gerar_pdf(titulo, html_conteudo):
    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
             body {{
                 font-family: Arial, sans-serif;
                 font-size: 18px;  /* Aumente esse valor para uma fonte maior */
                 line-height: 1.3;
                 padding: 2px;
             }}
             h1 {{
                 font-size: 26px;
             }}
         </style>
    </head>
    <body>
        <h1>{titulo}</h1>
        {html_conteudo}
    </body>
    </html>
    """
    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=result)
    if not pisa_status.err:
        return result.getvalue()
    return None

def ver_resumo(db, resumo_id):
    resumo_ref = db.collection("resumos").document(resumo_id)
    doc = resumo_ref.get()
    if not doc.exists:
        st.error("Resumo não encontrado.")
        return

    resumo = doc.to_dict()
    conteudo_html = resumo.get("conteudo", "<p>(Sem conteúdo ainda.)</p>")

    col1, col2, col3 = st.columns([1, 0.1, 0.15])
    with col1:
        st.title(f"📖 {resumo['nome']}")
        st.markdown(f"**Período:** {resumo['periodo']} | **Matéria:** {resumo['materia']}")

    with col2:
        st.markdown("######")
        if st.button("✏️ Editar"):
            st.session_state["pagina"] = "editar_resumo"
            st.session_state["resumo_id"] = resumo_id
            st.rerun()

    with col3:
        st.markdown("######")
        if st.button("📄 Exportar para PDF"):
            pdf_bytes = gerar_pdf(resumo["nome"], conteudo_html)
            if pdf_bytes:
                st.download_button(
                    label="📥 Baixar PDF",
                    data=pdf_bytes,
                    file_name=f"{resumo['nome']}.pdf",
                    mime="application/pdf"
                )
            else:
                st.error("Erro ao gerar PDF.")

    st.markdown("---")
    st.markdown(conteudo_html, unsafe_allow_html=True)
    st.markdown("---")
