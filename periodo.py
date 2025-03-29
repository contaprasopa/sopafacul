import streamlit as st
from datetime import datetime

def arredondar_personalizado(valor):
    decimal = valor % 1
    inteiro = int(valor)
    if decimal < 0.25:
        return float(inteiro)
    elif decimal < 0.75:
        return float(inteiro) + 0.5
    else:
        return float(inteiro) + 1.0


def app(db, periodo_id):
    periodo_ref = db.collection("periodo").document(periodo_id)
    materias_ref = periodo_ref.collection("materias")

    # Título e botão
    col_title, col_btn = st.columns([8, 1])
    with col_title:
        st.title(f"📘 Período {periodo_id}")
    with col_btn:
        if st.button("➕ Nova Matéria"):
            criar_materia(db, periodo_id)

    # Carrega todas as matérias em um dicionário
    materias_docs = list(materias_ref.stream())
    materias_dict = {doc.id: doc.to_dict() for doc in materias_docs}

    if not materias_dict:
        st.info("Nenhuma matéria adicionada ainda.")
    else:
        # Cabeçalhos estilo tabela
        st.markdown("---")
        header_cols = st.columns([4, 1, 1, 1])
        header_cols[0].markdown("**📚 Matérias**")
        header_cols[1].markdown("**📈 Nota**")
        header_cols[2].markdown("**✏️ Editar**")
        header_cols[3].markdown("**🗑️ Excluir**")
        st.markdown("---")

        # Loop pelas matérias
        for nome_materia, materia_data in materias_dict.items():
            provas = materia_data.get("provas", [])
            notas = materia_data.get("notas", {})
            pesos_bimestres = materia_data.get("pesos_bimestres", {"1º": 1.0, "2º": 1.0})
            total_por_bimestre = {"1º": {"nota": 0.0, "peso": 0.0}, "2º": {"nota": 0.0, "peso": 0.0}}

            for i, prova in enumerate(provas):
                nota = notas.get(str(i), 0.0)
                total_por_bimestre[prova['bimestre']]['nota'] += nota * prova['peso']
                total_por_bimestre[prova['bimestre']]['peso'] += prova['peso']

            bimestre_final = {}
            for bimestre, valores in total_por_bimestre.items():
                if valores['peso'] > 0:
                    bimestre_final[bimestre] = valores['nota'] / valores['peso']
                else:
                    bimestre_final[bimestre] = 0.0

            peso_total = pesos_bimestres["1º"] + pesos_bimestres["2º"]
            media_final = (
                bimestre_final["1º"] * pesos_bimestres["1º"] +
                bimestre_final["2º"] * pesos_bimestres["2º"]
            ) / peso_total if peso_total > 0 else 0.0

            cor = "green" if media_final >= 7 else "orange"

            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                with col1:
                    if st.button(nome_materia, key=f"abrir_{nome_materia}"):
                        st.session_state['pagina'] = 'materia_detalhe'
                        st.session_state['periodo_ativo'] = periodo_id
                        st.session_state['materia_ativa'] = nome_materia
                        st.rerun()
                with col2:
                    nota = arredondar_personalizado(media_final)
                    st.markdown(f"<span style='color:{cor}; font-weight:bold'>{nota:.2f}</span>", unsafe_allow_html=True)
                with col3:
                    if st.button("✏️", key=f"editar_{nome_materia}"):
                        editar_materia(db, periodo_id, nome_materia, materia_data)
                with col4:
                    if st.button("🗑️", key=f"excluir_{nome_materia}"):
                        materias_ref.document(nome_materia).delete()
                        st.success(f"Matéria '{nome_materia}' removida!")
                        st.rerun()


@st.dialog("➕ Nova Matéria")
def criar_materia(db, periodo_id):
    nome = st.text_input("Nome da Matéria")
    num_provas = st.number_input("Número de Provas", min_value=1, value=2, step=1)

    provas = []
    st.markdown("**Provas:**")

    for i in range(int(num_provas)):
        col_nome = st.text_input(f"Nome da Prova {i+1}", key=f"nome_prova_{i}")
        col_peso, col_bim = st.columns([1, 1])
        with col_peso:
            peso = st.number_input(f"Peso {i+1}", min_value=0.0, value=1.0, step=0.1, key=f"peso_prova_{i}")
        with col_bim:
            bimestre = st.selectbox(f"Bimestre {i+1}", ["1º", "2º"], key=f"bimestre_prova_{i}")
        provas.append({"nome": col_nome, "peso": peso, "bimestre": bimestre})


    st.markdown("**Pesos dos Bimestres:**")
    pesos_bimestres = {}
    for b in ["1º", "2º"]:
        pesos_bimestres[b] = st.number_input(f"Peso do {b} Bimestre", min_value=0.0, value=1.0, step=0.1, key=f"peso_bim_{b}")

    if st.button("Criar"):
        materia_data = {
            "nome": nome,
            "num_provas": num_provas,
            "provas": provas,
            "pesos_bimestres": pesos_bimestres,
            "notas": {},
        }

        materias_ref = db.collection("periodo").document(periodo_id).collection("materias")
        materias_ref.document(nome).set(materia_data)
        st.success("Matéria criada com sucesso!")
        st.rerun()


@st.dialog("✏️ Editar Matéria")
def editar_materia(db, periodo_id, nome_materia, materia_data):
    novo_nome = st.text_input("Nome da Matéria", value=materia_data['nome'])
    num_provas = st.number_input("Número de Provas", min_value=1, value=materia_data.get('num_provas', 1), step=1)

    st.markdown("**Provas:**")
    provas = []
    for i in range(int(num_provas)):
        provas_existentes = materia_data.get("provas", [])
        nome_default = provas_existentes[i].get("nome", f"Prova {i+1}") if i < len(provas_existentes) else f"Prova {i+1}"
        peso_default = provas_existentes[i]["peso"] if i < len(provas_existentes) else 1.0
        bimestre_default = provas_existentes[i]["bimestre"] if i < len(provas_existentes) else "1º"

        nome = st.text_input(f"Nome da Prova {i+1}", value=nome_default, key=f"editar_nome_prova_{i}")
        col_peso, col_bim = st.columns([1, 1])
        with col_peso:
            peso = st.number_input(f"Peso {i+1}", min_value=0.0, value=peso_default, step=0.1, key=f"editar_peso_prova_{i}")
        with col_bim:
            bimestre = st.selectbox(f"Bimestre {i+1}", ["1º", "2º"], index=["1º", "2º"].index(bimestre_default), key=f"editar_bimestre_prova_{i}")
        
        provas.append({"nome": nome, "peso": peso, "bimestre": bimestre})



    st.markdown("**Pesos dos Bimestres:**")
    pesos_bimestres = {}
    for b in ["1º", "2º"]:
        valor_bim = materia_data.get("pesos_bimestres", {}).get(b, 1.0)
        pesos_bimestres[b] = st.number_input(f"Peso do {b} Bimestre", min_value=0.0, value=valor_bim, step=0.1, key=f"editar_peso_bim_{b}")

    if st.button("Salvar Alterações"):
        novas_infos = {
            "nome": novo_nome,
            "num_provas": num_provas,
            "provas": provas,
            "pesos_bimestres": pesos_bimestres,
            "notas": materia_data.get("notas", {}),
        }

        materias_ref = db.collection("periodo").document(periodo_id).collection("materias")
        if novo_nome != nome_materia:
            materias_ref.document(novo_nome).set(novas_infos)
            materias_ref.document(nome_materia).delete()
        else:
            materias_ref.document(novo_nome).set(novas_infos)

        st.success("Matéria atualizada!")
        st.rerun()
