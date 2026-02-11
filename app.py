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
    st.error("ERRO CRÍTICO: O arquivo 'dados_curriculo.py' não foi encontrado na mesma pasta.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF Rafael Affonso Leite",
    layout="wide",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# --- 2. CSS CLÁSSICO (Limpo e Funcional) ---
st.markdown("""
<style>
    /* Estilo para as caixas de conteúdo selecionado */
    .tech-box { 
        border-left: 5px solid #2E86C1; 
        background-color: #f0f8ff; 
        padding: 15px; 
        border-radius: 5px; 
        margin-bottom: 10px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .eng-box { 
        border-left: 5px solid #C0392B; 
        background-color: #fdf2f0; 
        padding: 15px; 
        border-radius: 5px; 
        margin-bottom: 10px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Ajuste de fontes dos títulos */
    .main-header { 
        color: #1E3A8A; 
        text-align: center; 
        font-size: 28px; 
        font-weight: bold; 
        margin-bottom: 5px; 
        font-family: 'Arial', sans-serif;
    }
    .sub-header { 
        color: #555; 
        text-align: center; 
        font-size: 18px; 
        margin-bottom: 25px; 
        font-family: 'Arial', sans-serif;
    }

    /* Rodapé */
    .footer { 
        text-align: center; 
        color: #888; 
        font-size: 12px; 
        margin-top: 50px; 
        border-top: 1px solid #ddd; 
        padding-top: 20px; 
    }
    
    /* Ajuste de abas */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO COM LOGOS ---
c_logo_esq, c_texto, c_logo_dir = st.columns([1.5, 5, 1.5])

# Logo Prefeitura
with c_logo_esq:
    if os.path.exists("logo_prefeitura.png"):
        st.image("logo_prefeitura.png", use_container_width=True)
    elif os.path.exists("logo_prefeitura.jpg"):
        st.image("logo_prefeitura.jpg", use_container_width=True)

# Título Central
with c_texto:
    st.markdown('<div class="main-header">SISTEMA PLANEJAR</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">CEIEF Rafael Affonso Leite • Linguagens e Tecnologias</div>', unsafe_allow_html=True)

# Logo Escola
with c_logo_dir:
    if os.path.exists("logo_escola.png"):
        st.image("logo_escola.png", use_container_width=True)
    elif os.path.exists("logo_escola.jpg"):
        st.image("logo_escola.jpg", use_container_width=True)

st.markdown("---")

# --- 4. INICIALIZAÇÃO DE ESTADO ---
if 'conteudos_selecionados' not in st.session_state:
    st.session_state.conteudos_selecionados = []

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configurações")
    professor = st.text_input("Nome do Professor(a)")
    
    anos_disponiveis = list(CURRICULO_DB.keys())
    nivel_selecionado = st.selectbox("Ano de Escolaridade", anos_disponiveis)
    
    # Limpa lista se mudar o ano
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = nivel_selecionado
    if st.session_state.ano_anterior != nivel_selecionado:
        st.session_state.conteudos_selecionados = []
        st.session_state.ano_anterior = nivel_selecionado
        st.success("Ano alterado. Lista limpa.")

    # Regras de Turmas
    qtd_turmas_por_ano = {
        "Maternal II": 2, "Etapa I": 3, "Etapa II": 3,
        "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3
    }
    max_t = qtd_turmas_por_ano.get(nivel_selecionado, 3)
    
    prefixo = f"{nivel_selecionado} - Turma" if "Maternal" in nivel_selecionado or "Etapa" in nivel_selecionado else f"{nivel_selecionado} "
    opcoes_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]

    turmas_selecionadas = st.multiselect(
        "Selecione as Turmas (Espelhamento)", 
        opcoes_turmas,
        placeholder="Selecione as turmas..."
    )
    
    st.markdown("---")
    st.subheader("Período")
    meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 
             8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    mes_nome = st.selectbox("Mês", list(meses.values()))
    mes_num = [k for k, v in meses.items() if v == mes_nome][0]
    ano_atual = datetime.now().year
    
    if mes_num == 2:
        periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
        trimestre_doc = "1º Trimestre"
        st.info("Fevereiro: Mensal")
    else:
        quinzena = st.radio("Período", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
        ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
        
        if mes_num <= 4: trimestre_doc = "1º Trimestre"
        elif mes_num <= 8: trimestre_doc = "2º Trimestre"
        else: trimestre_doc = "3º Trimestre"

        if "1ª" in quinzena:
            periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}"
        else:
            periodo_texto = f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
            
    st.caption(f"Referência: {trimestre_doc}")

# --- 6. SEPARAÇÃO AUTOMÁTICA DE CONTEÚDOS ---
dados_ano = CURRICULO_DB.get(nivel_selecionado, {})
opcoes_tec = []
opcoes_ing = []

termos_ingles = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING', 'VOCABULÁRIO', 'FAMILY', 'COLORS']

for chave, lista_itens in dados_ano.items():
    if lista_itens:
        eixo_teste = lista_itens[0].get('eixo', '').upper()
        nome_categoria = chave.upper()

        eh_ingles = any(t in eixo_teste for t in termos_ingles) or any(t in nome_categoria for t in termos_ingles)

        if eh_ingles:
            opcoes_ing.append(chave)
        else:
            opcoes_tec.append(chave)

# --- 7. ÁREA PRINCIPAL (SELEÇÃO) ---

# Métricas simples
count_tec = sum(1 for x in st.session_state.conteudos_selecionados if x['tipo'] == 'Tecnologia')
count_ing = sum(1 for x in st.session_state.conteudos_selecionados if x['tipo'] == 'Inglês')
st.markdown(f"**Itens Selecionados:** Tecnologia: {count_tec} | Inglês: {count_ing}")

tab_tec, tab_ing, tab_rev = st.tabs(["💻 Tecnologia & Cultura", "📖 Linguagens (Inglês)", "📋 Revisão da Lista"])

# --- ABA TECNOLOGIA ---
with tab_tec:
    if opcoes_tec:
        c1, c2 = st.columns(2)
        with c1:
            geral_tec = st.selectbox("Eixo Temático", opcoes_tec, key="tec_g")
        
        itens_tec = dados_ano[geral_tec]
        opcoes_esp_tec = [i['especifico'] for i in itens_tec]
        
        with c2:
            esp_tec = st.selectbox("Conteúdo Específico", opcoes_esp_tec, key="tec_e")
            
        item_tec = next(i for i in itens_tec if i['especifico'] == esp_tec)
        
        st.info(f"**Objetivo:** {item_tec['objetivo']}")
        
        if st.button("Adicionar Tecnologia ➕", key="btn_tec"):
            novo = {
                "tipo": "Tecnologia", "eixo": item_tec['eixo'], "geral": geral_tec,
                "especifico": esp_tec, "objetivo": item_tec['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.success("Adicionado com sucesso!")
                st.rerun()
            else:
                st.warning("Este item já foi adicionado.")
    else:
        st.warning("Não há conteúdos de tecnologia cadastrados para esta etapa.")

# --- ABA INGLÊS ---
with tab_ing:
    if opcoes_ing:
        c1, c2 = st.columns(2)
        with c1:
            geral_ing = st.selectbox("Tópico / Habilidade", opcoes_ing, key="ing_g")
            
        itens_ing = dados_ano[geral_ing]
        opcoes_esp_ing = [i['especifico'] for i in itens_ing]
        
        with c2:
            esp_ing = st.selectbox("Prática Específica", opcoes_esp_ing, key="ing_e")
            
        item_ing = next(i for i in itens_ing if i['especifico'] == esp_ing)
        
        st.info(f"**Objetivo:** {item_ing['objetivo']}")
        
        if st.button("Adicionar Inglês ➕", key="btn_ing"):
            novo = {
                "tipo": "Inglês", "eixo": item_ing.get('eixo', 'Língua Inglesa'), "geral": geral_ing,
                "especifico": esp_ing, "objetivo": item_ing['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.success("Adicionado com sucesso!")
                st.rerun()
            else:
                st.warning("Este item já foi adicionado.")
    else:
        st.warning("Não há conteúdos de inglês cadastrados para esta etapa.")

# --- ABA REVISÃO ---
with tab_rev:
    if st.session_state.conteudos_selecionados:
        st.caption("Abaixo estão os itens que farão parte do seu planejamento.")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            css_class = "tech-box" if item['tipo'] == "Tecnologia" else "eng-box"
            icone = "💻" if item['tipo'] == "Tecnologia" else "📖"
            
            col_txt, col_btn = st.columns([0.9, 0.1])
            with col_txt:
                st.markdown(f"""
                <div class="{css_class}">
                    <strong>{icone} {item['eixo']} ({item['geral']})</strong><br>
                    {item['especifico']}<br>
                    <em>Obj: {item['objetivo']}</em>
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                st.write("")
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()
    else:
        st.info("Nenhum conteúdo selecionado. Utilize as abas anteriores para adicionar.")

st.markdown("---")

# --- 8. DETALHAMENTO PEDAGÓGICO ---
st.markdown("### 📝 Desenvolvimento da Aula")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        situacao_didatica = st.text_area("Descrição da Situação Didática (Obrigatório)", height=150,
                                         placeholder="Descreva o passo a passo da aula...")
    with c2:
        recursos = st.text_area("Recursos Didáticos (Obrigatório)", height=150,
                                placeholder="Liste os materiais e equipamentos...")
    
    c3, c4 = st.columns(2)
    with c3:
        avaliacao = st.text_area("Avaliação", height=100, placeholder="Como será verificado o aprendizado?")
    with c4:
        recuperacao = st.text_area("Recuperação Contínua (Obrigatório)", height=100,
                                   placeholder="Estratégias para alunos com dificuldades...")

# --- 9. CLASSE PDF ---
class PDF(FPDF):
    def header(self):
        # Logos (ajuste as coordenadas se necessário)
        if os.path.exists("logo_prefeitura.png"):
            self.image("logo_prefeitura.png", 10, 8, 25)
        elif os.path.exists("logo_prefeitura.jpg"):
            self.image("logo_prefeitura.jpg", 10, 8, 25)
            
        if os.path.exists("logo_escola.png"):
            self.image("logo_escola.png", 175, 8, 25)
        elif os.path.exists("logo_escola.jpg"):
            self.image("logo_escola.jpg", 175, 8, 25)

        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        self.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 8)
        data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")
        self.cell(0, 5, f'Documento emitido pelo Sistema Planejar em: {data_hora}', 0, 1, 'C')
        self.cell(0, 5, 'Assinatura do Professor: __________________________________________________', 0, 0, 'C')

# --- 10. FUNÇÕES GERADORAS ---
def clean_text(text):
    """Remove caracteres incompatíveis com latin-1"""
    if text:
        return text.encode('latin-1', 'replace').decode('latin-1')
    return ""

def gerar_pdf(conteudos, dados):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Identificação
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 5, clean_text(f"Período: {dados['Periodo']}"), 0, 1)
    pdf.set_font("Arial", '', 10)
    pdf.cell(0, 5, clean_text(f"Professor(a): {dados['Professor']}"), 0, 1)
    pdf.cell(0, 5, clean_text(f"Ano: {dados['Ano']} | Turmas: {dados['Turmas']} | {dados['Trimestre']}"), 0, 1)
    pdf.ln(5)
    
    # Conteúdos
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, clean_text("Objetivos e Conteúdos Selecionados"), 0, 1)
    pdf.set_font("Arial", '', 10)
    
    for item in conteudos:
        pdf.set_fill_color(240, 240, 240)
        pdf.multi_cell(0, 6, clean_text(f"EIXO: {item['eixo']} ({item['geral']})"), 1, 'L', True)
        pdf.multi_cell(0, 6, clean_text(f"ESPECÍFICO: {item['especifico']}"), 1, 'L')
        pdf.multi_cell(0, 6, clean_text(f"OBJETIVO: {item['objetivo']}"), 1, 'L')
        pdf.ln(2)

    pdf.ln(5)
    
    # Desenvolvimento
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, clean_text("Desenvolvimento Pedagógico"), 0, 1)
    
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, clean_text("Situação Didática:"), 0, 1)
    pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, clean_text(dados['Didatica'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, clean_text("Recursos Didáticos:"), 0, 1)
    pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, clean_text(dados['Recursos'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, clean_text("Avaliação:"), 0, 1)
    pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, clean_text(dados['Avaliacao'])); pdf.ln(3)
    
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 5, clean_text("Recuperação Contínua:"), 0, 1)
    pdf.set_font("Arial", '', 10); pdf.multi_cell(0, 5, clean_text(dados['Recuperacao'])); pdf.ln(3)
    
    return pdf.output(dest='S').encode('latin-1')

def gerar_docx(conteudos, dados):
    doc = Document()
    for section in doc.sections:
        section.top_margin = Cm(1.0); section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.0); section.right_margin = Cm(2.0)

    style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)

    # Cabeçalho Tabela
    header_table = doc.add_table(rows=1, cols=3); header_table.autofit = False
    c1 = header_table.cell(0,0); c1.width = Cm(2.5)
    if os.path.exists("logo_prefeitura.png"): 
        try: c1.paragraphs[0].add_run().add_picture("logo_prefeitura.png", width=Cm(2.0))
        except: pass
    elif os.path.exists("logo_prefeitura.jpg"):
        try: c1.paragraphs[0].add_run().add_picture("logo_prefeitura.jpg", width=Cm(2.0))
        except: pass
        
    c2 = header_table.cell(0,1); c2.width = Cm(11.0); p = c2.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\n").bold = True
    p.add_run("CEIEF RAFAEL AFFONSO LEITE\n").bold = True
    p.add_run("Planejamento de Linguagens e Tecnologias")
    
    c3 = header_table.cell(0,2); c3.width = Cm(2.5); p3 = c3.paragraphs[0]; p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists("logo_escola.png"):
        try: p3.add_run().add_picture("logo_escola.png", width=Cm(2.0))
        except: pass
    elif os.path.exists("logo_escola.jpg"):
        try: p3.add_run().add_picture("logo_escola.jpg", width=Cm(2.0))
        except: pass

    doc.add_paragraph()
    p_info = doc.add_paragraph()
    p_info.add_run(f"Período: {dados['Periodo']}\n").bold = True
    p_info.add_run(f"Professor(a): {dados['Professor']}\n")
    p_info.add_run(f"Ano: {dados['Ano']} | Turmas: {dados['Turmas']} | {dados['Trimestre']}")
    doc.add_paragraph("-" * 90)

    if conteudos:
        doc.add_heading("Objetivos e Conteúdos", level=3)
        t = doc.add_table(rows=1, cols=3); t.style = 'Table Grid'
        t.rows[0].cells[0].text = "Eixo / Geral"
        t.rows[0].cells[1].text = "Conteúdo Específico"
        t.rows[0].cells[2].text = "Objetivo"
        for item in conteudos:
            row = t.add_row().cells
            row[0].text = f"{item['eixo']}\n({item['geral']})"
            row[1].text = item['especifico']
            row[2].text = item['objetivo']

    doc.add_paragraph()
    doc.add_heading("Desenvolvimento", level=3)
    p = doc.add_paragraph(); p.add_run("Situação Didática:\n").bold = True; p.add_run(dados['Didatica'])
    p = doc.add_paragraph(); p.add_run("\nRecursos Didáticos:\n").bold = True; p.add_run(dados['Recursos'])
    p = doc.add_paragraph(); p.add_run("\nAvaliação:\n").bold = True; p.add_run(dados['Avaliacao'])
    p = doc.add_paragraph(); p.add_run("\nRecuperação Contínua:\n").bold = True; p.add_run(dados['Recuperacao'])

    # Rodapé Carimbo
    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    section = doc.sections[0]
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.text = f"Emitido em: {data_emissao} | Assinatura: ________________________________"
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER

    f = BytesIO(); doc.save(f); f.seek(0); return f

# --- 11. BOTÃO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)

# Orientação ao Professor
st.warning("⚠️ Atenção Professor: Após gerar o PDF, encaminhe-o digitalmente para a Coordenação.")

col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
with col_btn_2:
    if st.button("GERAR DOCUMENTOS (WORD + PDF)", type="primary", use_container_width=True):
        # Validação Corrigida
        conteudos_selecionados = st.session_state.conteudos_selecionados
        
        if not professor or not situacao_didatica or not conteudos_selecionados:
            st.error("Preencha o professor, a situação didática e adicione conteúdos.")
        elif not turmas_selecionadas:
            st.error("Selecione as turmas.")
        else:
            dados_plan = {
                "Professor": professor,
                "Ano": nivel_selecionado,
                "Turmas": ", ".join(turmas_selecionadas),
                "Periodo": periodo_texto,
                "Trimestre": trimestre_doc,
                "Didatica": situacao_didatica,
                "Recursos": recursos,
                "Avaliacao": avaliacao,
                "Recuperacao": recuperacao
            }
            
            # Gera os arquivos
            arq_word = gerar_docx(conteudos_selecionados, dados_plan)
            arq_pdf = gerar_pdf(conteudos_selecionados, dados_plan)
            
            nome_base = f"Plan_{nivel_selecionado.replace(' ','')}_{datetime.now().strftime('%d%m')}"
            
            st.success("Documentos gerados com sucesso!")
            
            c_down1, c_down2 = st.columns(2)
            with c_down1:
                st.download_button("📥 Baixar WORD (.docx)", arq_word, f"{nome_base}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
            with c_down2:
                st.download_button("📥 Baixar PDF (.pdf)", arq_pdf, f"{nome_base}.pdf", "application/pdf", use_container_width=True)

# Rodapé
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema para uso interno e exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
