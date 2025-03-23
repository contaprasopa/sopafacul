import streamlit as st
from datetime import datetime, date
import firebase_admin
from firebase_admin import credentials, firestore

def app():
    st.title("Coisas que a lindinha tem que fazer")
    cred = credentials.Certificate('sopa.json')
    firebase_admin.initialize_app(cred)
    db = firestore.Client()

    # --- Recupera e organiza as atividades do Firestore ---
    atividades_ref = db.collection("atividades").order_by("data")
    docs = atividades_ref.stream()

    atividades_prova = []
    atividades_atividade = []
    atividades_revisao = []

    for doc in docs:
        atividade = doc.to_dict()
        atividade["id"] = doc.id  # Guarda o ID para exclusão
        if atividade["tipo"] == "prova":
            atividades_prova.append(atividade)
        elif atividade["tipo"] == "atividade":
            atividades_atividade.append(atividade)
        elif atividade["tipo"] == "revisao":
            atividades_revisao.append(atividade)

    atividades_prova.sort(key=lambda x: x["data"])
    atividades_atividade.sort(key=lambda x: x["data"])
    atividades_revisao.sort(key=lambda x: x["data"])

    # --- Define as funções de diálogo para adicionar novas atividades ---
    @st.dialog("Nova Prova")
    def add_prova_dialog():
        data_input = st.date_input("Data", date.today())
        data_completa = datetime.combine(data_input, datetime.min.time())
        nome = st.text_input("Nome")
        valor = st.number_input("Valor", min_value=0.0, value=0.0, step=0.1)
        if st.button("Salvar"):
            try:
                db.collection("atividades").add({
                    "data": data_completa,
                    "nome": nome,
                    "tipo": "prova",
                    "valor": valor
                })
                st.success("Prova adicionada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar prova: {e}")

    @st.dialog("Nova Atividade")
    def add_atividade_dialog():
        data_input = st.date_input("Data", date.today())
        data_completa = datetime.combine(data_input, datetime.min.time())
        nome = st.text_input("Nome")
        valor = st.number_input("Valor", min_value=0.0, value=0.0, step=0.1)
        if st.button("Salvar"):
            try:
                db.collection("atividades").add({
                    "data": data_completa,
                    "nome": nome,
                    "tipo": "atividade",
                    "valor": valor
                })
                st.success("Atividade adicionada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar atividade: {e}")

    @st.dialog("Nova Revisão")
    def add_revisao_dialog():
        data_input = st.date_input("Data", date.today())
        data_completa = datetime.combine(data_input, datetime.min.time())
        nome = st.text_input("Nome")
        if st.button("Salvar"):
            try:
                db.collection("atividades").add({
                    "data": data_completa,
                    "nome": nome,
                    "tipo": "revisao"
                })
                st.success("Revisão adicionada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar revisão: {e}")

    # --- Exibe as atividades em três colunas com o botão de adição (símbolo "+") ---
    col_prova, col_atividade, col_revisao = st.columns(3)

    def exibir_coluna(col, lista, titulo, add_dialog_func, com_valor):
        with col:
            # Cabeçalho com título e botão de adicionar ("+")
            header_title, header_button = st.columns([6.3, 1])
            header_title.markdown(f"### {titulo}")
            if header_button.button(":material/add:", key=f"btn_{titulo}"):
                add_dialog_func()
            st.markdown("---")

            if com_valor:
                # Para provas e atividades: exibe colunas para Data, Valor e Nome
                col_date, col_valor, col_nome, col_action = st.columns([2.4, 1.4, 5.5, 1.6])
                col_date.markdown("**Data**")
                col_valor.markdown("**Valor**")
                col_nome.markdown("**Nome**")
                for atividade in lista:
                    row_date, row_valor, row_nome, row_delete = st.columns([2.4, 1.4, 5.5, 1.6])
                    data_formatada = atividade["data"].strftime("%d/%m/%Y")
                    row_date.write(data_formatada)
                    row_valor.write(atividade.get("valor", ""))
                    row_nome.write(atividade["nome"])
                    if row_delete.button(":material/delete:", key=atividade["id"]):
                        try:
                            db.collection("atividades").document(atividade["id"]).delete()
                            st.success("Atividade removida!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao remover atividade: {e}")
            else:
                # Para revisões: exibe apenas Data e Nome
                col_date, col_nome, col_action = st.columns([2.4, 6.8, 1.6])
                col_date.markdown("**Data**")
                col_nome.markdown("**Nome**")
                for atividade in lista:
                    row_date, row_nome, row_delete = st.columns([2.4, 6.8, 1.6])
                    data_formatada = atividade["data"].strftime("%d/%m/%Y")
                    row_date.write(data_formatada)
                    row_nome.write(atividade["nome"])
                    if row_delete.button(":material/delete:", key=atividade["id"]):
                        try:
                            db.collection("atividades").document(atividade["id"]).delete()
                            st.success("Atividade removida!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao remover atividade: {e}")

    exibir_coluna(col_prova, atividades_prova, "Provas", add_prova_dialog, True)
    exibir_coluna(col_atividade, atividades_atividade, "Atividades", add_atividade_dialog, True)
    exibir_coluna(col_revisao, atividades_revisao, "Revisões", add_revisao_dialog, False)
