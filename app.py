import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
import os

# --- GARANTIA DE DADOS ---
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO DE SISTEMA: Base de dados curricular não encontrada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DE ALTA FIDELIDADE ---
st.set_page_config(
    page_title="Planejar Elite | Gestão Pedagógica",
    layout="wide",
    page_icon="🔷",
    initial_sidebar_state="expanded"
)

# --- 2. MOTOR DE DESIGN (CSS PREMIUM - ZERO INFANTILIDADE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Base */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    /* Barra Lateral Dashboard */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #ffffff !important;
        font-size: 1.2rem;
        letter-spacing: 1px;
    }
    
    /* Inputs e Campos de Texto */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 1px solid #cbd5e1 !important;
        border-radius: 4px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        padding: 12px !important;
        font-size: 0.95rem !important;
        box-shadow: none !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        border-width: 2px !important;
    }

    /* Títulos e Hierarquia */
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: -0.025em !important;
    }

    /* Labels Profissionais */
    label {
        font-weight: 600 !important;
        color: #475569 !important;
        font-size: 0.8rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* Wizard / Passos do Processo */
    .wizard-bar {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        margin-bottom: 3rem;
        padding: 1rem;
        background: white;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    .step-unit {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-weight: 700;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    .step-active {
        color: #2563eb;
    }
    .step-number {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
    }
    .active-number {
        background: #2563eb;
        color: white;
    }

    /* Botões Elite */
    .stButton > button {
        border-radius: 4px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid #e2e8f0;
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border: none !important;
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    /* Container de Conteúdo */
    .content-card {
        background: white;
        padding: 2.5rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    
    /* Badges de Disciplina */
    .badge {
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-right: 10px;
    }
    .badge-tech { background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .badge-eng { background: #fef2f2; color: #991b1b; border: 1px solid #fecdd3; }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO (CORREÇÃO DEFINITIVA) ---
def render_refined_header():
    col_l, col_c, col_r = st.columns([1, 4, 1])
    with col_l:
        p_logo = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
        if os.path.exists(p_logo): st.image(p_logo, width=85)
    with col_c:
        st.markdown("<div style='text-align:center; padding-top:10px;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin:0; font-size:2.6rem; color:#0f172a !important;'>PLANEJAR ELITE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; font-weight:500; font-size:1rem; margin-top:-5px;'>SISTEMA INTEGRADO DE GESTÃO PEDAGÓGICA • CEIEF</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        e_logo = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
        if os.path.exists(e_logo): st.image(e_logo, width=85)
    st.markdown("<hr style='margin:1.5rem 0; border:0; border-top:2px solid #e2e8f0;'>", unsafe_allow_html=True)

render_refined_header()

# --- GESTÃO DE FLUXO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(s): st.session_state.step = s

# Wizard UI
c1, c2, c3 = st.columns([1,1,1])
with c1: 
    active = "step-active" if st.session_state.step == 1 else ""
    num_active = "active-number" if st.session_state.step == 1 else ""
    st.markdown(f"<div class='step-unit {active}'><div class='step-number {num_active}'>1</div> PARÂMETROS</div>", unsafe_allow_html=True)
with c2:
    active = "step-active" if st.session_state.step == 2 else ""
    num_active = "active-number" if st.session_state.step == 2 else ""
    st.markdown(f"<div class='step-unit {active}'><div class='step-number {num_active}'>2</div> MATRIZ CURRICULAR</div>", unsafe_allow_html=True)
with c3:
    active = "step-active" if st.session_state.step == 3 else ""
    num_active = "active-number" if st.session_state.step == 3 else ""
    st.markdown(f"<div class='step-unit {active}'><div class='step-number {num_active}'>3</div> EMISSÃO</div>", unsafe_allow_html=True)

st.write("")

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("### 01. Identificação Geral")
        
        col1, col2 = st.columns(2)
        with col1:
            professor = st.text_input("DOCENTE RESPONSÁVEL", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
            
            anos = list(CURRICULO_DB.keys())
            saved_ano = st.session_state.config.get('ano')
            idx_ano = anos.index(saved_ano) if saved_ano in anos else 0
            ano = st.selectbox("ANO DE ESCOLARIDADE", anos, index=idx_ano)
            
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(ano, 3)
            prefixo = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
            opts = [f"{prefixo}{i}" for i in range(1, max_t + 1)]
            
            saved_turmas = st.session_state.config.get('turmas', [])
            valid_defaults = [t for t in saved_turmas if t in opts]
            turmas = st.multiselect("TURMAS VINCULADAS", opts, default=valid_defaults)

        with col2:
            meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            saved_mes = st.session_state.config.get('mes')
            idx_mes = list(meses.values()).index(saved_mes) if saved_mes in list(meses.values()) else 0
            mes_nome = st.selectbox("MÊS DE REFERÊNCIA", list(meses.values()), index=idx_mes)
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("Regime de Planeamento Mensal Activo.")
            else:
                quinzena = st.radio("PERÍODO DE EXECUÇÃO", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                tri = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
                trimestre_doc = tri
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")
        if st.button("Configurar Matriz Curricular ➔", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("Campos obrigatórios em falta: Nome do Professor ou Turmas.")
            else:
                if st.session_state.config.get('ano') != ano: st.session_state.conteudos_selecionados = []
                st.session_state.config = {'professor': professor, 'ano': ano, 'turmas': turmas, 'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc}
                set_step(2); st.rerun()

# --- PASSO 2: MATRIZ ---
elif st.session_state.step == 2:
    st.markdown(f"### 02. Matriz Curricular: {st.session_state.config['ano']}")
    with st.container():
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec, op_ing = [], []
        termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
        for k, v in dados.items():
            if v:
                eixo = v[0]['eixo'].upper()
                if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
                else: op_tec.append(k)

        t1, t2 = st.tabs(["TECNOLOGIA & CULTURA DIGITAL", "LÍNGUA INGLESA"])
        
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("EIXO CURRICULAR", op_tec, key="t_g")
                itens = dados[g]
                e = c2.selectbox("HABILIDADE ESPECÍFICA", [i['especifico'] for i in itens], key="t_e")
                sel = next(i for i in itens if i['especifico'] == e)
                st.markdown(f"<div style='background:#f8fafc; padding:20px; border:1px solid #e2e8f0; border-radius:4px; margin-top:10px;'><span class='badge badge-tech'>OBJETIVO OFICIAL</span><div style='font-weight:600; font-size:1.1rem; color:#1e3a8a; margin-top:10px;'>{sel['objetivo']}</div></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Unidade de Aula ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Item adicionado com sucesso.")
            else: st.warning("Dados não localizados.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("TÓPICO DE LINGUAGEM", op_ing, key="i_g")
                itens = dados[g]
                e = c2.selectbox("PRÁTICA LINGUÍSTICA", [i['especifico'] for i in itens], key="i_e")
                sel = next(i for i in itens if i['especifico'] == e)
                st.markdown(f"<div style='background:#fff1f2; padding:20px; border:1px solid #fecdd3; border-radius:4px; margin-top:10px;'><span class='badge badge-eng'>OBJETIVO OFICIAL</span><div style='font-weight:600; font-size:1.1rem; color:#991b1b; margin-top:10px;'>{sel['objetivo']}</div></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Unidade de Aula ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Item adicionado com sucesso.")
            else: st.warning("Dados não localizados.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos Seleccionados")
        for i, it in enumerate(st.session_state.conteudos_selecionados):
            b_class = "badge-tech" if it['tipo'] == "Tecnologia" else "badge-eng"
            c_txt, c_btn = st.columns([0.96, 0.04])
            with c_txt: st.markdown(f"<div style='background:white; border:1px solid #cbd5e1; padding:15px; border-radius:4px; margin-bottom:8px;'><span class='badge {b_class}'>{it['tipo']}</span> <b>{it['geral']}</b>: {it['especifico']}</div>", unsafe_allow_html=True)
            with c_btn: 
                if st.button("✕", key=f"del_{i}"): st.session_state.conteudos_selecionados.pop(i); st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ IDENTIFICAÇÃO"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Seleccione ao menos um conteúdo da matriz.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("### 03. Detalhamento Pedagógico Estruturado")
    with st.container():
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        st.markdown("<div style='color:#be123c; font-weight:800; font-size:0.7rem; margin-bottom:1.5rem;'>TODOS OS CAMPOS SÃO DE PREENCHIMENTO OBRIGATÓRIO</div>", unsafe_allow_html=True)
        
        obj_esp = st.text_area("OBJECTIVOS ESPECÍFICOS DA AULA", height=100, placeholder="Defina os resultados práticos pretendidos...")
        
        col_x, col_y = st.columns(2)
        with col_x: sit = st.text_area("SITUAÇÃO DIDÁTICA / METODOLOGIA", height=220, placeholder="Passo a passo da aula...")
        with col_y: rec = st.text_area("RECURSOS DIDÁTICOS", height=220, placeholder="Materiais e ferramentas...")
        
        col_w, col_z = st.columns(2)
        with col_w: aval = st.text_area("PROCEDIMENTOS DE AVALIAÇÃO", height=120)
        with col_z: recup = st.text_area("ESTRATÉGIAS DE RECUPERAÇÃO CONTÍNUA", height=120)
        st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C'); pdf.ln(15)
        pdf.set_fill_color(248, 250, 252); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"DOCENTE: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR SELECCIONADA"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for l, v in [("Objectivos Específicos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1); pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Planejar Elite', 0, 1, 'C')
        pdf.cell(0, 5, 'Visto Coordenação: __________________________________', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\nPlaneamento Digital").bold = True
        doc.add_paragraph(f"Docente: {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        doc.add_heading("Matriz Curricular", 3)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento Pedagógico", 3)
        for l, v in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ VOLTAR PARA MATRIZ"): set_step(2); st.rerun()
    if c2.button("FINALIZAR E GERAR DOCUMENTAÇÃO 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]): st.error("Todos os campos de detalhamento são obrigatórios.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_arq = f"Planeamento_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("✅ Documentação gerada com sucesso!"); st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 Word (.docx)", w_file, f"{nome_arq}.docx", use_container_width=True)
            cd2.download_button("📕 PDF (.pdf)", p_file, f"{nome_arq}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:60px; padding:30px; color:#94a3b8; font-size:0.7rem; border-top:1px solid #e2e8f0; letter-spacing:1px;">
        SISTEMA PLANEJAR ELITE • DESENVOLVIDO POR JOSÉ VICTOR SOUZA GALLO<br>
        CEIEF RAFAEL AFFONSO LEITE © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
