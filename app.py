import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import calendar
from datetime import datetime

# IMPORTAÇÃO DO CURRÍCULO
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO: O arquivo 'dados_curriculo.py' não foi encontrado.")
    st.stop()

# --- 1. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Planejamento CEIEF Rafael Affonso Leite", layout="wide", page_icon="🏫")

st.markdown("""
<style>
    .main-header { color: #1E3A8A; text-align: center; font-size: 26px; font-weight: bold; margin-bottom: 0px; }
    .sub-header { color: #555; text-align: center; font-size: 18px; margin-bottom: 20px; }
    .tech-box { border-left: 5px solid #2E86C1; background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    .eng-box { border-left: 5px solid #C0392B; background-color: #fdf2f0; padding: 10px; border-radius: 5px; margin-bottom: 5px; }
    .footer { text-align: center; color: #888; font-size: 12px; margin-top: 50px; border-top: 1px solid #ddd; padding-top: 10px; }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
    font-size: 18px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">CEIEF RAFAEL AFFONSO LEITE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Planejamento de Linguagens e Tecnologias</div>', unsafe_allow_html=True)

# --- 2. INICIALIZAÇÃO ---
if 'conteudos_selecionados' not in st.session_state:
    st.session_state.conteudos_selecionados = []

# --- 3. BARRA LATERAL ---
with st.sidebar:
    st.header("⚙️ Configuração")
    professor = st.text_input("Nome do Professor(a)")
    
    anos_disponiveis = list(CURRICULO_DB.keys())
    nivel_selecionado = st.selectbox("Ano de Escolaridade", anos_disponiveis)
    
    # Limpa se mudar o ano
    if 'ano_anterior' not in st.session_state:
        st.session_state.ano_anterior = nivel_selecionado
    if st.session_state.ano_anterior != nivel_selecionado:
        st.session_state.conteudos_selecionados = []
        st.session_state.ano_anterior = nivel_selecionado
        st.toast("Ano alterado. Lista limpa.", icon="🧹")

    # --- CONFIGURAÇÃO DE TURMAS ---
    qtd_turmas_por_ano = {
        "Maternal II": 2, # 2 turmas
        "Etapa I": 3,     # 3 turmas
        "Etapa II": 3,    # 3 turmas
        "1º Ano": 3,      # 3 turmas
        "2º Ano": 3,      # 3 turmas
        "3º Ano": 3,      # 3 turmas
        "4º Ano": 3,      # 3 turmas
        "5º Ano": 3       # 3 turmas
    }
    
    max_turmas = qtd_turmas_por_ano.get(nivel_selecionado, 3)
    
    # Gera nomes das turmas baseado no nível
    if "Maternal" in nivel_selecionado or "Etapa" in nivel_selecionado:
         # Ex: "Etapa I - 1"
         opcoes_turmas = [f"{nivel_selecionado} - {i}" for i in range(1, max_turmas + 1)]
    else:
         # Ex: "1º Ano 1"
         opcoes_turmas = [f"{nivel_selecionado} {i}" for i in range(1, max_turmas + 1)]

    turmas_selecionadas = st.multiselect(
        "Selecione as Turmas (Espelhamento)", 
        opcoes_turmas,
        placeholder="Selecione as turmas...", 
        help="Selecione todas as turmas que utilizarão este mesmo planejamento."
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
            
    st.info(f"📅 Referência: {trimestre_doc}")

# --- 4. SEPARAÇÃO AUTOMÁTICA DOS CONTEÚDOS ---
dados_ano = CURRICULO_DB.get(nivel_selecionado, {})
opcoes_tec = []
opcoes_ing = []

termos_ingles = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING', 'VOCABULÁRIO']

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

tab_tec, tab_ing = st.tabs(["💻 Tecnologia & Cultura Digital", "📚 Linguagens (Inglês)"])

# --- ABA TECNOLOGIA ---
with tab_tec:
    st.caption("Selecione os conteúdos de Cultura Digital, Mundo Digital e Pensamento Computacional.")
    
    if opcoes_tec:
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            geral_tec = st.selectbox("Eixo / Conteúdo Geral", opcoes_tec, key="sel_tec_geral")
        
        itens_tec = dados_ano[geral_tec]
        opcoes_especificas_tec = [i['especifico'] for i in itens_tec]
        
        with col_t2:
            especifico_tec = st.selectbox("Conteúdo Específico", opcoes_especificas_tec, key="sel_tec_esp")
            
        item_selecionado_tec = next(i for i in itens_tec if i['especifico'] == especifico_tec)
        
        st.markdown(f"**Objetivo:** {item_selecionado_tec['objetivo']}")
        st.markdown(f"🗓️ *Previsão: {item_selecionado_tec['trimestre']}*")
        
        if st.button("➕ Adicionar Tecnologia", key="btn_add_tec"):
            novo = {
                "tipo": "Tecnologia",
                "eixo": item_selecionado_tec['eixo'],
                "geral": geral_tec,
                "especifico": especifico_tec,
                "objetivo": item_selecionado_tec['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.success("Conteúdo de Tecnologia adicionado!")
                st.rerun()
            else:
                st.warning("Já adicionado.")
    else:
        st.info("Não há conteúdos de tecnologia cadastrados para esta etapa.")

# --- ABA INGLÊS ---
with tab_ing:
    st.caption("Selecione os conteúdos de Oralidade, Leitura e Escrita.")
    
    if opcoes_ing:
        col_i1, col_i2 = st.columns([1, 1])
        with col_i1:
            geral_ing = st.selectbox("Tópico / Habilidade", opcoes_ing, key="sel_ing_geral")
            
        itens_ing = dados_ano[geral_ing]
        opcoes_especificas_ing = [i['especifico'] for i in itens_ing]
        
        with col_i2:
            especifico_ing = st.selectbox("Prática Específica", opcoes_especificas_ing, key="sel_ing_esp")
            
        item_selecionado_ing = next(i for i in itens_ing if i['especifico'] == especifico_ing)
        
        st.markdown(f"**Objetivo:** {item_selecionado_ing['objetivo']}")
        st.markdown(f"🗓️ *Previsão: {item_selecionado_ing['trimestre']}*")
        
        if st.button("➕ Adicionar Inglês", key="btn_add_ing"):
            novo = {
                "tipo": "Inglês",
                "eixo": item_selecionado_ing.get('eixo', 'Língua Inglesa'),
                "geral": geral_ing,
                "especifico": especifico_ing,
                "objetivo": item_selecionado_ing['objetivo']
            }
            if novo not in st.session_state.conteudos_selecionados:
                st.session_state.conteudos_selecionados.append(novo)
                st.success("Conteúdo de Inglês adicionado!")
                st.rerun()
            else:
                st.warning("Já adicionado.")
    else:
        st.info("Selecione um ano que tenha currículo de inglês cadastrado.")

# --- 6. RESUMO ---
st.markdown("---")
st.subheader(f"📋 Planejamento da Quinzena ({len(st.session_state.conteudos_selecionados)} itens)")

if len(st.session_state.conteudos_selecionados) > 0:
    for i, item in enumerate(st.session_state.conteudos_selecionados):
        css_class = "tech-box" if item["tipo"] == "Tecnologia" else "eng-box"
        icone = "💻" if item["tipo"] == "Tecnologia" else "📚"
        
        col_res1, col_res2 = st.columns([0.9, 0.1])
        with col_res1:
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{icone} {item['eixo']}</strong> | {item['geral']}<br>
                • {item['especifico']}<br>
                <small><em>Objetivo: {item['objetivo']}</em></small>
            </div>
            """, unsafe_allow_html=True)
        with col_res2:
            if st.button("🗑️", key=f"del_{i}"):
                st.session_state.conteudos_selecionados.pop(i)
                st.rerun()
else:
    st.info("Nenhum conteúdo adicionado. Use as abas acima para montar sua aula.")

st.markdown("---")

# --- 7. CAMPOS PEDAGÓGICOS ---
st.markdown("### 📝 Detalhamento Didático")

c1, c2 = st.columns(2)
with c1:
    situacao_didatica = st.text_area("Descrição da Situação Didática (Obrigatório)", height=150,
                                     placeholder="Descreva como as atividades de Tecnologia e/ou Inglês serão desenvolvidas...")
with c2:
    recursos = st.text_area("Recursos Didáticos (Obrigatório)", height=150,
                            placeholder="Computadores, Internet, Projetor, Materiais Maker, Flashcards...")

c3, c4 = st.columns(2)
with c3:
    avaliacao = st.text_area("Avaliação", placeholder="Como será verificado o aprendizado?")
with c4:
    recuperacao = st.text_area("Recuperação Contínua (Obrigatório)", 
                               placeholder="Estratégias para alunos com dificuldades...")

# --- 8. GERAR WORD ---
def gerar_docx(conteudos, dados_extras):
    doc = Document()
    
    sections = doc.sections
    for section in sections:
        section.top_margin = Cm(1.0)
        section.bottom_margin = Cm(1.5)
        section.left_margin = Cm(1.5)
        section.right_margin = Cm(1.5)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(10)

    # Cabeçalho
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run('PREFEITURA MUNICIPAL DE LIMEIRA\n').bold = True
    p.add_run('CEIEF RAFAEL AFFONSO LEITE\n').bold = True
    p.add_run('Planejamento de Linguagens e Tecnologias')

    # Identificação
    doc.add_paragraph()
    p_info = doc.add_paragraph()
    p_info.add_run(f'Período: {dados_extras["Periodo"]}\n')
    p_info.add_run(f'Professor(a): {dados_extras["Professor"]}\n')
    p_info.add_run(f'Ano: {dados_extras["Ano"]} | Turmas: {dados_extras["Turmas"]} | {dados_extras["Trimestre"]}')
    
    doc.add_paragraph("-" * 90)

    if conteudos:
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr = table.rows[0].cells
        hdr[0].text = 'Eixo'
        hdr[1].text = 'Conteúdo Geral'
        hdr[2].text = 'Conteúdo Específico'
        hdr[3].text = 'Objetivo do Ano'
        
        for cell in hdr:
            cell.paragraphs[0].runs[0].bold = True
            
        for item in conteudos:
            row = table.add_row().cells
            row[0].text = item['eixo']
            row[1].text = item['geral']
            row[2].text = item['especifico']
            row[3].text = item['objetivo']

    doc.add_paragraph() 
    
    doc.add_heading('Desenvolvimento', level=2)
    p = doc.add_paragraph()
    p.add_run("Situação Didática: ").bold = True
    p.add_run(dados_extras["Didatica"])
    
    p = doc.add_paragraph()
    p.add_run("\nRecursos Didáticos: ").bold = True
    p.add_run(dados_extras["Recursos"])
    
    p = doc.add_paragraph()
    p.add_run("\nAvaliação: ").bold = True
    p.add_run(dados_extras["Avaliacao"])
    
    p = doc.add_paragraph()
    p.add_run("\nRecuperação Contínua: ").bold = True
    p.add_run(dados_extras["Recuperacao"])

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

if st.button("Gerar Arquivo Word"):
    if not professor or not situacao_didatica or len(st.session_state.conteudos_selecionados) == 0:
        st.error("Preencha o professor, a situação didática e adicione pelo menos um conteúdo.")
    elif not turmas_selecionadas:
        st.error("Selecione pelo menos uma turma para gerar o planejamento.")
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
        
        # Nome do arquivo mais limpo
        safe_turmas = turmas_texto.replace(' ', '').replace(',', '_')
        if len(safe_turmas) > 20: safe_turmas = "Multiplas_Turmas"
        nome_arquivo = f"Plan_{nivel_selecionado}_{safe_turmas}.docx"
        
        st.success("Planejamento gerado com sucesso!")
        st.download_button("Baixar Planejamento (.docx)", arq, nome_arquivo)

# --- RODAPÉ ---
st.markdown("""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b> | CEIEF Rafael Affonso Leite © 2025
    </div>
""", unsafe_allow_html=True)