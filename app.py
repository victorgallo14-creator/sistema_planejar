import streamlit as st
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from fpdf import FPDF
from io import BytesIO
import calendar
from datetime import datetime
import os

# --- MATRIZ CURRICULAR ---
try:
    from dados_curriculo import CURRICULO_DB
except ModuleNotFoundError:
    st.error("ERRO: Base de dados curricular não encontrada.")
    st.stop()

# --- 1. CONFIGURAÇÃO BÁSICA ---
st.set_page_config(
    page_title="Sistema Planejar",
    layout="centered", # Melhor para leitura e telemóvel
    page_icon="📝"
)

# --- 2. ESTILO MÍNIMO (APENAS CONTRASTE) ---
st.markdown("""
<style>
    /* Garante que o texto seja bem escuro e legível */
    html, body, [class*="css"] {
        color: #1a1a1a !important;
    }
    /* Destaque para os títulos de secção */
    .stHeader {
        border-bottom: 2px solid #1e3a8a;
        padding-bottom: 5px;
        margin-top: 20px;
    }
    /* Estilo para as caixas de selecção adicionadas */
    .selected-item {
        background-color: #f0f2f6;
        padding: 10px;
        border-left: 5px solid #1e3a8a;
        margin-bottom: 10px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CABEÇALHO ---
col_l, col_r = st.columns([1, 1])
with col_l:
    logo_p = "logo_prefeitura.png" if os.path.exists("logo_prefeitura.png") else "logo_prefeitura.jpg"
    if os.path.exists(logo_p): st.image(logo_p, width=100)
with col_r:
    logo_e = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo_escola.jpg"
    if os.path.exists(logo_e): st.image(logo_e, width=100)

st.title("SISTEMA PLANEJAR")
st.subheader("CEIEF Rafael Affonso Leite")
st.markdown("---")

# --- 4. IDENTIFICAÇÃO ---
st.header("1. Identificação")
professor = st.text_input("Professor(a) Responsável", placeholder="Digite o seu nome")

c1, c2 = st.columns(2)
with c1:
    anos = list(CURRICULO_DB.keys())
    ano = st.selectbox("Ano de Escolaridade", anos)
with c2:
    # Lógica de Turmas
    qtd_turmas = {"Maternal II": 2, "Etapa I": 3, "Etapa II": 3, "1º Ano": 3, "2º Ano": 3, "3º Ano": 3, "4º Ano": 3, "5º Ano": 3}
    max_t = qtd_turmas.get(ano, 3)
    opts = [f"{ano} - Turma {i}" if "Maternal" in ano or "Etapa" in ano else f"{ano} {i}" for i in range(1, max_t + 1)]
    turmas = st.multiselect("Turmas", opts)

c3, c4 = st.columns(2)
with c3:
    meses = {2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
    mes_nome = st.selectbox("Mês de Referência", list(meses.values()))
    mes_num = [k for k, v in meses.items() if v == mes_nome][0]
with c4:
    if mes_num == 2:
        periodo_texto = "01/02/2026 a 28/02/2026"
        st.write("Planeamento Mensal (Fevereiro)")
    else:
        quinzena = st.radio("Quinzena", ["1ª Quinzena", "2ª Quinzena"], horizontal=True)
        ultimo = calendar.monthrange(2026, mes_num)[1]
        periodo_texto = f"01/{mes_num:02d}/2026 a 15/{mes_num:02d}/2026" if "1ª" in quinzena else f"16/{mes_num:02d}/2026 a {ultimo}/{mes_num:02d}/2026"

trimestre_doc = "1º Trimestre" if mes_num <= 4 else "2º Trimestre" if mes_num <= 8 else "3º Trimestre"

# --- 5. SELECÇÃO DA MATRIZ ---
st.header("2. Conteúdos da Matriz")
if 'lista' not in st.session_state: st.session_state.lista = []

dados = CURRICULO_DB.get(ano, {})
# Separação simples de disciplinas
op_tec = [k for k, v in dados.items() if "INGLÊS" not in k.upper() and "ORALIDADE" not in v[0]['eixo'].upper()]
op_ing = [k for k in dados.keys() if k not in op_tec]

tab1, tab2 = st.tabs(["💻 Tecnologia", "🇬🇧 Inglês"])

with tab1:
    if op_tec:
        g_tec = st.selectbox("Eixo", op_tec, key="g_tec")
        e_tec = st.selectbox("Habilidade", [i['especifico'] for i in dados[g_tec]], key="e_tec")
        sel_t = next(i for i in dados[g_tec] if i['especifico'] == e_tec)
        st.info(f"**Objetivo:** {sel_t['objetivo']}")
        if st.button("Adicionar Tecnologia", use_container_width=True):
            st.session_state.lista.append({'tipo': 'Tecnologia', 'geral': g_tec, 'especifico': e_tec, 'objetivo': sel_t['objetivo']})
            st.toast("Adicionado!")

with tab2:
    if op_ing:
        g_ing = st.selectbox("Tópico", op_ing, key="g_ing")
        e_ing = st.selectbox("Prática", [i['especifico'] for i in dados[g_ing]], key="e_ing")
        sel_i = next(i for i in dados[g_ing] if i['especifico'] == e_ing)
        st.info(f"**Objetivo:** {sel_i['objetivo']}")
        if st.button("Adicionar Inglês", use_container_width=True):
            st.session_state.lista.append({'tipo': 'Inglês', 'geral': g_ing, 'especifico': e_ing, 'objetivo': sel_i['objetivo']})
            st.toast("Adicionado!")

# Visualização da lista
if st.session_state.lista:
    st.write("**Conteúdos Selecionados:**")
    for i, item in enumerate(st.session_state.lista):
        c_item, c_del = st.columns([0.9, 0.1])
        c_item.markdown(f"<div class='selected-item'><b>{item['tipo']}</b> | {item['especifico']}</div>", unsafe_allow_html=True)
        if c_del.button("X", key=f"del_{i}"):
            st.session_state.lista.pop(i)
            st.rerun()

# --- 6. DETALHAMENTO ---
st.header("3. Detalhamento Pedagógico")
st.caption("Todos os campos abaixo são obrigatórios.")

obj_esp = st.text_area("Objetivos Específicos da Aula")
sit = st.text_area("Situação Didática / Metodologia")
rec = st.text_area("Recursos Didáticos")
aval = st.text_area("Avaliação")
recup = st.text_area("Recuperação Contínua")

# --- 7. GERAÇÃO ---
def clean(t): return t.encode('latin-1', 'replace').decode('latin-1') if t else ""

def gerar_pdf():
    pdf = FPDF(); pdf.add_page(); pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, 'CEIEF RAFAEL AFFONSO LEITE', 0, 1, 'C')
    pdf.set_font('Arial', '', 10); pdf.cell(0, 5, 'Planeamento de Aula', 0, 1, 'C'); pdf.ln(10)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 7, clean(f"Professor: {professor} | Ano: {ano} | Turmas: {', '.join(turmas)}"), 1, 1, 'L')
    pdf.cell(0, 7, clean(f"Período: {periodo_texto} ({trimestre_doc})"), 1, 1, 'L'); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, "MATRIZ CURRICULAR", 0, 1)
    pdf.set_font("Arial", '', 9)
    for it in st.session_state.lista: pdf.multi_cell(0, 5, clean(f"[{it['tipo']}] {it['especifico']}"), 1, 'L')
    pdf.ln(5); pdf.set_font("Arial", 'B', 10); pdf.cell(0, 8, "DETALHAMENTO", 0, 1)
    for l, v in [("Objetivos", obj_esp), ("Metodologia", sit), ("Recursos", rec), ("Avaliacao", aval), ("Recuperacao", recup)]:
        pdf.set_font("Arial", 'B', 9); pdf.cell(0, 5, clean(l + ":"), 0, 1)
        pdf.set_font("Arial", '', 9); pdf.multi_cell(0, 5, clean(v)); pdf.ln(2)
    pdf.set_y(-20); pdf.set_font('Arial', 'I', 8); pdf.cell(0, 10, f'Emitido em: {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')
    return pdf.output(dest='S').encode('latin-1')

def gerar_docx():
    doc = Document(); style = doc.styles['Normal']; font = style.font; font.name = 'Arial'; font.size = Pt(10)
    doc.add_heading('CEIEF RAFAEL AFFONSO LEITE', 0)
    doc.add_paragraph(f"Professor: {professor}\nAno: {ano} | Turmas: {', '.join(turmas)}\nPeríodo: {periodo_texto}")
    doc.add_heading("Matriz Curricular", 1)
    for it in st.session_state.lista: doc.add_paragraph(f"• {it['especifico']}", style='List Bullet')
    doc.add_heading("Detalhamento", 1)
    for l, v in [("Objetivos", obj_esp), ("Metodologia", sit), ("Recursos", rec), ("Avaliação", aval), ("Recuperação", recup)]:
        p = doc.add_paragraph(); p.add_run(l + ": ").bold = True; p.add_run(v)
    f = BytesIO(); doc.save(f); f.seek(0); return f

st.markdown("---")
if st.button("GERAR PLANEAMENTO FINAL", type="primary", use_container_width=True):
    if not all([professor, turmas, obj_esp, sit, rec, aval, recup]) or not st.session_state.lista:
        st.error("Por favor, preencha todos os campos e selecione os conteúdos da matriz.")
    else:
        pdf_file = gerar_pdf()
        word_file = gerar_docx()
        st.success("Documentos gerados com sucesso!")
        st.download_button("Baixar PDF", pdf_file, "planeamento.pdf", "application/pdf", use_container_width=True)
        st.download_button("Baixar Word", word_file, "planeamento.docx", use_container_width=True)

# --- RODAPÉ ---
st.write("")
st.caption(f"Desenvolvido por José Victor Souza Gallo • CEIEF Rafael Affonso Leite © {datetime.now().year}")
