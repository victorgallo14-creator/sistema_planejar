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
    page_title="Planejamento Digital",
    layout="wide",
    page_icon="📝",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "CLEAN & MODERN" ---
st.markdown("""
<style>
    /* Fonte e Cores Globais */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }
    
    /* Fundo da Aplicação */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Cabeçalho Limpo */
    .header-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .header-subtitle {
        font-size: 1.1rem;
        font-weight: 400;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 1rem;
    }

    /* Cards de Seleção (Estilo Material Design) */
    .info-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 1rem;
        border-top: 5px solid #3B82F6; /* Azul Padrão */
    }
    
    .card-tech { border-top-color: #3B82F6; }
    .card-eng { border-top-color: #EA580C; } /* Laranja para Inglês */

    .card-header {
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        margin-bottom: 0.5rem;
    }
    
    .card-body {
        font-size: 1.1rem;
        font-weight: 500;
        color: #1E293B;
        margin-bottom: 0.5rem;
    }
    
    .card-footer {
        background-color: #F1F5F9;
        padding: 0.75rem;
        border-radius: 6px;
        font-size: 0.9rem;
        color: #475569;
        font-style: italic;
    }

    /* Ajuste de Botões */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
    }
    
    /* Melhoria na Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    
    /* Títulos de Seção */
    h3 {
        color: #1E293B;
        font-weight: 600;
        padding-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO NATIVO (RESPONSIVO) ---
# Usar colunas do Streamlit garante que funcione bem no celular
c_logo_e, c_titulo, c_logo_d = st.columns([1, 4, 1])

with c_logo_e:
    if os.path.exists("logo_prefeitura.png"):
        st.image("logo_prefeitura.png", use_container_width=True)
    elif os.path.exists("logo_prefeitura.jpg"):
        st.image("logo_prefeitura.jpg", use_container_width=True)

with c_titulo:
    st.markdown('<div class="header-title">CEIEF RAFAEL AFFONSO LEITE</div>', unsafe_allow_html=True)
    st.markdown('<div class="header-subtitle">Planejamento Pedagógico Digital</div>', unsafe_allow_html=True)

with c_logo_d:
    if os.path.exists("logo_escola.png"):
        st.image("logo_escola.png", use_container_width=True)
    elif os.path.exists("logo_escola.jpg"):
        st.image("logo_escola.jpg", use_container_width=True)

# --- 4. INICIALIZAÇÃO DE VARIÁVEIS ---
if 'conteudos_selecionados' not in st.session_state:
    st.session_state.conteudos_selecionados = []

# --- 5. BARRA LATERAL (CONFIGURAÇÕES) ---
with st.sidebar:
    st.header("⚙️ Parâmetros")
    
    professor = st.text_input("Professor(a)", placeholder="Nome completo...")
    
    # Seleção de Ano
    anos = list(CURRICULO_DB.keys())
    nivel_selecionado = st.selectbox("Ano de Escolaridade", anos)
    
    # Limpa dados se mudar o ano
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = nivel_selecionado
    if st.session_state.ano_anterior != nivel_selecionado:
        st.session_state.conteudos_selecionados = []
        st.session_state.ano_anterior = nivel_selecionado
        st.toast("Ano alterado. Planejamento reiniciado.", icon="🔄")

    # Regras de Turmas
    qtd_turmas = {
        "Maternal II": 2, "Etapa I": 3, "Etapa II": 3,
        "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3
    }
    max_t = qtd_turmas.get(nivel_selecionado, 3)
    
    prefixo = f"{nivel_selecionado} - Turma" if "Maternal" in nivel_selecionado or "Etapa" in nivel_selecionado else f"{nivel_selecionado} "
    opcoes_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]

    turmas = st.multiselect("Turmas", opcoes_turmas, placeholder="Selecione...")
    
    st.divider()
    
    st.subheader("🗓️ Data")
    meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 
             8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    mes_nome = st.selectbox("Mês", list(meses.values()))
    mes_num = [k for k, v in meses.items() if v == mes_nome][0]
    ano_atual = datetime.now().year
    
    # Lógica de Período
    if mes_num == 2:
        periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
        trimestre_doc = "1º Trimestre"
        st.info("Fevereiro: Planejamento Mensal")
    else:
        quinzena = st.radio("Período", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
        ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
        
        # Definição do Trimestre
        if mes_num <= 4: trimestre_doc = "1º Trimestre"
        elif mes_num <= 8: trimestre_doc = "2º Trimestre"
        else: trimestre_doc = "3º Trimestre"

        if "1ª" in quinzena:
            periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}"
        else:
            periodo_texto = f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
            
    st.caption(f"Referência: {trimestre_doc}")

# --- 6. SEPARAÇÃO INTELIGENTE DO CURRÍCULO ---
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

# --- 7. ÁREA PRINCIPAL (LAYOUT DE ABAS LIMPO) ---

# Métricas de Progresso
total_tec = sum(1 for x in st.session_state.conteudos_selecionados if x['tipo'] == 'Tecnologia')
total_ing = sum(1 for x in st.session_state.conteudos_selecionados if x['tipo'] == 'Inglês')

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Itens de Tecnologia", total_tec)
col_m2.metric("Itens de Inglês", total_ing)
col_m3.metric("Total Selecionado", total_tec + total_ing)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["💻 Adicionar Tecnologia", "📖 Adicionar Inglês", "📋 Revisar Planejamento"])

# --- ABA 1: TECNOLOGIA ---
with tab1:
    if opcoes_tec:
        c1, c2 = st.columns(2)
        with c1:
            geral_tec = st.selectbox("Eixo Temático", opcoes_tec, key="tec_geral")
        
        itens_tec = dados_ano[geral_tec]
        opcoes_esp_tec = [i['especifico'] for i in itens_tec]
        
        with c2:
            esp_tec = st.selectbox("Habilidade Específica", opcoes_esp_tec, key="tec_esp")
            
        item_tec = next(i for i in itens_tec if i['especifico'] == esp_tec)
        
        # Card de Visualização Limpo
        st.markdown(f"""
        <div class="info-card card-tech">
            <div class="card-header">OBJETIVO DE APRENDIZAGEM</div>
            <div class="card-body">{item_tec['objetivo']}</div>
            <div class="card-footer">📅 Previsão Curricular: {item_tec['trimestre']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Adicionar Item de Tecnologia", key="add_tec"):
            novo = {
                "tipo": "Tecnologia",
                "eixo": item_tec['eixo'],
                "geral": geral_tec,
                "especifico": esp_tec,
                "objetivo": item_tec['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.toast("Tecnologia adicionada!", icon="✅")
                st.rerun()
            else:
                st.warning("Item já está na lista.")
    else:
        st.info("Nenhum conteúdo de tecnologia disponível para este ano.")

# --- ABA 2: INGLÊS ---
with tab2:
    if opcoes_ing:
        c1, c2 = st.columns(2)
        with c1:
            geral_ing = st.selectbox("Eixo / Tópico", opcoes_ing, key="ing_geral")
            
        itens_ing = dados_ano[geral_ing]
        opcoes_esp_ing = [i['especifico'] for i in itens_ing]
        
        with c2:
            esp_ing = st.selectbox("Prática de Linguagem", opcoes_esp_ing, key="ing_esp")
            
        item_ing = next(i for i in itens_ing if i['especifico'] == esp_ing)
        
        # Card de Visualização Limpo (Cor diferente)
        st.markdown(f"""
        <div class="info-card card-eng">
            <div class="card-header">OBJETIVO DE APRENDIZAGEM</div>
            <div class="card-body">{item_ing['objetivo']}</div>
            <div class="card-footer">📅 Previsão Curricular: {item_ing['trimestre']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Adicionar Item de Inglês", key="add_ing"):
            novo = {
                "tipo": "Inglês",
                "eixo": item_ing.get('eixo', 'Língua Inglesa'),
                "geral": geral_ing,
                "especifico": esp_ing,
                "objetivo": item_ing['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.toast("Inglês adicionado!", icon="✅")
                st.rerun()
            else:
                st.warning("Item já está na lista.")
    else:
        st.info("Nenhum conteúdo de inglês disponível para este ano.")

# --- ABA 3: REVISÃO ---
with tab3:
    if len(st.session_state.conteudos_selecionados) > 0:
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            classe_cor = "card-tech" if item['tipo'] == "Tecnologia" else "card-eng"
            icone = "💻" if item['tipo'] == "Tecnologia" else "🇬🇧"
            
            c_texto, c_del = st.columns([0.9, 0.1])
            with c_texto:
                st.markdown(f"""
                <div class="info-card {classe_cor}" style="padding: 1rem; margin-bottom: 0.5rem;">
                    <div style="font-weight:bold; color:#334155;">{icone} {item['geral']}</div>
                    <div style="font-size:0.9rem;">{item['especifico']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c_del:
                st.write("") # Espaço para alinhar
                if st.button("❌", key=f"del_{i}", help="Remover"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()
    else:
        st.info("Sua lista de planejamento está vazia.")

# --- 8. DETALHAMENTO E GERAÇÃO ---
st.markdown("### 📝 Desenvolvimento da Aula")

with st.container():
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        situacao_didatica = st.text_area("Situação Didática (Obrigatório)", height=150, help="Descreva a metodologia...")
    with col_d2:
        recursos = st.text_area("Recursos Didáticos (Obrigatório)", height=150, help="Materiais e equipamentos...")
    
    col_d3, col_d4 = st.columns(2)
    with col_d3:
        avaliacao = st.text_area("Avaliação", height=100)
    with col_d4:
        recuperacao = st.text_area("Recuperação Contínua (Obrigatório)", height=100)

# --- 9. FUNÇÃO GERAR WORD ---
def gerar_docx(conteudos, dados):
    doc = Document()
    
    # Margens (ABNT Padrão para Doc Interno)
    for section in doc.sections:
        section.top_margin = Cm(1.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)

    # Estilos
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Tabela de Cabeçalho (Invisível para alinhar logos)
    table_head = doc.add_table(rows=1, cols=3)
    table_head.autofit = False
    
    # Logo Esq
    c1 = table_head.cell(0,0)
    c1.width = Cm(2.5)
    if os.path.exists("logo_prefeitura.png"):
        try: c1.paragraphs[0].add_run().add_picture("logo_prefeitura.png", width=Cm(2.0))
        except: pass
    elif os.path.exists("logo_prefeitura.jpg"):
        try: c1.paragraphs[0].add_run().add_picture("logo_prefeitura.jpg", width=Cm(2.0))
        except: pass

    # Texto Centro
    c2 = table_head.cell(0,1)
    c2.width = Cm(11.0)
    p = c2.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\n").bold = True
    p.add_run("CEIEF RAFAEL AFFONSO LEITE\n").bold = True
    p.add_run("Planejamento de Linguagens e Tecnologias")

    # Logo Dir
    c3 = table_head.cell(0,2)
    c3.width = Cm(2.5)
    p_dir = c3.paragraphs[0]
    p_dir.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists("logo_escola.png"):
        try: p_dir.add_run().add_picture("logo_escola.png", width=Cm(2.0))
        except: pass
    elif os.path.exists("logo_escola.jpg"):
        try: p_dir.add_run().add_picture("logo_escola.jpg", width=Cm(2.0))
        except: pass

    doc.add_paragraph()

    # Dados
    p_dados = doc.add_paragraph()
    p_dados.add_run(f"Período: {dados['Periodo']}\n").bold = True
    p_dados.add_run(f"Professor(a): {dados['Professor']}\n")
    p_dados.add_run(f"Ano: {dados['Ano']} | Turmas: {dados['Turmas']} | {dados['Trimestre']}")
    
    doc.add_paragraph("-" * 80)

    # Tabela de Conteúdos
    if conteudos:
        doc.add_heading("Objetivos e Conteúdos", level=3)
        t = doc.add_table(rows=1, cols=3)
        t.style = 'Table Grid'
        
        # Cabeçalho da Tabela
        hdr = t.rows[0].cells
        hdr[0].text = "Eixo / Geral"
        hdr[1].text = "Conteúdo Específico"
        hdr[2].text = "Objetivo"
        
        for cell in hdr:
            cell.paragraphs[0].runs[0].bold = True
            
        for item in conteudos:
            row = t.add_row().cells
            row[0].text = f"{item['eixo']}\n({item['geral']})"
            row[1].text = item['especifico']
            row[2].text = item['objetivo']

    doc.add_paragraph()

    # Campos de Texto
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

    # Salvar na memória
    f = BytesIO()
    doc.save(f)
    f.seek(0)
    return f

# --- 10. BOTÃO FINAL ---
st.markdown("<br>", unsafe_allow_html=True)

if st.button("GERAR DOCUMENTO WORD", type="primary", use_container_width=True):
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
        
        st.success("Documento gerado!")
        st.download_button("📥 Baixar Arquivo", arq, nome_arq, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# Rodapé Simples
st.markdown("<div style='text-align:center; color:#999; margin-top:50px; font-size:12px;'>Desenvolvido por Victor | CEIEF Rafael Affonso Leite © 2025</div>", unsafe_allow_html=True)
