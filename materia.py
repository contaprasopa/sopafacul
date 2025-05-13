import streamlit as st

def app(db, periodo_id, materia_nome):
    st.title(f"📖 {materia_nome} — Notas")
    st.markdown("---")

    doc_ref = db.collection("periodo").document(periodo_id).collection("materias").document(materia_nome)
    doc = doc_ref.get()
    if not doc.exists:
        st.error("Matéria não encontrada.")
        return

    data = doc.to_dict()
    provas = data.get("provas", [])
    notas = data.get("notas", {})
    pesos_bimestres = data.get("pesos_bimestres", {"1º": 1.0, "2º": 1.0})

    # Select box para escolher o bimestre para edição
    bimestre_selecionado = st.selectbox("Escolha o bimestre para editar as notas", ["1º", "2º"])
    st.markdown("---")

    total_por_bimestre = {"1º": {"nota": 0.0, "peso": 0.0}, "2º": {"nota": 0.0, "peso": 0.0}}

    for i, prova in enumerate(provas):
        nota_atual = notas.get(str(i), 0.0)
        key_nota = f"{periodo_id}_{materia_nome}_nota_input_{i}"
    
        if key_nota not in st.session_state:
            st.session_state[key_nota] = nota_atual
    
        nota_simulada = st.session_state.get(key_nota, nota_atual)
    
        total_por_bimestre[prova['bimestre']]['nota'] += nota_simulada * prova['peso']
        total_por_bimestre[prova['bimestre']]['peso'] += prova['peso']
    
        if prova['bimestre'] != bimestre_selecionado:
            continue
    
        col1, col2, col3 = st.columns([4, 2, 2])
        with col1:
            nome_prova = prova.get("nome", f"Prova {i+1}")
            st.markdown(f"**{nome_prova}**")
            st.markdown(f"Bimestre: `{prova['bimestre']}` | Peso: `{prova['peso']}`")
    
        with col2:
            st.number_input(
                f"Nota {i+1}", min_value=0.0, max_value=10.0,
                value=nota_simulada, step=0.1, key=key_nota
            )
    
        with col3:
            st.markdown("<div style='margin-top: 28px;'>", unsafe_allow_html=True)
            if st.button("Salvar", key=f"salvar_nota_{i}"):
                notas[str(i)] = st.session_state[key_nota]
                doc_ref.update({"notas": notas})
                st.success(f"Nota da Prova {i+1} salva!")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


    st.markdown("---")

    # Calcula médias dos bimestres
    bimestre_final = {}
    for bimestre, valores in total_por_bimestre.items():
        if valores['peso'] > 0:
            bimestre_final[bimestre] = valores['nota'] / valores['peso']
        else:
            bimestre_final[bimestre] = 0.0

    media_final = (
        bimestre_final["1º"] * pesos_bimestres["1º"] +
        bimestre_final["2º"] * pesos_bimestres["2º"]
    ) / (pesos_bimestres["1º"] + pesos_bimestres["2º"])

    # Mostra as médias finais
    st.subheader("📊 Médias")
    st.write(f"1º Bimestre: **{bimestre_final['1º']:.2f}**")
    st.write(f"2º Bimestre: **{bimestre_final['2º']:.2f}**")
    st.markdown(f"### Média Final na Disciplina: **{media_final:.2f}**")
    st.markdown("---")
