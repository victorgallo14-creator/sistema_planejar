import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA MATRIZ ---
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO DE SISTEMA: A base de dados curricular não foi encontrada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | Gestão Pedagógica",
    layout="wide",
    page_icon="📘",
    initial_sidebar_state="expanded"
)

# --- 2. CSS CUSTOMIZADO (ALTO CONTRASTE & CORPORATIVO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* Configuração Geral */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    /* BARRA LATERAL (Dark Enterprise Style) */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }
    [data-testid="stSidebar"] .stTextInput input {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: white !important;
    }

    /* CAMPOS DE ENTRADA (Foco em Visibilidade) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #94a3b8 !important; /* Borda visível e sólida */
        border-radius: 6px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        padding: 10px !important;
        font-weight: 500 !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }

    /* BLOCOS DE CONTEÚDO (Cards) */
    .dashboard-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }

    /* TÍTULOS */
    h1, h2, h3 {
        color: #0f172a !important;
        font-weight: 800 !important;
        letter-spacing: -0.02em;
    }
    
    label {
        font-weight: 700 !important;
        color: #475569 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        margin-bottom: 4px !important;
        letter-spacing: 0.025em;
    }

    /* BOTÕES */
    .stButton > button {
        border-radius: 6px;
        height: 3.2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    /* Botão Principal (Azul Institucional) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
    }

    /* WIZARD (Indicador de Passos) */
    .wizard-container {
        display: flex;
        justify-content: space-around;
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .wizard-step {
        font-size: 0.8rem;
        font-weight: 800;
        color: #94a3b8;
    }
    .wizard-active {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
    }

    /* BADGES */
    .badge-label {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO PROFISSIONAL ---
with st.container():
    col_l, col_c, col_r = st.columns([1, 4, 1])
    with col_l:
        logo_p = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
        if os.path.exists(logo_p): st.image(logo_p, width=90)
    with col_c:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin:0; font-size:2.2rem; color:#1e3a8a !important;'>SISTEMA PLANEJAR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; font-weight:600; text-transform:uppercase; font-size:0.9rem; margin-top:-5px;'>Gestão Pedagógica Digital • CEIEF Rafael Affonso Leite</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        logo_e = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
        if os.path.exists(logo_e): st.image(logo_e, width=90)

st.markdown("---")

# --- GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# INDICADOR DE PROGRESSO
step_cols = st.columns(3)
labels = ["01. Identificação", "02. Matriz Curricular", "03. Detalhamento"]
for i, label in enumerate(labels):
    is_active = "wizard-active" if st.session_state.step == (i+1) else ""
    step_cols[i].markdown(f"<div class='wizard-container'><span class='wizard-step {is_active}'>{label.upper()}</span></div>", unsafe_allow_html=True)

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("### Parâmetros do Documento")
        
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Professor(a) Responsável", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
            anos = list(CURRICULO_DB.keys())
            saved_ano = st.session_state.config.get('ano')
            idx = anos.index(saved_ano) if saved_ano in anos else 0
            ano = st.selectbox("Ano de Escolaridade", anos, index=idx)
            
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(ano, 3)
            prefix = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
            opts = [f"{prefix}{i}" for i in range(1, max_t + 1)]
            saved_turmas = st.session_state.config.get('turmas', [])
            valid_defaults = [t for t in saved_turmas if t in opts]
            turmas = st.multiselect("Vincular Turmas", opts, default=valid_defaults)

        with c2:
            meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            saved_mes = st.session_state.config.get('mes')
            idx_mes = list(meses.values()).index(saved_mes) if saved_mes in list(meses.values()) else 0
            mes_nome = st.selectbox("Mês de Referência", list(meses.values()), index=idx_mes)
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("Nota: Planeamento Mensal (Fevereiro)")
            else:
                quinzena = st.radio("Período de Execução", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                trimestre_doc = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Avançar para Matriz Curricular ➔", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("Atenção: Nome do professor e turmas são obrigatórios.")
            else:
                if st.session_state.config.get('ano') != ano: st.session_state.conteudos_selecionados = []
                st.session_state.config = {'professor': professor, 'ano': ano, 'turmas': turmas, 'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc}
                next_step(); st.rerun()

# --- PASSO 2: MATRIZ CURRICULAR ---
elif st.session_state.step == 2:
    st.markdown(f"#### Matriz Curricular Oficial: {st.session_state.config['ano']}")
    with st.container():
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec, op_ing = [], []
        termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
        for k, v in dados.items():
            if v:
                eixo = v[0]['eixo'].upper()
                if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
                else: op_tec.append(k)

        t1, t2 = st.tabs(["TECNOLOGIA E CULTURA DIGITAL", "LÍNGUA INGLESA"])
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Eixo Curricular", op_tec, key="t_g")
                itens = dados[g]
                e = c2.selectbox("Habilidade Específica", [i['especifico'] for i in itens], key="t_e")
                sel = next(i for i in itens if i['especifico'] == e)
                st.markdown(f"<div style='background:#f8fafc; padding:15px; border:1px solid #cbd5e1; border-radius:6px; margin-top:10px;'><div class='badge-label'>OBJETIVO</div><div style='font-weight:600; color:#1e3a8a;'>{sel['objetivo']}</div></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Aula ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Item adicionado.")
            else: st.warning("Sem dados disponíveis.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Tópico de Linguagem", op_ing, key="i_g")
                itens = dados[g]
                e = c2.selectbox("Prática Linguística", [i['especifico'] for i in itens], key="i_e")
                sel = next(i for i in itens if i['especifico'] == e)
                st.markdown(f"<div style='background:#fdf2f2; padding:15px; border:1px solid #fecdd3; border-radius:6px; margin-top:10px;'><div class='badge-label'>OBJETIVO</div><div style='font-weight:600; color:#991b1b;'>{sel['objetivo']}</div></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Aula ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Item adicionado.")
            else: st.warning("Sem dados disponíveis.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.conteudos_selecionados:
        st.markdown("##### Itens na Lista de Planeamento")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            col_t, col_b = st.columns([0.96, 0.04])
            with col_t: st.markdown(f"<div style='background:white; border:1px solid #cbd5e1; padding:12px; border-radius:4px; margin-bottom:5px;'><strong>[{item['tipo']}] {item['geral']}</strong>: {item['especifico']}</div>", unsafe_allow_html=True)
            with col_b: 
                if st.button("✕", key=f"del_{i}"): 
                    st.session_state.conteudos_selecionados.pop(i); st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Identificação"): prev_step(); st.rerun()
    if c2.button("Avançar para Detalhamento ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Seleccione ao menos um item da matriz.")
        else: next_step(); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("#### Detalhamento Pedagógico Estruturado")
    with st.container():
        st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#e11d48; font-weight:800; font-size:0.75rem; margin-bottom:10px;'>TODOS OS CAMPOS ABAIXO SÃO OBRIGATÓRIOS</div>", unsafe_allow_html=True)
        
        obj_esp = st.text_area("Objetivos Específicos da Aula", height=100, placeholder="Defina os resultados práticos desejados...")
        c1, c2 = st.columns(2)
        with c1: sit = st.text_area("Situação Didática / Metodologia", height=200, placeholder="Passo a passo...")
        with c2: rec = st.text_area("Recursos Didáticos", height=200, placeholder="Materiais e ferramentas...")
        
        c3, c4 = st.columns(2)
        with c3: aval = st.text_area("Avaliação", height=100)
        with c4: recup = st.text_area("Recuperação Contínua", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C'); pdf.ln(15)
        pdf.set_fill_color(245, 245, 245); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PROFESSOR: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for l, v in [("Objetivos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1); pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Matriz"): prev_step(); st.rerun()
    if c2.button("Finalizar e Emitir Documentos 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]): st.error("Todos os campos do detalhamento são obrigatórios.")
        else:
            f_data = st.session_state.config
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome = f"Plan_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("✅ Documento gerado com sucesso!"); st.balloons()
            st.download_button("📥 Descarregar Documento PDF", p_file, f"{nome}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:50px; padding:20px; color:#64748b; font-size:0.75rem; border-top:1px solid #e2e8f0;">
        PROPRIEDADE EXCLUSIVA DO CEIEF RAFAEL AFFONSO LEITE<br>
        Desenvolvido por <b>José Victor Souza Gallo</b> • {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
