import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import calendar
from datetime import datetime
import os
import base64

# IMPORTAÇÃO DO CURRÍCULO
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO: O arquivo 'dados_curriculo.py' não foi encontrado.")
    st.stop()

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Planejamento CEIEF",
    layout="wide",
    page_icon="🏫",
    initial_sidebar_state="expanded"
)

# --- FUNÇÃO PARA CONVERTER IMAGEM EM BASE64 (Para o HTML customizado) ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

# Carrega logos se existirem
img_pref = get_image_base64("logo_prefeitura.png") or get_image_base64("logo_prefeitura.jpg")
img_esc = get_image_base64("logo_escola.png") or get_image_base64("logo_escola.jpg")

# --- CSS PERSONALIZADO (ESTILO INSTITUCIONAL) ---
st.markdown("""
<style>
    /* Importando fonte profissional (Roboto/Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1f2937;
    }

    /* Fundo geral */
    .stApp {
        background-color: #f3f4f6;
    }

    /* Cabeçalho Institucional Customizado */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border-bottom: 4px solid #1E3A8A;
    }
    
    .header-logo {
        max-height: 80px;
        width: auto;
    }

    .header-text {
        text-align: center;
        flex-grow: 1;
        padding: 0 1rem;
    }

    .header-title {
        color: #1E3A8A; /* Azul Marinho Institucional */
        font-size: 1.8rem;
        font-weight: 800;
        margin: 0;
        line-height: 1.2;
    }

    .header-subtitle {
        color: #4B5563;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Responsividade para Celular */
    @media (max-width: 768px) {
        .header-container {
            flex-direction: column;
            gap: 1rem;
            text-align: center;
        }
        .header-title { font-size: 1.4rem; }
        .header-subtitle { font-size: 0.9rem; }
        .header-logo { max-height: 60px; }
    }

    /* Cards de Conteúdo Selecionado */
    .content-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #ccc;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .content-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-tech { border-color: #2563EB; } /* Azul para Tech */
    .card-eng { border-color: #DC2626; }  /* Vermelho para Inglês */

    .card-title {
        font-weight: 700;
        font-size: 1rem;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .card-detail {
        font-size: 0.9rem;
        color: #4B5563;
        margin-bottom: 0.5rem;
    }
    .card-obj {
        font-size: 0.85rem;
        color: #6B7280;
        font-style: italic;
        background-color: #F9FAFB;
        padding: 0.5rem;
        border-radius: 4px;
    }

    /* Estilo da Barra Lateral */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #1E3A8A;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1e40af;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff;
        border-radius: 4px;
        padding: 10px 20px;
        border: 1px solid #e5e7eb;
    }
    .stTabs [aria-selected="true"] {
        background-color: #EFF6FF !important;
        border-color: #1E3A8A !important;
        color: #1E3A8A !important;
        font-weight: bold;
    }

    /* Rodapé */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #9CA3AF;
        font-size: 0.8rem;
        margin-top: 3rem;
        border-top: 1px solid #E5E7EB;
    }
</style>
""", unsafe_allow_html=True)

# --- CABEÇALHO HTML PURO (Para controle total do layout) ---
# Se não tiver imagem, usa um placeholder transparente
img_pref_src = img_pref if img_pref else "https://via.placeholder.com/150x80?text=..."
img_esc_src = img_esc if img_esc else "https://via.placeholder.com/150x80?text=..."

html_header = f"""
<div class="header-container">
    <img src="{img_pref_src}" class="header-logo" style="{'' if img_pref else 'visibility:hidden'}">
    <div class="header-text">
        <h1 class="header-title">CEIEF RAFAEL AFFONSO LEITE</h1>
        <p class="header-subtitle">Sistema de Planejamento Digital • Linguagens e Tecnologias</p>
    </div>
    <img src="{img_esc_src}" class="header-logo" style="{'' if img_esc else 'visibility:hidden'}">
</div>
"""
st.markdown(html_header, unsafe_allow_html=True)

# --- 2. INICIALIZAÇÃO ---
if 'conteudos_selecionados' not in st.session_state:
    st.session_state.conteudos_selecionados = []

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    professor = st.text_input("Nome do Professor(a)", placeholder="Digite seu nome...")
    
    anos_disponiveis = list(CURRICULO_DB.keys())
    nivel_selecionado = st.selectbox("Ano de Escolaridade", anos_disponiveis)
    
    # Lógica de limpar ao mudar de ano
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = nivel_selecionado
    if st.session_state.ano_anterior != nivel_selecionado:
        st.session_state.conteudos_selecionados = []
        st.session_state.ano_anterior = nivel_selecionado
        st.toast("Ano alterado. A lista de conteúdos foi limpa.", icon="🧹")

    # Configuração de turmas
    qtd_turmas_por_ano = {
        "Maternal II": 2, "Etapa I": 3, "Etapa II": 3,
        "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3
    }
    max_turmas = qtd_turmas_por_ano.get(nivel_selecionado, 3)
    
    if "Maternal" in nivel_selecionado or "Etapa" in nivel_selecionado:
         opcoes_turmas = [f"{nivel_selecionado} - {i}" for i in range(1, max_turmas + 1)]
    else:
         opcoes_turmas = [f"{nivel_selecionado} {i}" for i in range(1, max_turmas + 1)]

    turmas_selecionadas = st.multiselect(
        "Selecione as Turmas", 
        opcoes_turmas,
        placeholder="Clique para selecionar...", 
        help="O mesmo planejamento será aplicado para as turmas selecionadas."
    )
    
    st.markdown("---")
    st.markdown("### 🗓️ Período")
    meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 
             8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    mes_nome = st.selectbox("Mês de Referência", list(meses.values()))
    mes_num = [k for k, v in meses.items() if v == mes_nome][0]
    ano_atual = datetime.now().year
    
    if mes_num == 2:
        periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
        trimestre_doc = "1º Trimestre"
    else:
        quinzena = st.radio("Quinzena", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
        ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
        
        if mes_num <= 4: trimestre_doc = "1º Trimestre"
        elif mes_num <= 8: trimestre_doc = "2º Trimestre"
        else: trimestre_doc = "3º Trimestre"

        if "1ª" in quinzena:
            periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}"
        else:
            periodo_texto = f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
            
    st.info(f"📅 **Referência:** {trimestre_doc}")

# --- 4. SEPARAÇÃO AUTOMÁTICA DOS CONTEÚDOS ---
dados_ano = CURRICULO_DB.get(nivel_selecionado, {})
opcoes_tec = []
opcoes_ing = []

termos_ingles = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING', 'VOCABULÁRIO', 'FAMILY', 'COLORS']

for chave, lista_itens in dados_ano.items():
    if lista_itens:
        eixo_item = lista_itens[0].get('eixo', '').upper()
        nome_categoria = chave.upper()

        eh_ingles = any(termo in eixo_item for termo in termos_ingles) or \
                    any(termo in nome_categoria for termo in termos_ingles)

        if eh_ingles:
            opcoes_ing.append(chave)
        else:
            opcoes_tec.append(chave)

# --- 5. ÁREA DE SELEÇÃO (ABAS) ---
st.markdown("### 📚 Seleção de Conteúdos")

tab_tec, tab_ing = st.tabs(["💻 Tecnologia & Cultura Digital", "📖 Linguagens (Inglês)"])

# --- ABA TECNOLOGIA ---
with tab_tec:
    if opcoes_tec:
        c1, c2 = st.columns([1, 1])
        with c1:
            geral_tec = st.selectbox("Eixo / Tema", opcoes_tec, key="sel_tec_geral")
        
        itens_tec = dados_ano[geral_tec]
        opcoes_especificas_tec = [i['especifico'] for i in itens_tec]
        
        with c2:
            especifico_tec = st.selectbox("Conteúdo Específico", opcoes_especificas_tec, key="sel_tec_esp")
            
        item_selecionado_tec = next(i for i in itens_tec if i['especifico'] == especifico_tec)
        
        # Card de Pré-visualização
        st.markdown(f"""
        <div class="content-card card-tech" style="background-color: #F0F9FF;">
            <div class="card-title">🎯 Objetivo de Aprendizagem</div>
            <div class="card-detail">{item_selecionado_tec['objetivo']}</div>
            <div style="text-align:right; font-size:0.8em; color:#666;">Previsto: {item_selecionado_tec['trimestre']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Adicionar ao Planejamento ➕", key="btn_add_tec", use_container_width=True):
            novo = {
                "tipo": "Tecnologia",
                "eixo": item_selecionado_tec['eixo'],
                "geral": geral_tec,
                "especifico": especifico_tec,
                "objetivo": item_selecionado_tec['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.success("Conteúdo adicionado!")
                st.rerun()
            else:
                st.warning("Este conteúdo já foi adicionado.")
    else:
        st.info("Não há conteúdos de tecnologia cadastrados para esta etapa.")

# --- ABA INGLÊS ---
with tab_ing:
    if opcoes_ing:
        c1, c2 = st.columns([1, 1])
        with c1:
            geral_ing = st.selectbox("Habilidade / Tópico", opcoes_ing, key="sel_ing_geral")
            
        itens_ing = dados_ano[geral_ing]
        opcoes_especificas_ing = [i['especifico'] for i in itens_ing]
        
        with c2:
            especifico_ing = st.selectbox("Prática Específica", opcoes_especificas_ing, key="sel_ing_esp")
            
        item_selecionado_ing = next(i for i in itens_ing if i['especifico'] == especifico_ing)
        
        # Card de Pré-visualização
        st.markdown(f"""
        <div class="content-card card-eng" style="background-color: #FEF2F2;">
            <div class="card-title">🎯 Objetivo de Aprendizagem</div>
            <div class="card-detail">{item_selecionado_ing['objetivo']}</div>
            <div style="text-align:right; font-size:0.8em; color:#666;">Previsto: {item_selecionado_ing['trimestre']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Adicionar ao Planejamento ➕", key="btn_add_ing", use_container_width=True):
            novo = {
                "tipo": "Inglês",
                "eixo": item_selecionado_ing.get('eixo', 'Língua Inglesa'),
                "geral": geral_ing,
                "especifico": especifico_ing,
                "objetivo": item_selecionado_ing['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.success("Conteúdo adicionado!")
                st.rerun()
            else:
                st.warning("Este conteúdo já foi adicionado.")
    else:
        st.info("Não há conteúdos de inglês cadastrados para esta etapa.")

# --- 6. RESUMO VISUAL ---
st.markdown("---")
st.markdown("### 📋 Resumo do Planejamento")

if len(st.session_state.conteudos_selecionados) > 0:
    for i, item in enumerate(st.session_state.conteudos_selecionados):
        # Estilização do card baseada no tipo
        border_class = "card-tech" if item["tipo"] == "Tecnologia" else "card-eng"
        icone = "💻" if item["tipo"] == "Tecnologia" else "📖"
        bg_icon = "#EFF6FF" if item["tipo"] == "Tecnologia" else "#FEF2F2"
        
        col_card, col_del = st.columns([0.9, 0.1])
        with col_card:
            st.markdown(f"""
            <div class="content-card {border_class}">
                <div class="card-title" style="display:flex; align-items:center; gap:10px;">
                    <span style="background:{bg_icon}; padding:5px; border-radius:50%; font-size:1.2em;">{icone}</span>
                    {item['eixo']} <span style="font-weight:400; color:#666;">| {item['geral']}</span>
                </div>
                <div class="card-detail">{item['especifico']}</div>
                <div class="card-obj"><strong>Objetivo:</strong> {item['objetivo']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col_del:
            # Botão de deletar centralizado verticalmente
            st.write("") 
            st.write("")
            if st.button("🗑️", key=f"del_{i}", help="Remover este item"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()
else:
    st.info("Nenhum conteúdo selecionado. Utilize as abas acima para adicionar.")

st.markdown("---")

# --- 7. CAMPOS PEDAGÓGICOS ---
st.markdown("### 📝 Detalhamento Didático")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        situacao_didatica = st.text_area("Descrição da Situação Didática (Obrigatório)", height=200,
                                         placeholder="Descreva o passo a passo da aula, metodologia e interação com os alunos...")
    with c2:
        recursos = st.text_area("Recursos Didáticos (Obrigatório)", height=200,
                                placeholder="Liste os materiais: Computadores, Internet, Projetor, Materiais Maker, Flashcards...")

    c3, c4 = st.columns(2)
    with c3:
        avaliacao = st.text_area("Avaliação", height=100, placeholder="Como será verificado o aprendizado?")
    with c4:
        recuperacao = st.text_area("Recuperação Contínua (Obrigatório)", height=100,
                                   placeholder="Estratégias para alunos com dificuldades...")

# --- 8. GERAR WORD ---
def gerar_docx(conteudos, dados_extras):
    doc = Document()
    
    # Margens
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(1.0)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(10)

    # --- CABEÇALHO DO DOCUMENTO ---
    header_table = doc.add_table(rows=1, cols=3)
    header_table.autofit = False
    
    # Logo Prefeitura (Esq)
    cell_left = header_table.cell(0, 0)
    cell_left.width = Cm(2.5)
    if os.path.exists("logo_prefeitura.png"):
        try: cell_left.paragraphs[0].add_run().add_picture("logo_prefeitura.png", width=Cm(2.0))
        except: pass
    elif os.path.exists("logo_prefeitura.jpg"):
        try: cell_left.paragraphs[0].add_run().add_picture("logo_prefeitura.jpg", width=Cm(2.0))
        except: pass

    # Texto (Centro)
    cell_center = header_table.cell(0, 1)
    cell_center.width = Cm(11.0)
    p_header = cell_center.paragraphs[0]
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.add_run('PREFEITURA MUNICIPAL DE LIMEIRA\n').bold = True
    p_header.add_run('CEIEF RAFAEL AFFONSO LEITE\n').bold = True
    p_header.add_run('Planejamento de Linguagens e Tecnologias')

    # Logo Escola (Dir)
    cell_right = header_table.cell(0, 2)
    cell_right.width = Cm(2.5)
    paragraph_right = cell_right.paragraphs[0]
    paragraph_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists("logo_escola.png"):
        try: paragraph_right.add_run().add_picture("logo_escola.png", width=Cm(2.0))
        except: pass
    elif os.path.exists("logo_escola.jpg"):
        try: paragraph_right.add_run().add_picture("logo_escola.jpg", width=Cm(2.0))
        except: pass

    doc.add_paragraph() # Espaço

    # Dados de Identificação
    p_info = doc.add_paragraph()
    p_info.add_run(f'Período: {dados_extras["Periodo"]}\n').bold = True
    p_info.add_run(f'Professor(a): {dados_extras["Professor"]}\n')
    p_info.add_run(f'Ano: {dados_extras["Ano"]} | Turmas: {dados_extras["Turmas"]} | {dados_extras["Trimestre"]}')
    
    doc.add_paragraph("-" * 90)

    # Tabela de Conteúdos
    if conteudos:
        doc.add_heading('Objetivos e Conteúdos Selecionados', level=3)
        table = doc.add_table(rows=1, cols=3)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text = 'Eixo / Geral'
        hdr[1].text = 'Conteúdo Específico'
        hdr[2].text = 'Objetivo de Aprendizagem'
        
        # Formatação do cabeçalho
        for cell in hdr:
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            
        for item in conteudos:
            row = table.add_row().cells
            row[0].text = f"{item['eixo']}\n({item['geral']})"
            row[1].text = item['especifico']
            row[2].text = item['objetivo']
            
            # Ajuste de fonte da tabela
            for cell in row:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(9)

    doc.add_paragraph() 
    
    # Detalhes Pedagógicos
    doc.add_heading('Desenvolvimento Metodológico', level=3)
    
    p = doc.add_paragraph()
    p.add_run("Situação Didática:\n").bold = True
    p.add_run(dados_extras["Didatica"])
    
    p = doc.add_paragraph()
    p.add_run("\nRecursos Didáticos:\n").bold = True
    p.add_run(dados_extras["Recursos"])
    
    p = doc.add_paragraph()
    p.add_run("\nAvaliação:\n").bold = True
    p.add_run(dados_extras["Avaliacao"])
    
    p = doc.add_paragraph()
    p.add_run("\nRecuperação Contínua:\n").bold = True
    p.add_run(dados_extras["Recuperacao"])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.markdown("<br>", unsafe_allow_html=True)

# Botão de Ação
col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
with col_btn_2:
    if st.button("📄 Gerar Documento de Planejamento", use_container_width=True):
        if not professor or not situacao_didatica or len(st.session_state.conteudos_selecionados) == 0:
            st.error("⚠️ Preencha o nome do professor, a situação didática e adicione pelo menos um conteúdo.")
        elif not turmas_selecionadas:
            st.error("⚠️ Selecione pelo menos uma turma.")
        else:
            turmas_texto = ", ".join(turmas_selecionadas)
            
            dados = {
                "Professor": professor,
                "Ano": nivel_selecionado,
                "Turmas": turmas_texto,
                "Periodo": periodo_texto,
                "Trimestre": trimestre_doc,
                "Didatica": situacao_didatica,
                "Recursos": recursos,
                "Avaliacao": avaliacao,
                "Recuperacao": recuperacao
            }
            
            arq = gerar_docx(st.session_state.conteudos_selecionados, dados)
            
            safe_turmas = turmas_texto.replace(' ', '').replace(',', '_')
            if len(safe_turmas) > 20: safe_turmas = "Multiplas_Turmas"
            nome_arquivo = f"Plan_{nivel_selecionado}_{safe_turmas}.docx"
            
            st.success("✅ Planejamento gerado com sucesso!")
            st.download_button(
                label="📥 Clique aqui para Baixar o Arquivo Word",
                data=arq,
                file_name=nome_arquivo,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>Victor</b> | CEIEF Rafael Affonso Leite © 2025
    </div>
""", unsafe_allow_html=True)
