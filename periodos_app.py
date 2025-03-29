import streamlit as st
from datetime import datetime

def app(db):
    st.markdown("## 🎓 Selecione um Período")

    periodos_ref = db.collection("periodo")
    periodos_docs = list(periodos_ref.stream())

    # Ordena numericamente pelo ID do período
    try:
        periodos_docs.sort(key=lambda x: int(x.id))
    except ValueError:
        st.error("Os IDs dos períodos devem ser números para ordenar corretamente.")
        return

    if not periodos_docs:
        st.info("Nenhum período encontrado. Que tal adicionar um no Firebase?")
        return

    colunas_por_linha = 6

    for linha in range(0, len(periodos_docs), colunas_por_linha):
        cols = st.columns(colunas_por_linha)
        for i in range(colunas_por_linha):
            index = linha + i
            if index < len(periodos_docs):
                periodo_doc = periodos_docs[index]
                with cols[i]:
                    if st.button(f"📘 Período {periodo_doc.id}", key=f"periodo_{index}"):
                        st.session_state["pagina"] = "periodo_detalhe"
                        st.session_state["periodo_ativo"] = periodo_doc.id
                        st.rerun()
