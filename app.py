import streamlit as st
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
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
    initial_sidebar_state="expanded"
)

# --- 2. GESTÃO DE ESTADO (INICIALIZAÇÃO ANTECIPADA) ---
if 'step' not in st.session_state: 
    st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: 
    st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: 
    st.session_state.config = {}

def set_step(s): 
    st.session_state.step = s

# --- 3. ESTILIZAÇÃO CSS (PREMIUM UI - OUTFIT FONT) ---
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

    /* BARRA LATERAL ENTERPRISE */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #f1f5f9 !important;
    }

    /* HEADER PREMIUM (O QUE VOCÊ GOSTOU) */
    .premium-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-text h1 {
        margin: 0;
        font-weight: 800;
        font-size: 2.5rem;
        color: white;
        letter-spacing: -1px;
    }
    .header-text p {
        margin: 5px 0 0 0;
        font-weight: 300;
        opacity: 0.9;
        font-size: 1.1rem;
    }

    /* CARDS MODERNOS */
    .card-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    /* INPUTS PADRONIZADOS E VISÍVEIS */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }

    /* BOTÕES ELITE */
    .stButton > button {
        border-radius: 12px;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    /* Botão Primário (Avançar/Gerar) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: #1e3a8a !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.2);
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 20px -5px rgba(30, 58, 138, 0.3);
    }

    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #1e3a8a, #3b82f6);
    }

    /* TAGS */
    .status-tag {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 10px;
    }
    .tag-tech { background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .tag-eng { background-color: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }

    /* LABELS */
    label {
        font-weight: 700 !important;
        color: #334155 !important;
        font-size: 0.85rem !important;
        margin-bottom: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE APOIO ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as img_file:
            return f"data:image/png;base64,{base64.b64encode(img_file.read()).decode()}"
    return None

# --- 4. HEADER PREMIUM COM LOGOS ---
logo_pref_b64 = get_image_base64("logo_prefeitura.png") or get_image_base64("logo_prefeitura.jpg")
logo_esc_b64 = get_image_base64("logo_escola.png") or get_image_base64("logo_escola.jpg")

st.markdown(f"""
<div class="premium-header">
    <div style="display: flex; align-items: center; gap: 2rem;">
        {f'<img src="{logo_pref_b64}" style="height:75px; background:white; padding:8px; border-radius:12px;">' if logo_pref_b64 else ''}
        <div class="header-text">
            <h1>Sistema Planejar</h1>
            <p>Gestão Pedagógica • CEIEF Rafael Affonso Leite</p>
        </div>
    </div>
    {f'<img src="{logo_esc_b64}" style="height:75px; background:white; padding:8px; border-radius:12px;">' if logo_esc_b64 else '<div style="font-size:3rem;">🏫</div>'}
</div>
""", unsafe_allow_html=True)

# --- FLUXO DE NAVEGAÇÃO ---
progresso = {1: 33, 2: 66, 3: 100}
st.progress(progresso[st.session_state.step])
st.write("")

# --- PASSO 1: CONFIGURAÇÃO ---
if st.session_state.step == 1:
    with st.sidebar:
        st.markdown("### 🛠️ CONFIGURAÇÕES")
        st.write("Defina os parâmetros iniciais do seu planejamento quinzinal ou mensal.")

    st.markdown('<div class="card-container">', unsafe_allow_html=True)
    st.markdown("### 📋 Identificação da Aula")
    
    c1, c2 = st.columns(2)
    with c1:
        professor = st.text_input("PROFESSOR(A) RESPONSÁVEL", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
        
        anos = list(CURRICULO_DB.keys())
        saved_ano = st.session_state.config.get('ano')
        idx_ano = anos.index(saved_ano) if saved_ano in anos else 0
        ano = st.selectbox("ANO DE ESCOLARIDADE", anos, index=idx_ano)
        
        # Turmas
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
            periodo_texto = "01/02/2026 a 28/02/2026"
            trimestre_doc = "1º Trimestre"
            st.info("Planejamento Mensal (Fevereiro)")
        else:
            quinzena = st.radio("PERÍODO", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
            tri = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"
            ultimo = calendar.monthrange(2026, mes_num)[1]
            periodo_texto = f"01/{mes_num:02d}/2026 a 15/{mes_num:02d}/2026" if "1ª" in quinzena else f"16/{mes_num:02d}/2026 a {ultimo}/{mes_num:02d}/2026"
            trimestre_doc = tri
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Avançar para Matriz Curricular ➔", type="primary", use_container_width=True):
        if not professor or not turmas:
            st.error("ERRO: O preenchimento do docente e das turmas é obrigatório.")
        else:
            if st.session_state.config.get('ano') != ano: 
                st.session_state.conteudos_selecionados = []
            st.session_state.config = {'professor': professor, 'ano': ano, 'turmas': turmas, 'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc}
            set_step(2); st.rerun()

# --- PASSO 2: MATRIZ ---
elif st.session_state.step == 2:
    st.markdown(f"### 📖 Matriz Curricular: **{st.session_state.config['ano']}**")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec, op_ing = [], []
        termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
        for k, v in dados.items():
            if v:
                eixo = v[0]['eixo'].upper()
                if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
                else: op_tec.append(k)

        t1, t2 = st.tabs(["💻 Tecnologia & Cultura Digital", "🇬🇧 Língua Inglesa"])
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("EIXO CURRICULAR", op_tec, key="t_g")
                e = c2.selectbox("HABILIDADE", [i['especifico'] for i in dados[g]], key="t_e")
                sel = next(i for i in dados[g] if i['especifico'] == e)
                st.markdown(f"<div style='background:#f1f5f9; padding:1.5rem; border-radius:12px; border:1px solid #cbd5e1; margin-top:10px;'><span class='status-tag tag-tech'>Objetivo de Aprendizagem</span><br><b>{sel['objetivo']}</b></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Lista ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Adicionado!")
            else: st.warning("Sem dados.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("TÓPICO", op_ing, key="i_g")
                e = c2.selectbox("PRÁTICA", [i['especifico'] for i in dados[g]], key="i_e")
                sel = next(i for i in dados[g] if i['especifico'] == e)
                st.markdown(f"<div style='background:#fef2f2; padding:1.5rem; border-radius:12px; border:1px solid #fecdd3; margin-top:10px;'><span class='status-tag tag-eng'>Objetivo de Aprendizagem</span><br><b>{sel['objetivo']}</b></div>", unsafe_allow_html=True)
                if st.button("Adicionar à Lista ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Adicionado!")
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos Selecionados")
        for i, it in enumerate(st.session_state.conteudos_selecionados):
            col_t, col_b = st.columns([0.95, 0.05])
            with col_t: st.markdown(f"<div style='background:white; border:1px solid #e2e8f0; padding:1rem; border-radius:12px; margin-bottom:10px;'><b>[{it['tipo']}]</b> {it['geral']}: {it['especifico']}</div>", unsafe_allow_html=True)
            with col_b: 
                if st.button("✕", key=f"del_{i}"): st.session_state.conteudos_selecionados.pop(i); st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Seleccione ao menos um conteúdo.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("### ✍️ Detalhamento Pedagógico")
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        st.markdown("<div style='color:#be123c; font-weight:800; font-size:0.75rem; margin-bottom:1rem;'>CAMPOS OBRIGATÓRIOS PARA EMISSÃO</div>", unsafe_allow_html=True)
        
        obj_esp = st.text_area("OBJETIVOS ESPECÍFICOS DA AULA", height=100, placeholder="Descreva os resultados práticos desejados...", value=st.session_state.config.get('obj_esp', ''))
        
        c1, c2 = st.columns(2)
        with c1: sit = st.text_area("SITUAÇÃO DIDÁTICA / METODOLOGIA", height=200, placeholder="Passo a passo...", value=st.session_state.config.get('sit', ''))
        with c2: rec = st.text_area("RECURSOS DIDÁTICOS", height=200, placeholder="Materiais...", value=st.session_state.config.get('rec', ''))
        
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
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planejamento Pedagógico Digital', 0, 1, 'C'); pdf.ln(10)
        pdf.set_fill_color(245, 247, 250); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 7, clean(f"DOCENTE: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for l, v in [("Objetivos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1); pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
        pdf.set_y(-20); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 10, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Sistema Planejar', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("CEIEF RAFAEL AFFONSO LEITE\nPlanejamento de Linguagens e Tecnologias").bold = True
        doc.add_paragraph(f"Docente: {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        doc.add_heading("Matriz Curricular", 2)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento Pedagógico", 2)
        for l, v in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ Matriz"): set_step(2); st.rerun()
    if c2.button("GERAR PLANEJAMENTO FINAL 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]): 
            st.error("Erro: Preencha todos os campos do detalhamento pedagógico.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_arq = f"Planeamento_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("✅ Documentação gerada!"); st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 Baixar WORD", w_file, f"{nome_arq}.docx", use_container_width=True)
            cd2.download_button("📕 Baixar PDF", p_file, f"{nome_arq}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:60px; padding:30px; color:#94a3b8; font-size:0.8rem; border-top:1px solid #e2e8f0;">
        <b>SISTEMA PLANEJAR ELITE</b><br>
        Desenvolvido por José Victor Souza Gallo • CEIEF Rafael Affonso Leite © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
