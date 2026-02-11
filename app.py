import streamlit as st
from docx import Document
from docx.shared import Pt, Cm, RGBColor
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
    st.error("ERRO CRÍTICO: O ficheiro 'dados_curriculo.py' não foi encontrado.")
    st.stop()

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Sistema Planejar | CEIEF",
    layout="wide",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# --- 2. CSS DE ALTA VISIBILIDADE (CONTRASTE REFORÇADO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* RESET E FONTE GLOBAL */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #0f172a; /* Azul marinho muito escuro para máxima leitura */
    }
    
    /* FUNDO DA APLICAÇÃO (Cinza para destacar as caixas brancas) */
    .stApp {
        background-color: #f1f5f9;
    }
    
    /* CABEÇALHO INSTITUCIONAL */
    .header-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    
    /* CAIXAS DE CONTEÚDO (Cards) */
    .content-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #e2e8f0; /* Borda visível */
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }

    /* REFORÇO VISUAL DOS CAMPOS DE INPUT (O segredo da visibilidade) */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border: 2px solid #94a3b8 !important; /* Borda cinza média para ser bem visível */
        border-radius: 8px !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-size: 1rem !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2) !important;
    }

    /* TÍTULOS DE SEÇÃO */
    .section-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* BOTÕES */
    .stButton > button {
        border-radius: 8px;
        height: 3.5rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.2s;
    }
    
    /* INDICADOR DE PASSOS */
    .step-bar {
        display: flex;
        justify-content: space-around;
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        margin-bottom: 2rem;
    }
    .step-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #94a3b8;
    }
    .step-label.active {
        color: #2563eb;
    }

    /* LABELS DOS CAMPOS */
    label {
        font-weight: 700 !important;
        color: #334155 !important;
        margin-bottom: 5px !important;
    }

    /* TAGS */
    .badge {
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    .badge-tech { background-color: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe; }
    .badge-eng { background-color: #fee2e2; color: #991b1b; border: 1px solid #fecdd3; }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded}"
    return None

# --- 3. CABEÇALHO RECONSTRUÍDO (VISIBILIDADE GARANTIDA) ---
# Usamos colunas nativas para evitar o erro de código aparecer no ecrã
st.markdown('<div class="header-banner">', unsafe_allow_html=True)
col_l, col_c, col_r = st.columns([1, 4, 1])

with col_l:
    logo_p = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
    if os.path.exists(logo_p):
        st.image(logo_p, width=80)
    else:
        st.markdown("🏛️")

with col_c:
    st.markdown("""
        <h1 style="color:white; margin:0; font-size:2.2rem; font-weight:800;">SISTEMA PLANEJAR</h1>
        <p style="color:rgba(255,255,255,0.9); margin:0; font-weight:400;">CEIEF Rafael Affonso Leite • Gestão Pedagógica Digital</p>
    """, unsafe_allow_html=True)

with col_r:
    logo_e = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
    if os.path.exists(logo_e):
        st.image(logo_e, width=80)
    else:
        st.markdown("🏫")
st.markdown('</div>', unsafe_allow_html=True)

# --- GESTÃO DE ESTADO ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'conteudos_selecionados' not in st.session_state: st.session_state.conteudos_selecionados = []
if 'config' not in st.session_state: st.session_state.config = {}

def set_step(s): st.session_state.step = s

# BARRA DE PROGRESSO VISÍVEL
st.markdown(f"""
<div class="step-bar">
    <span class="step-label {'active' if st.session_state.step==1 else ''}">1. IDENTIFICAÇÃO</span>
    <span class="step-label {'active' if st.session_state.step==2 else ''}">2. MATRIZ CURRICULAR</span>
    <span class="step-label {'active' if st.session_state.step==3 else ''}">3. FINALIZAÇÃO</span>
</div>
""", unsafe_allow_html=True)

# --- PASSO 1: IDENTIFICAÇÃO ---
if st.session_state.step == 1:
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Parâmetros do Planeamento</div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            professor = st.text_input("Nome do Professor(a) Responsável", value=st.session_state.config.get('professor', ''), placeholder="Ex: José Victor Souza Gallo")
            
            anos = list(CURRICULO_DB.keys())
            saved_ano = st.session_state.config.get('ano')
            idx = anos.index(saved_ano) if saved_ano in anos else 0
            ano = st.selectbox("Ano de Escolaridade", anos, index=idx)
            
            # Turmas
            qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
            max_t = qtd_turmas.get(ano, 3)
            prefix = f"{ano} - Turma" if "Maternal" in ano or "Etapa" in ano else f"{ano} "
            opts = [f"{prefix}{i}" for i in range(1, max_t + 1)]
            
            saved_turmas = st.session_state.config.get('turmas', [])
            valid_defaults = [t for t in saved_turmas if t in opts]
            turmas = st.multiselect("Selecione as Turmas", opts, default=valid_defaults)

        with c2:
            meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
            saved_mes = st.session_state.config.get('mes')
            idx_mes = list(meses.values()).index(saved_mes) if saved_mes in list(meses.values()) else 0
            mes_nome = st.selectbox("Mês de Referência", list(meses.values()), index=idx_mes)
            mes_num = [k for k, v in meses.items() if v == mes_nome][0]
            ano_atual = datetime.now().year
            
            if mes_num == 2:
                periodo_texto = f"01/02/{ano_atual} a 28/02/{ano_atual}"
                trimestre_doc = "1º Trimestre"
                st.info("ℹ️ Planeamento Mensal para o mês de Fevereiro.")
            else:
                quinzena = st.radio("Período de Execução (Quinzena)", ["1ª Quinzena (01-15)", "2ª Quinzena (16-Fim)"])
                ultimo_dia = calendar.monthrange(ano_atual, mes_num)[1]
                if mes_num <= 4: trimestre_doc = "1º Trimestre"
                elif mes_num <= 8: trimestre_doc = "2º Trimestre"
                else: trimestre_doc = "3º Trimestre"
                periodo_texto = f"01/{mes_num:02d}/{ano_atual} a 15/{mes_num:02d}/{ano_atual}" if "1ª" in quinzena else f"16/{mes_num:02d}/{ano_atual} a {ultimo_dia}/{mes_num:02d}/{ano_atual}"
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Avançar para Seleção de Conteúdos ➔", type="primary", use_container_width=True):
            if not professor or not turmas:
                st.warning("⚠️ Todos os campos desta etapa são obrigatórios.")
            else:
                if 'ano' in st.session_state.config and st.session_state.config['ano'] != ano:
                    st.session_state.conteudos_selecionados = []
                st.session_state.config = {
                    'professor': professor, 'ano': ano, 'turmas': turmas, 
                    'mes': mes_nome, 'periodo': periodo_texto, 'trimestre': trimestre_doc
                }
                set_step(2)
                st.rerun()

# --- PASSO 2: MATRIZ CURRICULAR ---
elif st.session_state.step == 2:
    st.markdown(f"### Matriz Curricular: {st.session_state.config['ano']}")
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        dados = CURRICULO_DB.get(st.session_state.config['ano'], {})
        op_tec, op_ing = [], []
        termos = ['ORALIDADE', 'LEITURA', 'ESCRITA', 'INGLÊS', 'LISTENING', 'READING', 'WRITING']
        
        for k, v in dados.items():
            if v:
                eixo = v[0]['eixo'].upper()
                if any(t in eixo for t in termos) or any(t in k.upper() for t in termos): op_ing.append(k)
                else: op_tec.append(k)

        t1, t2 = st.tabs(["TECNOLOGIA & CULTURA DIGITAL", "LÍNGUA INGLESA"])
        
        with t1:
            if op_tec:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Eixo Curricular", op_tec, key="t_g")
                itens = dados[g]
                e = c2.selectbox("Habilidade Específica", [i['especifico'] for i in itens], key="t_e")
                sel = next(i for i in itens if i['especifico'] == e)
                
                st.markdown(f"""
                <div style="background:#f8fafc; padding:20px; border-radius:10px; border:1px solid #cbd5e1; margin:10px 0;">
                    <span class="badge badge-tech">Objetivo Curricular</span>
                    <p style="margin-top:10px; font-weight:600;">{sel['objetivo']}</p>
                    <small style="color:#64748b;">Trimestre Previsto: {sel['trimestre']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar Conteúdo ➕", key="bt_t"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Tecnologia', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("✅ Conteúdo adicionado!")
            else: st.warning("Não existem dados de tecnologia para este ano.")

        with t2:
            if op_ing:
                c1, c2 = st.columns(2)
                g = c1.selectbox("Tópico de Linguagem", op_ing, key="i_g")
                itens = dados[g]
                e = c2.selectbox("Prática de Estudo", [i['especifico'] for i in itens], key="i_e")
                sel = next(i for i in itens if i['especifico'] == e)
                
                st.markdown(f"""
                <div style="background:#fff1f2; padding:20px; border-radius:10px; border:1px solid #fecdd3; margin:10px 0;">
                    <span class="badge badge-eng">Objetivo Curricular</span>
                    <p style="margin-top:10px; font-weight:600; color:#881337;">{sel['objetivo']}</p>
                    <small style="color:#64748b;">Trimestre Previsto: {sel['trimestre']}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("Adicionar Conteúdo ➕", key="bt_i"):
                    st.session_state.conteudos_selecionados.append({'tipo': 'Inglês', 'eixo': sel['eixo'], 'geral': g, 'especifico': e, 'objetivo': sel['objetivo']})
                    st.toast("✅ Conteúdo adicionado!")
            else: st.warning("Não existem dados de inglês para este ano.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # LISTA DE SELECCIONADOS (BEM VISÍVEL)
    if st.session_state.conteudos_selecionados:
        st.markdown("#### Conteúdos Seleccionados para este Planeamento")
        for i, item in enumerate(st.session_state.conteudos_selecionados):
            tag_cls = "badge-tech" if item['tipo'] == "Tecnologia" else "badge-eng"
            c_txt, c_btn = st.columns([0.94, 0.06])
            with c_txt:
                st.markdown(f"""
                <div style="background:white; border:2px solid #e2e8f0; padding:15px; border-radius:8px; margin-bottom:10px;">
                    <span class="badge {tag_cls}">{item['tipo']}</span> 
                    <span style="font-weight:700; margin-left:10px;">{item['geral']}</span>
                    <div style="font-size:0.95rem; margin-top:8px; color:#334155;">{item['especifico']}</div>
                </div>
                """, unsafe_allow_html=True)
            with c_btn:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.conteudos_selecionados.pop(i)
                    st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Parâmetros"): set_step(1); st.rerun()
    if c2.button("Avançar para Detalhes Finais ➔", type="primary", use_container_width=True):
        if not st.session_state.conteudos_selecionados:
            st.error("⚠️ Seleccione pelo menos um item da matriz oficial antes de continuar.")
        else:
            set_step(3); st.rerun()

# --- PASSO 3: DETALHAMENTO E EMISSÃO ---
elif st.session_state.step == 3:
    st.markdown("### Desenvolvimento Didático")
    
    with st.container():
        st.markdown('<div class="content-container">', unsafe_allow_html=True)
        
        # CAMPO OBRIGATÓRIO
        st.markdown("**1. Objetivos Específicos da Aula (Obrigatório)**")
        obj_esp = st.text_area("objetivos_label", height=100, label_visibility="collapsed", placeholder="Quais os resultados pretendidos nesta aula específica?", value=st.session_state.config.get('obj_esp', ''))
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**2. Situação Didática / Metodologia (Obrigatório)**")
            sit = st.text_area("sit_label", height=180, label_visibility="collapsed", placeholder="Passo a passo da atividade...", value=st.session_state.config.get('sit', ''))
        with c2:
            st.markdown("**3. Recursos Didáticos (Obrigatório)**")
            rec = st.text_area("rec_label", height=180, label_visibility="collapsed", placeholder="Ferramentas, materiais, internet...", value=st.session_state.config.get('rec', ''))
        
        st.markdown("---")
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**4. Procedimentos de Avaliação (Obrigatório)**")
            aval = st.text_area("aval_label", height=100, label_visibility="collapsed", value=st.session_state.config.get('aval', ''))
        with c4:
            st.markdown("**5. Recuperação Contínua (Obrigatório)**")
            recup = st.text_area("recup_label", height=100, label_visibility="collapsed", value=st.session_state.config.get('recup', ''))
            
        st.markdown('</div>', unsafe_allow_html=True)

    st.session_state.config.update({'obj_esp': obj_esp, 'sit': sit, 'rec': rec, 'aval': aval, 'recup': recup})

    # --- GERADORES ---
    def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

    def gerar_pdf(dados, conteudos):
        pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
        
        # Logos
        if os.path.exists("logo_prefeitura.png"): pdf.image("logo_prefeitura.png", 10, 8, 25)
        elif os.path.exists("logo_prefeitura.jpg"): pdf.image("logo_prefeitura.jpg", 10, 8, 25)
        if os.path.exists("logo_escola.png"): pdf.image("logo_escola.png", 175, 8, 25)
        elif os.path.exists("logo_escola.jpg"): pdf.image("logo_escola.jpg", 175, 8, 25)

        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 5, 'PREFEITURA MUNICIPAL DE LIMEIRA', 0, 1, 'C')
        pdf.cell(0, 5, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
        pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planejamento de Linguagens e Tecnologias', 0, 1, 'C'); pdf.ln(15)

        # Cabeçalho Cinza
        pdf.set_fill_color(245, 245, 245)
        pdf.set_font("Arial", 'B', 9)
        pdf.cell(0, 6, clean(f"PROFESSOR(A): {dados['professor']}"), 1, 1, 'L', True)
        pdf.cell(0, 6, clean(f"ANO: {dados['ano']} | TURMAS: {', '.join(dados['turmas'])}"), 1, 1, 'L', True)
        pdf.cell(0, 6, clean(f"PERÍODO: {dados['periodo']} ({dados['trimestre']})"), 1, 1, 'L', True)
        pdf.ln(5)

        # Matriz
        pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("CONTEÚDOS DA MATRIZ CURRICULAR"), 0, 1)
        pdf.set_font("Arial", '', 9)
        for it in conteudos:
            pdf.set_fill_color(252, 252, 252)
            pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['geral']}: {it['especifico']}"), 1, 'L', True)
            pdf.ln(1)

        # Detalhamento
        pdf.ln(4); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, clean("DETALHAMENTO PEDAGÓGICO"), 0, 1)
        for l, v in [("Objetivos Específicos", dados['obj_esp']), ("Situação Didática", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1)
            pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)

        pdf.set_y(-25); pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, f'Emitido pelo Sistema Planejar em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'C')
        pdf.cell(0, 5, 'Visto Coordenação: _______________________________', 0, 0, 'C')
        return pdf.output(dest='S').encode('latin-1')

    def gerar_docx(dados, conteudos):
        doc = Document()
        for s in doc.sections: s.top_margin = Cm(1); s.bottom_margin = Cm(1.5); s.left_margin = Cm(1.5); s.right_margin = Cm(1.5)
        
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run("PREFEITURA MUNICIPAL DE LIMEIRA\nCEIEF RAFAEL AFFONSO LEITE\nPlanejamento de Linguagens e Tecnologias").bold = True
        
        doc.add_paragraph(f"Professor(a): {dados['professor']}\nAno: {dados['ano']} | Turmas: {', '.join(dados['turmas'])}\nPeríodo: {dados['periodo']}")
        
        doc.add_heading("Matriz Curricular", 3)
        for it in conteudos: 
            p = doc.add_paragraph(style='List Bullet')
            p.add_run(f"{it['geral']}: ").bold = True
            p.add_run(it['especifico'])
            
        doc.add_heading("Detalhamento Pedagógico", 3)
        for l, v in [("Objetivos Específicos", dados['obj_esp']), ("Situação Didática", dados['sit']), ("Recursos", dados['rec']), ("Avaliação", dados['aval']), ("Recuperação", dados['recup'])]:
            p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
            
        f = BytesIO(); doc.save(f); f.seek(0); return f

    c1, c2 = st.columns(2)
    if c1.button("⬅ Voltar para Matriz"): set_step(2); st.rerun()
    if c2.button("FINALIZAR E EMITIR DOCUMENTOS 🚀", type="primary", use_container_width=True):
        if not all([obj_esp, sit, rec, aval, recup]):
            st.error("⚠️ Erro: Todos os campos de detalhamento são obrigatórios.")
        else:
            f_data = st.session_state.config
            word_f = gerar_docx(f_data, st.session_state.conteudos_selecionados)
            pdf_f = gerar_pdf(f_data, st.session_state.conteudos_selecionados)
            nome_f = f"Planejar_{f_data['ano'].replace(' ','')}_{datetime.now().strftime('%d%m')}"
            
            st.success("🎉 Planejamento finalizado com sucesso!")
            st.balloons()
            
            cd1, cd2 = st.columns(2)
            cd1.download_button("📄 Descarregar WORD (.docx)", word_f, f"{nome_f}.docx", use_container_width=True)
            cd2.download_button("📕 Descarregar PDF (.pdf)", pdf_f, f"{nome_f}.pdf", use_container_width=True)

# --- RODAPÉ ---
st.markdown(f"""
    <div class="footer">
        Desenvolvido por <b>José Victor Souza Gallo</b><br>
        Sistema de uso interno e exclusivo do CEIEF Rafael Affonso Leite © {datetime.now().year}
    </div>
""", unsafe_allow_html=True)
