import streamlit as st
from datetime import datetime, date, timedelta
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_calendar import calendar
import pytz
import random

def app(db):
    st.title("Coisas que a lindinha tem que fazer")

    atividades_ref = db.collection("atividades").order_by("data")
    docs = atividades_ref.stream()

    atividades_prova = []
    atividades_atividade = []
    atividades_revisao = []

    for doc in docs:
        atividade = doc.to_dict()
        atividade["id"] = doc.id
        if atividade["tipo"] == "prova":
            atividades_prova.append(atividade)
        elif atividade["tipo"] == "atividade":
            atividades_atividade.append(atividade)
        elif atividade["tipo"] == "revisao":
            atividades_revisao.append(atividade)

    atividades_prova.sort(key=lambda x: x["data"])
    atividades_atividade.sort(key=lambda x: x["data"])
    atividades_revisao.sort(key=lambda x: x["data"])

    @st.dialog("Nova Prova")
    def add_prova_dialog():
        data_input = st.date_input("Data", date.today())
        data_completa = datetime.combine(data_input, datetime.min.time())
        nome = st.text_input("Nome")
        valor = st.number_input("Valor", min_value=0.0, value=0.0, step=0.1)
        hora_inicio = st.time_input("Horário de Início", step=300)
        hora_fim = st.time_input("Horário de Fim", step=300)
        if st.button("Salvar"):
            try:
                db.collection("atividades").add({
                    "data": data_completa,
                    "nome": nome,
                    "tipo": "prova",
                    "valor": valor,
                    "inicio": hora_inicio.strftime("%H:%M"),
                    "fim": hora_fim.strftime("%H:%M")
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
        hora_inicio = st.time_input("Horário de Início", step=300)
        hora_fim = st.time_input("Horário de Fim", step=300)
        if st.button("Salvar"):
            try:
                db.collection("atividades").add({
                    "data": data_completa,
                    "nome": nome,
                    "tipo": "atividade",
                    "valor": valor,
                    "inicio": hora_inicio.strftime("%H:%M"),
                    "fim": hora_fim.strftime("%H:%M")
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
        hora_inicio = st.time_input("Horário de Início", step=300)
        hora_fim = st.time_input("Horário de Fim", step=300)
        if st.button("Salvar"):
            try:
                db.collection("atividades").add({
                    "data": data_completa,
                    "nome": nome,
                    "tipo": "revisao",
                    "inicio": hora_inicio.strftime("%H:%M"),
                    "fim": hora_fim.strftime("%H:%M")
                })
                st.success("Revisão adicionada com sucesso!")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao adicionar revisão: {e}")

    col_prova, col_atividade, col_revisao = st.columns(3)

    def exibir_coluna(col, lista, titulo, add_dialog_func, com_valor):
        with col:
            header_title, header_button = st.columns([6.3, 1])
            header_title.markdown(f"### {titulo}")
            if header_button.button(":material/add:", key=f"btn_{titulo}"):
                add_dialog_func()
            st.markdown("---")

            if com_valor:
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

    st.markdown("---")
    st.header("🗓️ Calendário de Atividades")

    periodo_2_ref = db.collection("periodo").document("2")
    materias_docs = list(periodo_2_ref.collection("materias").stream())
    materias_2 = [m.to_dict() | {"id": m.id} for m in materias_docs]

    eventos = []
    cor_materias = {}
    cores_disponiveis = [
        "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899",
        "#14b8a6", "#6366f1", "#f43f5e", "#22c55e"
    ]

    dias_index = {
        "segunda": 0, "terça": 1, "quarta": 2,
        "quinta": 3, "sexta": 4, "sábado": 5, "domingo": 6
    }

    horarios_por_dia = {i: [] for i in range(7)}
    hoje = datetime.now().date()
    for materia in materias_2:
        nome = materia["nome"]
        if nome not in cor_materias:
            cor_materias[nome] = cores_disponiveis[len(cor_materias) % len(cores_disponiveis)]

        horarios = materia.get("horarios", {})

        for dia, lista_horarios in horarios.items():
            dia_index = dias_index[dia]
            for h in lista_horarios:
                horarios_por_dia[dia_index].append({
                    "inicio": h["inicio"],
                    "fim": h["fim"],
                    "materia": nome,
                    "cor": cor_materias[nome]
                })
                for i in range(0, 30):
                    dia_atual = hoje + timedelta(days=i)
                    if dia_atual.weekday() == dia_index:
                        data_str = dia_atual.strftime("%Y-%m-%d")
                        inicio = f"{data_str}T{h['inicio']}:00"
                        fim = f"{data_str}T{h['fim']}:00"
                        professor = h.get("professor", "")
                        eventos.append({
                            "title": f"📚 {nome} - {professor}",
                            "start": inicio,
                            "end": fim,
                            "color": cor_materias[nome],
                            "display": "auto"
                        })

    atividades_lista = [a.to_dict() for a in db.collection("atividades").stream()]

    for atividade in atividades_lista:
        nome_atividade = atividade["nome"]
        tipo = atividade.get("tipo", "atividade")
        prefixo = ""
        if tipo == "prova":
            prefixo = "Prova: "
        elif tipo == "atividade":
            prefixo = "Atividade: "
        elif tipo == "revisao":
            prefixo = "Revisão: "

        data = atividade["data"]
        data_str = data.strftime("%Y-%m-%d")
        hora_inicio = atividade.get("inicio") or "08:00"
        hora_fim = atividade.get("fim") or "09:00"

        a_inicio = datetime.strptime(hora_inicio, "%H:%M").time()
        a_fim = datetime.strptime(hora_fim, "%H:%M").time()

        cor_atividade = "#f97316"
        dia_semana = data.weekday()
        for h in horarios_por_dia.get(dia_semana, []):
            h_inicio = datetime.strptime(h["inicio"], "%H:%M").time()
            h_fim = datetime.strptime(h["fim"], "%H:%M").time()
            if h_inicio <= a_inicio <= h_fim or h_inicio <= a_fim <= h_fim:
                cor_atividade = h["cor"]
                break

        eventos.append({
            "title": f"➡️ {prefixo}{nome_atividade}",
            "start": f"{data_str}T{hora_inicio}:00",
            "end": f"{data_str}T{hora_fim}:00",
            "color": cor_atividade,
            "display": "auto"
        })

    calendar_options = {
        "initialView": "timeGridWeek",
        "editable": False,
        "selectable": False,
        "locale": "pt-br",
        "allDaySlot": False,
        "slotMinTime": "06:00:00",
        "slotMaxTime": "18:30:00",
        "eventDisplay": "block",
        "eventTimeFormat": {
            "hour": "2-digit",
            "minute": "2-digit",
            "hour12": False
        },
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "timeGridWeek,timeGridDay"
        },
        "slotLabelFormat": {
            "hour": "2-digit",
            "minute": "2-digit",
            "hour12": False
        },
        "height": "auto",
        "eventMaxLines": 5,
        "dayMaxEventRows": True
    }

    calendar(events=eventos, options=calendar_options)
