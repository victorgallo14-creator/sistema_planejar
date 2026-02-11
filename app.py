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
    st.error("ERRO DE SISTEMA: A base de dados curricular não foi localizada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | Gestão Pedagógica",
    layout="wide",
    page_icon="📘",
    initial_sidebar_state="expanded"
)

# --- 2. DESIGN SYSTEM (CORPORATE & CLEAN) ---
st.markdown("""
<style>
    /* Fontes Corporativas */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    /* Header Institucional */
    .header-container {
        background: white;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 2rem;
    }
    
    .header-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .header-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.2rem;
        font-weight: 400;
    }

    .header-logo-img {
        max-height: 50px;
        width: auto;
    }

    /* Cards e Containers */
    .card-container {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }

    /* Títulos de Seção */
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e2e8f0;
    }

    /* Tags de Status Sóbrias */
    .status-tag {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .tag-tech { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .tag-eng { background-color: #fff1f2; color: #be123c; border: 1px solid #fecdd3; }

    /* Barra de Progresso Minimalista */
    .step-indicator {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 1rem;
    }
    .step-item {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 500;
        margin-right: 1.5rem;
        padding-bottom: 0.5rem;
        cursor: default;
    }
    .step-active {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
    }

    /* Botões Corporativos */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        height: 2.5rem;
        border: 1px solid #e2e8f0;
        background-color: white;
        color: #334155;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background-color: #f8fafc;
        border-color: #cbd5e1;
        color: #0f172a;
    }
    /* Botão Primário (Ação Principal) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background-color: #2563eb;
        color: white;
        border: none;
    }
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background-color: #1d4ed8;
    }

    /* Ajustes Gerais */
    .stTextInput > label, .stSelectbox > label, .stTextArea > label {
        font-size: 0.85rem;
        font-weight: 500;
        color: #475569;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1.5rem;
        color: #94a3b8;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO (HTML PURO) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

logo_pref = get_image_base64("logo_prefeitura.png") or get_image_base64("logo_prefeitura.jpg")
logo_esc = get_image_base64("logo_escola.png") or get_image_base64("logo_escola.jpg")
logo_pref_html = f'<img src="{logo_pref}" class="header-logo-img">' if logo_pref else ''
logo_esc_html = f'<img src="{logo_esc}" class="header-logo-img">' if logo_esc else ''

st.markdown(f"""
<div class="header-container">
    <div style="display:flex; align-items:center; gap:1rem;">
        {logo_pref_html}
        <div>
            <div class="header-title">SISTEMA PLANEJAR</div>
            <div class="header-subtitle">Gestão Pedagógica • CEIEF Rafael Affonso Leite</div>
        </div>
    </div>
    <div>{logo_esc_html}</div>
</div>
""", unsafe_allow_html=True)

# --- 4. GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(step): st.session_state.step = step

# Indicador de Passos (Wizard Corporativo)
s1_class = "step-item step-active" if st.session_state.step == 1 else "step-item"
s2_class = "step-item step-active" if st.session_state.step == 2 else "step-item"
s3_class = "step-item step-active" if st.session_state.step == 3 else "step-item"

st.markdown(f"""
<div class="step-indicator">
    <div class="{s1_class}">1. Parâmetros Gerais</div>
    <div class="{s2_class}">2. Seleção Curricular</div>
    <div class="{s3_class}">3. Detalhamento & Emissão</div>
</div>
""", unsafe_allow_html=True)

# --- PASSO 1: CONFIGURAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown('<div class="section-title">Dados de Identificação</div>', unsafe_allow_html=True)
        with st.container(): # Simula card
            c1, c2 = st.columns(2)
            with c1:
                professor = st.text_input("Docente Responsável", value=st.session_state.config.get('professor', ''))
                anos = list(CURRICULO_DB.keys())
                idx_ano = anos.index(st.session_state.config['ano']) if 'ano' in st.session_state.config and st.session_state.config['ano'] in anos else 0
                ano = st.selectbox("Ano de Escolaridade", anos, index=idx_ano)
                
                # Regra de Turmas
                qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
                max_t = qtd_turmas.get(ano, 3)
                prefixo = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
                opts_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]
                
                turmas = st.multiselect("Turmas (Vínculo)", opts_turmas, default=st.session_state.config.get('turmas', []))

            with c2:
                meses = {2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
                idx_mes = list(meses.values()).index(st.session_state.config['mes']) if 'mes' in st.session_state.config else 0
                mes_nome = st.selectbox("Mês de Referência", list(meses.values()), index=idx_mes)
                mes_num = [k for k, v in meses.items() if v == mes_nome][0]
                ano_atual = datetime.now().year
                
                if mes_num == 2:
                    periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                    trimestre_doc = "1º Trimestre"
                    st.caption("ℹ️ Fevereiro: Planejamento Mensal")
                else:
                    quinzena = st.radio("Período de Execução", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                    ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                    if mes_num <= 4: trimestre_doc = "1º Trimestre"
                    elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                    else: trimestre_doc = "3º Trimestre"
                    periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Avançar", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("Preencha todos os campos obrigatórios.")
            else:
                if 'ano' in st.session_state.config and st.session_state.config['ano'] != ano:
                    st.session_state.conteudos_selecionados = []
                st.session_state.config = {
                    'professor': professor, 'ano': ano, 'turmas': turmas, 
                    'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc
                }
                set_step(2)
                st.rerun()

# --- PASSO 2: SELEÇÃO DE CONTEÚDO ---
elif st.session_state.step == 2:
    ano_atual = st.session_state.config['ano']
    st.markdown(f'<div class="section-title">Matriz Curricular: {ano_atual}</div>', unsafe_allow_html=True)
    
    dados = CURRICULO_DB.get(ano_atual, {})
    op_tec, op_ing = [], []
    termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
    for k, v in dados.items():
        eixo = v[0]['eixo'].upper() if v else ""
        if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
        else: op_tec.append(k)

    t1, t2 = st.tabs(["Tecnologia & Cultura Digital", "Linguagens (Inglês)"])
    
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Eixo Temático", op_tec)
            itens = dados[g]
            e = c2.selectbox("Habilidade", [i['especifico'] for i in itens])
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div class="card-container" style="border-left: 4px solid #3b82f6;">
                <div style="font-size:0.8rem; color:#64748b; margin-bottom:0.5rem;">OBJETIVO DO CURRÍCULO</div>
                <div style="font-weight:600; color:#1e293b;">{sel['objetivo']}</div>
                <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.5rem;">Previsão: {sel['trimestre']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Item", key="add_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Item adicionado", icon="✅")
        else: st.info("Matriz curricular não disponível para este segmento.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Tópico", op_ing)
            itens = dados[g]
            e = c2.selectbox("Prática", [i['especifico'] for i in itens])
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div class="card-container" style="border-left: 4px solid #ef4444;">
                <div style="font-size:0.8rem; color:#64748b; margin-bottom:0.5rem;">OBJETIVO DO CURRÍCULO</div>
                <div style="font-weight:600; color:#1e293b;">{sel['objetivo']}</div>
                <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.5rem;">Previsão: {sel['trimestre']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Item", key="add_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Item adicionado", icon="✅")
        else: st.info("Matriz curricular não disponível para este segmento.")

    # Lista de Itens
    if st.session_state.conteudos_selecionados:
        st.markdown("---")
        st.markdown(f"**Itens Selecionados ({len(st.session_state.conteudos_selecionados)})**")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            tag_class = "tag-tech" if item['tipo'] == "Tecnologia" else "tag-eng"
            c_txt, c_del = st.columns([0.9, 0.1])
            c_txt.markdown(f"""
            <div style="background:white; padding:10px; border:1px solid #e2e8f0; border-radius:6px; margin-bottom:5px;">
                <span class="status-tag {tag_class}">{item['tipo']}</span> 
                <span style="font-weight:600; font-size:0.9rem; margin-left:8px;">{item['geral']}</span>
                <div style="font-size:0.85rem; color:#64748b; margin-top:4px;">{item['especifico']}</div>
            </div>
            """, unsafe_allow_html=True)
            if c_del.button("✕", key=f"del_{i}"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()
                
    st.markdown("<br>", unsafe_allow_html=True)
    c_b1, c_b2 = st.columns(2)
    if c_b1.button("Voltar"): set_step(1); st.rerun()
    if c_b2.button("Avançar", type="primary"):
        if not st.session_state.conteudos_selecionados: st.error("Selecione ao menos um item da matriz.")
        else: set_step(3); st.rerun()

# --- PASSO 3: DETALHAMENTO ---
elif st.session_state.step == 3:
    st.markdown('<div class="section-title">Detalhamento Pedagógico</div>', unsafe_allow_html=True)
    
    with st.container():
        st.caption("Preencha os campos abaixo para compor o documento oficial.")
        
        # CAMPO NOVO: Objetivos Específicos
        objetivos_especificos = st.text_area(
            "Objetivos Específicos da Aula", 
            height=100, 
            placeholder="Descreva os objetivos pontuais desta aula (além dos previstos no currículo)...",
            value=st.session_state.config.get('objetivos_especificos', '')
        )
        
        c1, c2 = st.columns(2)
        situacao = c1.text_area("Situação Didática / Metodologia", height=150, placeholder="Descreva o passo a passo da aula...", value=st.session_state.config.get('situacao', ''))
        recursos = c2.text_area("Recursos Didáticos", height=150, placeholder="Materiais, equipamentos e ferramentas...", value=st.session_state.config.get('recursos', ''))
        
        c3, c4 = st.columns(2)
        avaliacao = c3.text_area("Procedimentos de Avaliação", height=100, value=st.session_state.config.get('avaliacao', ''))
        recuperacao = c4.text_area("Recuperação Contínua", height=100, value=st.session_state.config.get('recuperacao', ''))
        
        st.session_state.config.update({
            'objetivos_especificos': objetivos_especificos,
            'situacao': situacao, 'recursos': recursos, 
            'avaliacao': avaliacao, 'recuperacao': recuperacao
        })

    def gerar_pdf(dados, conteudos):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Logos
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C')
        pdf.ln(15)

        def clean(txt): return txt.encode('latin-1', 'replace').decode('latin-1')
        
        # Dados Cabeçalho
        pdf.set_fill_color(245, 247, 250)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PERÍODO: {dados['periodo']} ({dados['trimestre']})"), 0, 1, 'L', True)
        pdf.cell(0, 6, clean(f"PROFESSOR(A): {dados['professor']}"), 0, 1, 'L', True)
        pdf.cell(0, 6, clean(f"ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 0, 1, 'L', True)
        pdf.ln(5)

        # Matriz Curricular
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, clean("MATRIZ CURRICULAR SELECIONADA"), 0, 1)
        pdf.set_font("Arial", '', 9)
        
        for item in conteudos:
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(0, 5, clean(f"EIXO: {item['eixo']} | TEMA: {item['geral']}"), 0, 1)
            pdf.set_font("Arial", '', 8)
            pdf.multi_cell(0, 5, clean(f"Habilidade: {item['especifico']}"), 0, 'L')
            pdf.multi_cell(0, 5, clean(f"Objetivo Curricular: {item['objetivo']}"), 0, 'L')
            pdf.ln(2)
        
        pdf.ln(3)

        # Detalhamento
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        
        # Novo Campo no PDF
        if dados['objetivos_especificos']:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Objetivos Específicos da Aula:"), 0, 1)
            pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['objetivos_especificos'])); pdf.ln(3)

        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Situação Didática:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['situacao'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recursos:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recursos'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Avaliação:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['avaliacao'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recuperação:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recuperacao'])); pdf.ln(3)

        # Rodapé
        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, f'Emitido em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.cell(0, 5, 'Visto Coordenação: _______________________________', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document()
        for s in doc.sections: s.top_margin = Cm(1); s.bottom_margin = Cm(1.5); s.left_margin = Cm(1.5); s.right_margin = Cm(1.5)
        style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
        
        t = doc.add_table(rows=1, cols=3); t.autofit = False
        c1 = t.cell(0,0); c1.width = Cm(2.5)
        if os.path.exists("logo_prefeitura.png"): c1.paragraphs[0].add_run().add_picture("logo_prefeitura.png", width=Cm(2.0))
        c2 = t.cell(0,1); c2.width = Cm(11.0); p = c2.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\n").bold = True; p.add_run("Planejamento de Linguagens e Tecnologias")
        c3 = t.cell(0,2); c3.width = Cm(2.5); p3 = c3.paragraphs[0]; p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        if os.path.exists("logo_escola.png"): p3.add_run().add_picture("logo_escola.png", width=Cm(2.0))

        doc.add_paragraph()
        p = doc.add_paragraph()
        p.add_run(f"Período: {dados['periodo']}\n").bold = True
        p.add_run(f"Professor(a): {dados['professor']}\n")
        p.add_run(f"Ano: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}")
        doc.add_paragraph("-" * 90)

        if conteudos:
            doc.add_heading("Matriz Curricular", 3)
            tb = doc.add_table(rows=1, cols=3); tb.style = 'Table Grid'
            tb.rows[0].cells[0].text = "Eixo"; tb.rows[0].cells[1].text = "Conteúdo Específico"; tb.rows[0].cells[2].text = "Objetivo Curricular"
            for item in conteudos:
                r = tb.add_row().cells
                r[0].text = f"{item['eixo']}\n({item['geral']})"
                r[1].text = item['especifico']
                r[2].text = item['objetivo']

        doc.add_paragraph(); doc.add_heading("Detalhamento Pedagógico", 3)
        
        if dados['objetivos_especificos']:
            p = doc.add_paragraph(); p.add_run("Objetivos Específicos da Aula:\n").bold = True; p.add_run(dados['objetivos_especificos'])
            
        p = doc.add_paragraph(); p.add_run("Situação Didática:\n").bold = True; p.add_run(dados['situacao'])
        p = doc.add_paragraph(); p.add_run("\nRecursos:\n").bold = True; p.add_run(dados['recursos'])
        p = doc.add_paragraph(); p.add_run("\nAvaliação:\n").bold = True; p.add_run(dados['avaliacao'])
        p = doc.add_paragraph(); p.add_run("\nRecuperação:\n").bold = True; p.add_run(dados['recuperacao'])

        f = BytesIO(); doc.save(f); f.seek(0); return f

    # AVISO E BOTÕES
    st.info("ℹ️ Após finalizar, envie o PDF para a coordenação pedagógica.")
    
    c_b1, c_b2 = st.columns(2)
    if c_b1.button("Voltar"): set_step(2); st.rerun()
    if c_b2.button("Emitir Documentos", type="primary"):
        if not situacao or not recursos or not recuperacao:
            st.error("Preencha os campos obrigatórios.")
        else:
            f_data = st.session_state.config
            word_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            pdf_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            
            nome = f"Plan_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            
            c_d1, c_d2 = st.columns(2)
            c_d1.download_button("Baixar Word (.docx)", word_file, f"{nome}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            c_d2.download_button("Baixar PDF (.pdf)", pdf_file, f"{nome}.pdf", "application/pdf", use_container_width=True)
            st.success("Documentos gerados com sucesso.")

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema de uso exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
