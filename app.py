import streamlit as st
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime, timedelta, timezone
import os
import base64

# --- MATRIZ CURRICULAR ---
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO: Base de dados curricular não encontrada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# --- 2. GESTÃO DE ESTADO ---
if 'step' not in st.session_state: 
    st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: 
    st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: 
    st.session_state.config = {}

def set_step(s): 
    st.session_state.step = s

# --- 3. ESTILIZAÇÃO CSS (PREMIUM UI - LOGO EXTERNO & RESPONSIVO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #1e293b;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    /* REMOVER MENU LATERAL */
    [data-testid="stSidebar"], [data-testid="stSidebarNav"] {
        display: none !important;
    }
    .st-emotion-cache-16ids0d {
        display: none !important;
    }
    
    /* Centralizar conteúdo principal */
    .block-container {
        padding-top: 2rem !important;
        max-width: 1100px !important;
    }

    /* QUADRANTE DO LOGO (BRANCO EXTERNO) */
    .logo-quadrant {
        display: flex;
        align-items: center;
        justify-content: center;
        background: white;
        padding: 10px;
        border-radius: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 120px; /* Altura fixa para manter alinhamento */
    }

    /* CAIXA AZUL DE TÍTULO */
    .premium-header-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .header-text-main {
        margin: 0;
        font-weight: 800;
        font-size: 2.4rem !important;
        color: white !important;
        letter-spacing: -1.5px;
        line-height: 1;
    }
    .header-text-sub {
        margin: 8px 0 0 0;
        font-weight: 400;
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* AJUSTE PARA MOBILE */
    @media (max-width: 768px) {
        .header-text-main { font-size: 1.8rem !important; }
        .logo-quadrant { 
            height: auto; 
            padding: 15px; 
            margin-top: 10px; 
        }
        .pencil-logo-mobile {
            font-size: 2rem !important;
        }
    }

    /* CARDS E INPUTS */
    .card-container {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #cbd5e1 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* BOTÕES */
    .stButton > button {
        border-radius: 12px;
        height: 3.8rem;
        font-weight: 700;
        font-size: 1.1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border: none;
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: #1e3a8a !important;
        color: white !important;
    }

    /* TAGS */
    .status-tag {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 12px;
        border: 1px solid transparent;
    }
    .tag-tech { background-color: #eff6ff; color: #1e40af; border-color: #bfdbfe; }
    .tag-eng { background-color: #fff1f2; color: #be123c; border-color: #fecdd3; }

    label {
        font-weight: 700 !important;
        color: #334155 !important;
        font-size: 0.85rem !important;
        margin-bottom: 8px !important;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def get_brazil_time():
    fuso_horario = timezone(timedelta(hours=-3))
    return datetime.now(fuso_horario)

# --- 4. RENDERIZAÇÃO DO CABEÇALHO ---
# Layout de 2 colunas: Título (Esquerda/Centro) e Logo Escola (Direita)
col_main_title, col_logo_esc = st.columns([8, 2], vertical_alignment="center")

with col_main_title:
    st.markdown(f"""
    <div class="premium-header-box">
        <h1 class="header-text-main">Sistema Planejar</h1>
        <p class="header-text-sub">Gestão Pedagógica Digital • CEIEF Rafael Affonso Leite</p>
    </div>
    """, unsafe_allow_html=True)

with col_logo_esc:
    # Quadrante branco externo com o emoji de lápis
    st.markdown("""
    <div class="logo-quadrant">
        <div class="pencil-logo-mobile" style="font-size: 3.5rem; text-align: center;">✏️</div>
    </div>
    """, unsafe_allow_html=True)

# --- FLUXO DE NAVEGAÇÃO ---
st.write("")
progresso = {1: 33, 2: 66, 3: 100}
st.progress(progresso[st.session_state.step])
st.write("")

# --- PASSO 1: CONFIGURAÇÃO ---
if st.session_state.step == 1:
    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 📋 Identificação do Planeamento")
    
    c1, c2 = st.columns(2)
    with c1:
        professor = st.text_input("PROFESSOR(A) RESPONSÁVEL", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
        
        anos = list(CURRICULO_DB.keys())
        saved_ano = st.session_state.config.get('ano')
        idx_ano = anos.index(saved_ano) if saved_ano in anos else 0
        ano = st.selectbox("ANO DE ESCOLARIDADE", anos, index=idx_ano)
        
        qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
        max_t = qtd_turmas.get(ano, 3)
        prefix = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
        opts = [f"{prefix}{i}" for i in range(1, max_t + 1)]
        
        valid_defaults = [t for t in st.session_state.config.get('turmas', []) if t in opts]
        turmas = st.multiselect("TURMAS VINCULADAS", opts, default=valid_defaults)

    with c2:
        meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        saved_mes = st.session_state.config.get('mes')
        idx_mes = list(meses.values()).index(saved_mes) if saved_mes in list(meses.values()) else 0
        mes_nome = st.selectbox("MÊS DE REFERÊNCIA", list(meses.values()), index=idx_mes)
        mes_num = [k for k, v in meses.items() if v == mes_nome][0]
        
        if mes_num == 2:
            quinzena_label = "Mês Inteiro"
            periodo_texto = "01/02/2026 a 28/02/2026"
            trimestre_doc = "1º Trimestre"
            st.info("Nota: Fevereiro é Planejamento Mensal.")
        else:
            quinzena_sel = st.radio("PERÍODO DE EXECUÇÃO", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"], horizontal=True)
            quinzena_label = quinzena_sel.split(" (")[0]
            tri = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"
            ultimo = calendar.monthrange(2026, mes_num)[1]
            periodo_texto = f"01/{mes_num:02d}/2026 a 15/{mes_num:02d}/2026" if "1ª" in quinzena_sel else f"16/{mes_num:02d}/2026 a {ultimo}/{mes_num:02d}/2026"
            trimestre_doc = tri
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Avançar para Matriz Curricular ➔", type="primary", use_container_width=True):
        if not professor or not turmas:
            st.error("ERRO: O nome do docente e a vinculação das turmas são obrigatórios.")
        else:
            if st.session_state.config.get('ano') != ano: 
                st.session_state.conteudos_selecionados = []
            st.session_state.config = {
                'professor': professor, 'ano': ano, 'turmas': turmas, 
                'mes': mes_nome, 'periodo': periodo_texto, 
                'trimestre': trimestre_doc, 'quinzena': quinzena_label
            }
            set_step(2); st.rerun()

# --- PASSO 2: MATRIZ ---
elif st.session_state.step == 2:
    st.markdown(f"### 📖 Matriz Curricular: **{st.session_state.config['ano']}**")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec = [k for k, v in dados.items() if "INGLÊS" not in k.upper() and "ORALIDADE" not in v[0]['eixo'].upper()]
        op_ing = [k for k in dados.keys() if k not in op_tec]

        t1, t2 = st.tabs(["💻 Tecnologia & Cultura Digital", "🇬🇧 Língua Inglesa"])
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("EIXO CURRICULAR", op_tec, key="t_g")
                e = c2.selectbox("HABILIDADE ESPECÍFICA", [i['especifico'] for i in dados[g]], key="t_e")
                sel = next(i for i in dados[g] if i['especifico'] == e)
                st.markdown(f"<div style='background:#f1f5f9; padding:1.5rem; border-radius:12px; border:1px solid #cbd5e1; margin-top:10px;'><span class='status-tag tag-tech'>Objetivo do Currículo</span><br><b>{sel['objetivo']}</b></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Lista ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Item adicionado!")
            else: st.warning("Dados não localizados.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("TÓPICO DE LINGUAGEM", op_ing, key="i_g")
                e = c2.selectbox("PRÁTICA LINGUÍSTICA", [i['especifico'] for i in dados[g]], key="i_e")
                sel = next(i for i in dados[g] if i['especifico'] == e)
                st.markdown(f"<div style='background:#fef2f2; padding:1.5rem; border-radius:12px; border:1px solid #fecdd3; margin-top:10px;'><span class='status-tag tag-eng'>Objetivo do Currículo</span><br><b>{sel['objetivo']}</b></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Lista ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Item adicionado!")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos em Planejamento")
        for i, it in enumerate(st.session_state.conteudos_selecionados):
            col_t, col_b = st.columns([0.96, 0.04])
            with col_t: st.markdown(f"<div style='background:white; border:1px solid #e2e8f0; padding:1rem; border-radius:12px; margin-bottom:10px;'><b>[{it['tipo']}]</b> {it['geral']}: {it['especifico']}</div>", unsafe_allow_html=True)
            with col_b: 
                if st.button("✕", key=f"del_{i}"): st.session_state.conteudos_selecionados.pop(i); st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Identificação"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhamento ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Erro: Selecione ao menos um conteúdo.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("### ✍️ Detalhamento Pedagógico")
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<div style='color:#be123c; font-weight:800; font-size:0.8rem; margin-bottom:1.5rem;'>TODOS OS CAMPOS SÃO OBRIGATÓRIOS PARA A EMISSÃO OFICIAL</div>", unsafe_allow_html=True)
        
        obj_esp = st.text_area("OBJECTIVOS ESPECÍFICOS DA AULA", height=120, placeholder="Defina os resultados práticos pretendidos...", value=st.session_state.config.get('obj_esp', ''))
        
        c1, c2 = st.columns(2)
        with c1: sit = st.text_area("SITUAÇÃO DIDÁTICA / METODOLOGIA", height=220, placeholder="Passo a passo da atividade...", value=st.session_state.config.get('sit', ''))
        with c2: rec = st.text_area("RECURSOS DIDÁTICOS", height=220, placeholder="Materiais e ferramentas...", value=st.session_state.config.get('rec', ''))
        
        c3, c4 = st.columns(2)
        with c3: aval = st.text_area("PROCEDIMENTOS DE AVALIAÇÃO", height=120, value=st.session_state.config.get('aval', ''))
        with c4: recup = st.text_area("RECUPERAÇÃO CONTÍNUA", height=120, value=st.session_state.config.get('recup', ''))
        st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    # --- GERADORES ---
    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planeamento de Linguagens e Tecnologias', 0, 1, 'C'); pdf.ln(10)
        
        pdf.set_fill_color(245, 247, 250); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 7, clean(f"DOCENTE: {dados['professor']}"), 1, 1, 'L', True)
        pdf.cell(0, 7, clean(f"ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.cell(0, 7, clean(f"MÊS: {dados['mes']} | PERÍODO: {dados['quinzena']} | TRIMESTRE: {dados['trimestre']}"), 1, 1, 'L', True)
        pdf.cell(0, 7, clean(f"INTERVALO: {dados['periodo']}"), 1, 1, 'L', True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR SELECIONADA"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for l, v in [("Objetivos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1); pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
        
        horario_br = get_brazil_time().strftime("%d/%m/%Y %H:%M:%S")
        pdf.set_y(-20); pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, f'Emitido pelo Sistema Planejar (GMT-3) em: {horario_br}', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("CEIEF RAFAEL AFFONSO LEITE\nPlaneamento de Linguagens e Tecnologias").bold = True
        
        doc.add_paragraph(f"Docente: {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}")
        doc.add_paragraph(f"Mês: {dados['mes']} | Período: {dados['quinzena']} | Trimestre: {dados['trimestre']}\nIntervalo: {dados['periodo']}")
        
        doc.add_heading("Matriz Curricular", 2)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento Pedagógico", 2)
        for l, v in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
        
        horario_br = get_brazil_time().strftime("%d/%m/%Y %H:%M:%S")
        doc.add_paragraph(f"\nEmitido eletronicamente em: {horario_br} (GMT-3)")
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ Matriz"): set_step(2); st.rerun()
    if c2.button("GERAR PLANEAMENTO FINAL 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]): 
            st.error("Erro: Preencha todos os campos obrigatórios.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_arq = f"Planeamento_{f_data['mes']}_{f_data['ano'].replace(' ','')}"
            st.success("✅ Documentação gerada com sucesso!"); st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 Descarregar WORD", w_file, f"{nome_arq}.docx", use_container_width=True)
            cd2.download_button("📕 Descarregar PDF", p_file, f"{nome_arq}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:80px; padding:40px; color:#94a3b8; font-size:0.85rem; border-top:1px solid #e2e8f0;">
        <b>SISTEMA PLANEJAR ELITE V7.2</b><br>
        Desenvolvido por José Victor Souza Gallo • CEIEF Rafael Affonso Leite © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
