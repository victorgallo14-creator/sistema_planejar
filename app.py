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

# --- 2. CSS DE ALTA PERFORMANCE VISUAL (DESIGN PREMIUM) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    /* RESET E FONTE GLOBAL */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b; 
    }
    
    /* FUNDO DA APLICAÇÃO (Cinza Frio para profundidade) */
    .stApp {
        background-color: #f1f5f9;
    }
    
    /* CABEÇALHO INSTITUCIONAL REFORMULADO */
    .header-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border-bottom: 5px solid #1e3a8a;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        margin-bottom: 2rem;
    }
    
    .app-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1e3a8a;
        letter-spacing: -0.02em;
        margin: 0;
    }
    
    .app-subtitle {
        font-size: 1rem;
        color: #64748b;
        font-weight: 500;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* CAIXAS DE CONTEÚDO (Cards Brancos com Contorno) */
    .content-card {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        margin-bottom: 1.5rem;
    }

    /* REFORÇO VISUAL DOS CAMPOS DE INPUT */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background-color: #ffffff !important;
        color: #1e293b !important;
        padding: 10px !important;
        font-size: 1rem !important;
        transition: all 0.2s ease;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #1e3a8a !important;
        box-shadow: 0 0 0 3px rgba(30, 58, 138, 0.1) !important;
    }

    /* BOTÕES PROFISSIONAIS */
    .stButton > button {
        border-radius: 8px;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
    }
    
    /* BOTÃO AVANÇAR (PRIMÁRIO) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(30, 58, 138, 0.2) !important;
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background-color: #2563eb !important;
        transform: translateY(-2px);
    }

    /* INDICADOR DE PROGRESSO MINIMALISTA */
    .progress-nav {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        background: white;
        padding: 0.75rem;
        border-radius: 50px;
        border: 1px solid #e2e8f0;
    }
    .nav-dot {
        flex: 1;
        text-align: center;
        font-size: 0.85rem;
        font-weight: 700;
        color: #94a3b8;
    }
    .nav-dot.active {
        color: #1e3a8a;
    }

    /* LABELS DOS CAMPOS */
    label {
        font-weight: 600 !important;
        color: #334155 !important;
        margin-bottom: 8px !important;
        font-size: 0.9rem !important;
    }

    /* TAGS DE CONTEÚDO */
    .badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .badge-tech { background-color: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; }
    .badge-eng { background-color: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }
    
    /* MENSAGEM DE OBRIGATORIEDADE */
    .mandatory-alert {
        border-left: 4px solid #ef4444;
        background-color: #fef2f2;
        padding: 1rem;
        border-radius: 6px;
        color: #991b1b;
        font-weight: 600;
        margin-bottom: 1rem;
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

# --- 3. CABEÇALHO (FIXO E SEGURO) ---
with st.container():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    c_l, c_title, c_r = st.columns([1, 4, 1])
    
    with c_l:
        logo_p = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
        if os.path.exists(logo_p):
            st.image(logo_p, width=90)
    
    with c_title:
        st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
        st.markdown('<h1 class="app-title">SISTEMA PLANEJAR</h1>', unsafe_allow_html=True)
        st.markdown('<p class="app-subtitle">Gestão Pedagógica Profissional • CEIEF Rafael Affonso Leite</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with c_r:
        logo_e = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
        if os.path.exists(logo_e):
            st.image(logo_e, width=90)
    st.markdown('</div>', unsafe_allow_html=True)

# --- GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(s): st.session_state.step = s

# NAVEGAÇÃO DE ETAPAS
st.markdown(f"""
<div class="progress-nav">
    <div class="nav-dot {'active' if st.session_state.step==1 else ''}">01. IDENTIFICAÇÃO</div>
    <div class="nav-dot {'active' if st.session_state.step==2 else ''}">02. CURRÍCULO</div>
    <div class="nav-dot {'active' if st.session_state.step==3 else ''}">03. EMISSÃO</div>
</div>
""", unsafe_allow_html=True)

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown("#### Parâmetros do Planeamento")
        st.write("")
        
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Docente Responsável", value=st.session_state.config.get('professor', ''), placeholder="Nome Completo")
            
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
                st.info("Planeamento Mensal (Fevereiro)")
            else:
                quinzena = st.radio("Período de Execução", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Continuar para Matriz Curricular ➔", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("Todos os campos de identificação são de preenchimento obrigatório.")
            else:
                if 'ano' in st.session_state.config and st.session_state.config['ano'] != ano:
                    st.session_state.conteudos_selecionados = []
                st.session_state.config = {
                    'professor': professor, 'ano': ano, 'turmas': turmas, 
                    'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc
                }
                set_step(2)
                st.rerun()

# --- PASSO 2: MATRIZ CURRICULAR ---
elif st.session_state.step == 2:
    st.markdown(f"#### Matriz Oficial: {st.session_state.config['ano']}")
    
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec, op_ing = [], []
        termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING']
        
        for k, v in dados.items():
            if v:
                eixo = v[0]['eixo'].upper()
                if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
                else: op_tec.append(k)

        t1, t2 = st.tabs(["Tecnologia & Cultura Digital", "Língua Inglesa"])
        
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Eixo Curricular", op_tec, key="t_g")
                itens = dados[g]
                e = c2.selectbox("Habilidade Específica", [i['especifico'] for i in itens], key="t_e")
                sel = next(i for i in itens if i['especifico'] == e)
                
                st.markdown(f"""
                <div style="background:#f8fafc; padding:20px; border-radius:10px; border:1px solid #cbd5e1; margin-top:10px;">
                    <span class="badge badge-tech">Objetivo Curricular</span>
                    <p style="font-weight:600; font-size:1.1rem; margin:10px 0;">{sel['objetivo']}</p>
                    <small style="color:#64748b;">Trimestre: {sel['trimestre']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar à Lista ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Conteúdo adicionado!")
            else: st.warning("Sem dados de tecnologia.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Tópico Curricular", op_ing, key="i_g")
                itens = dados[g]
                e = c2.selectbox("Prática Linguística", [i['especifico'] for i in itens], key="i_e")
                sel = next(i for i in itens if i['especifico'] == e)
                
                st.markdown(f"""
                <div style="background:#fff1f2; padding:20px; border-radius:10px; border:1px solid #fecdd3; margin-top:10px;">
                    <span class="badge badge-eng">Objetivo Curricular</span>
                    <p style="font-weight:600; font-size:1.1rem; color:#881337; margin:10px 0;">{sel['objetivo']}</p>
                    <small style="color:#64748b;">Trimestre: {sel['trimestre']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar à Lista ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Conteúdo adicionado!")
            else: st.warning("Sem dados de inglês.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos Adicionados")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            tag_cls = "badge-tech" if item['tipo'] == "Tecnologia" else "badge-eng"
            c_txt, c_btn = st.columns([0.95, 0.05])
            with c_txt:
                st.markdown(f"""
                <div style="background:white; border:1px solid #e2e8f0; padding:12px; border-radius:8px; margin-bottom:8px;">
                    <span class="badge {tag_cls}">{item['tipo']}</span> 
                    <span style="font-weight:700; margin-left:10px;">{item['geral']}</span>
                    <div style="font-size:0.9rem; margin-top:5px; color:#475569;">{item['especifico']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c_btn:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Identificação"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes Finais ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados:
            st.error("Adicione pelo menos um item da matriz oficial.")
        else:
            set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("#### Detalhamento Pedagógico Obrigatório")
    
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        
        st.markdown('<div class="mandatory-alert">Os campos abaixo são necessários para a emissão do documento oficial.</div>', unsafe_allow_html=True)
        
        obj_esp = st.text_area("1. Objectivos Específicos da Aula", height=100, placeholder="Defina os resultados esperados para estas aulas...", value=st.session_state.config.get('obj_esp', ''))
        
        c1, c2 = st.columns(2)
        with c1:
            sit = st.text_area("2. Situação Didática / Metodologia", height=200, placeholder="Passo a passo da atividade...", value=st.session_state.config.get('sit', ''))
        with c2:
            rec = st.text_area("3. Recursos Didáticos", height=200, placeholder="Ferramentas e materiais utilizados...", value=st.session_state.config.get('rec', ''))
        
        c3, c4 = st.columns(2)
        with c3:
            aval = st.text_area("4. Avaliação", height=100, value=st.session_state.config.get('aval', ''))
        with c4:
            recup = st.text_area("5. Recuperação Contínua", height=100, value=st.session_state.config.get('recup', ''))
        st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    # --- GERADORES ---
    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C'); pdf.ln(15)
        pdf.set_fill_color(240, 245, 255); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PROFESSOR: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos:
            pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for lab, val in [("Obj. Específicos", dados['obj_esp']), ("Situação Didática", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(lab + ":"), 0, 1)
            pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(val)); pdf.ln(2)
        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f'Emitido em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\nPlanejamento de Linguagens e Tecnologias").bold = True
        doc.add_paragraph(f"Professor: {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        doc.add_heading("Matriz Curricular", 3)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento Pedagógico", 3)
        for lab, val in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(lab + ": ").bold = True; p.add_run(val)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Matriz"): set_step(2); st.rerun()
    if c2.button("Finalizar e Gerar Planeamento 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]):
            st.error("Todos os campos do detalhamento pedagógico são obrigatórios.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_arq = f"Planeamento_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("Documentos prontos para entrega!")
            st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 Word (.docx)", w_file, f"{nome_arq}.docx", use_container_width=True)
            cd2.download_button("📕 PDF (.pdf)", p_file, f"{nome_arq}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:50px; padding:20px; color:#94a3b8; font-size:0.8rem; border-top:1px solid #e2e8f0;">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema de uso interno e exclusivo do CEIEF Rafael Affonso Leite © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
