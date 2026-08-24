import streamlit as st
from datetime import datetime

# --- Configuração básica da página (título que aparece na aba do navegador) ---
st.set_page_config(page_title="Minha Lista de Tarefas", page_icon="📝")

# --- Título mostrado no topo da página ---
st.title("📝 Minha Lista de Tarefas")

# --- "Memória" do app ---
# O Streamlit "esquece" tudo toda vez que a página recarrega.
# Por isso usamos o st.session_state: é como uma caixinha onde guardamos
# a lista de tarefas enquanto o app está aberto.
if "tarefas" not in st.session_state:
    st.session_state.tarefas = []  # começa vazia

# --- Função para adicionar uma tarefa nova ---
def adicionar_tarefa():
    texto = st.session_state.nova_tarefa  # pega o que foi digitado no campo
    if texto.strip() != "":  # só adiciona se não estiver vazio
        data_criacao = datetime.now().strftime("%d/%m/%Y %H:%M")  # data e hora atuais, formatadas
        st.session_state.tarefas.append({"texto": texto, "feita": False, "data": data_criacao})
        st.session_state.nova_tarefa = ""  # limpa o campo depois de adicionar

# --- Campo de texto + botão de adicionar ---
st.text_input(
    "Digite uma nova tarefa:",
    key="nova_tarefa",
    on_change=adicionar_tarefa  # chama a função quando o usuário aperta Enter
)

st.divider()

# --- Mostrando a lista de tarefas na tela ---
if len(st.session_state.tarefas) == 0:
    st.info("Nenhuma tarefa ainda. Adicione uma acima! 👆")
else:
    for i, tarefa in enumerate(st.session_state.tarefas):
        # cria uma checkbox para cada tarefa; quando marcada, riscamos o texto
        col1, col2 = st.columns([3, 1])  # divide a linha em duas colunas: tarefa e data
        with col1:
            marcada = st.checkbox(tarefa["texto"], value=tarefa["feita"], key=f"tarefa_{i}")
            st.session_state.tarefas[i]["feita"] = marcada
        with col2:
            st.caption(f"🕒 {tarefa['data']}")  # mostra a data pequena, ao lado

    # --- Contador simples de progresso ---
    total = len(st.session_state.tarefas)
    feitas = sum(1 for t in st.session_state.tarefas if t["feita"])
    st.caption(f"{feitas} de {total} tarefas concluídas")
    