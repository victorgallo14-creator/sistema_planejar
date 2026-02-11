import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
import os

# --- MATRIZ CURRICULAR ---
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO: Base de dados curricular não encontrada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DE ALTA PERFORMANCE ---
st.set_page_config(
    page_title="Planejar Elite | Gestão Pedagógica",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# --- 2. GESTÃO DE ESTADO (INICIALIZAÇÃO) ---
if 'step' not in st.session_state: 
    st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: 
    st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: 
    st.session_state.config = {}

def set_step(s): 
    st.session_state.step = s

# --- 3. DESIGN SYSTEM (UX/UI PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Configurações Globais */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1E293B;
    }
    
    .stApp {
        background-color: #F8FAFC;
    }

    /* Barra Lateral (Dashboard Hub) */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #1E293B;
    }
    [data-testid="stSidebar"] * {
        color: #F1F5F9 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #334155;
    }

    /* Cabeçalho Institucional */
    .app-header {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    /* Stepper (Indicador de Progresso SaaS) */
    .stepper-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2.5rem;
        padding: 0 10%;
    }
    .step-box {
        text-align: center;
        flex: 1;
        position: relative;
    }
    .step-circle {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: #E2E8F0;
        color: #64748B;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 8px;
        font-weight: 700;
        font-size: 0.85rem;
        transition: all 0.3s ease;
    }
    .step-circle.active {
        background: #6366F1;
        color: white;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.2);
    }
    .step-text {
        font-size: 0.75rem;
        font-weight: 700;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-text.active { color: #1E293B; }

    /* Cards e Containers */
    .enterprise-card {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.02);
        margin-bottom: 2rem;
    }

    /* Inputs Padronizados (High Visibility) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        color: #1E293B !important;
        font-weight: 500 !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1) !important;
    }

    /* Botões Premium */
    .stButton > button {
        border-radius: 12px;
        height: 3.8rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* Botão Primário */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: #6366F1 !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.3);
    }
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background: #4F46E5 !important;
        transform: translateY(-2px);
    }

    /* Labels Profissionais */
    label {
        font-weight: 700 !important;
        color: #475569 !important;
        font-size: 0.8rem !important;
        margin-bottom: 8px !important;
        text-transform: uppercase;
    }

    /* Badges de Conteúdo */
    .content-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .badge-blue { background: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; }
    .badge-rose { background: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }
    
    /* Responsividade Celular */
    @media (max-width: 768px) {
        .app-header { flex-direction: column; text-align: center; gap: 1rem; }
        .stepper-container { padding: 0; }
        .enterprise-card { padding: 1.5rem; }
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER NATIVO E SEGURO ---
with st.container():
    col_h1, col_h2, col_h3 = st.columns([1, 4, 1])
    with col_h1:
        logo_p = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
        if os.path.exists(logo_p): st.image(logo_p, width=90)
    with col_h2:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin:0; font-size:2.2rem; font-weight:800; color:#0F172A;'>SISTEMA PLANEJAR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='margin:0; color:#64748B; font-weight:500; font-size:0.9rem;'>PEDAGOGIA DE ALTA PERFORMANCE • CEIEF</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_h3:
        logo_e = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
        if os.path.exists(logo_e): st.image(logo_e, width=90)

st.write("")

# --- 5. STEPPER VISUAL ---
st.markdown(f"""
<div class="stepper-container">
    <div class="step-box">
        <div class="step-circle {'active' if st.session_state.step >= 1 else ''}">1</div>
        <div class="step-text {'active' if st.session_state.step >= 1 else ''}">Parâmetros</div>
    </div>
    <div class="step-box">
        <div class="step-circle {'active' if st.session_state.step >= 2 else ''}">2</div>
        <div class="step-text {'active' if st.session_state.step >= 2 else ''}">Matriz</div>
    </div>
    <div class="step-box">
        <div class="step-circle {'active' if st.session_state.step >= 3 else ''}">3</div>
        <div class="step-text {'active' if st.session_state.step >= 3 else ''}">Emissão</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    with st.sidebar:
        st.markdown("### 🏢 UNIDADE ESCOLAR")
        st.write("CEIEF Rafael Affonso Leite")
        st.markdown("---")
        st.caption("Acesse os parâmetros principais para iniciar o documento oficial.")

    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### 🔑 Identificação do Documento")
    st.write("")
    
    c1, c2 = st.columns(2)
    with c1:
        professor = st.text_input("PROFESSOR RESPONSÁVEL", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
        anos = list(CURRICULO_DB.keys())
        saved_ano = st.session_state.config.get('ano')
        idx_ano = anos.index(saved_ano) if saved_ano in anos else 0
        ano = st.selectbox("ANO DE ESCOLARIDADE", anos, index=idx_ano)
        
        qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
        max_t = qtd_turmas.get(ano, 3)
        opts = [f"{ano} - Turma {i}" if "Maternal" in ano or "Etapa" in ano else f"{ano} {i}" for i in range(1, max_t + 1)]
        valid_defaults = [t for t in st.session_state.config.get('turmas', []) if t in opts]
        turmas = st.multiselect("TURMAS VINCULADAS", opts, default=valid_defaults)

    with c2:
        meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        mes_nome = st.selectbox("MÊS DE REFERÊNCIA", list(meses.values()))
        mes_num = [k for k, v in meses.items() if v == mes_nome][0]
        
        if mes_num == 2:
            periodo_texto = "01/02/2026 a 28/02/2026"
            trimestre_doc = "1º Trimestre"
            st.info("ℹ️ Planejamento Mensal detectado.")
        else:
            quinzena = st.radio("PERÍODO DE EXECUÇÃO", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
            tri = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"
            ultimo = calendar.monthrange(2026, mes_num)[1]
            periodo_texto = f"01/{mes_num:02d}/2026 a 15/{mes_num:02d}/2026" if "1ª" in quinzena else f"16/{mes_num:02d}/2026 a {ultimo}/{mes_num:02d}/2026"
            trimestre_doc = tri
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Configurar Matriz Curricular ➔", type="primary", use_container_width=True):
        if not professor or not turmas:
            st.error("Campos obrigatórios em branco.")
        else:
            if st.session_state.config.get('ano') != ano: st.session_state.conteudos_selecionados = []
            st.session_state.config = {'professor': professor, 'ano': ano, 'turmas': turmas, 'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc}
            set_step(2); st.rerun()

# --- PASSO 2: MATRIZ ---
elif st.session_state.step == 2:
    with st.sidebar:
        st.markdown("### 📊 STATUS DA MATRIZ")
        st.write(f"Ano: {st.session_state.config['ano']}")
        st.write(f"Itens: {len(st.session_state.conteudos_selecionados)}")

    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown(f"### 🎯 Matriz Curricular: {st.session_state.config['ano']}")
    
    dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
    op_tec = [k for k, v in dados.items() if "INGLÊS" not in k.upper() and "ORALIDADE" not in v[0]['eixo'].upper()]
    op_ing = [k for k in dados.keys() if k not in op_tec]

    t1, t2 = st.tabs(["TECNOLOGIA E CULTURA DIGITAL", "LÍNGUA INGLESA"])
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("EIXO ESTRUTURANTE", op_tec, key="t_g")
            e = c2.selectbox("HABILIDADE ESPECÍFICA", [i['especifico'] for i in dados[g]], key="t_e")
            sel = next(i for i in dados[g] if i['especifico'] == e)
            st.markdown(f"<div style='background:#F8FAFC; padding:1.5rem; border-radius:12px; border:1px solid #E2E8F0; margin-top:10px;'><span class='content-badge badge-blue'>Objetivo Curricular</span><div style='font-weight:600; color:#1E293B;'>{sel['objetivo']}</div></div>", unsafe_allow_html=True)
            if st.button("Vincular à Unidade ➕", key="bt_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Item vinculado!")
        else: st.warning("Dados não localizados.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("TÓPICO CURRICULAR", op_ing, key="i_g")
            e = c2.selectbox("PRÁTICA LINGUÍSTICA", [i['especifico'] for i in dados[g]], key="i_e")
            sel = next(i for i in dados[g] if i['especifico'] == e)
            st.markdown(f"<div style='background:#FFF1F2; padding:1.5rem; border-radius:12px; border:1px solid #FECDD3; margin-top:10px;'><span class='content-badge badge-rose'>Objetivo Curricular</span><div style='font-weight:600; color:#881337;'>{sel['objetivo']}</div></div>", unsafe_allow_html=True)
            if st.button("Vincular à Unidade ➕", key="bt_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Item vinculado!")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.conteudos_selecionados:
        st.markdown("#### Itens em Revisão")
        for i, it in enumerate(st.session_state.conteudos_selecionados):
            col_t, col_b = st.columns([0.94, 0.06])
            with col_t: st.markdown(f"<div style='background:white; border:1px solid #E2E8F0; padding:1rem; border-radius:12px; margin-bottom:10px;'><b>[{it['tipo']}]</b> {it['geral']}: {it['especifico']}</div>", unsafe_allow_html=True)
            with col_b: 
                if st.button("✕", key=f"del_{i}"): st.session_state.conteudos_selecionados.pop(i); st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ IDENTIFICAÇÃO"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhamento ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Selecione ao menos um item.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    with st.sidebar:
        st.markdown("### 📋 CHECKLIST")
        st.write("✓ Identificação concluída")
        st.write("✓ Matriz vinculada")
        st.markdown("---")
        st.caption("Finalize o texto pedagógico para gerar os arquivos Word e PDF.")

    st.markdown('<div class="enterprise-card">', unsafe_allow_html=True)
    st.markdown("### ✍️ Detalhamento Pedagógico (Obrigatório)")
    
    obj_esp = st.text_area("OBJETIVOS ESPECÍFICOS DA AULA", height=100, placeholder="Descreva os resultados práticos desejados...")
    
    col_a, col_b = st.columns(2)
    with col_a: sit = st.text_area("SITUAÇÃO DIDÁTICA / METODOLOGIA", height=200, placeholder="Passo a passo...")
    with col_b: rec = st.text_area("RECURSOS DIDÁTICOS", height=200, placeholder="Materiais...")
    
    col_c, col_d = st.columns(2)
    with col_c: aval = st.text_area("AVALIAÇÃO", height=100)
    with col_d: recup = st.text_area("RECUPERAÇÃO CONTÍNUA", height=100)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    # --- GERADORES ---
    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planejamento Digital de Unidade', 0, 1, 'C'); pdf.ln(10)
        pdf.set_fill_color(245, 247, 250); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 7, clean(f"PROFESSOR: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DESENVOLVIMENTO"), 0, 1)
        for l, v in [("Objetivos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliacao", dados['aval']), ("Recuperacao", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1); pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
        pdf.set_y(-20); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 10, f'Emitido pelo Sistema Planejar em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("CEIEF RAFAEL AFFONSO LEITE\nPlanejamento de Linguagens e Tecnologias").bold = True
        doc.add_paragraph(f"Professor: {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        doc.add_heading("Matriz Curricular", 2)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento", 2)
        for l, v in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ MATRIZ"): set_step(2); st.rerun()
    if c2.button("Gerar Documentação Final 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]): st.error("Campos pendentes.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome = f"Planejar_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("✅ Planejamento gerado com sucesso!"); st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 WORD (.DOCX)", w_file, f"{nome}.docx", use_container_width=True)
            cd2.download_button("📕 PDF (.PDF)", p_file, f"{nome}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:60px; padding:30px; color:#94A3B8; font-size:0.75rem; border-top:1px solid #E2E8F0;">
        PEDAGOGIA DE ALTA PERFORMANCE • DESENVOLVIDO POR JOSÉ VICTOR SOUZA GALLO<br>
        CEIEF RAFAEL AFFONSO LEITE © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
