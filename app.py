import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import calendar
from datetime import datetime
import os

# IMPORTAÇÃO DO CURRÍCULO
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO CRÍTICO: O arquivo 'dados_curriculo.py' não foi encontrado na mesma pasta.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar",
    layout="wide",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# --- 2. ESTILO CSS (PREMIUM & CLEAN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }
    
    .stApp { background-color: #F8F9FA; }
    
    /* Cabeçalho */
    .header-title {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1E3A8A; /* Azul Institucional */
        margin: 0;
        text-align: center;
        line-height: 1.2;
    }
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 400;
        color: #64748B;
        text-align: center;
        margin-top: 5px;
    }

    /* Cards */
    .info-card {
        background-color: white;
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 0.8rem;
        border-left: 5px solid #ccc;
    }
    .card-tech { border-left-color: #3B82F6; }
    .card-eng { border-left-color: #EA580C; }

    /* Botões */
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        height: 3rem;
    }

    /* Rodapé */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #94a3b8;
        font-size: 0.85rem;
        margin-top: 4rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO VISUAL (Com Logos) ---
c_logo_esq, c_texto, c_logo_dir = st.columns([1.5, 5, 1.5])

# Logo Prefeitura (Esquerda)
with c_logo_esq:
    if os.path.exists("logo_prefeitura.png"):
        st.image("logo_prefeitura.png", use_container_width=True)
    elif os.path.exists("logo_prefeitura.jpg"):
        st.image("logo_prefeitura.jpg", use_container_width=True)

# Texto Central
with c_texto:
    st.markdown('<div class="header-title">SISTEMA PLANEJAR</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">CEIEF Rafael Affonso Leite • Linguagens e Tecnologias</div>', unsafe_allow_html=True)

# Logo Escola (Direita)
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
    professor = st.text_input("Professor(a)", placeholder="Nome completo...")
    
    anos = list(CURRICULO_DB.keys())
    nivel_selecionado = st.selectbox("Ano de Escolaridade", anos)
    
    # Limpa lista ao mudar de ano
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = nivel_selecionado
    if st.session_state.ano_anterior != nivel_selecionado:
        st.session_state.conteudos_selecionados = []
        st.session_state.ano_anterior = nivel_selecionado
        st.toast("Ano alterado. Lista limpa.", icon="🧹")

    # Regras de Turmas
    qtd_turmas = {
        "Maternal II": 2, "Etapa I": 3, "Etapa II": 3,
        "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3
    }
    max_t = qtd_turmas.get(nivel_selecionado, 3)
    
    prefixo = f"{nivel_selecionado} - Turma" if "Maternal" in nivel_selecionado or "Etapa" in nivel_selecionado else f"{nivel_selecionado} "
    opcoes_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]

    turmas = st.multiselect("Turmas (Espelhamento)", opcoes_turmas, placeholder="Selecione as turmas...")
    
    st.divider()
    
    st.subheader("🗓️ Data")
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
            
    st.caption(f"Trimestre: {trimestre_doc}")

# --- 6. SEPARAÇÃO DE CONTEÚDOS ---
dados_ano = CURRICULO_DB.get(nivel_selecionado, {})
opcoes_tec = []
opcoes_ing = []

# Termos que identificam Inglês
termos_ing = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING', 'VOCABULÁRIO', 'FAMILY', 'COLORS']

for chave, lista_itens in dados_ano.items():
    if lista_itens:
        eixo_teste = lista_itens[0].get('eixo', '').upper()
        cat_teste = chave.upper()
        
        eh_ingles = any(t in eixo_teste for t in termos_ing) or any(t in cat_teste for t in termos_ing)
        
        if eh_ingles:
            opcoes_ing.append(chave)
        else:
            opcoes_tec.append(chave)

# --- 7. ÁREA PRINCIPAL (SELEÇÃO) ---

# Métricas
total_tec = sum(1 for x in st.session_state.conteudos_selecionados if x['tipo'] == 'Tecnologia')
total_ing = sum(1 for x in st.session_state.conteudos_selecionados if x['tipo'] == 'Inglês')
col1, col2, col3 = st.columns(3)
col1.metric("Tecnologia", total_tec)
col2.metric("Inglês", total_ing)
col3.metric("Total", total_tec + total_ing)

st.markdown("### 📚 Seleção de Conteúdos")

tab_tec, tab_ing, tab_rev = st.tabs(["💻 Tecnologia & Cultura", "📖 Linguagens (Inglês)", "📋 Revisão"])

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
        
        st.markdown(f"**Objetivo:** {item_tec['objetivo']}")
        
        if st.button("Adicionar Tecnologia ➕", key="btn_tec"):
            novo = {
                "tipo": "Tecnologia", "eixo": item_tec['eixo'], "geral": geral_tec,
                "especifico": esp_tec, "objetivo": item_tec['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.toast("Adicionado!", icon="✅")
                st.rerun()
            else:
                st.warning("Já adicionado.")
    else:
        st.info("Sem conteúdos de tecnologia para este ano.")

# --- ABA INGLÊS ---
with tab_ing:
    if opcoes_ing:
        c1, c2 = st.columns(2)
        with c1:
            geral_ing = st.selectbox("Tópico", opcoes_ing, key="ing_g")
            
        itens_ing = dados_ano[geral_ing]
        opcoes_esp_ing = [i['especifico'] for i in itens_ing]
        
        with c2:
            esp_ing = st.selectbox("Prática", opcoes_esp_ing, key="ing_e")
            
        item_ing = next(i for i in itens_ing if i['especifico'] == esp_ing)
        
        st.markdown(f"**Objetivo:** {item_ing['objetivo']}")
        
        if st.button("Adicionar Inglês ➕", key="btn_ing"):
            novo = {
                "tipo": "Inglês", "eixo": item_ing.get('eixo', 'Língua Inglesa'), "geral": geral_ing,
                "especifico": esp_ing, "objetivo": item_ing['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.toast("Adicionado!", icon="✅")
                st.rerun()
            else:
                st.warning("Já adicionado.")
    else:
        st.info("Sem conteúdos de inglês para este ano.")

# --- ABA REVISÃO ---
with tab_rev:
    if st.session_state.conteudos_selecionados:
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            border = "card-tech" if item['tipo'] == "Tecnologia" else "card-eng"
            icone = "💻" if item['tipo'] == "Tecnologia" else "📖"
            
            c_txt, c_btn = st.columns([0.9, 0.1])
            with c_txt:
                st.markdown(f"""
                <div class="info-card {border}">
                    <strong>{icone} {item['geral']}</strong><br>{item['especifico']}
                </div>""", unsafe_allow_html=True)
            with c_btn:
                st.write("")
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()
    else:
        st.info("Nenhum item selecionado.")

# --- 8. DETALHAMENTO ---
st.markdown("### 📝 Desenvolvimento da Aula")

with st.container():
    c1, c2 = st.columns(2)
    with c1:
        situacao_didatica = st.text_area("Situação Didática (Obrigatório)", height=150, placeholder="Descreva a metodologia...")
    with c2:
        recursos = st.text_area("Recursos Didáticos (Obrigatório)", height=150, placeholder="Materiais e equipamentos...")
    
    c3, c4 = st.columns(2)
    with c3:
        avaliacao = st.text_area("Avaliação", height=100)
    with c4:
        recuperacao = st.text_area("Recuperação Contínua (Obrigatório)", height=100)

# --- 9. GERAÇÃO DO WORD ---
def gerar_docx(conteudos, dados):
    doc = Document()
    
    for section in doc.sections:
        section.top_margin = Cm(1.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Cabeçalho com Logos
    table_head = doc.add_table(rows=1, cols=3)
    table_head.autofit = False
    
    # Imagens locais
    logo_pref = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
    logo_esc = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"

    # Logo Esq
    c1 = table_head.cell(0,0); c1.width = Cm(2.5)
    if os.path.exists(logo_pref):
        try: c1.paragraphs[0].add_run().add_picture(logo_pref, width=Cm(2.0))
        except: pass
        
    # Texto Centro
    c2 = table_head.cell(0,1); c2.width = Cm(11.0)
    p = c2.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\n").bold = True
    p.add_run("CEIEF RAFAEL AFFONSO LEITE\n").bold = True
    p.add_run("Planejamento de Linguagens e Tecnologias")
    
    # Logo Dir
    c3 = table_head.cell(0,2); c3.width = Cm(2.5)
    p_dir = c3.paragraphs[0]
    p_dir.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists(logo_esc):
        try: p_dir.add_run().add_picture(logo_esc, width=Cm(2.0))
        except: pass

    doc.add_paragraph()

    # Dados
    p_info = doc.add_paragraph()
    p_info.add_run(f"Período: {dados['Periodo']}\n").bold = True
    p_info.add_run(f"Professor(a): {dados['Professor']}\n")
    p_info.add_run(f"Ano: {dados['Ano']} | Turmas: {dados['Turmas']} | {dados['Trimestre']}")
    
    doc.add_paragraph("-" * 80)

    # Tabela Conteúdos
    if conteudos:
        doc.add_heading("Objetivos e Conteúdos", level=3)
        t = doc.add_table(rows=1, cols=3)
        t.style = 'Table Grid'
        hdr = t.rows[0].cells
        hdr[0].text = "Eixo / Geral"; hdr[1].text = "Conteúdo Específico"; hdr[2].text = "Objetivo"
        
        for cell in hdr:
            cell.paragraphs[0].runs[0].bold = True
            
        for item in conteudos:
            row = t.add_row().cells
            row[0].text = f"{item['eixo']}\n({item['geral']})"
            row[1].text = item['especifico']
            row[2].text = item['objetivo']

    doc.add_paragraph()
    doc.add_heading("Desenvolvimento", level=3)
    
    p = doc.add_paragraph()
    p.add_run("Situação Didática:\n").bold = True
    p.add_run(dados['Didatica'])
    
    p = doc.add_paragraph()
    p.add_run("\nRecursos Didáticos:\n").bold = True
    p.add_run(dados['Recursos'])
    
    p = doc.add_paragraph()
    p.add_run("\nAvaliação:\n").bold = True
    p.add_run(dados['Avaliacao'])
    
    p = doc.add_paragraph()
    p.add_run("\nRecuperação Contínua:\n").bold = True
    p.add_run(dados['Recuperacao'])

    f = BytesIO()
    doc.save(f)
    f.seek(0)
    return f

# --- 10. BOTÃO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)

if st.button("GERAR DOCUMENTO WORD", type="primary", use_container_width=True):
    # Correção da lógica que causava erro de sintaxe
    conteudos_selecionados = st.session_state.conteudos_selecionados
    
    if not professor or not situacao_didatica or not conteudos_selecionados:
        st.error("Preencha o professor, a situação didática e adicione conteúdos.")
    elif not turmas:
        st.error("Selecione as turmas.")
    else:
        dados = {
            "Professor": professor,
            "Ano": nivel_selecionado,
            "Turmas": ", ".join(turmas),
            "Periodo": periodo_texto,
            "Trimestre": trimestre_doc,
            "Didatica": situacao_didatica,
            "Recursos": recursos,
            "Avaliacao": avaliacao,
            "Recuperacao": recuperacao
        }
        
        arq = gerar_docx(conteudos_selecionados, dados)
        nome_arq = f"Plan_{nivel_selecionado.replace(' ','')}_{datetime.now().strftime('%d%m')}.docx"
        
        st.success("Documento gerado com sucesso!")
        st.download_button("📥 Baixar Arquivo", arq, nome_arq, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# Rodapé
st.markdown("""
    <div class="footer">
        Sistema para uso interno e exclusivo do CEIEF Rafael Affonso Leite
    </div>
""", unsafe_allow_html=True)
