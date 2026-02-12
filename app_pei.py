import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gerador de PEI | AEE",
    layout="wide",
    page_icon="🧩",
    initial_sidebar_state="collapsed"
)

# --- ESTILO VISUAL (CLEAN & ACESSÍVEL) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #1e293b;
    }
    .stApp { background-color: #f8fafc; }
    
    /* Cabeçalho */
    .header-box {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"], .stDateInput input {
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        background-color: white;
        color: #0f172a;
        padding: 10px;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #0ea5e9;
        box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.2);
    }
    
    /* Cards */
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    /* Botões */
    .stButton > button {
        background-color: #0ea5e9;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: bold;
        height: 3rem;
        width: 100%;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        background-color: #0284c7;
    }
    
    h3 { color: #0f172a; font-weight: 700; margin-top: 20px; }
    label { font-weight: 600; color: #475569; }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO ---
st.markdown("""
<div class="header-box">
    <h1 style='margin:0; font-size: 2.2rem; font-weight:800;'>SISTEMA PEI DIGITAL</h1>
    <p style='margin:5px 0 0 0; opacity:0.9; font-weight:400;'>Plano Educacional Individualizado • Modelo SME 2025</p>
</div>
""", unsafe_allow_html=True)

# --- FORMULÁRIO EM ABAS ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "1. Identificação", 
    "2. Saúde e Terapias", 
    "3. Contexto Escolar", 
    "4. Plano Pedagógico", 
    "5. Emissão"
])

# --- ABA 1: IDENTIFICAÇÃO ---
with tab1:
    st.markdown("### 📋 Identificação do Estudante e Equipa")
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([3, 1, 1])
        nome_aluno = c1.text_input("Nome do Estudante")
        nasc = c2.date_input("Data de Nascimento", format="DD/MM/YYYY", min_value=datetime(2010,1,1))
        
        # Cálculo de idade aproximado visual
        idade_hoje = ""
        if nasc:
            idade_hoje = str((datetime.now().date() - nasc).days // 365)
        
        idade = c3.text_input("Idade (anos)", value=idade_hoje)
        
        c4, c5 = st.columns([1, 2])
        ano_escolar = c4.text_input("Ano de Escolaridade (Ex: Maternal II A)")
        responsaveis = c5.text_input("Nome dos Responsáveis")
        telefone = st.text_input("Telefone de Contacto")
        
        st.markdown("---")
        st.markdown("#### 👩‍🏫 Equipa Escolar")
        col_prof1, col_prof2 = st.columns(2)
        prof_polivalente = col_prof1.text_input("Professor(a) Polivalente/Regente")
        prof_aee = col_prof2.text_input("Professor(a) Educação Especial (AEE)")
        
        col_prof3, col_prof4, col_prof5 = st.columns(3)
        prof_arte = col_prof3.text_input("Professor(a) Arte")
        prof_edfisica = col_prof4.text_input("Professor(a) Ed. Física")
        prof_tec = col_prof5.text_input("Professor(a) Linguagens e Tecnologias")
        
        c_date, c_rev = st.columns(2)
        data_elaboracao = c_date.date_input("Data de Elaboração", datetime.now(), format="DD/MM/YYYY")
        revisoes = c_rev.text_input("Previsão de Revisão", "Trimestral")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 2: SAÚDE ---
with tab2:
    st.markdown("### 🏥 Informações de Saúde")
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.write("**O estudante tem diagnóstico conclusivo?**")
        tem_laudo = st.radio("Diagnóstico", ["Sim", "Não"], horizontal=True, label_visibility="collapsed")
        
        c1, c2 = st.columns(2)
        diag_def = c1.text_input("Deficiência (Qual?)")
        diag_tea = c2.text_input("Transtorno do Neurodesenvolvimento (TEA/TDAH?)")
        diag_outros = st.text_input("Outros Transtornos / Síndromes / Altas Habilidades")
        
        st.markdown("---")
        st.markdown("#### Terapias Externas (Frequência e Horário)")
        
        c_t1, c_t2 = st.columns(2)
        terapia_psi = c_t1.text_input("🧠 Psicologia", placeholder="Ex: 2ª feira às 14h")
        terapia_fono = c_t2.text_input("🗣️ Fonoaudiologia", placeholder="Ex: 4ª feira às 09h")
        
        c_t3, c_t4 = st.columns(2)
        terapia_to = c_t3.text_input("🤲 Terapia Ocupacional")
        terapia_outras = c_t4.text_input("➕ Outras terapias")
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 3: CONTEXTO ---
with tab3:
    st.markdown("### 🏫 Organização do Trabalho Pedagógico")
    with st.container():
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        col_aee1, col_aee2 = st.columns(2)
        cronograma_aee = col_aee1.text_input("Dias e Horários do atendimento AEE")
        apoio_escolar = col_aee2.text_input("Possui Profissional de Apoio (Cuidador)?")
        
        st.markdown("---")
        st.markdown("#### Pauta da Reunião / Expectativas")
        expectativa_familia = st.text_area("Quais as expectativas da família em relação à escola?", height=100)
        expectativa_escola = st.text_area("Quais as expectativas da escola em relação ao estudante?", height=100)
        st.markdown('</div>', unsafe_allow_html=True)

# --- ABA 4: PEDAGÓGICO ---
with tab4:
    st.markdown("### 🎯 Plano Educacional Individualizado (Metas)")
    st.info("Preencha os objetivos, estratégias e recursos para cada área de conhecimento.")
    
    areas = [
        "Linguagem Verbal",
        "Linguagem Matemática",
        "Indivíduo e Sociedade",
        "Arte",
        "Cultura Corporal do Movimento",
        "Linguagens e Tecnologias"
    ]
    
    # Dicionário para guardar os dados
    if 'plano_pei' not in st.session_state: st.session_state.plano_pei = {}
    
    for area in areas:
        # Destaque visual para a área de Tecnologias
        expanded = True if area == "Linguagens e Tecnologias" else False
        
        with st.expander(f"📚 Área: {area}", expanded=expanded):
            c1, c2 = st.columns(2)
            obj = c1.text_area(f"Objetivos a serem alcançados", height=120, key=f"obj_{area}", placeholder=f"Metas para {area}...")
            estr = c2.text_area(f"Estratégias / Intervenções", height=120, key=f"estr_{area}", placeholder="Como trabalhar...")
            
            c3, c4 = st.columns(2)
            rec = c3.text_area(f"Recursos Materiais / Humanos", height=80, key=f"rec_{area}")
            aval = c4.text_area(f"Avaliação / Resultados", height=80, key=f"aval_{area}")
            
            st.session_state.plano_pei[area] = {
                "objetivos": obj, "estrategias": estr, "recursos": rec, "avaliacao": aval
            }
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    observacoes_finais = st.text_area("Observações Gerais e Recomendações Finais", height=100)
    st.markdown('</div>', unsafe_allow_html=True)

# --- CLASSE PDF (REPRODUÇÃO FIEL DO MODELO) ---
class PDF_PEI(FPDF):
    def header(self):
        # Logos e Cabeçalho
        if os.path.exists("logo_prefeitura.png"): self.image("logo_prefeitura.png", 10, 8, 25)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        self.cell(0, 5, 'SECRETARIA MUNICIPAL DE EDUCAÇÃO', 0, 1, 'C')
        self.ln(5)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'PLANO EDUCACIONAL ESPECIALIZADO - PEI', 1, 1, 'C')
        self.ln(5)

    def section_header(self, text):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(220, 230, 240)
        self.cell(0, 8, text, 1, 1, 'L', 1)
        self.ln(2)

    def field_value(self, label, value, ln=1):
        self.set_font('Arial', 'B', 10)
        self.cell(45, 6, label + ": ", 0, 0)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 6, str(value))
        if ln==1: self.ln(1)

    def pedagogical_row(self, area, dados):
        # Título da Área
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(245, 245, 245)
        self.cell(0, 8, area.upper(), 1, 1, 'C', 1)
        
        # Cabeçalhos da Tabela
        self.set_font('Arial', 'B', 8)
        w = [47.5, 47.5, 47.5, 47.5] # Largura das 4 colunas
        
        x = self.get_x()
        y = self.get_y()
        
        self.cell(w[0], 6, "OBJETIVOS", 1, 0, 'C')
        self.cell(w[1], 6, "ESTRATÉGIAS", 1, 0, 'C')
        self.cell(w[2], 6, "RECURSOS", 1, 0, 'C')
        self.cell(w[3], 6, "AVALIAÇÃO", 1, 1, 'C')
        
        self.set_font('Arial', '', 8)
        self.ln()
        
        # Guardar posição Y inicial
        x_start = self.get_x()
        y_start = self.get_y()
        
        # Conteúdo
        txts = [dados['objetivos'], dados['estrategias'], dados['recursos'], dados['avaliacao']]
        
        # Calcular altura máxima
        heights = []
        for i in range(4):
            # Hack para calcular altura sem desenhar
            lines = self.multi_cell(w[i], 5, txts[i], split_only=True)
            h = max(len(lines) * 5, 10) # Altura mínima de 10
            heights.append(h)
            
        max_h = max(heights)
        
        # Desenha as células reais
        self.set_xy(x_start, y_start)
        self.multi_cell(w[0], 5, txts[0], 0, 'L')
        
        self.set_xy(x_start + w[0], y_start)
        self.multi_cell(w[1], 5, txts[1], 0, 'L')
        
        self.set_xy(x_start + w[0]*2, y_start)
        self.multi_cell(w[2], 5, txts[2], 0, 'L')
        
        self.set_xy(x_start + w[0]*3, y_start)
        self.multi_cell(w[3], 5, txts[3], 0, 'L')
        
        # Desenha as bordas
        self.set_xy(x_start, y_start)
        self.rect(x_start, y_start, w[0], max_h)
        self.rect(x_start + w[0], y_start, w[1], max_h)
        self.rect(x_start + w[0]*2, y_start, w[2], max_h)
        self.rect(x_start + w[0]*3, y_start, w[3], max_h)
        
        self.set_y(y_start + max_h)

def clean(t):
    if not t: return "-"
    return t.encode('latin-1', 'replace').decode('latin-1')

def create_pei_pdf():
    pdf = PDF_PEI()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. IDENTIFICAÇÃO
    pdf.section_header("I. IDENTIFICAÇÃO DO ESTUDANTE")
    pdf.field_value("Estudante", clean(nome_aluno))
    pdf.field_value("Nascimento", f"{nasc.strftime('%d/%m/%Y')} (Idade: {clean(idade)})")
    pdf.field_value("Ano/Turma", clean(ano_escolar))
    pdf.field_value("Responsáveis", clean(responsaveis))
    pdf.field_value("Contatos", clean(telefone))
    pdf.ln(3)
    
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, "Equipe Escolar:", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, clean(f"Polivalente: {prof_polivalente}\nAEE: {prof_aee}\nArte: {prof_arte} | Ed. Física: {prof_edfisica}\nTecnologias: {prof_tec}"))
    pdf.ln(5)
    
    # 2. SAÚDE
    pdf.section_header("II. INFORMAÇÕES DE SAÚDE")
    pdf.field_value("Diagnóstico Conclusivo", clean(tem_laudo))
    if diag_def: pdf.field_value("Deficiência", clean(diag_def))
    if diag_tea: pdf.field_value("TEA/TDAH", clean(diag_tea))
    if diag_outros: pdf.field_value("Outros", clean(diag_outros))
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, "Terapias de Apoio:", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, clean(f"- Psicologia: {terapia_psi}\n- Fonoaudiologia: {terapia_fono}\n- T.O.: {terapia_to}\n- Outras: {terapia_outras}"))
    pdf.ln(5)
    
    # 3. ORGANIZAÇÃO
    pdf.section_header("III. ORGANIZAÇÃO PEDAGÓGICA")
    pdf.field_value("Horários AEE", clean(cronograma_aee))
    pdf.field_value("Profissional de Apoio", clean(apoio_escolar))
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10); pdf.cell(0, 6, "Expectativas (Família/Escola):", 0, 1)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, clean(f"Família: {expectativa_familia}\n\nEscola: {expectativa_escola}"))
    pdf.ln(5)
    
    # 4. PLANO PEDAGÓGICO
    pdf.add_page()
    pdf.section_header("IV. PLANO PEDAGÓGICO INDIVIDUALIZADO")
    for area, dados in st.session_state.plano_pei.items():
        pdf.pedagogical_row(clean(area), {k: clean(v) for k, v in dados.items()})
    
    # 5. OBSERVAÇÕES E ASSINATURAS
    pdf.ln(5)
    pdf.section_header("V. CONSIDERAÇÕES FINAIS E ASSINATURAS")
    pdf.set_font('Arial', '', 10)
    pdf.multi_cell(0, 6, clean(observacoes_finais), 1)
    
    pdf.ln(15)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, clean(f"Limeira, {data_elaboracao.strftime('%d/%m/%Y')}"), 0, 1, 'C')
    pdf.ln(10)
    
    # Assinaturas em duas colunas
    pdf.set_font('Arial', '', 8)
    y = pdf.get_y()
    pdf.line(20, y, 90, y); pdf.line(110, y, 180, y)
    pdf.cell(90, 5, "Gestor Escolar", 0, 0, 'C'); pdf.cell(90, 5, "Coordenador Pedagógico", 0, 1, 'C')
    pdf.ln(15)
    
    y = pdf.get_y()
    pdf.line(20, y, 90, y); pdf.line(110, y, 180, y)
    pdf.cell(90, 5, "Professor AEE", 0, 0, 'C'); pdf.cell(90, 5, "Professor Regente", 0, 1, 'C')
    pdf.ln(15)
    
    y = pdf.get_y()
    pdf.line(20, y, 90, y); pdf.line(110, y, 180, y)
    pdf.cell(90, 5, "Prof. Linguagens e Tecnologias", 0, 0, 'C'); pdf.cell(90, 5, "Responsável pelo Estudante", 0, 1, 'C')
    
    return bytes(pdf.output(dest='S').encode('latin-1'))

# --- ABA 5: EMISSÃO ---
with tab5:
    st.markdown("### 📄 Emitir Documento Oficial")
    
    if st.button("GERAR PEI EM PDF 🚀", type="primary", use_container_width=True):
        if not nome_aluno:
            st.error("Preencha pelo menos o nome do aluno na aba 1.")
        else:
            try:
                pdf_bytes = create_pei_pdf()
                nome_arq = f"PEI_{nome_aluno.replace(' ', '_')}_{datetime.now().year}.pdf"
                
                st.success("PEI Gerado com Sucesso!")
                st.download_button(
                    label="📥 Baixar PEI (PDF)",
                    data=pdf_bytes,
                    file_name=nome_arq,
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Erro ao gerar PDF: {e}")
