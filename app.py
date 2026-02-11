import streamlit as st
from docx import Document
from docx.shared import Pt, Cm, RGBColor
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
    page_title="Planejar Elite | Dashboard",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="expanded"
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

# --- 3. CSS CUSTOMIZADO (PADRONIZAÇÃO E RESPONSIVIDADE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* RESET GLOBAL */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #1e293b;
    }
    
    .stApp {
        background-color: #f4f7fa;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* CONTAINER PADRONIZADO (CARDS) */
    .dashboard-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
        margin-bottom: 1.5rem;
        width: 100%;
    }
    
    /* INPUTS PADRONIZADOS */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #f8fafc !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 12px !important;
        padding: 12px !important;
        font-weight: 500 !important;
        color: #1e293b !important;
        min-height: 45px;
    }
    
    /* BOTÕES PADRONIZADOS */
    .stButton > button {
        border-radius: 12px;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
        width: 100%;
    }

    /* ACENTOS DE COR */
    .accent-purple { border-top: 6px solid #8b5cf6; }
    .accent-blue { border-top: 6px solid #3b82f6; }
    .accent-teal { border-top: 6px solid #14b8a6; }
    .accent-red { border-top: 6px solid #f43f5e; }

    /* RESPONSIVIDADE PARA O HEADER */
    .top-bar {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
        gap: 15px;
    }

    @media (max-width: 768px) {
        .top-bar {
            flex-direction: column;
            text-align: center;
        }
        .status-container {
            display: flex;
            flex-direction: column;
            gap: 5px;
            width: 100%;
        }
        .status-step {
            margin-right: 0 !important;
            width: 100%;
        }
    }

    /* STATUS STEPS */
    .status-step {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 800;
        background: #e2e8f0;
        color: #64748b;
        margin-right: 5px;
        text-align: center;
    }
    .status-active {
        background: #6366f1;
        color: white;
    }

    /* LABELS */
    label {
        font-weight: 700 !important;
        color: #64748b !important;
        font-size: 0.8rem !important;
        margin-bottom: 8px !important;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER DO APLICATIVO ---
def render_header():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown(f"""
        <div class="top-bar">
            <div style="display:flex; align-items:center; gap:15px; flex-wrap: wrap;">
                <div style="background:#6366f1; width:45px; height:45px; border-radius:10px; display:flex; align-items:center; justify-content:center; color:white; font-weight:800; font-size:1.2rem;">P</div>
                <div>
                    <h2 style="margin:0; font-size:1.3rem; letter-spacing:-1px;">PLANEJAR ELITE</h2>
                    <p style="margin:0; font-size:0.75rem; color:#64748b; font-weight:600;">CEIEF RAFAEL AFFONSO LEITE • GESTÃO</p>
                </div>
            </div>
            <div class="status-container">
                <span class="status-step {'status-active' if st.session_state.step==1 else ''}">01 ID</span>
                <span class="status-step {'status-active' if st.session_state.step==2 else ''}">02 MATRIZ</span>
                <span class="status-step {'status-active' if st.session_state.step==3 else ''}">03 DOC</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        logo_esc = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
        if os.path.exists(logo_esc):
            st.image(logo_esc, width=70)

render_header()

# --- PASSO 1: CONFIGURAÇÃO ---
if st.session_state.step == 1:
    with st.sidebar:
        st.markdown("## DASHBOARD")
        st.write("Identifique os parâmetros do planejamento para iniciar.")
        st.markdown("---")
        st.caption("v6.0 Responsive Enterprise")

    st.markdown('<div class="dashboard-card accent-purple">', unsafe_allow_html=True)
    st.markdown("### 🛠️ Identificação da Unidade")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        professor = st.text_input("DOCENTE RESPONSÁVEL", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
        anos = list(CURRICULO_DB.keys())
        saved_ano = st.session_state.config.get('ano')
        idx_ano = anos.index(saved_ano) if saved_ano in anos else 0
        ano = st.selectbox("ANO DE ESCOLARIDADE", anos, index=idx_ano)
        
        qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
        max_t = qtd_turmas.get(ano, 3)
        opts = [f"{ano} - Turma {i}" if "Maternal" in ano or "Etapa" in ano else f"{ano} {i}" for i in range(1, max_t + 1)]
        valid_defaults = [t for t in st.session_state.config.get('turmas', []) if t in opts]
        turmas = st.multiselect("TURMAS VINCULADAS", opts, default=valid_defaults)

    with col2:
        meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
        mes_nome = st.selectbox("MÊS DE REFERÊNCIA", list(meses.values()))
        mes_num = [k for k, v in meses.items() if v == mes_nome][0]
        
        if mes_num == 2:
            periodo_texto = "01/02/2026 a 28/02/2026"
            trimestre_doc = "1º Trimestre"
            st.info("Regime Mensal (Fevereiro)")
        else:
            quinzena = st.radio("QUINZENA", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
            tri = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"
            ultimo = calendar.monthrange(2026, mes_num)[1]
            periodo_texto = f"01/{mes_num:02d}/2026 a 15/{mes_num:02d}/2026" if "1ª" in quinzena else f"16/{mes_num:02d}/2026 a {ultimo}/{mes_num:02d}/2026"
            trimestre_doc = tri

    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("Configurar Matriz Curricular ➔", type="secondary"):
        if not professor or not turmas:
            st.error("ERRO: Preencha o nome do docente e as turmas.")
        else:
            if st.session_state.config.get('ano') != ano: st.session_state.conteudos_selecionados = []
            st.session_state.config = {'professor': professor, 'ano': ano, 'turmas': turmas, 'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc}
            set_step(2); st.rerun()

# --- PASSO 2: MATRIZ ---
elif st.session_state.step == 2:
    with st.sidebar:
        st.markdown("## CURRÍCULO")
        st.info(f"Matriz: {st.session_state.config['ano']}")

    st.markdown('<div class="dashboard-card accent-blue">', unsafe_allow_html=True)
    st.markdown(f"### 📖 Matriz Curricular: {st.session_state.config['ano']}")
    
    dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
    op_tec, op_ing = [], []
    termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
    for k, v in dados.items():
        if v:
            eixo = v[0]['eixo'].upper()
            if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
            else: op_tec.append(k)

    t1, t2 = st.tabs(["TECNOLOGIA", "INGLÊS"])
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("EIXO CURRICULAR", op_tec, key="t_g")
            e = c2.selectbox("HABILIDADE", [i['especifico'] for i in dados[g]], key="t_e")
            sel = next(i for i in dados[g] if i['especifico'] == e)
            st.markdown(f"<div style='background:#f1f5f9; padding:1.5rem; border-radius:12px; border:1px solid #e2e8f0; margin-top:10px;'><b>OBJETIVO DE APRENDIZAGEM:</b><br>{sel['objetivo']}</div>", unsafe_allow_html=True)
            if st.button("Vincular Conteúdo ➕", key="bt_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("✅ Adicionado!")
        else: st.warning("Sem dados.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("TÓPICO", op_ing, key="i_g")
            e = c2.selectbox("PRÁTICA", [i['especifico'] for i in dados[g]], key="i_e")
            sel = next(i for i in dados[g] if i['especifico'] == e)
            st.markdown(f"<div style='background:#fdf2f2; padding:1.5rem; border-radius:12px; border:1px solid #fecdd3; margin-top:10px;'><b>OBJETIVO DE APRENDIZAGEM:</b><br>{sel['objetivo']}</div>", unsafe_allow_html=True)
            if st.button("Vincular Conteúdo ➕", key="bt_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("✅ Adicionado!")
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos em Planejamento")
        for i, it in enumerate(st.session_state.conteudos_selecionados):
            col_t, col_b = st.columns([0.9, 0.1])
            with col_t: st.markdown(f"<div style='background:white; border:1px solid #e2e8f0; padding:1rem; border-radius:12px; margin-bottom:10px;'><b>[{it['tipo']}]</b> {it['geral']}: {it['especifico']}</div>", unsafe_allow_html=True)
            with col_b: 
                if st.button("✕", key=f"del_{i}"): st.session_state.conteudos_selecionados.pop(i); st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ VOLTAR"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes ➔", type="secondary"):
        if not st.session_state.conteudos_selecionados: st.error("Erro: Selecione ao menos um conteúdo.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    with st.sidebar:
        st.markdown("## EMISSÃO")
        st.write("Finalize o detalhamento para gerar os arquivos.")

    st.markdown('<div class="dashboard-card accent-teal">', unsafe_allow_html=True)
    st.markdown("### ✍️ Detalhamento Didático (Obrigatório)")
    
    obj_esp = st.text_area("OBJETIVOS ESPECÍFICOS DA AULA", height=100, placeholder="Descreva os resultados práticos desejados...")
    
    col_a, col_b = st.columns(2)
    with col_a: sit = st.text_area("SITUAÇÃO DIDÁTICA / METODOLOGIA", height=200, placeholder="Descreva o passo a passo da atividade...")
    with col_b: rec = st.text_area("RECURSOS DIDÁTICOS", height=200, placeholder="Ferramentas digitais, materiais, etc...")
    
    col_c, col_d = st.columns(2)
    with col_c: aval = st.text_area("AVALIAÇÃO", height=100)
    with col_d: recup = st.text_area("RECUPERAÇÃO CONTÍNUA", height=100)
    st.markdown("</div>", unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C'); pdf.ln(10)
        pdf.set_fill_color(245, 247, 250); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 7, clean(f"PROFESSOR: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for l, v in [("Objetivos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1); pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
        pdf.set_y(-20); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Sistema Planejar Elite', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("CEIEF RAFAEL AFFONSO LEITE\nPlanejamento Digital Profissional").bold = True
        doc.add_paragraph(f"Professor(a): {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        doc.add_heading("Matriz Curricular", 2)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento Pedagógico", 2)
        for l, v in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ VOLTAR PARA MATRIZ"): set_step(2); st.rerun()
    if c2.button("GERAR PLANEJAMENTO FINAL 🚀", type="primary"):
        if not all([obj_esp, sit, rec, aval, recup]): st.error("ERRO: Todos os campos são obrigatórios.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_arq = f"Planejamento_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("✅ Planejamento emitido!"); st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 WORD (.DOCX)", w_file, f"{nome_arq}.docx")
            cd2.download_button("📕 PDF (.PDF)", p_file, f"{nome_arq}.pdf")

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:60px; padding:30px; color:#94a3b8; font-size:0.75rem; border-top:1px solid #e2e8f0;">
        PLANEJAR ELITE • DASHBOARD SYSTEM • DESENVOLVIDO POR JOSÉ VICTOR SOUZA GALLO<br>
        CEIEF RAFAEL AFFONSO LEITE © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
