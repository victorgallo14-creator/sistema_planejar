import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
import os

# --- CONFIGURAÇÃO DE SEGURANÇA E MATRIZ ---
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO DE SISTEMA: Base de dados curricular não detectada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF",
    layout="wide",
    page_icon="📘",
    initial_sidebar_state="expanded"
)

# --- 2. CSS DE ALTO CONTRASTE E PADRÃO CORPORATIVO ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }
    
    .stApp {
        background-color: #f8fafc;
    }

    /* ESTILO DOS CAMPOS DE ENTRADA (VISIBILIDADE MÁXIMA) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #475569 !important; /* Borda escura definida */
        border-radius: 6px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        padding: 12px !important;
        font-weight: 500 !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #1e3a8a !important;
        box-shadow: 0 0 0 2px rgba(30, 58, 138, 0.1) !important;
    }

    /* CARDS DE CONTEÚDO */
    .content-block {
        background-color: #ffffff;
        padding: 2.5rem;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }

    /* TÍTULOS E LABELS */
    h1, h2, h3, h4 {
        color: #1e3a8a !important;
        font-weight: 800 !important;
    }
    
    label {
        font-weight: 700 !important;
        color: #334155 !important;
        text-transform: uppercase;
        font-size: 0.8rem !important;
        margin-bottom: 6px !important;
    }

    /* BOTÕES PROFISSIONAIS */
    .stButton > button {
        border-radius: 4px;
        height: 3.2rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s ease;
    }
    
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background-color: #1e3a8a !important;
        color: #ffffff !important;
        border: none !important;
    }

    /* NAVEGAÇÃO POR PASSOS */
    .step-nav {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2.5rem;
        border-bottom: 2px solid #e2e8f0;
    }
    .step-indicator {
        padding: 15px 20px;
        font-weight: 800;
        font-size: 0.85rem;
        color: #94a3b8;
    }
    .step-active {
        color: #1e3a8a;
        border-bottom: 4px solid #1e3a8a;
    }

    /* ALERTAS E BADGES */
    .badge {
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 800;
        border: 1px solid #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO (ESTRUTURA NATIVA ESTÁVEL) ---
with st.container():
    c_logo_l, c_main, c_logo_r = st.columns([1, 4, 1])
    
    with c_logo_l:
        logo_pref = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
        if os.path.exists(logo_pref):
            st.image(logo_pref, width=100)
            
    with c_main:
        st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='margin:0; font-size:2.4rem;'>SISTEMA PLANEJAR</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color:#64748b; font-weight:600; margin-top:-10px;'>CEIEF RAFAEL AFFONSO LEITE • GESTÃO PEDAGÓGICA</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_logo_r:
        logo_escola = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
        if os.path.exists(logo_escola):
            st.image(logo_escola, width=100)

st.markdown("---")

# --- GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(s): st.session_state.step = s

# INDICADOR DE PROGRESSO
c1, c2, c3 = st.columns(3)
with c1: st.markdown(f"<div class='step-indicator {'step-active' if st.session_state.step==1 else ''}'>01 IDENTIFICAÇÃO</div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='step-indicator {'step-active' if st.session_state.step==2 else ''}'>02 MATRIZ CURRICULAR</div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='step-indicator {'step-active' if st.session_state.step==3 else ''}'>03 EMISSÃO OFICIAL</div>", unsafe_allow_html=True)

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown("<div class='content-block'>", unsafe_allow_html=True)
        st.markdown("### Parâmetros Gerais")
        st.write("")
        
        col1, col2 = st.columns(2)
        with col1:
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

        with col2:
            meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            saved_mes = st.session_state.config.get('mes')
            idx_mes = list(meses.values()).index(saved_mes) if saved_mes in list(meses.values()) else 0
            mes_nome = st.selectbox("Mês de Referência", list(meses.values()), index=idx_mes)
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("Regime de Planeamento Mensal (Fevereiro)")
            else:
                quinzena = st.radio("Período de Execução", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("Avançar para Seleção de Conteúdos ➔", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("ERRO: O preenchimento do professor e das turmas é obrigatório.")
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
    st.markdown(f"### Matriz Oficial de Ensino: {st.session_state.config['ano']}")
    
    with st.container():
        st.markdown("<div class='content-block'>", unsafe_allow_html=True)
        
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec, op_ing = [], []
        termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
        
        for k, v in dados.items():
            if v:
                eixo = v[0]['eixo'].upper()
                if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
                else: op_tec.append(k)

        t1, t2 = st.tabs(["Tecnologia e Cultura Digital", "Língua Inglesa"])
        
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Eixo Curricular", op_tec, key="t_g")
                itens = dados[g]
                e = c2.selectbox("Habilidade Específica", [i['especifico'] for i in itens], key="t_e")
                sel = next(i for i in itens if i['especifico'] == e)
                
                st.markdown(f"""
                <div style="background:#f1f5f9; padding:20px; border-radius:6px; border:2px solid #cbd5e1; margin-top:10px;">
                    <div style="font-weight:700; color:#1e3a8a; font-size:1.1rem;">{sel['objetivo']}</div>
                    <div style='margin-top:8px; color:#475569; font-size:0.85rem;'>Planeamento para: {sel['trimestre']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar à Matriz de Aula ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Sucesso: Item adicionado.")
            else: st.warning("Não existem conteúdos cadastrados.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Tópico de Linguagem", op_ing, key="i_g")
                itens = dados[g]
                e = c2.selectbox("Prática Linguística", [i['especifico'] for i in itens], key="i_e")
                sel = next(i for i in itens if i['especifico'] == e)
                
                st.markdown(f"""
                <div style="background:#fdf2f2; padding:20px; border-radius:6px; border:2px solid #fecdd3; margin-top:10px;">
                    <div style="font-weight:700; color:#991b1b; font-size:1.1rem;">{sel['objetivo']}</div>
                    <div style='margin-top:8px; color:#475569; font-size:0.85rem;'>Planeamento para: {sel['trimestre']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar à Matriz de Aula ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("Sucesso: Item adicionado.")
            else: st.warning("Não existem conteúdos cadastrados.")
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos Seleccionados")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            cor = "#eff6ff" if item['tipo'] == "Tecnologia" else "#fef2f2"
            c_txt, c_btn = st.columns([0.96, 0.04])
            with c_txt:
                st.markdown(f"""
                <div style="background:{cor}; border:2px solid #cbd5e1; padding:15px; border-radius:4px; margin-bottom:8px;">
                    <strong>[{item['tipo']}] {item['geral']}</strong>: {item['especifico']}
                </div>
                """, unsafe_allow_html=True)
            with c_btn:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Identificação"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhamento ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados:
            st.error("ERRO: Seleccione pelo menos um item da matriz oficial.")
        else:
            set_step(3); st.rerun()

# --- PASSO 3: EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("### Desenvolvimento Pedagógico")
    
    with st.container():
        st.markdown("<div class='content-block'>", unsafe_allow_html=True)
        
        st.markdown("<div class='mandatory-alert'>CAMPOS OBRIGATÓRIOS PARA EMISSÃO OFICIAL</div>", unsafe_allow_html=True)
        
        obj_esp = st.text_area("Objetivos Específicos da Aula", height=100, placeholder="Quais os resultados práticos pretendidos para estas aulas?")
        
        col_a, col_b = st.columns(2)
        with col_a:
            sit = st.text_area("Situação Didática / Metodologia", height=200, placeholder="Descreva o passo a passo da aula...")
        with col_b:
            rec = st.text_area("Recursos Didáticos", height=200, placeholder="Materiais, ferramentas digitais, kits maker...")
        
        col_c, col_d = st.columns(2)
        with col_c:
            aval = st.text_area("Avaliação", height=100)
        with col_d:
            recup = st.text_area("Recuperação Contínua", height=100)
        st.markdown("</div>", unsafe_allow_html=True)

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
        pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PROFESSOR: {dados['professor']} | ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR SELECCIONADA"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos:
            pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L')
        pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for label, val in [("Obj. Específicos", dados['obj_esp']), ("Metodologia", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(label + ":"), 0, 1)
            pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(val)); pdf.ln(2)
        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 5, f'Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M")} | Sistema Planejar', 0, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\nPlanejamento de Linguagens e Tecnologias").bold = True
        doc.add_paragraph(f"Professor(a): {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        doc.add_heading("Matriz Curricular", 3)
        for it in conteudos: doc.add_paragraph(f"• {it['geral']}: {it['especifico']}", style='List Bullet')
        doc.add_heading("Detalhamento Pedagógico", 3)
        for label, val in [("Obj. Específicos", dados['obj_esp']), ("Situação", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(label + ": ").bold = True; p.add_run(val)
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Matriz"): set_step(2); st.rerun()
    if c2.button("FINALIZAR E GERAR DOCUMENTOS 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]):
            st.error("ERRO: Todos os campos de detalhamento são obrigatórios.")
        else:
            f_data = st.session_state.config
            w_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            p_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_arq = f"Planejar_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            st.success("Planeamento gerado com sucesso!")
            st.balloons()
            cd1, cd2 = st.columns(2)
            cd1.download_button("Baixar WORD (.docx)", w_file, f"{nome_arq}.docx", use_container_width=True)
            cd2.download_button("Baixar PDF (.pdf)", p_file, f"{nome_arq}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div style="text-align:center; margin-top:50px; padding:20px; color:#64748b; font-size:0.75rem; border-top:1px solid #e2e8f0;">
        PROPRIEDADE EXCLUSIVA DO CEIEF RAFAEL AFFONSO LEITE<br>
        Desenvolvido por <b>José Victor Souza Gallo</b> • {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
