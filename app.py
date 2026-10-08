import os
from datetime import date
import pandas as pd
import streamlit as st

DB_FILE = "agendamentos.csv"


def carregar_dados():
  if os.path.exists(DB_FILE):
    return pd.read_csv(DB_FILE)
  else:
    return pd.DataFrame(
        columns=[
            "Nome",
            "Setor",
            "Data",
            "Turno",
            "Datashow",
            "Motivo",
        ]
    )


def salvar_dados(df):
  df.to_csv(DB_FILE, index=False)


st.set_page_config(
    page_title="Agendamento da Sala de Reunião - Seme", layout="centered"
)

st.title("📅 Agendamento da Sala de Reunião")
st.markdown("Secretaria Municipal de Educação")

df_agendamentos = carregar_dados()

aba1, aba2 = st.tabs(["Novo Agendamento", "Painel do Secretário (Relatórios)"])

with aba1:
  st.subheader("Faça o seu agendamento")

  with st.form("form_agendamento"):
    nome = st.text_input("Seu Nome Completo")
    setor = st.text_input("Seu Setor / Departamento")
    data_reuniao = st.date_input(
        "Data da Reunião", min_value=date.today()
    )
    turno = st.selectbox(
        "Turno", ["Manhã (08h às 12h)", "Tarde (13h às 17h)", "Dia Todo"]
    )
    datashow = st.selectbox(
        "Vai precisar de Datashow?", ["Não", "Sim"]
    )
    motivo = st.text_area("Motivo / Assunto da Reunião")

    enviar = st.form_submit_button("Confirmar Agendamento")

    if enviar:
      if not nome or not setor or not motivo:
        st.warning("Por favor, preencha todos os campos!")
      else:
        data_str = data_reuniao.strftime("%Y-%m-%d")

        conflito = False
        if not df_agendamentos.empty:
          mesma_data = df_agendamentos[df_agendamentos["Data"] == data_str]
          if not mesma_data.empty:
            if (
                turno == "Dia Todo"
                or "Dia Todo" in mesma_data["Turno"].values
                or turno in mesma_data["Turno"].values
            ):
              conflito = True

        if conflito:
          st.error(
              "❌ Esta data/turno já está ocupada! Escolha outro dia ou"
              " horário."
          )
        else:
          novo_registro = pd.DataFrame(
              [{
                  "Nome": nome,
                  "Setor": setor,
                  "Data": data_str,
                  "Turno": turno,
                  "Datashow": datashow,
                  "Motivo": motivo,
              }]
          )
          df_agendamentos = pd.concat(
              [df_agendamentos, novo_registro], ignore_index=True
          )
          salvar_dados(df_agendamentos)

          st.success("✅ Sala agendada com sucesso!")

          # Mensagem específica caso tenha selecionado Datashow
          if datashow == "Sim":
            st.warning(
                "⚠️ **Atenção:** Você selecionou que precisará de"
                " **Datashow**. Por favor, entre em contato com o **Núcleo de"
                " Tecnologias Educacionais** para solicitar e garantir a"
                " reserva do equipamento!"
            )

  st.divider()
  st.subheader("Dias já reservados:")
  if not df_agendamentos.empty:
    st.dataframe(
        df_agendamentos[["Data", "Turno", "Setor", "Datashow"]],
        use_container_width=True,
    )
  else:
    st.info("Nenhum agendamento realizado até o momento.")

with aba2:
  st.subheader("🔒 Área Restrita - Painel do Secretário")

  SENHA_MESTRE = "semed01"
  senha_digitada = st.text_input(
      "Digite a senha de acesso ao painel:", type="password"
  )

  if senha_digitada == SENHA_MESTRE:
    st.success("Acesso autorizado!")

    if df_agendamentos.empty:
      st.info("Ainda não há dados para gerar relatórios.")
    else:
      st.markdown("### 🏆 Pessoas que mais utilizam a sala")
      ranking_pessoas = df_agendamentos["Nome"].value_counts().reset_index()
      ranking_pessoas.columns = ["Nome", "Total de Agendamentos"]
      st.dataframe(ranking_pessoas, use_container_width=True)

      st.markdown("### 🏢 Agendamentos por Setor")
      ranking_setor = df_agendamentos["Setor"].value_counts().reset_index()
      ranking_setor.columns = ["Setor", "Total"]
      st.bar_chart(ranking_setor.set_index("Setor"))

      st.markdown("### 📋 Histórico Completo de Reservas")
      st.dataframe(df_agendamentos, use_container_width=True)

      csv = df_agendamentos.to_csv(index=False).encode("utf-8")
      st.download_button(
          label="Baixar Relatório em CSV (Excel)",
          data=csv,
          file_name="relatorio_sala_reuniao.csv",
          mime="text/csv",
      )
  elif senha_digitada != "":
    st.error("❌ Senha incorreta! Apenas o secretário possui acesso.")
  else:
    st.info("Por favor, digite a senha para visualizar os relatórios.")
