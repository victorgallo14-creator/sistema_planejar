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
    page_icon="📘",
    initial_sidebar_state="expanded"
)

# --- 2. CSS (DESIGN CORPORATIVO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    /* Header Container Visual (Fundo Branco atrás das colunas) */
    [data-testid="stHeader"] {
        background-color: transparent;
    }
    
    .main-header-container {
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-bottom: 4px solid #1E3A8A;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin: 0;
        line-height: 1.2;
    }
    
    .app-subtitle {
        font-size: 1rem;
        color: #64748b;
        font-weight: 400;
        margin-top: 5px;
    }

    /* Cards */
    .card-container {
        background: white;
        border-radius: 8px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .card-tech { border-left: 5px solid #3b82f6; }
    .card-eng { border-left: 5px solid #ef4444; }

    /* Botões */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        height: 2.6rem;
        border: 1px solid #cbd5e1;
        background-color: white;
        color: #334155;
        width: 100%;
    }
    .stButton > button:hover {
        border-color: #1E3A8A;
        color: #1E3A8A;
        background-color: #f1f5f9;
    }
    
    /* Botão Primário (Ação) */
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"] {
        background-color: #1E3A8A;
        color: white;
        border: none;
    }
    div[data-testid="stVerticalBlock"] > div > div > div > div > button[kind="primary"]:hover {
        background-color: #1e3a8a;
        opacity: 0.9;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
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

# --- 3. CABEÇALHO DO SISTEMA (NATIVO E SEGURO) ---
# Container branco para o cabeçalho
with st.container():
    col_logo_esq, col_titulo, col_logo_dir = st.columns([1.5, 6, 1.5])
    
    # Logo Prefeitura (Esq)
    with col_logo_esq:
        if os.path.exists("logo_prefeitura.png"):
            st.image("logo_prefeitura.png", use_container_width=True)
        elif os.path.exists("logo_prefeitura.jpg"):
            st.image("logo_prefeitura.jpg", use_container_width=True)
    
    # Títulos (Centro)
    with col_titulo:
        st.markdown("""
        <div class="main-header-container">
            <div class="app-title">SISTEMA PLANEJAR</div>
            <div class="app-subtitle">Gestão Pedagógica • CEIEF Rafael Affonso Leite</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Logo Escola (Dir)
    with col_logo_dir:
        if os.path.exists("logo_escola.png"):
            st.image("logo_escola.png", use_container_width=True)
        elif os.path.exists("logo_escola.jpg"):
            st.image("logo_escola.jpg", use_container_width=True)

# --- 4. GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(step): st.session_state.step = step

# Indicador de Passos
c_s1, c_s2, c_s3 = st.columns(3)
def step_ui(label, num):
    active = st.session_state.step == num
    color = "#1E3A8A" if active else "#94a3b8"
    weight = "700" if active else "400"
    border = f"border-bottom: 3px solid {color};" if active else "border-bottom: 1px solid #e2e8f0;"
    return f"<div style='text-align:center; color:{color}; font-weight:{weight}; padding:10px; {border}'>{label}</div>"

with c_s1: st.markdown(step_ui("1. Parâmetros", 1), unsafe_allow_html=True)
with c_s2: st.markdown(step_ui("2. Currículo", 2), unsafe_allow_html=True)
with c_s3: st.markdown(step_ui("3. Emissão", 3), unsafe_allow_html=True)

st.write("") # Espaço

# --- PASSO 1: CONFIGURAÇÃO ---
if st.session_state.step == 1:
    st.markdown("### 🛠️ Configuração da Aula")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Docente Responsável", value=st.session_state.config.get('professor', ''))
            
            anos = list(CURRICULO_DB.keys())
            saved_ano = st.session_state.config.get('ano')
            idx_ano = anos.index(saved_ano) if saved_ano in anos else 0
            ano = st.selectbox("Ano de Escolaridade", anos, index=idx_ano)
            
            # Regra de Turmas
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(ano, 3)
            prefixo = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
            opts_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]
            
            # Validação de Default
            saved_turmas = st.session_state.config.get('turmas', [])
            valid_defaults = [t for t in saved_turmas if t in opts_turmas]
            
            turmas = st.multiselect("Turmas (Vínculo)", opts_turmas, default=valid_defaults, placeholder="Selecione as turmas...")

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
                st.info("Nota: Fevereiro é Planejamento Mensal.")
            else:
                quinzena = st.radio("Período de Execução", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button("Avançar para Conteúdos ➡️", type="primary"):
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
    st.markdown(f"### 2️⃣ Matriz Curricular: **{ano_atual}**")
    
    dados = CURRICULO_DB.get(ano_atual, {})
    op_tec, op_ing = [], []
    termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING']
    
    for k, v in dados.items():
        if v:
            eixo = v[0]['eixo'].upper()
            if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
            else: op_tec.append(k)

    t1, t2 = st.tabs(["💻 Tecnologia & Cultura Digital", "🇬🇧 Linguagens (Inglês)"])
    
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Eixo Temático", op_tec, key="t_g")
            itens = dados[g]
            e = c2.selectbox("Habilidade", [i['especifico'] for i in itens], key="t_e")
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div class="card-container card-tech" style="background:#f0f9ff; border-left:4px solid #3b82f6;">
                <small style="color:#0369a1; font-weight:bold;">OBJETIVO DE APRENDIZAGEM</small>
                <div style="margin:5px 0; font-weight:500;">{sel['objetivo']}</div>
                <small style="color:#64748b;">📅 {sel['trimestre']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Item", key="add_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Adicionado!", icon="✅")
        else: st.warning("Matriz não disponível para este ano.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Tópico", op_ing, key="i_g")
            itens = dados[g]
            e = c2.selectbox("Prática", [i['especifico'] for i in itens], key="i_e")
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div class="card-container card-eng" style="background:#fff1f2; border-left:4px solid #be123c;">
                <small style="color:#be123c; font-weight:bold;">OBJETIVO DE APRENDIZAGEM</small>
                <div style="margin:5px 0; font-weight:500;">{sel['objetivo']}</div>
                <small style="color:#64748b;">📅 {sel['trimestre']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Item", key="add_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.toast("Adicionado!", icon="✅")
        else: st.warning("Matriz não disponível para este ano.")

    # Lista
    if st.session_state.conteudos_selecionados:
        st.markdown("---")
        st.markdown(f"**Itens Selecionados ({len(st.session_state.conteudos_selecionados)})**")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            icone = "💻" if item['tipo'] == "Tecnologia" else "🇬🇧"
            c_txt, c_btn = st.columns([0.9, 0.1])
            c_txt.info(f"{icone} **{item['geral']}**: {item['especifico']}")
            if c_btn.button("🗑️", key=f"del_{i}"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()

    c_b1, c_b2 = st.columns(2)
    if c_b1.button("⬅️ Voltar"): set_step(1); st.rerun()
    if c_b2.button("Avançar para Detalhes ➡️", type="primary"):
        if not st.session_state.conteudos_selecionados: st.error("Selecione ao menos um item da matriz.")
        else: set_step(3); st.rerun()

# --- PASSO 3: DETALHAMENTO E EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("### 3️⃣ Detalhamento Pedagógico")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        # CAMPO OBRIGATÓRIO (ALTERADO)
        objetivos_especificos = st.text_area(
            "Objetivos Específicos da Aula (Obrigatório)", 
            height=100, 
            placeholder="Descreva os objetivos pontuais desta aula (além dos previstos no currículo)...",
            value=st.session_state.config.get('objetivos_especificos', '')
        )
        
        c1, c2 = st.columns(2)
        situacao = c1.text_area("Situação Didática (Obrigatório)", height=150, placeholder="Passo a passo...", value=st.session_state.config.get('situacao', ''))
        recursos = c2.text_area("Recursos (Obrigatório)", height=150, placeholder="Materiais...", value=st.session_state.config.get('recursos', ''))
        
        c3, c4 = st.columns(2)
        avaliacao = c3.text_area("Avaliação", height=100, value=st.session_state.config.get('avaliacao', ''))
        recuperacao = c4.text_area("Recuperação Contínua", height=100, value=st.session_state.config.get('recuperacao', ''))
        
        st.markdown('</div>', unsafe_allow_html=True)
        
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
        elif os.path.exists("logo_prefeitura.jpg"): pdf.image("logo_prefeitura.jpg", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        elif os.path.exists("logo_escola.jpg"): pdf.image("logo_escola.jpg", 175, 8, 25)

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C')
        pdf.ln(15)

        def clean(txt): return txt.encode('latin-1', 'replace').decode('latin-1') if txt else ""
        
        # Dados
        pdf.set_fill_color(240, 245, 255)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PERÍODO: {dados['periodo']} ({dados['trimestre']})"), 0, 1, 'L', True)
        pdf.cell(0, 6, clean(f"PROFESSOR(A): {dados['professor']}"), 0, 1, 'L', True)
        pdf.cell(0, 6, clean(f"ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 0, 1, 'L', True)
        pdf.ln(5)

        # Matriz
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for item in conteudos:
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(0, 5, clean(f"EIXO: {item['eixo']} | TEMA: {item['geral']}"), 0, 1)
            pdf.set_font("Arial", '', 8)
            pdf.multi_cell(0, 5, clean(f"Habilidade: {item['especifico']}"), 0, 'L')
            pdf.multi_cell(0, 5, clean(f"Objetivo: {item['objetivo']}"), 0, 'L')
            pdf.ln(2)
        
        pdf.ln(3)
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        
        # Agora é obrigatório e sempre aparece
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Objetivos Específicos:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['objetivos_especificos'])); pdf.ln(3)

        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Situação Didática:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['situacao'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recursos:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recursos'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Avaliação:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['avaliacao'])); pdf.ln(3)
        
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recuperação:"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recuperacao'])); pdf.ln(3)

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
            tb.rows[0].cells[0].text = "Eixo"; tb.rows[0].cells[1].text = "Conteúdo Específico"; tb.rows[0].cells[2].text = "Objetivo Curricular"
            for item in conteudos:
                r = tb.add_row().cells
                r[0].text = f"{item['eixo']}\n({item['geral']})"
                r[1].text = item['especifico']
                r[2].text = item['objetivo']

        doc.add_paragraph(); doc.add_heading("Detalhamento Pedagógico", 3)
        
        # Campo Novo no Word
        p = doc.add_paragraph(); p.add_run("Objetivos Específicos:\n").bold = True; p.add_run(dados['objetivos_especificos'])
            
        p = doc.add_paragraph(); p.add_run("Situação Didática:\n").bold = True; p.add_run(dados['situacao'])
        p = doc.add_paragraph(); p.add_run("\nRecursos:\n").bold = True; p.add_run(dados['recursos'])
        p = doc.add_paragraph(); p.add_run("\nAvaliação:\n").bold = True; p.add_run(dados['avaliacao'])
        p = doc.add_paragraph(); p.add_run("\nRecuperação:\n").bold = True; p.add_run(dados['recuperacao'])

        f = BytesIO(); doc.save(f); f.seek(0); return f

    st.info("ℹ️ Lembrete: Envie o PDF para a coordenação.")
    
    c_b1, c_b2 = st.columns(2)
    if c_b1.button("⬅️ Voltar"): set_step(2); st.rerun()
    if c_b2.button("Emitir Documentos (Word + PDF)", type="primary"):
        # Validação Atualizada
        if not situacao or not recursos or not recuperacao or not objetivos_especificos:
            st.error("Preencha todos os campos obrigatórios, incluindo os Objetivos Específicos.")
        else:
            f_data = st.session_state.config
            word_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            pdf_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            
            nome = f"Plan_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            
            c_d1, c_d2 = st.columns(2)
            c_d1.download_button("Baixar Word (.docx)", word_file, f"{nome}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            c_d2.download_button("Baixar PDF (.pdf)", pdf_file, f"{nome}.pdf", "application/pdf", use_container_width=True)
            st.success("Sucesso! Arquivos prontos.")

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema de uso exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
