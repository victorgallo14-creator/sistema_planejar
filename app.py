import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
import os
import base64

# IMPORTAÇÃO DO CURRÍCULO
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO CRÍTICO: O arquivo 'dados_curriculo.py' não foi encontrado.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF",
    layout="wide",
    page_icon="🔷",
    initial_sidebar_state="expanded"
)

# --- 2. CSS AVANÇADO (ENTERPRISE UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* RESET E FONTE GLOBAL */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b; 
    }
    
    /* FUNDO DA APLICAÇÃO (Cinza Azulado Moderno) */
    .stApp {
        background-color: #f1f5f9;
    }
    
    /* BARRA LATERAL (Dark Mode - Estilo Dashboard) */
    [data-testid="stSidebar"] {
        background-color: #0f172a; /* Navy Blue Profundo */
        border-right: 1px solid #1e293b;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    [data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        color: white !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #334155;
    }
    
    /* CABEÇALHO PRINCIPAL (Card Flutuante) */
    .header-box {
        background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 0.9rem;
        opacity: 0.9;
        font-weight: 300;
        margin-top: 5px;
    }
    .header-logo {
        height: 60px;
        width: auto;
        background: white;
        padding: 8px;
        border-radius: 8px;
    }
    
    /* CARDS DE CONTEÚDO (Brancos com Sombra Suave) */
    .glass-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* ETAPAS (WIZARD) */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        position: relative;
    }
    .step-item {
        flex: 1;
        text-align: center;
        padding: 10px;
        font-weight: 600;
        font-size: 0.9rem;
        color: #94a3b8;
        border-bottom: 3px solid #cbd5e1;
        transition: all 0.3s;
    }
    .step-active {
        color: #1e40af;
        border-bottom: 3px solid #1e40af;
    }
    
    /* BOTÕES (Design Moderno) */
    .stButton > button {
        border-radius: 8px;
        height: 3rem;
        font-weight: 600;
        border: none;
        background-color: white;
        color: #1e293b;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #f8fafc;
        border-color: #cbd5e1;
        transform: translateY(-1px);
    }
    
    /* Botão Primário (Azul) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background: #2563eb;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
    }
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background: #1d4ed8;
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
    }

    /* TAGS */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
    }
    .tag-tech { background: #e0f2fe; color: #0284c7; }
    .tag-eng { background: #fee2e2; color: #dc2626; }
    
    /* ALERTA OBRIGATÓRIO */
    .required-field {
        border-left: 3px solid #dc2626;
        padding-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

# --- CABEÇALHO ---
logo_pref = get_image_base64("logo_prefeitura.png") or get_image_base64("logo_prefeitura.jpg")
logo_esc = get_image_base64("logo_escola.png") or get_image_base64("logo_escola.jpg")

logo_pref_html = f'<img src="{logo_pref}" class="header-logo">' if logo_pref else ''
logo_esc_html = f'<img src="{logo_esc}" class="header-logo">' if logo_esc else ''

st.markdown(f"""
<div class="header-box">
    <div style="display:flex; align-items:center; gap:1.5rem;">
        {logo_pref_html}
        <div>
            <div class="header-title">SISTEMA PLANEJAR</div>
            <div class="header-subtitle">CEIEF Rafael Affonso Leite • Portal do Professor</div>
        </div>
    </div>
    {logo_esc_html}
</div>
""", unsafe_allow_html=True)

# --- GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(s): st.session_state.step = s

# WIZARD DE NAVEGAÇÃO
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f'<div class="step-item {"step-active" if st.session_state.step==1 else ""}">1. Parâmetros</div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="step-item {"step-active" if st.session_state.step==2 else ""}">2. Currículo</div>', unsafe_allow_html=True)
with c3: st.markdown(f'<div class="step-item {"step-active" if st.session_state.step==3 else ""}">3. Emissão</div>', unsafe_allow_html=True)
st.write("")

# --- PASSO 1: PARÂMETROS ---
if st.session_state.step == 1:
    with st.sidebar:
        st.markdown("### 📋 Painel de Controle")
        st.info("Preencha os dados básicos na área principal para desbloquear as próximas etapas.")

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Identificação da Aula")
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Docente Responsável", value=st.session_state.config.get('professor', ''))
            
            anos = list(CURRICULO_DB.keys())
            saved_ano = st.session_state.config.get('ano')
            idx = anos.index(saved_ano) if saved_ano in anos else 0
            ano = st.selectbox("Ano de Escolaridade", anos, index=idx)
            
            # Turmas
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(ano, 3)
            prefix = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
            opts = [f"{prefix}{i}" for i in range(1, max_t + 1)]
            
            saved_turmas = st.session_state.config.get('turmas', [])
            valid_defaults = [t for t in saved_turmas if t in opts]
            turmas = st.multiselect("Turmas (Vínculo)", opts, default=valid_defaults, placeholder="Selecione as turmas...")

        with c2:
            meses = {2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
            saved_mes = st.session_state.config.get('mes')
            idx_mes = list(meses.values()).index(saved_mes) if saved_mes in list(meses.values()) else 0
            mes_nome = st.selectbox("Mês de Referência", list(meses.values()), index=idx_mes)
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.caption("ℹ️ Mês de Fevereiro (Planejamento Mensal)")
            else:
                quinzena = st.radio("Período de Execução", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        col_nav1, col_nav2 = st.columns([3, 1])
        with col_nav2:
            if st.button("Continuar ➔", type="primary", use_container_width=True):
                if not professor or not turmas:
                    st.error("Preenchimento obrigatório pendente.")
                else:
                    if 'ano' in st.session_state.config and st.session_state.config['ano'] != ano:
                        st.session_state.conteudos_selecionados = []
                    st.session_state.config = {
                        'professor': professor, 'ano': ano, 'turmas': turmas, 
                        'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc
                    }
                    set_step(2)
                    st.rerun()

# --- PASSO 2: CURRÍCULO ---
elif st.session_state.step == 2:
    with st.sidebar:
        st.markdown(f"### 📌 {st.session_state.config['ano']}")
        st.caption("Navegue pelas abas abaixo para adicionar conteúdos de Tecnologia e Inglês.")
        
        st.markdown("---")
        st.markdown("**Itens Adicionados:**")
        if st.session_state.conteudos_selecionados:
            for i, item in enumerate(st.session_state.conteudos_selecionados):
                label = "TECH" if item['tipo'] == "Tecnologia" else "ING"
                st.text(f"[{label}] {item['geral']}")
        else:
            st.caption("Nenhum item.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
    op_tec, op_ing = [], []
    termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING']
    
    for k, v in dados.items():
        if v:
            eixo = v[0]['eixo'].upper()
            if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
            else: op_tec.append(k)

    t1, t2 = st.tabs(["Tecnologia", "Inglês"])
    
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Eixo Temático", op_tec, key="t_g")
            itens = dados[g]
            e = c2.selectbox("Habilidade", [i['especifico'] for i in itens], key="t_e")
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div style="background:#f8fafc; padding:15px; border-radius:8px; border-left:4px solid #3b82f6; margin:10px 0;">
                <div style="font-size:0.8rem; color:#64748b; font-weight:700;">OBJETIVO</div>
                <div style="color:#334155;">{sel['objetivo']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar à Lista ➕", key="bt_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Adicionado!", icon="✅")
                st.rerun() # Atualiza sidebar
        else: st.warning("Sem dados.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Tópico", op_ing, key="i_g")
            itens = dados[g]
            e = c2.selectbox("Prática", [i['especifico'] for i in itens], key="i_e")
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div style="background:#fff1f2; padding:15px; border-radius:8px; border-left:4px solid #be123c; margin:10px 0;">
                <div style="font-size:0.8rem; color:#be123c; font-weight:700;">OBJETIVO</div>
                <div style="color:#881337;">{sel['objetivo']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar à Lista ➕", key="bt_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Adicionado!", icon="✅")
                st.rerun()
        else: st.warning("Sem dados.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lista Visual
    if st.session_state.conteudos_selecionados:
        st.markdown("##### Itens Selecionados")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            tag_cls = "tag-tech" if item['tipo'] == "Tecnologia" else "tag-eng"
            c_txt, c_btn = st.columns([0.9, 0.1])
            c_txt.markdown(f"""
            <div style="background:white; border:1px solid #e2e8f0; padding:10px; border-radius:6px; margin-bottom:5px;">
                <span class="status-tag {tag_cls}">{item['tipo']}</span> 
                <span style="font-weight:600; margin-left:8px;">{item['geral']}</span>
                <div style="font-size:0.9rem; margin-top:4px; color:#475569;">{item['especifico']}</div>
            </div>
            """, unsafe_allow_html=True)
            if c_btn.button("✕", key=f"del_{i}"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    if c1.button("⬅️ Voltar"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes ➡️", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Adicione itens.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    with st.sidebar:
        st.markdown("### 📄 Revisão Final")
        st.info("Preencha todos os campos obrigatórios marcados em vermelho.")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### Detalhamento Pedagógico")
    
    # Campo Obrigatório com destaque visual
    st.markdown("""<div class="required-field" style="margin-bottom:5px; font-weight:600; font-size:0.9rem;">Objetivos Específicos da Aula</div>""", unsafe_allow_html=True)
    obj_esp = st.text_area("Objetivos Específicos", height=100, label_visibility="collapsed", placeholder="Descreva os objetivos pontuais desta aula...", value=st.session_state.config.get('obj_esp', ''))
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="required-field" style="margin-bottom:5px; font-weight:600; font-size:0.9rem;">Situação Didática</div>""", unsafe_allow_html=True)
        sit = st.text_area("Situação Didática", height=150, label_visibility="collapsed", placeholder="Metodologia...", value=st.session_state.config.get('sit', ''))
    with c2:
        st.markdown("""<div class="required-field" style="margin-bottom:5px; font-weight:600; font-size:0.9rem;">Recursos Didáticos</div>""", unsafe_allow_html=True)
        rec = st.text_area("Recursos", height=150, label_visibility="collapsed", placeholder="Materiais...", value=st.session_state.config.get('rec', ''))
    
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""<div class="required-field" style="margin-bottom:5px; font-weight:600; font-size:0.9rem;">Avaliação</div>""", unsafe_allow_html=True)
        aval = st.text_area("Avaliação", height=100, label_visibility="collapsed", value=st.session_state.config.get('aval', ''))
    with c4:
        st.markdown("""<div class="required-field" style="margin-bottom:5px; font-weight:600; font-size:0.9rem;">Recuperação Contínua</div>""", unsafe_allow_html=True)
        recup = st.text_area("Recuperação", height=100, label_visibility="collapsed", value=st.session_state.config.get('recup', ''))
    
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    # --- FUNÇÕES DE GERAÇÃO (PDF/WORD) ---
    def clean(txt): return txt.encode('latin-1', 'replace').decode('latin-1') if txt else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        
        # Logos
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        elif os.path.exists("logo_prefeitura.jpg"): pdf.image("logo_prefeitura.jpg", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        elif os.path.exists("logo_escola.jpg"): pdf.image("logo_escola.jpg", 175, 8, 25)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C'); pdf.ln(15)

        # Cabeçalho Cinza
        pdf.set_fill_color(241, 245, 249); pdf.set_draw_color(226, 232, 240)
        pdf.rect(10, pdf.get_y(), 190, 20, 'F')
        pdf.set_xy(12, pdf.get_y()+2)
        pdf.set_font("Arial", 'B', 9); pdf.cell(20, 5, clean("Período:"), 0, 0); pdf.set_font("Arial", '', 9); pdf.cell(0, 5, clean(f"{dados['periodo']} ({dados['trimestre']})"), 0, 1)
        pdf.set_x(12); pdf.set_font("Arial", 'B', 9); pdf.cell(20, 5, clean("Professor:"), 0, 0); pdf.set_font("Arial", '', 9); pdf.cell(0, 5, clean(dados['professor']), 0, 1)
        pdf.set_x(12); pdf.set_font("Arial", 'B', 9); pdf.cell(20, 5, clean("Turmas:"), 0, 0); pdf.set_font("Arial", '', 9); pdf.cell(0, 5, clean(f"{dados['ano']} - {', '.join(dados['turmas'])}"), 0, 1)
        pdf.ln(5)

        # Matriz
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for item in conteudos:
            pdf.set_fill_color(248, 250, 252)
            pdf.multi_cell(0, 5, clean(f"[{item['tipo']}] {item['geral']}"), 1, 'L', True)
            pdf.multi_cell(0, 5, clean(f"Hab: {item['especifico']}"), 1, 'L')
            pdf.multi_cell(0, 5, clean(f"Obj: {item['objetivo']}"), 1, 'L')
            pdf.ln(1)

        # Detalhamento
        pdf.ln(2)
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Objetivos Específicos:"), 0, 1); 
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['obj_esp'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Situação Didática:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['sit'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recursos:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['rec'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Avaliação:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['aval'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recuperação:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recup'])); pdf.ln(3)

        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, f'Emitido em: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Sistema Planejar', 0, 1, 'C')
        pdf.cell(0, 5, 'Visto Coordenação: _______________________________', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document()
        for s in doc.sections: s.top_margin = Cm(1); s.bottom_margin = Cm(1.5); s.left_margin = Cm(1.5); s.right_margin = Cm(1.5)
        style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        
        t = doc.add_table(rows=1, cols=3); t.autofit = False
        c1 = t.cell(0,0); c1.width = Cm(2.5)
        if os.path.exists("logo_prefeitura.png"): 
            try: c1.paragraphs[0].add_run().add_picture("logo_prefeitura.png", width=Cm(2.0))
            except: pass
        elif os.path.exists("logo_prefeitura.jpg"):
             try: c1.paragraphs[0].add_run().add_picture("logo_prefeitura.jpg", width=Cm(2.0))
             except: pass
        
        c2 = t.cell(0,1); c2.width = Cm(11.0); p = c2.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\n").bold = True; p.add_run("Planejamento de Linguagens e Tecnologias")
        
        c3 = t.cell(0,2); c3.width = Cm(2.5); p3 = c3.paragraphs[0]; p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if os.path.exists("logo_escola.png"): 
            try: p3.add_run().add_picture("logo_escola.png", width=Cm(2.0))
            except: pass
        elif os.path.exists("logo_escola.jpg"):
             try: p3.add_run().add_picture("logo_escola.jpg", width=Cm(2.0))
             except: pass

        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run(f"Período: {dados['periodo']}\n").bold = True
        p.add_run(f"Professor(a): {dados['professor']}\n")
        p.add_run(f"Ano: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}")
        doc.add_paragraph("-" * 90)

        if conteudos:
            doc.add_heading("Matriz Curricular", 3)
            tb = doc.add_table(rows=1, cols=3); tb.style = 'Table Grid'
            tb.rows[0].cells[0].text = "Eixo"; tb.rows[0].cells[1].text = "Conteúdo"; tb.rows[0].cells[2].text = "Objetivo"
            for item in conteudos:
                r = tb.add_row().cells
                r[0].text = f"{item['eixo']}\n({item['geral']})"
                r[1].text = item['especifico']
                r[2].text = item['objetivo']

        doc.add_paragraph(); doc.add_heading("Detalhamento Pedagógico", 3)
        
        p = doc.add_paragraph(); p.add_run("Objetivos Específicos:\n").bold = True; p.add_run(dados['obj_esp'])
        p = doc.add_paragraph(); p.add_run("\nSituação Didática:\n").bold = True; p.add_run(dados['sit'])
        p = doc.add_paragraph(); p.add_run("\nRecursos:\n").bold = True; p.add_run(dados['rec'])
        p = doc.add_paragraph(); p.add_run("\nAvaliação:\n").bold = True; p.add_run(dados['aval'])
        p = doc.add_paragraph(); p.add_run("\nRecuperação:\n").bold = True; p.add_run(dados['recup'])

        f = BytesIO(); doc.save(f); f.seek(0); return f

    # AÇÃO DE DOWNLOAD
    c_b1, c_b2 = st.columns(2)
    if c_b1.button("⬅️ Voltar"): set_step(2); st.rerun()
    if c_b2.button("Emitir Documentos Oficiais (PDF + Word)", type="primary", use_container_width=True):
        if not obj_esp or not sit or not rec or not aval or not recup:
            st.error("Todos os campos de detalhamento são obrigatórios.")
        else:
            f_data = st.session_state.config
            word_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            pdf_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            
            nome = f"Plan_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            
            st.success("✅ Documentos emitidos com sucesso!")
            
            c_d1, c_d2 = st.columns(2)
            c_d1.download_button("📄 Baixar Word (.docx)", word_file, f"{nome}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            c_d2.download_button("📕 Baixar PDF (.pdf)", pdf_file, f"{nome}.pdf", "application/pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema de uso exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
