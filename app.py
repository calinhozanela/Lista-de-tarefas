import streamlit as st
import json
import os
from datetime import datetime, date

# 1. Configuração da Página
st.set_page_config(
    page_title="Gerenciador de Tarefas Privado", 
    page_icon="🔒", 
    layout="wide"
)

ARQUIVO_TAREFAS = "tarefas.json"
ARQUIVO_USUARIOS = "usuarios.json"

# Credenciais Fixas (Sua garantia de nunca perder o acesso)
USUARIO_PADRAO = "carlos zanela"
SENHA_PADRAO = "123456"  # Troque pela senha que preferir antes de colar

# 2. Funções para Gerenciar Usuários
def carregar_usuarios():
    usuarios = {}
    if os.path.exists(ARQUIVO_USUARIOS):
        try:
            with open(ARQUIVO_USUARIOS, "r", encoding="utf-8") as f:
                usuarios = json.load(f)
        except Exception:
            usuarios = {}
            
    if USUARIO_PADRAO not in usuarios:
        usuarios[USUARIO_PADRAO] = SENHA_PADRAO
        salvar_usuarios(usuarios)
        
    return usuarios

def salvar_usuarios(usuarios):
    with open(ARQUIVO_USUARIOS, "w", encoding="utf-8") as f:
        json.dump(usuarios, f, ensure_ascii=False, indent=4)

# 3. Funções para Gerenciar Tarefas
def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        try:
            with open(ARQUIVO_TAREFAS, "r", encoding="utf-8") as f:
                data = json.load(f)
                for user, tarefas in data.items():
                    for t in tarefas:
                        if t.get("vencimento"):
                            t["vencimento"] = datetime.strptime(t["vencimento"], "%Y-%m-%d").date()
                return data
        except Exception:
            return {}
    return {}

def salvar_tarefas(todas_tarefas):
    data_para_salvar = {}
    for user, tarefas in todas_tarefas.items():
        lista_user = []
        for t in tarefas:
            t_copy = t.copy()
            if isinstance(t_copy.get("vencimento"), date):
                t_copy["vencimento"] = t_copy["vencimento"].strftime("%Y-%m-%d")
            lista_user.append(t_copy)
        data_para_salvar[user] = lista_user

    with open(ARQUIVO_TAREFAS, "w", encoding="utf-8") as f:
        json.dump(data_para_salvar, f, ensure_ascii=False, indent=4)

# Inicialização da Sessão
if "usuarios" not in st.session_state:
    st.session_state.usuarios = carregar_usuarios()

if "todas_tarefas" not in st.session_state:
    st.session_state.todas_tarefas = carregar_tarefas()

if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

if "editando_index" not in st.session_state:
    st.session_state.editando_index = None

TAGS_PRIORIDADE = {
    "Baixa": "🟡 Baixa",
    "Normal": "🟢 Normal",
    "Urgente / Importante": "🔴 Urgente / Importante"
}

# --- TELA DE AUTENTICAÇÃO ---
if st.session_state.usuario_logado is None:
    st.title("🔒 Acesso ao Gerenciador de Tarefas")
    
    tab_login, tab_cadastro = st.tabs(["🔑 Entrar", "📝 Criar Conta"])
    
    with tab_login:
        with st.form("form_login"):
            usuario = st.text_input("Usuário").strip()   # corrigido
            senha = st.text_input("Senha", type="password")
            btn_entrar = st.form_submit_button("Entrar")
            
            if btn_entrar:
                st.session_state.usuarios = carregar_usuarios()
                if usuario in st.session_state.usuarios and st.session_state.usuarios[usuario] == senha:
                    st.session_state.usuario_logado = usuario
                    st.success("Login realizado com sucesso!")
                    st.rerun()
                else:
                    st.error("Usuário ou senha incorretos.")

    with tab_cadastro:
        with st.form("form_cadastro"):
            novo_usuario = st.text_input("Escolha um Nome de Usuário").strip()   # corrigido
            nova_senha = st.text_input("Escolha uma Senha", type="password")
            btn_cadastrar = st.form_submit_button("Cadastrar")
            
            if btn_cadastrar:
                if not novo_usuario or not nova_senha:
                    st.error("Preencha todos os campos!")
                elif novo_usuario in st.session_state.usuarios:
                    st.error("Este usuário já existe.")
                else:
                    st.session_state.usuarios[novo_usuario] = nova_senha
                    salvar_usuarios(st.session_state.usuarios)
                    st.success("Conta criada com sucesso! Faça login na aba 'Entrar'.")

    st.stop()

# --- ÁREA PRIVADA (APÓS LOGIN) ---
user_atual = st.session_state.usuario_logado

if user_atual not in st.session_state.todas_tarefas:
    st.session_state.todas_tarefas[user_atual] = []

minhas_tarefas = st.session_state.todas_tarefas[user_atual]

# Barra Lateral
st.sidebar.title(f"👤 Olá, {user_atual.title()}!")
if st.sidebar.button("🚪 Sair (Logout)"):
    st.session_state.usuario_logado = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🔍 Filtros & Opções")
busca = st.sidebar.text_input("Buscar tarefa...", placeholder="Digite palavras-chave")

categorias = ["Todas", "Trabalho", "Estudos", "Pessoal", "Finanças", "Saúde", "Outros"]
cat_filtrada = st.sidebar.selectbox("Filtrar por Categoria", categorias)
prio_filtrada = st.sidebar.selectbox("Filtrar por Prioridade", ["Todas", "Baixa", "Normal", "Urgente / Importante"])
status_filtro = st.sidebar.radio("Filtrar por Status", ["Todas", "Pendentes", "Concluídas"])

# --- CONTEÚDO PRINCIPAL ---
st.title("✅ Minhas Tarefas Privadas")

# Dashboard de Métricas
total = len(minhas_tarefas)
concluidas = sum(1 for t in minhas_tarefas if t["concluida"])
pendentes = total - concluidas
progresso = (concluidas / total) if total > 0 else 0.0

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total", total)
col_m2.metric("Pendentes", pendentes)
col_m3.metric("Concluídas", concluidas)

st.progress(progresso, text=f"Progresso: {int(progresso * 100)}%")
st.markdown("---")

# Criar Nova Tarefa
with st.expander("➕ **Adicionar Nova Tarefa**", expanded=True):
    with st.form(key="form_nova_tarefa", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            texto = st.text_input("Descrição da Tarefa*", placeholder="Ex: Estudar para a prova...")
        with col2:
            categoria = st.selectbox("Categoria", ["Trabalho", "Estudos", "Pessoal", "Finanças", "Saúde", "Outros"])

        col3, col4 = st.columns([1, 1])
        with col3:
            prioridade = st.selectbox("Prioridade", ["Baixa", "Normal", "Urgente / Importante"], index=1)
        with col4:
            vencimento = st.date_input("Data de Vencimento", value=date.today())

        btn_salvar = st.form_submit_button("Adicionar Tarefa")

        if btn_salvar:
            if texto.strip() == "":
                st.error("Por favor, informe a descrição!")
            else:
                nova = {
                    "texto": texto,
                    "categoria": categoria,
                    "prioridade": prioridade,
                    "vencimento": vencimento,
                    "concluida": False
                }
                minhas_tarefas.append(nova)
                salvar_tarefas(st.session_state.todas_tarefas)
                st.success("Tarefa adicionada!")
                st.rerun()

# (resto do código de edição, filtros e exibição de tarefas continua igual)
