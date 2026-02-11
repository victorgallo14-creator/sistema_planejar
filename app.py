import streamlit as st
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from io import BytesIO
import calendar
from datetime import datetime
import os
import base64

# --- CONFIGURAÇÃO DA PÁGINA (WIDE MODE & TITLE) ---
st.set_page_config(
    page_title="Sistema Planejar",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="collapsed"
)

# IMPORTAÇÃO DO CURRÍCULO
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO CRÍTICO: Base de dados curricular não encontrada.")
    st.stop()

# --- ESTILIZAÇÃO CSS AVANÇADA (PREMIUM UI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
        color: #1e293b;
        background-color: #f8fafc;
    }
    
    /* Header Premium */
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
    .header-text h1 {
        margin: 0;
        font-weight: 700;
        font-size: 2rem;
        color: white;
    }
    .header-text p {
        margin: 5px 0 0 0;
        font-weight: 300;
        opacity: 0.9;
        font-size: 1rem;
    }

    /* Cards Modernos */
    .card-container {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }
    .card-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    
    /* Tags de Status */
    .status-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .tag-tech { background-color: #dbeafe; color: #1e40af; }
    .tag-eng { background-color: #fee2e2; color: #991b1b; }

    /* Barra de Progresso Customizada */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Botões Refinados */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    .primary-btn {
        background-color: #1e3a8a !important;
        color: white !important;
    }
    
    /* Ajuste para Mobile */
    @media (max-width: 768px) {
        .premium-header {
            flex-direction: column;
            text-align: center;
            gap: 1rem;
        }
        .header-logo {
            display: none; /* Esconde logo no mobile para economizar espaço */
        }
    }
    
    /* Wizard Steps */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 2rem;
        padding: 0 1rem;
    }
    .step {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #e2e8f0;
        color: #64748b;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        position: relative;
        z-index: 1;
    }
    .step.active {
        background-color: #3b82f6;
        color: white;
        box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.2);
    }
    .step-line {
        position: absolute;
        top: 15px;
        left: 0;
        right: 0;
        height: 2px;
        background-color: #e2e8f0;
        z-index: 0;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER PREMIUM ---
def render_header():
    st.markdown("""
    <div class="premium-header">
        <div class="header-text">
            <h1>Sistema Planejar</h1>
            <p>Sistema interno - CEIEF Rafael Affonso Leite</p>
        </div>
        <div class="header-logo" style="font-size: 2.5rem;">
            🏫
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- GERENCIAMENTO DE ESTADO ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state:
    st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state:
    st.session_state.config = {}

# --- NAVEGAÇÃO ENTRE PASSOS ---
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

# --- PASSO 1: CONFIGURAÇÃO INICIAL (WIZARD) ---
def render_step1():
    st.markdown("### 1️⃣ Configuração da Aula")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Professor(a) Responsável", value=st.session_state.config.get('professor', ''))
            
            anos = list(CURRICULO_DB.keys())
            nivel_idx = 0
            if 'nivel' in st.session_state.config and st.session_state.config['nivel'] in anos:
                nivel_idx = anos.index(st.session_state.config['nivel'])
            
            nivel = st.selectbox("Ano de Escolaridade", anos, index=nivel_idx)
            
            # Lógica de Turmas
            qtd_turmas = {
                "Maternal II": 2, "Etapa I": 3, "Etapa II": 3,
                "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3
            }
            max_t = qtd_turmas.get(nivel, 3)
            prefixo = f"{nivel} - Turma" if "Maternal" in nivel or "Etapa" in nivel else f"{nivel} "
            opcoes_turmas = [f"{prefixo}{i}" for i in range(1, max_t + 1)]
            
            turmas = st.multiselect("Turmas (Espelhamento)", opcoes_turmas, default=st.session_state.config.get('turmas', []))

        with c2:
            meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 
                     8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            
            mes_nome = st.selectbox("Mês de Referência", list(meses.values()))
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("ℹ️ Fevereiro: Planejamento Mensal")
            else:
                quinzena = st.radio("Período Quinzenal", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"

                if "1ª" in quinzena:
                    periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}"
                else:
                    periodo_texto = f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
            
            st.success(f"🗓️ **Período Selecionado:** {periodo_texto} ({trimestre_doc})")

        st.markdown('</div>', unsafe_allow_html=True)
        
        # Validação para avançar
        if st.button("Próximo Passo ➡️", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.toast("⚠️ Preencha o nome do professor e selecione as turmas.", icon="⚠️")
            else:
                # Salva no estado
                st.session_state.config = {
                    'professor': professor,
                    'nivel': nivel,
                    'turmas': turmas,
                    'periodo': periodo_texto,
                    'trimestre': trimestre_doc
                }
                # Limpa conteúdos se mudou o nível
                if 'nivel_antigo' in st.session_state and st.session_state.nivel_antigo != nivel:
                    st.session_state.conteudos_selecionados = []
                st.session_state.nivel_antigo = nivel
                
                next_step()
                st.rerun()

# --- PASSO 2: SELEÇÃO DE CONTEÚDO (SHOPPING STYLE) ---
def render_step2():
    st.markdown(f"### 2️⃣ Seleção de Conteúdos ({st.session_state.config['nivel']})")
    
    # Lógica de Separação
    dados_ano = CURRICULO_DB.get(st.session_state.config['nivel'], {})
    opcoes_tec = []
    opcoes_ing = []
    termos_ing = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING', 'VOCABULÁRIO', 'FAMILY', 'COLORS']

    for chave, lista in dados_ano.items():
        if lista:
            eixo = lista[0].get('eixo', '').upper()
            chave_upper = chave.upper()
            if any(t in eixo for t in termos_ing) or any(t in chave_upper for t in termos_ing):
                opcoes_ing.append(chave)
            else:
                opcoes_tec.append(chave)

    # Abas Modernas
    t1, t2 = st.tabs(["💻 Tecnologia & Cultura", "🇬🇧 Linguagens (Inglês)"])
    
    # --- ABA TECNOLOGIA ---
    with t1:
        if opcoes_tec:
            col_l, col_r = st.columns([1, 1])
            with col_l:
                geral = st.selectbox("Eixo Temático", opcoes_tec, key="tec_g")
            
            itens = dados_ano[geral]
            opcoes_esp = [i['especifico'] for i in itens]
            with col_r:
                especifico = st.selectbox("Habilidade", opcoes_esp, key="tec_e")
            
            item_sel = next(i for i in itens if i['especifico'] == especifico)
            
            # Card Preview
            st.markdown(f"""
            <div class="card-container" style="border-left: 5px solid #3b82f6;">
                <span class="status-tag tag-tech">Tecnologia</span>
                <h4>{item_sel['eixo']}</h4>
                <p><strong>Objetivo:</strong> {item_sel['objetivo']}</p>
                <small style="color:#64748b;">📅 {item_sel['trimestre']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Tecnologia ➕", key="add_tec", type="secondary", use_container_width=True):
                novo = {"tipo": "Tecnologia", "eixo": item_sel['eixo'], "geral": geral, "especifico": especifico, "objetivo": item_sel['objetivo']}
                if novo not in st.session_state.conteudos_selecionados:
                    st.session_state.conteudos_selecionados.append(novo)
                    st.toast("Item adicionado!", icon="✅")
                else:
                    st.toast("Item já existe na lista.", icon="ℹ️")

    # --- ABA INGLÊS ---
    with t2:
        if opcoes_ing:
            col_l, col_r = st.columns([1, 1])
            with col_l:
                geral = st.selectbox("Tópico", opcoes_ing, key="ing_g")
            
            itens = dados_ano[geral]
            opcoes_esp = [i['especifico'] for i in itens]
            with col_r:
                especifico = st.selectbox("Prática", opcoes_esp, key="ing_e")
            
            item_sel = next(i for i in itens if i['especifico'] == especifico)
            
            # Card Preview
            st.markdown(f"""
            <div class="card-container" style="border-left: 5px solid #ef4444;">
                <span class="status-tag tag-eng">Inglês</span>
                <h4>{item_sel['eixo']}</h4>
                <p><strong>Objetivo:</strong> {item_sel['objetivo']}</p>
                <small style="color:#64748b;">📅 {item_sel['trimestre']}</small>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Adicionar Inglês ➕", key="add_ing", type="secondary", use_container_width=True):
                novo = {"tipo": "Inglês", "eixo": item_sel.get('eixo', 'Língua Inglesa'), "geral": geral, "especifico": especifico, "objetivo": item_sel['objetivo']}
                if novo not in st.session_state.conteudos_selecionados:
                    st.session_state.conteudos_selecionados.append(novo)
                    st.toast("Item adicionado!", icon="✅")
                else:
                    st.toast("Item já existe na lista.", icon="ℹ️")

    # --- LISTA DE ITENS SELECIONADOS (CARRINHO) ---
    st.markdown("---")
    st.markdown(f"##### 🛒 Itens Selecionados ({len(st.session_state.conteudos_selecionados)})")
    
    if st.session_state.conteudos_selecionados:
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            cor = "#dbeafe" if item['tipo'] == "Tecnologia" else "#fee2e2"
            icone = "💻" if item['tipo'] == "Tecnologia" else "🇬🇧"
            
            c1, c2 = st.columns([0.85, 0.15])
            with c1:
                st.markdown(f"""
                <div style="background-color: {cor}; padding: 10px; border-radius: 8px; margin-bottom: 5px; font-size: 0.9rem;">
                    <strong>{icone} {item['geral']}</strong><br>{item['especifico']}
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()
    else:
        st.info("Nenhum item selecionado ainda.")

    # Navegação
    c_back, c_next = st.columns(2)
    with c_back:
        if st.button("⬅️ Voltar"):
            prev_step()
            st.rerun()
    with c_next:
        if st.button("Avançar para Detalhes ➡️", type="primary"):
            if not st.session_state.conteudos_selecionados:
                st.error("Selecione pelo menos um conteúdo.")
            else:
                next_step()
                st.rerun()

# --- PASSO 3: DETALHAMENTO E EXPORTAÇÃO ---
def render_step3():
    st.markdown("### 3️⃣ Detalhamento Pedagógico")
    
    with st.container():
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        situacao = c1.text_area("Situação Didática (Obrigatório)", height=150, placeholder="Descreva a metodologia...", value=st.session_state.config.get('situacao', ''))
        recursos = c2.text_area("Recursos (Obrigatório)", height=150, placeholder="Materiais necessários...", value=st.session_state.config.get('recursos', ''))
        
        c3, c4 = st.columns(2)
        avaliacao = c3.text_area("Avaliação", height=100, value=st.session_state.config.get('avaliacao', ''))
        recuperacao = c4.text_area("Recuperação Contínua (Obrigatório)", height=100, value=st.session_state.config.get('recuperacao', ''))
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Salva textos no estado para não perder se voltar
        st.session_state.config.update({
            'situacao': situacao, 'recursos': recursos,
            'avaliacao': avaliacao, 'recuperacao': recuperacao
        })

    # GERAÇÃO DO WORD
    c_back, c_final = st.columns(2)
    with c_back:
        if st.button("⬅️ Voltar Seleção"):
            prev_step()
            st.rerun()
            
    with c_final:
        if st.button("🚀 Gerar Documento Oficial", type="primary", use_container_width=True):
            if not situacao or not recursos or not recuperacao:
                st.error("Preencha os campos obrigatórios!")
            else:
                # Prepara dados finais
                final_data = st.session_state.config
                final_data['Turmas'] = ", ".join(final_data['turmas'])
                
                # Gera DOC
                doc_buffer = gerar_docx_premium(st.session_state.conteudos_selecionados, final_data)
                
                st.balloons()
                st.success("Documento gerado com sucesso!")
                
                filename = f"Plan_{final_data['nivel'].replace(' ','')}_{datetime.now().strftime('%d-%m')}.docx"
                
                st.download_button(
                    label="📥 Baixar Arquivo Word (.docx)",
                    data=doc_buffer,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )

# --- FUNÇÃO DE GERAÇÃO DO WORD (Mantida e otimizada) ---
def gerar_docx_premium(conteudos, dados):
    doc = Document()
    
    # Margens ABNT
    for section in doc.sections:
        section.top_margin = Cm(1.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.0)
        section.right_margin = Cm(2.0)

    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    # Cabeçalho com Imagens
    table_head = doc.add_table(rows=1, cols=3)
    table_head.autofit = False
    
    # Carrega imagens locais
    logo_pref = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
    logo_esc = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"

    # Célula Esq
    c1 = table_head.cell(0,0); c1.width = Cm(2.5)
    if os.path.exists(logo_pref):
        try: c1.paragraphs[0].add_run().add_picture(logo_pref, width=Cm(2.0))
        except: pass
        
    # Célula Centro
    c2 = table_head.cell(0,1); c2.width = Cm(11.0)
    p = c2.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\n").bold = True
    p.add_run("CEIEF RAFAEL AFFONSO LEITE\n").bold = True
    p.add_run("Planejamento de Linguagens e Tecnologias")
    
    # Célula Dir
    c3 = table_head.cell(0,2); c3.width = Cm(2.5)
    p_dir = c3.paragraphs[0]
    p_dir.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists(logo_esc):
        try: p_dir.add_run().add_picture(logo_esc, width=Cm(2.0))
        except: pass

    doc.add_paragraph() # Espaço

    # Dados de Identificação
    p_info = doc.add_paragraph()
    p_info.add_run(f"Período: {dados['periodo']}\n").bold = True
    p_info.add_run(f"Professor(a): {dados['professor']}\n")
    p_info.add_run(f"Ano: {dados['nivel']} | Turmas: {dados['Turmas']} | {dados['trimestre']}")
    
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
    p.add_run(dados['situacao'])
    
    p = doc.add_paragraph()
    p.add_run("\nRecursos Didáticos:\n").bold = True
    p.add_run(dados['recursos'])
    
    p = doc.add_paragraph()
    p.add_run("\nAvaliação:\n").bold = True
    p.add_run(dados['avaliacao'])
    
    p = doc.add_paragraph()
    p.add_run("\nRecuperação Contínua:\n").bold = True
    p.add_run(dados['recuperacao'])

    f = BytesIO()
    doc.save(f)
    f.seek(0)
    return f

# --- FLUXO PRINCIPAL ---
render_header()

# Barra de Progresso Visual
progress_map = {1: 33, 2: 66, 3: 100}
st.progress(progress_map[st.session_state.step])

# Renderiza o passo atual
if st.session_state.step == 1:
    render_step1()
elif st.session_state.step == 2:
    render_step2()
elif st.session_state.step == 3:
    render_step3()

# Rodapé Premium
st.markdown("""
    <div style='margin-top: 50px; text-align: center; color: #94a3b8; font-size: 0.8rem; border-top: 1px solid #e2e8f0; padding-top: 20px;'>
        <b>Sistema Planejar</b> • © 2025 José Victor Souza Gallo
    </div>
""", unsafe_allow_html=True)
