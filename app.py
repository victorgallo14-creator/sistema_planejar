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
    st.error("ERRO CRÍTICO: Base de dados curricular não encontrada.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF Rafael Affonso Leite",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PREMIUM ---
st.markdown("""
<style>
    @import url('[https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap](https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap)');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    .premium-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .header-text h1 { margin: 0; font-weight: 700; font-size: 2rem; color: white; }
    .header-text p { margin: 5px 0 0 0; font-weight: 300; opacity: 0.9; font-size: 1rem; }
    .header-logo-img { height: 80px; width: auto; background-color: white; padding: 5px; border-radius: 8px; }

    .card-container {
        background: white; border-radius: 12px; padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); border: 1px solid #e2e8f0; margin-bottom: 1rem;
    }
    
    .status-tag {
        display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px;
        font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
    }
    .tag-tech { background-color: #dbeafe; color: #1e40af; }
    .tag-eng { background-color: #fee2e2; color: #991b1b; }

    .stButton > button { border-radius: 8px; font-weight: 500; border: none; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .primary-btn { background-color: #1e3a8a !important; color: white !important; }
    
    /* Aviso de Coordenação */
    .coordenacao-box {
        background-color: #fff7ed;
        border-left: 5px solid #f97316;
        padding: 15px;
        border-radius: 5px;
        color: #9a3412;
        font-weight: bold;
        margin-bottom: 20px;
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

def render_header():
    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
    logo_base64 = get_image_base64(logo_path)
    logo_html = f'<img src="{logo_base64}" class="header-logo-img">' if logo_base64 else '<div style="font-size: 2.5rem;">🏫</div>'

    st.markdown(f"""
    <div class="premium-header">
        <div class="header-text">
            <h1>Sistema Planejar</h1>
            <p>Sistema para uso interno e exclusivo do CEIEF Rafael Affonso Leite</p>
        </div>
        <div class="header-logo">{logo_html}</div>
    </div>
    """, unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def next_step(): st.session_state.step += 1
def prev_step(): st.session_state.step -= 1

# --- CLASSE PARA GERAR O PDF ---
class PDF(FPDF):
    def header(self):
        # Logos
        if os.path.exists("logo_prefeitura.png"): self.image("logo_prefeitura.png", 10, 8, 25)
        elif os.path.exists("logo_prefeitura.jpg"): self.image("logo_prefeitura.jpg", 10, 8, 25)
        
        if os.path.exists("logo_escola.png"): self.image("logo_escola.png", 175, 8, 25)
        elif os.path.exists("logo_escola.jpg"): self.image("logo_escola.jpg", 175, 8, 25)

        # Título
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        self.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")
        self.cell(0, 10, f'Página {self.page_no()} | Emitido em: {data_hora} | Sistema Planejar', 0, 0, 'C')

# --- PASSO 1: CONFIGURAÇÃO ---
def render_step1():
    st.markdown("### 1️⃣ Configuração da Aula")
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Professor(a) Responsável", value=st.session_state.config.get('professor', ''))
            anos = list(CURRICULO_DB.keys())
            nivel_idx = anos.index(st.session_state.config['nivel']) if 'nivel' in st.session_state.config and st.session_state.config['nivel'] in anos else 0
            nivel = st.selectbox("Ano de Escolaridade", anos, index=nivel_idx)
            
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(nivel, 3)
            prefixo = f"{nivel} - Turma" if "Maternal" in nivel or "Etapa" in nivel else f"{nivel} "
            opcoes_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]
            turmas = st.multiselect("Turmas (Espelhamento)", opcoes_turmas, default=st.session_state.config.get('turmas', []))

        with c2:
            meses = {2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun", 7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"}
            mes_nome = st.selectbox("Mês", list(meses.values()))
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("ℹ️ Fevereiro: Mensal")
            else:
                quinzena = st.radio("Período", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
            
            st.success(f"🗓️ **Período:** {periodo_texto}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Próximo Passo ➡️", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.toast("⚠️ Preencha professor e turmas.", icon="⚠️")
            else:
                st.session_state.config = {'professor': professor, 'nivel': nivel, 'turmas': turmas, 'periodo': periodo_texto, 'trimestre': trimestre_doc}
                if 'nivel_antigo' in st.session_state and st.session_state.nivel_antigo != nivel:
                    st.session_state.conteudos_selecionados = []
                st.session_state.nivel_antigo = nivel
                next_step()
                st.rerun()

# --- PASSO 2: SELEÇÃO ---
def render_step2():
    st.markdown(f"### 2️⃣ Seleção de Conteúdos ({st.session_state.config['nivel']})")
    dados_ano = CURRICULO_DB.get(st.session_state.config['nivel'], {})
    opcoes_tec, opcoes_ing = [], []
    termos_ing = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING']

    for chave, lista in dados_ano.items():
        if lista:
            eixo = lista[0].get('eixo', '').upper()
            if any(t in eixo for t in termos_ing) or any(t in chave.upper() for t in termos_ing):
                opcoes_ing.append(chave)
            else:
                opcoes_tec.append(chave)

    t1, t2 = st.tabs(["💻 Tecnologia", "🇬🇧 Inglês"])
    
    with t1:
        if opcoes_tec:
            c1, c2 = st.columns(2)
            geral = c1.selectbox("Eixo", opcoes_tec, key="t_g")
            itens = dados_ano[geral]
            esp = c2.selectbox("Habilidade", [i['especifico'] for i in itens], key="t_e")
            item = next(i for i in itens if i['especifico'] == esp)
            st.info(f"**Objetivo:** {item['objetivo']}")
            if st.button("Adicionar ➕", key="add_t"):
                st.session_state.conteudos_selecionados.append({"tipo": "Tecnologia", "eixo": item['eixo'], "geral": geral, "especifico": esp, "objetivo": item['objetivo']})
                st.toast("Adicionado!", icon="✅")
        else: st.warning("Sem conteúdos.")

    with t2:
        if opcoes_ing:
            c1, c2 = st.columns(2)
            geral = c1.selectbox("Tópico", opcoes_ing, key="i_g")
            itens = dados_ano[geral]
            esp = c2.selectbox("Prática", [i['especifico'] for i in itens], key="i_e")
            item = next(i for i in itens if i['especifico'] == esp)
            st.info(f"**Objetivo:** {item['objetivo']}")
            if st.button("Adicionar ➕", key="add_i"):
                st.session_state.conteudos_selecionados.append({"tipo": "Inglês", "eixo": item['eixo'], "geral": geral, "especifico": esp, "objetivo": item['objetivo']})
                st.toast("Adicionado!", icon="✅")
        else: st.warning("Sem conteúdos.")

    st.divider()
    if st.session_state.conteudos_selecionados:
        for i, it in enumerate(st.session_state.conteudos_selecionados):
            st.text(f"✅ {it['eixo']} | {it['especifico']}")
            
    c_back, c_next = st.columns(2)
    with c_back:
        if st.button("⬅️ Voltar"): prev_step(); st.rerun()
    with c_next:
        if st.button("Avançar ➡️", type="primary"): 
            if not st.session_state.conteudos_selecionados: st.error("Selecione algo.")
            else: next_step(); st.rerun()

# --- PASSO 3: DETALHAMENTO ---
def render_step3():
    st.markdown("### 3️⃣ Detalhamento")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        situacao = c1.text_area("Situação Didática", height=150, value=st.session_state.config.get('situacao', ''))
        recursos = c2.text_area("Recursos", height=150, value=st.session_state.config.get('recursos', ''))
        c3, c4 = st.columns(2)
        avaliacao = c3.text_area("Avaliação", height=100, value=st.session_state.config.get('avaliacao', ''))
        recuperacao = c4.text_area("Recuperação Contínua", height=100, value=st.session_state.config.get('recuperacao', ''))
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.session_state.config.update({'situacao': situacao, 'recursos': recursos, 'avaliacao': avaliacao, 'recuperacao': recuperacao})

    # AVISO DE COORDENAÇÃO
    st.markdown("""
    <div class="coordenacao-box">
        📢 ATENÇÃO PROFESSOR:<br>
        Após gerar o PDF, verifique se todas as informações estão corretas e encaminhe o arquivo digitalmente para o Professor Coordenador para validação.
    </div>
    """, unsafe_allow_html=True)

    c_back, c_final = st.columns(2)
    with c_back:
        if st.button("⬅️ Voltar"): prev_step(); st.rerun()
            
    with c_final:
        if st.button("🚀 Gerar Documentos (Word + PDF)", type="primary", use_container_width=True):
            if not situacao or not recursos or not recuperacao:
                st.error("Preencha os campos obrigatórios!")
            else:
                final_data = st.session_state.config
                final_data['Turmas'] = ", ".join(final_data['turmas'])
                
                # Gera DOC
                doc_buffer = gerar_docx_premium(st.session_state.conteudos_selecionados, final_data)
                
                # Gera PDF
                pdf_buffer = gerar_pdf_premium(st.session_state.conteudos_selecionados, final_data)
                
                st.success("Arquivos gerados com sucesso!")
                
                fname = f"Plan_{final_data['nivel'].replace(' ','')}_{datetime.now().strftime('%d-%m')}"
                
                c_down1, c_down2 = st.columns(2)
                with c_down1:
                    st.download_button("📥 Baixar WORD (.docx)", doc_buffer, f"{fname}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                with c_down2:
                    st.download_button("📥 Baixar PDF (.pdf)", pdf_buffer, f"{fname}.pdf", "application/pdf", use_container_width=True)

# --- GERADOR WORD (Com Carimbo) ---
def gerar_docx_premium(conteudos, dados):
    doc = Document()
    for section in doc.sections: section.top_margin = Cm(1.0); section.bottom_margin = Cm(1.5); section.left_margin = Cm(1.5); section.right_margin = Cm(1.5)
    style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)

    # Carimbo de Tempo
    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    
    # Cabeçalho
    table_head = doc.add_table(rows=1, cols=3); table_head.autofit = False
    c1 = table_head.cell(0,0); c1.width = Cm(2.5)
    if os.path.exists("logo_prefeitura.png"): c1.paragraphs[0].add_run().add_picture("logo_prefeitura.png", width=Cm(2.0))
    
    c2 = table_head.cell(0,1); c2.width = Cm(11.0); p = c2.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\n").bold = True; p.add_run("Planejamento de Linguagens e Tecnologias")
    
    c3 = table_head.cell(0,2); c3.width = Cm(2.5); p_dir = c3.paragraphs[0]; p_dir.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists("logo_escola.png"): p_dir.add_run().add_picture("logo_escola.png", width=Cm(2.0))

    doc.add_paragraph()
    p_info = doc.add_paragraph()
    p_info.add_run(f"Período: {dados['periodo']}\n").bold = True
    p_info.add_run(f"Professor(a): {dados['professor']}\n")
    p_info.add_run(f"Ano: {dados['nivel']} | Turmas: {dados['Turmas']} | {dados['trimestre']}")
    doc.add_paragraph("-" * 90)

    if conteudos:
        doc.add_heading("Objetivos e Conteúdos", level=3)
        t = doc.add_table(rows=1, cols=3); t.style = 'Table Grid'
        hdr = t.rows[0].cells; hdr[0].text = "Eixo / Geral"; hdr[1].text = "Conteúdo Específico"; hdr[2].text = "Objetivo"
        for item in conteudos:
            row = t.add_row().cells
            row[0].text = f"{item['eixo']}\n({item['geral']})"
            row[1].text = item['especifico']
            row[2].text = item['objetivo']

    doc.add_paragraph()
    doc.add_heading("Desenvolvimento", level=3)
    p = doc.add_paragraph(); p.add_run("Situação Didática:\n").bold = True; p.add_run(dados['situacao'])
    p = doc.add_paragraph(); p.add_run("\nRecursos Didáticos:\n").bold = True; p.add_run(dados['recursos'])
    p = doc.add_paragraph(); p.add_run("\nAvaliação:\n").bold = True; p.add_run(dados['avaliacao'])
    p = doc.add_paragraph(); p.add_run("\nRecuperação Contínua:\n").bold = True; p.add_run(dados['recuperacao'])

    # Rodapé com Carimbo
    section = doc.sections[0]
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.text = f"Documento emitido pelo Sistema Planejar em {data_emissao} | Assinatura do Professor: __________________________"
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

    f = BytesIO(); doc.save(f); f.seek(0); return f

# --- GERADOR PDF (Com Carimbo) ---
def gerar_pdf_premium(conteudos, dados):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Tratamento de caracteres latin-1
    def clean(text):
        return text.encode('latin-1', 'replace').decode('latin-1')

    # Dados
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, clean(f"Período: {dados['periodo']}"), 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, clean(f"Professor(a): {dados['professor']}"), 0, 1)
    pdf.cell(0, 5, clean(f"Ano: {dados['nivel']} | Turmas: {dados['Turmas']} | {dados['trimestre']}"), 0, 1)
    pdf.ln(5)
    
    # Tabela
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, clean("Objetivos e Conteúdos Selecionados"), 0, 1)
    pdf.set_font("Arial", '', 9)
    
    for item in conteudos:
        pdf.set_fill_color(240, 240, 240)
        pdf.multi_cell(0, 6, clean(f"EIXO: {item['eixo']} ({item['geral']})"), 1, 'L', True)
        pdf.multi_cell(0, 6, clean(f"ESP: {item['especifico']}"), 1, 'L')
        pdf.multi_cell(0, 6, clean(f"OBJ: {item['objetivo']}"), 1, 'L')
        pdf.ln(2)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 8, clean("Desenvolvimento Pedagógico"), 0, 1)
    
    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Situação Didática:"), 0, 1)
    pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['situacao'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recursos Didáticos:"), 0, 1)
    pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recursos'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Avaliação:"), 0, 1)
    pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['avaliacao'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean("Recuperação Contínua:"), 0, 1)
    pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(dados['recuperacao'])); pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin-1')

# --- FLUXO PRINCIPAL ---
render_header()
if st.session_state.step == 1: render_step1()
elif st.session_state.step == 2: render_step2()
elif st.session_state.step == 3: render_step3()

# Rodapé com Assinatura
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema para uso interno e exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
