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

# IMPORTAÇÃO DO CURRÍCULO
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO CRÍTICO: O ficheiro 'dados_curriculo.py' não foi encontrado.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# --- 2. CSS AVANÇADO (ENTERPRISE UI REVISADO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* RESET E FONTE GLOBAL */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b; 
    }
    
    /* FUNDO DA APLICAÇÃO (Cinza Suave para contraste) */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* BARRA LATERAL (Dark Mode Profissional) */
    [data-testid="stSidebar"] {
        background-color: #111827; /* Azul Marinho Quase Preto */
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] * {
        color: #f9fafb !important;
    }
    [data-testid="stSidebar"] .stTextInput input, [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #1f2937;
        border: 1px solid #374151;
        color: white !important;
    }
    
    /* CABEÇALHO REESTRUTURADO */
    .header-wrapper {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* CARDS DE CONTEÚDO (Branco Puro sobre fundo Cinza) */
    .glass-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e5e7eb;
        margin-bottom: 1.5rem;
    }
    
    /* ETAPAS (WIZARD) */
    .step-item {
        flex: 1;
        text-align: center;
        padding: 12px;
        font-weight: 700;
        font-size: 0.85rem;
        color: #64748b;
        border-bottom: 3px solid #e5e7eb;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .step-active {
        color: #2563eb;
        border-bottom: 3px solid #2563eb;
    }
    
    /* BOTÕES */
    .stButton > button {
        border-radius: 8px;
        height: 3.2rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    /* TAGS */
    .tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .tag-tech { background: #dbeafe; color: #1e40af; }
    .tag-eng { background: #fee2e2; color: #991b1b; }
    
    /* ALERTA OBRIGATÓRIO */
    .required-label {
        color: #e11d48;
        font-size: 0.75rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: block;
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

# --- 3. CABEÇALHO (REVISADO PARA GARANTIR VISIBILIDADE) ---
logo_pref_b64 = get_image_base64("logo_prefeitura.png") or get_image_base64("logo_prefeitura.jpg")
logo_esc_b64 = get_image_base64("logo_escola.png") or get_image_base64("logo_escola.jpg")

# Usamos um container com layout flexível via HTML inline para o cabeçalho ser "imortal"
st.markdown(f"""
<div style="background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); 
            padding: 2rem; border-radius: 12px; color: white; margin-bottom: 2rem; 
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);">
    <div style="display: flex; align-items: center; gap: 1.5rem;">
        {f'<img src="{logo_pref_b64}" style="height:65px; background:white; padding:5px; border-radius:8px;">' if logo_pref_b64 else '<div style="font-size:2rem;"> </div>'}
        <div style="text-align: left;">
            <h1 style="margin:0; font-size: 1.8rem; font-weight: 800; color: white; line-height:1;">SISTEMA PLANEJAR</h1>
            <p style="margin:5px 0 0 0; font-size: 0.95rem; opacity: 0.85; font-weight: 400;">CEIEF Rafael Affonso Leite • Gestão Pedagógica Digital</p>
        </div>
    </div>
    {f'<img src="{logo_esc_b64}" style="height:65px; background:white; padding:5px; border-radius:8px;">' if logo_esc_b64 else '<div style="font-size:2rem;">🏫</div>'}
</div>
""", unsafe_allow_html=True)

# --- GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(s): st.session_state.step = s

# WIZARD DE NAVEGAÇÃO
cols_step = st.columns(3)
with cols_step[0]: st.markdown(f'<div class="step-item {"step-active" if st.session_state.step==1 else ""}">1. Parâmetros</div>', unsafe_allow_html=True)
with cols_step[1]: st.markdown(f'<div class="step-item {"step-active" if st.session_state.step==2 else ""}">2. Matriz Curricular</div>', unsafe_allow_html=True)
with cols_step[2]: st.markdown(f'<div class="step-item {"step-active" if st.session_state.step==3 else ""}">3. Emissão Final</div>', unsafe_allow_html=True)
st.write("")

# --- PASSO 1: PARÂMETROS ---
if st.session_state.step == 1:
    with st.sidebar:
        st.markdown("### ℹ️ Ajuda")
        st.write("Defina o professor, o ano e as turmas para as quais este planeamento será válido.")

    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Identificação do Planeamento")
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Professor(a) Responsável", value=st.session_state.config.get('professor', ''), placeholder="Nome completo...")
            
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
            turmas = st.multiselect("Turmas Seleccionadas", opts, default=valid_defaults, placeholder="Escolha uma ou mais turmas...")

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
                st.info("Planeamento Mensal (Fevereiro)")
            else:
                quinzena = st.radio("Período Quinzenal", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Avançar para Conteúdos ➔", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("Por favor, preencha o nome do professor e seleccione as turmas.")
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
        st.markdown(f"### 📋 Matriz: {st.session_state.config['ano']}")
        st.write("Adicione os objectivos da matriz oficial utilizando as abas ao lado.")
        st.markdown("---")
        if st.session_state.conteudos_selecionados:
            st.markdown("**Adicionados:**")
            for item in st.session_state.conteudos_selecionados:
                st.caption(f"• {item['geral']}")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
    op_tec, op_ing = [], []
    termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING']
    
    for k, v in dados.items():
        if v:
            eixo = v[0]['eixo'].upper()
            if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
            else: op_tec.append(k)

    t1, t2 = st.tabs(["💻 Tecnologia & Cultura Digital", "🇬🇧 Língua Inglesa"])
    
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Eixo Temático", op_tec, key="t_g")
            itens = dados[g]
            e = c2.selectbox("Habilidade Específica", [i['especifico'] for i in itens], key="t_e")
            sel = next(i for i in itens if i['especifico'] == e)
            st.info(f"**Objectivo:** {sel['objetivo']}")
            if st.button("Adicionar à Lista ➕", key="bt_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Adicionado com sucesso!", icon="✅")
        else: st.warning("Sem conteúdos de tecnologia disponíveis.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Tópico Curricular", op_ing, key="i_g")
            itens = dados[g]
            e = c2.selectbox("Prática de Linguagem", [i['especifico'] for i in itens], key="i_e")
            sel = next(i for i in itens if i['especifico'] == e)
            st.error(f"**Objectivo:** {sel['objetivo']}")
            if st.button("Adicionar à Lista ➕", key="bt_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Adicionado com sucesso!", icon="✅")
        else: st.warning("Sem conteúdos de inglês disponíveis.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.conteudos_selecionados:
        st.markdown("##### Matriz Seleccionada")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            tag_cls = "tag-tech" if item['tipo'] == "Tecnologia" else "tag-eng"
            c_txt, c_btn = st.columns([0.92, 0.08])
            c_txt.markdown(f"""
            <div style="background:white; border:1px solid #e5e7eb; padding:12px; border-radius:8px; margin-bottom:8px;">
                <span class="tag {tag_cls}">{item['tipo']}</span> 
                <span style="font-weight:700; margin-left:10px;">{item['geral']}</span>
                <div style="font-size:0.85rem; color:#475569; margin-top:5px;">{item['especifico']}</div>
            </div>
            """, unsafe_allow_html=True)
            if c_btn.button("✕", key=f"del_{i}"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados: st.error("Seleccione pelo menos um item da matriz.")
        else: set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### Desenvolvimento Pedagógico")
        
        st.markdown('<span class="required-label">OBJECTIVOS ESPECÍFICOS DA AULA</span>', unsafe_allow_html=True)
        obj_esp = st.text_area("obj_label", height=100, label_visibility="collapsed", placeholder="Quais os objectivos pontuais desta aula?", value=st.session_state.config.get('obj_esp', ''))
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<span class="required-label">SITUAÇÃO DIDÁTICA / METODOLOGIA</span>', unsafe_allow_html=True)
            sit = st.text_area("sit_label", height=180, label_visibility="collapsed", placeholder="Passo a passo da actividade...", value=st.session_state.config.get('sit', ''))
        with c2:
            st.markdown('<span class="required-label">RECURSOS DIDÁTICOS</span>', unsafe_allow_html=True)
            rec = st.text_area("rec_label", height=180, label_visibility="collapsed", placeholder="Computadores, materiais maker, etc...", value=st.session_state.config.get('rec', ''))
        
        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<span class="required-label">PROCEDIMENTOS DE AVALIAÇÃO</span>', unsafe_allow_html=True)
            aval = st.text_area("aval_label", height=100, label_visibility="collapsed", value=st.session_state.config.get('aval', ''))
        with c4:
            st.markdown('<span class="required-label">RECUPERAÇÃO CONTÍNUA</span>', unsafe_allow_html=True)
            recup = st.text_area("recup_label", height=100, label_visibility="collapsed", value=st.session_state.config.get('recup', ''))
    st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    # --- GERAÇÃO ---
    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C'); pdf.ln(15)
        pdf.set_fill_color(240, 245, 255); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PROFESSOR: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 0, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR SELECCIONADA"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos:
            pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO"), 0, 1)
        for label, val in [("Obj. Específicos", dados['obj_esp']), ("Situação Didática", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(label + ":"), 0, 1)
            pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(val)); pdf.ln(2)
        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f'Emitido em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\nPlaneamento de Linguagens e Tecnologias").bold = True
        doc.add_paragraph(f"Professor: {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        if conteudos:
            doc.add_heading("Conteúdos", 3)
            for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento", 3)
        for label, val in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(label + ": ").bold = True; p.add_run(val)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c_b1, c_b2 = st.columns(2)
    if c_b1.button("⬅ Voltar"): set_step(2); st.rerun()
    if c_b2.button("Emitir Documentos (PDF + Word)", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]):
            st.error("Todos os campos de detalhamento são obrigatórios.")
        else:
            f_data = st.session_state.config
            word_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            pdf_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome = f"Planeamento_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("Documentos prontos para download!")
            c_d1, c_d2 = st.columns(2)
            c_d1.download_button("📄 Word (.docx)", word_file, f"{nome}.docx", use_container_width=True)
            c_d2.download_button("📕 PDF (.pdf)", pdf_file, f"{nome}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema de uso exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)

