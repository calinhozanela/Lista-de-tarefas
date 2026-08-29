import streamlit as st
import json
import os
from datetime import date

st.set_page_config(page_title="Gerenciador de Tarefas", page_icon="✅", layout="wide")

ARQUIVO_TAREFAS = "tarefas.json"
ARQUIVO_USUARIOS = "usuarios.json"

USUARIO_PADRAO = "carlos zanela"
SENHA_PADRAO = "123456"

# --- Funções auxiliares ---
def carregar_usuarios():
    if os.path.exists(ARQUIVO_USUARIOS):
        with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {USUARIO_PADRAO: SENHA_PADRAO}

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_tarefas(todas_tarefas):
    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(todas_tarefas, f, ensure_ascii=False, indent=4)

# --- Inicialização ---
if "usuarios" not in st.session_state:
    st.session_state.usuarios = carregar_usuarios()
if "todas_tarefas" not in st.session_state:
    st.session_state.todas_tarefas = carregar_tarefas()
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

# --- LOGIN ---
if st.session_state.usuario_logado is None:
    # Exibe a logo centralizada/no topo da tela de login
    if os.path.exists("logo.webp"):
        st.image("logo.webp", width=180)

    st.title("🔒 Login no Gerenciador de Tarefas")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in st.session_state.usuarios and st.session_state.usuarios[usuario] == senha:
            st.session_state.usuario_logado = usuario
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
    if st.button("Criar Conta"):
        if usuario and senha:
            if usuario in st.session_state.usuarios:
                st.error("Usuário já existe.")
            else:
                st.session_state.usuarios[usuario] = senha
                salvar_usuarios(st.session_state.usuarios)
                st.success("Conta criada com sucesso!")
    st.stop()

# --- ÁREA PRIVADA ---
user = st.session_state.usuario_logado
if user not in st.session_state.todas_tarefas:
    st.session_state.todas_tarefas[user] = []

tarefas = st.session_state.todas_tarefas[user]

# --- LOGO NA BARRA LATERAL ---
if os.path.exists("logo.webp"):
    st.sidebar.image("logo.webp", use_container_width=True)

st.sidebar.title(f"👤 Usuário: {user}")
if st.sidebar.button("🚪 Logout"):
    st.session_state.usuario_logado = None
    st.rerun()

st.title("✅ Minhas Tarefas")

# --- Adicionar tarefa ---
with st.form("nova_tarefa", clear_on_submit=True):
    texto = st.text_input("Descrição da tarefa")
    categoria = st.selectbox("Categoria", ["Trabalho", "Estudos", "Pessoal", "Outros"])
    vencimento = st.date_input("Data de vencimento", value=date.today())
    prioridade = st.selectbox("Prioridade", ["Baixa", "Normal", "Urgente"], index=1)
    adicionar = st.form_submit_button("Adicionar")
    if adicionar and texto.strip():
        nova = {
            "texto": texto,
            "categoria": categoria,
            "vencimento": str(vencimento),
            "prioridade": prioridade,
            "concluida": False
        }
        tarefas.append(nova)
        salvar_tarefas(st.session_state.todas_tarefas)
        st.success("Tarefa adicionada!")
        st.rerun()

# --- Exibir tarefas ---
if not tarefas:
    st.info("Nenhuma tarefa cadastrada.")
else:
    for i, t in enumerate(tarefas):
        cols = st.columns([0.05, 0.45, 0.25, 0.25])
        with cols[0]:
            status = st.checkbox("", value=t["concluida"], key=f"chk_{i}")
            if status != t["concluida"]:
                tarefas[i]["concluida"] = status
                salvar_tarefas(st.session_state.todas_tarefas)
                st.rerun()
        with cols[1]:
            st.write(f"**{t['texto']}**" if not t["concluida"] else f"~~{t['texto']}~~")
        with cols[2]:
            st.caption(f"📁 {t['categoria']} | ⏳ {t['prioridade']}")
        with cols[3]:
            st.caption(f"📅 {t['vencimento']}")
        if st.button("🗑️ Excluir", key=f"del_{i}"):
            tarefas.pop(i)
            salvar_tarefas(st.session_state.todas_tarefas)
            st.rerun()

# --- Lazy loading exemplo ---
with st.expander("📊 Estatísticas (carregamento sob demanda)"):
    st.write(f"Total de tarefas: {len(tarefas)}")
    concluidas = sum(1 for t in tarefas if t["concluida"])
    st.write(f"Tarefas concluídas: {concluidas}")
    # Mantido o seu st.image dentro das estatísticas
    if os.path.exists("logo.webp"):
        st.image("logo.webp", caption="Imagem otimizada em WebP", use_container_width=True)
