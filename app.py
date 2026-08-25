import streamlit as st
import json
import os
from datetime import datetime, date

# 1. Configuração da Página
st.set_page_config(
    page_title="Gerenciador de Tarefas Pro", 
    page_icon="✅", 
    layout="wide"
)

ARQUIVO_DADOS = "tarefas.json"

# 2. Persistência de Dados (Funções para Salvar e Carregar)
def carregar_tarefas():
    if os.path.exists(ARQUIVO_DADOS):
        try:
            with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
                tarefas = json.load(f)
                # Converter datas salvas em string de volta para objeto date
                for t in tarefas:
                    if t.get("vencimento"):
                        t["vencimento"] = datetime.strptime(t["vencimento"], "%Y-%m-%d").date()
                return tarefas
        except Exception:
            return []
    return []

def salvar_tarefas(tarefas):
    tarefas_para_salvar = []
    for t in tarefas:
        t_copy = t.copy()
        if isinstance(t_copy.get("vencimento"), date):
            t_copy["vencimento"] = t_copy["vencimento"].strftime("%Y-%m-%d")
        tarefas_para_salvar.append(t_copy)
    
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(tarefas_para_salvar, f, ensure_ascii=False, indent=4)

# 3. Inicialização da Memória da Sessão
if "tarefas" not in st.session_state:
    st.session_state.tarefas = carregar_tarefas()

# --- BARRA LATERAL (Filtros e Ações) ---
st.sidebar.header("🔍 Filtros & Opções")

# Filtro por Busca
busca = st.sidebar.text_input("Buscar tarefa...", placeholder="Digite palavras-chave")

# Filtro por Categoria
categorias = ["Todas", "Trabalho", "Estudos", "Pessoal", "Finanças", "Saúde", "Outros"]
cat_filtrada = st.sidebar.selectbox("Filtrar por Categoria", categorias)

# Filtro por Status
status_filtro = st.sidebar.radio("Filtrar por Status", ["Todas", "Pendentes", "Concluídas"])

st.sidebar.markdown("---")
if st.sidebar.button("🧹 Limpar Todas as Tarefas", type="secondary"):
    st.session_state.tarefas = []
    salvar_tarefas([])
    st.rerun()

# --- CONTEÚDO PRINCIPAL ---
st.title("✅ Gerenciador de Tarefas Pro")
st.caption("Organize seus compromissos com prioridades, prazos e categorias.")

# 4. Painel de Métricas e Progresso
total = len(st.session_state.tarefas)
concluidas = sum(1 for t in st.session_state.tarefas if t["concluida"])
pendentes = total - concluidas
progresso = (concluidas / total) if total > 0 else 0.0

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Total de Tarefas", total)
col_m2.metric("Pendentes", pendentes)
col_m3.metric("Concluídas", concluidas)

st.progress(progresso, text=f"Progresso de Conclusão: {int(progresso * 100)}%")
st.markdown("---")

# 5. Formulário para Adicionar Nova Tarefa
with st.expander("➕ **Adicionar Nova Tarefa**", expanded=True):
    with st.form(key="form_nova_tarefa", clear_on_submit=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            texto = st.text_input("Descrição da Tarefa*", placeholder="Ex: Entregar trabalho acadêmico")
        with col2:
            categoria = st.selectbox("Categoria", ["Trabalho", "Estudos", "Pessoal", "Finanças", "Saúde", "Outros"])

        col3, col4 = st.columns([1, 1])
        with col3:
            prioridade = st.select_slider("Prioridade", options=["Baixa", "Média", "Alta"], value="Média")
        with col4:
            vencimento = st.date_input("Data de Vencimento", value=date.today())

        btn_salvar = st.form_submit_button("Salvar Tarefa")

        if btn_salvar:
            if texto.strip() == "":
                st.error("Por favor, informe a descrição da tarefa!")
            else:
                nova = {
                    "texto": texto,
                    "categoria": categoria,
                    "prioridade": prioridade,
                    "vencimento": vencimento,
                    "concluida": False
                }
                st.session_state.tarefas.append(nova)
                salvar_tarefas(st.session_state.tarefas)
                st.success("Tarefa adicionada com sucesso!")
                st.rerun()

# 6. Exibição das Tarefas
st.subheader("📌 Minhas Tarefas")

# Aplicação dos Filtros
tarefas_exibicao = st.session_state.tarefas

if status_filtro == "Pendentes":
    tarefas_exibicao = [t for t in tarefas_exibicao if not t["concluida"]]
elif status_filtro == "Concluídas":
    tarefas_exibicao = [t for t in tarefas_exibicao if t["concluida"]]

if cat_filtrada != "Todas":
    tarefas_exibicao = [t for t in tarefas_exibicao if t.get("categoria") == cat_filtrada]

if busca.strip():
    tarefas_exibicao = [t for t in tarefas_exibicao if busca.lower() in t["texto"].lower()]

# Mapeamento de Cores por Prioridade
cores_prioridade = {
    "Alta": "🔴 **[Alta]**",
    "Média": "🟡 **[Média]**",
    "Baixa": "🟢 **[Baixa]**"
}

if not tarefas_exibicao:
    st.info("Nenhuma tarefa encontrada com os filtros selecionados.")
else:
    for i, tarefa in enumerate(st.session_state.tarefas):
        # Apenas exibe se a tarefa estiver no conjunto filtrado
        if tarefa in tarefas_exibicao:
            with st.container():
                c_check, c_desc, c_meta, c_del = st.columns([0.05, 0.55, 0.3, 0.1])

                # Checkbox de status
                with c_check:
                    status = st.checkbox("", value=tarefa["concluida"], key=f"chk_{i}")
                    if status != tarefa["concluida"]:
                        st.session_state.tarefas[i]["concluida"] = status
                        salvar_tarefas(st.session_state.tarefas)
                        st.rerun()

                # Texto / Descrição
                with c_desc:
                    if tarefa["concluida"]:
                        st.markdown(f"~~{tarefa['texto']}~~")
                    else:
                        st.write(f"**{tarefa['texto']}**")

                # Metadados (Categoria, Prioridade, Data)
                with c_meta:
                    prio_tag = cores_prioridade.get(tarefa.get("prioridade", "Média"), "")
                    data_str = tarefa["vencimento"].strftime("%d/%m/%Y") if isinstance(tarefa.get("vencimento"), date) else ""
                    st.caption(f"📂 {tarefa.get('categoria', 'Geral')} | {prio_tag} | 📅 {data_str}")

                # Botão Excluir
                with c_del:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.tarefas.pop(i)
                        salvar_tarefas(st.session_state.tarefas)
                        st.rerun()
            st.divider()
