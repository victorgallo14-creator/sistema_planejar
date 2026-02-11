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
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# --- 2. DESIGN SYSTEM (CSS Inovador) ---
st.markdown("""
<style>
    /* Fontes e Cores Globais */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
    }
    
    .stApp {
        background-color: #f1f5f9;
    }

    /* Header Moderno */
    .header-container {
        background: white;
        padding: 1.5rem 2rem;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 2rem;
        border-bottom: 4px solid #2563eb;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .header-title {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }
    
    .header-subtitle {
        font-size: 1rem;
        color: #64748b;
        margin-top: 0.25rem;
        font-weight: 400;
    }

    .header-logo-img {
        max-height: 60px;
        width: auto;
    }

    /* Cards de Conteúdo */
    .content-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }

    .card-tech { border-left: 5px solid #3b82f6; }
    .card-eng { border-left: 5px solid #ef4444; }

    .card-label {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 700;
        color: #94a3b8;
        margin-bottom: 0.5rem;
    }
    
    .card-text {
        font-size: 1rem;
        font-weight: 600;
        color: #334155;
        margin-bottom: 0.5rem;
    }

    .card-meta {
        font-size: 0.85rem;
        color: #64748b;
        background-color: #f8fafc;
        padding: 0.5rem;
        border-radius: 6px;
    }

    /* Botões */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        height: 2.8rem;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    
    /* Wizard Steps (Progresso) */
    .step-container {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        position: relative;
    }
    .step-item {
        z-index: 2;
        text-align: center;
        background: #f1f5f9;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        color: #94a3b8;
        border: 2px solid #e2e8f0;
    }
    .step-active {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 4rem;
        padding: 2rem;
        color: #cbd5e1;
        font-size: 0.8rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO COM LOGOS (HTML PURO PARA LAYOUT PERFEITO) ---
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
    <div style="flex:1;">{logo_pref_html}</div>
    <div style="flex:4; text-align:center;">
        <div class="header-title">SISTEMA PLANEJAR</div>
        <div class="header-subtitle">CEIEF Rafael Affonso Leite • Uso Interno</div>
    </div>
    <div style="flex:1; text-align:right;">{logo_esc_html}</div>
</div>
""", unsafe_allow_html=True)

# --- 4. GESTÃO DE ESTADO (WIZARD) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(step): st.session_state.step = step

# Barra de Progresso Visual
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1: 
    if st.session_state.step == 1: st.markdown('<div class="step-item step-active">1. Configuração</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="step-item">1. Configuração</div>', unsafe_allow_html=True)
with col_s2:
    if st.session_state.step == 2: st.markdown('<div class="step-item step-active">2. Conteúdos</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="step-item">2. Conteúdos</div>', unsafe_allow_html=True)
with col_s3:
    if st.session_state.step == 3: st.markdown('<div class="step-item step-active">3. Finalização</div>', unsafe_allow_html=True)
    else: st.markdown('<div class="step-item">3. Finalização</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- PASSO 1: CONFIGURAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown("### 🛠️ Configuração Inicial")
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Professor(a)", value=st.session_state.config.get('professor', ''))
            anos = list(CURRICULO_DB.keys())
            idx_ano = anos.index(st.session_state.config['ano']) if 'ano' in st.session_state.config and st.session_state.config['ano'] in anos else 0
            ano = st.selectbox("Ano de Escolaridade", anos, index=idx_ano)
            
            # Regra de Turmas
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(ano, 3)
            prefixo = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
            opts_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]
            
            turmas = st.multiselect("Turmas (Espelhamento)", opts_turmas, default=st.session_state.config.get('turmas', []))

        with c2:
            meses = {2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
            idx_mes = list(meses.values()).index(st.session_state.config['mes']) if 'mes' in st.session_state.config else 0
            mes_nome = st.selectbox("Mês", list(meses.values()), index=idx_mes)
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("📅 Mês de Fevereiro: Planejamento Mensal")
            else:
                quinzena = st.radio("Período", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"

        if st.button("Avançar para Conteúdos ➡️", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.error("Preencha todos os campos para continuar.")
            else:
                # Se mudou o ano, limpa conteúdos anteriores
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
    st.markdown(f"### 2️⃣ Seleção de Conteúdos: **{ano_atual}**")
    
    dados = CURRICULO_DB.get(ano_atual, {})
    # Separação
    op_tec, op_ing = [], []
    termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS']
    for k, v in dados.items():
        eixo = v[0]['eixo'].upper() if v else ""
        if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
        else: op_tec.append(k)

    t1, t2 = st.tabs(["💻 Tecnologia & Cultura", "🇬🇧 Linguagens (Inglês)"])
    
    with t1:
        if op_tec:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Eixo / Tema", op_tec)
            itens = dados[g]
            e = c2.selectbox("Habilidade Específica", [i['especifico'] for i in itens])
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div class="content-card card-tech">
                <div class="card-label">OBJETIVO DE APRENDIZAGEM</div>
                <div class="card-text">{sel['objetivo']}</div>
                <div class="card-meta">📅 {sel['trimestre']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Tecnologia ➕", key="add_t"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.success("Adicionado!")
        else: st.warning("Sem conteúdos nesta categoria.")

    with t2:
        if op_ing:
            c1, c2 = st.columns(2)
            g = c1.selectbox("Tópico", op_ing)
            itens = dados[g]
            e = c2.selectbox("Prática", [i['especifico'] for i in itens])
            sel = next(i for i in itens if i['especifico'] == e)
            
            st.markdown(f"""
            <div class="content-card card-eng">
                <div class="card-label">OBJETIVO DE APRENDIZAGEM</div>
                <div class="card-text">{sel['objetivo']}</div>
                <div class="card-meta">📅 {sel['trimestre']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Inglês ➕", key="add_i"):
                st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                st.success("Adicionado!")
        else: st.warning("Sem conteúdos nesta categoria.")

    # Lista de Selecionados
    if st.session_state.conteudos_selecionados:
        st.markdown("---")
        st.markdown("##### 🛒 Itens Selecionados")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            cor = "#eff6ff" if item['tipo'] == "Tecnologia" else "#fef2f2"
            icone = "💻" if item['tipo'] == "Tecnologia" else "🇬🇧"
            c_txt, c_del = st.columns([0.9, 0.1])
            c_txt.markdown(f"<div style='background:{cor}; padding:10px; border-radius:8px; font-size:0.9rem;'><strong>{icone} {item['geral']}</strong><br>{item['especifico']}</div>", unsafe_allow_html=True)
            if c_del.button("🗑️", key=f"del_{i}"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()
                
    c_b1, c_b2 = st.columns(2)
    if c_b1.button("⬅️ Voltar"): set_step(1); st.rerun()
    if c_b2.button("Avançar para Detalhes ➡️", type="primary"):
        if not st.session_state.conteudos_selecionados: st.error("Selecione pelo menos um item.")
        else: set_step(3); st.rerun()

# --- PASSO 3: DETALHAMENTO E DOWNLOAD ---
elif st.session_state.step == 3:
    st.markdown("### 3️⃣ Detalhamento Pedagógico")
    
    with st.container():
        st.markdown('<div class="content-card" style="border:none;">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        sit = c1.text_area("Situação Didática", height=150, value=st.session_state.config.get('situacao', ''))
        rec = c2.text_area("Recursos", height=150, value=st.session_state.config.get('recursos', ''))
        c3, c4 = st.columns(2)
        aval = c3.text_area("Avaliação", height=100, value=st.session_state.config.get('avaliacao', ''))
        recup = c4.text_area("Recuperação Contínua", height=100, value=st.session_state.config.get('recuperacao', ''))
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.config.update({'situacao': sit, 'recursos': rec, 'avaliacao': aval, 'recuperacao': recup})

    # Funções de Geração (Word e PDF) dentro do passo 3 para acesso aos dados
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

        # Dados
        def clean(txt): return txt.encode('latin-1', 'replace').decode('latin-1')
        
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 5, clean(f"Período: {dados['periodo']}"), 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, clean(f"Professor(a): {dados['professor']}"), 0, 1)
        pdf.cell(0, 5, clean(f"Ano: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}"), 0, 1)
        pdf.ln(5)

        # Tabela
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("Objetivos e Conteúdos"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for item in conteudos:
            pdf.set_fill_color(245, 247, 250)
            pdf.multi_cell(0, 6, clean(f"EIXO: {item['eixo']} ({item['geral']})"), 1, 'L', True)
            pdf.multi_cell(0, 6, clean(f"ESP: {item['especifico']}"), 1, 'L')
            pdf.multi_cell(0, 6, clean(f"OBJ: {item['objetivo']}"), 1, 'L')
            pdf.ln(2)
        
        # Texto Livre
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("Desenvolvimento"), 0, 1)
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
            doc.add_heading("Conteúdos", 3)
            tb = doc.add_table(rows=1, cols=3); tb.style = 'Table Grid'
            tb.rows[0].cells[0].text = "Eixo"; tb.rows[0].cells[1].text = "Conteúdo"; tb.rows[0].cells[2].text = "Objetivo"
            for item in conteudos:
                r = tb.add_row().cells
                r[0].text = f"{item['eixo']}\n({item['geral']})"
                r[1].text = item['especifico']
                r[2].text = item['objetivo']

        doc.add_paragraph(); doc.add_heading("Desenvolvimento", 3)
        p = doc.add_paragraph(); p.add_run("Situação:\n").bold = True; p.add_run(dados['situacao'])
        p = doc.add_paragraph(); p.add_run("\nRecursos:\n").bold = True; p.add_run(dados['recursos'])
        p = doc.add_paragraph(); p.add_run("\nAvaliação:\n").bold = True; p.add_run(dados['avaliacao'])
        p = doc.add_paragraph(); p.add_run("\nRecuperação:\n").bold = True; p.add_run(dados['recuperacao'])

        f = BytesIO(); doc.save(f); f.seek(0); return f

    # AVISO E BOTÕES
    st.warning("⚠️ Atenção: Após baixar o PDF, envie para a coordenação.")
    
    c_b1, c_b2 = st.columns(2)
    if c_b1.button("⬅️ Voltar"): set_step(2); st.rerun()
    if c_b2.button("🚀 Gerar Documentos", type="primary", use_container_width=True):
        if not sit or not rec:
            st.error("Preencha os campos obrigatórios.")
        else:
            f_data = st.session_state.config
            word_file = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            pdf_file = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            
            nome = f"Plan_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            
            c_d1, c_d2 = st.columns(2)
            c_d1.download_button("📥 Baixar WORD", word_file, f"{nome}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            c_d2.download_button("📥 Baixar PDF", pdf_file, f"{nome}.pdf", "application/pdf", use_container_width=True)
            st.success("Sucesso!")

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema para uso interno e exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
