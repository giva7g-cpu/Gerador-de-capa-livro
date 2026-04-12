"""
=============================================================================
  GERADOR DE CAPA DE LIVRO — APLICATIVO WEB (STREAMLIT)
  Para hospedar gratuitamente no Streamlit Cloud / Railway / Render
=============================================================================
"""

import io
import os
import math
import tempfile
from dataclasses import dataclass, field
from typing import Optional

import streamlit as st
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import CMYKColor, white

# ═══════════════════════════════════════════════════════════════════════════
#  CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Gerador de Capa de Livro",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS personalizado
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
  }

  .main-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #1a1a2e;
    margin-bottom: 0;
    line-height: 1.1;
  }
  .main-subtitle {
    font-size: 0.9rem;
    color: #6b7280;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2rem;
  }
  .metric-card {
    background: #f8f7f4;
    border-left: 3px solid #c9a84c;
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin: 6px 0;
  }
  .metric-label {
    font-size: 0.68rem;
    color: #9ca3af;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 2px;
  }
  .metric-value {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1a1a2e;
  }
  .section-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #1a1a2e;
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 6px;
    margin: 1.2rem 0 0.8rem 0;
  }
  .upload-hint {
    font-size: 0.72rem;
    color: #9ca3af;
    margin-top: 4px;
  }
  .warning-box {
    background: #fffbeb;
    border: 1px solid #f59e0b;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.8rem;
    color: #92400e;
  }
  .success-box {
    background: #f0fdf4;
    border: 1px solid #22c55e;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.8rem;
    color: #166534;
  }
  .stButton > button {
    background: #1a1a2e;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 0.6rem 2rem;
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    letter-spacing: 0.08em;
    font-size: 0.85rem;
    width: 100%;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: #c9a84c;
    color: #1a1a2e;
  }
  div[data-testid="stSidebarContent"] {
    background: #1a1a2e;
  }
  div[data-testid="stSidebarContent"] label,
  div[data-testid="stSidebarContent"] .stMarkdown,
  div[data-testid="stSidebarContent"] p {
    color: #e5e7eb !important;
  }
  div[data-testid="stSidebarContent"] .section-header {
    color: #c9a84c !important;
    border-bottom-color: #374151 !important;
  }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════
#  TABELA DE PAPÉIS
# ═══════════════════════════════════════════════════════════════════════════

ESPESSURA_PAPEL = {
    "Pólen 80g":    0.113,
    "Offset 75g":   0.095,
    "Offset 90g":   0.110,
    "Couchê 90g":   0.092,
    "Couchê 115g":  0.108,
}


def calcular_lombada(num_paginas: int, tipo_papel: str) -> float:
    espessura = ESPESSURA_PAPEL[tipo_papel]
    lombada = (num_paginas / 2) * espessura
    return max(lombada, 5.0)  # mínimo 5mm


# ═══════════════════════════════════════════════════════════════════════════
#  GERADOR DE PDF
# ═══════════════════════════════════════════════════════════════════════════

COR_MARCAS  = CMYKColor(0, 0, 0, 1)
COR_DOBRA   = CMYKColor(0.7, 0, 0, 0)
COR_SANGRIA = CMYKColor(1, 0, 1, 0)
COR_KDP     = CMYKColor(0, 0, 0.15, 0.05)


def preparar_imagem_bytes(img_bytes: bytes, largura_mm: float, altura_mm: float, dpi=300) -> Optional[str]:
    """Converte bytes de imagem upload para arquivo temporário CMYK 300DPI."""
    try:
        img = Image.open(io.BytesIO(img_bytes))
        px_w = round((largura_mm / 25.4) * dpi)
        px_h = round((altura_mm / 25.4) * dpi)

        if img.mode == "RGBA":
            fundo = Image.new("RGB", img.size, (255, 255, 255))
            fundo.paste(img, mask=img.split()[3])
            img = fundo
        if img.mode != "CMYK":
            img = img.convert("CMYK")

        img = img.resize((px_w, px_h), Image.LANCZOS)

        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name, format="JPEG", quality=95, dpi=(dpi, dpi))
        return tmp.name
    except Exception as e:
        st.error(f"Erro ao processar imagem: {e}")
        return None


def gerar_pdf(
    largura_mm, altura_mm, lombada_mm, sangria_mm,
    img_capa_bytes, img_contra_bytes, img_lombada_bytes,
    kdp=False, marcas=True, guias=True, linha_sangria=True,
) -> bytes:
    """Gera o PDF e retorna os bytes para download."""

    larg_total = (largura_mm * 2) + lombada_mm + (sangria_mm * 2)
    alt_total  = altura_mm + (sangria_mm * 2)

    x_contracapa = sangria_mm
    x_lombada    = sangria_mm + largura_mm
    x_capa       = sangria_mm + largura_mm + lombada_mm

    # Dimensões de cada seção
    dim_contra_w = largura_mm + sangria_mm
    dim_capa_w   = largura_mm + sangria_mm
    dim_lomb_w   = lombada_mm
    dim_h        = alt_total

    # Prepara imagens
    tmp_files = []
    with st.spinner("Processando imagens em 300 DPI..."):
        path_capa   = preparar_imagem_bytes(img_capa_bytes,   dim_capa_w,   dim_h) if img_capa_bytes   else None
        path_contra = preparar_imagem_bytes(img_contra_bytes, dim_contra_w, dim_h) if img_contra_bytes else None
        path_lomb   = preparar_imagem_bytes(img_lombada_bytes, dim_lomb_w,  dim_h) if img_lombada_bytes else None
        for p in [path_capa, path_contra, path_lomb]:
            if p: tmp_files.append(p)

    # Gera PDF em memória
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(larg_total * mm, alt_total * mm), pageCompression=1)
    c.setTitle("Capa do Livro — Arquivo para Gráfica")
    c.setAuthor("Gerador de Capa de Livro")

    # Fundo branco
    c.setFillColor(white)
    c.rect(0, 0, larg_total * mm, alt_total * mm, fill=1, stroke=0)

    def inserir(path, x_mm, y_mm, w_mm, h_mm, nome):
        if path:
            c.drawImage(ImageReader(path), x_mm*mm, y_mm*mm,
                        width=w_mm*mm, height=h_mm*mm,
                        preserveAspectRatio=False, mask="auto")
        else:
            c.setFillColor(CMYKColor(0,0,0,0.06))
            c.rect(x_mm*mm, y_mm*mm, w_mm*mm, h_mm*mm, fill=1, stroke=0)
            c.setFont("Helvetica", 8)
            c.setFillColor(CMYKColor(0,0,0,0.25))
            c.drawCentredString((x_mm+w_mm/2)*mm, (y_mm+h_mm/2)*mm, nome)

    inserir(path_contra, 0,         0, dim_contra_w, dim_h, "CONTRACAPA")
    inserir(path_lomb,   x_lombada, 0, dim_lomb_w,   dim_h, "LOMBADA")
    inserir(path_capa,   x_capa,    0, dim_capa_w,   dim_h, "CAPA")

    # Linha de sangria
    if linha_sangria:
        c.setStrokeColor(COR_SANGRIA)
        c.setLineWidth(0.35)
        c.setDash(3, 2)
        c.rect(sangria_mm*mm, sangria_mm*mm,
               (larg_total - 2*sangria_mm)*mm,
               (alt_total  - 2*sangria_mm)*mm)

    # Guias da lombada
    if guias:
        c.setStrokeColor(COR_DOBRA)
        c.setLineWidth(0.5)
        c.setDash(4, 3)
        c.line(x_lombada*mm, 0, x_lombada*mm, alt_total*mm)
        c.line((x_lombada+lombada_mm)*mm, 0, (x_lombada+lombada_mm)*mm, alt_total*mm)
        c.setDash()
        c.setFont("Helvetica", 5)
        c.setFillColor(COR_DOBRA)
        c.drawCentredString((x_lombada+lombada_mm/2)*mm, (sangria_mm*0.4)*mm,
                            f"LOMBADA {lombada_mm:.1f}mm")

    # Marcas de corte
    if marcas:
        c.setStrokeColor(COR_MARCAS)
        c.setLineWidth(0.25)
        c.setDash()
        comp = 5*mm
        afst = 3*mm
        cx = sangria_mm*mm
        cy = sangria_mm*mm
        dx = (larg_total - sangria_mm)*mm
        dy = (alt_total  - sangria_mm)*mm

        for px, py, sx, sy in [
            (cx, cy, -1, -1), (dx, cy, +1, -1),
            (cx, dy, -1, +1), (dx, dy, +1, +1),
        ]:
            c.line(px + sx*afst, py, px + sx*(afst+comp), py)
            c.line(px, py + sy*afst, px, py + sy*(afst+comp))

    # Reserva KDP
    if kdp:
        bw, bh = 50*mm, 30*mm
        bx = (x_lombada - 50 - 5)*mm
        by = (sangria_mm + 5)*mm
        c.setFillColor(COR_KDP)
        c.setStrokeColor(CMYKColor(0,0,0,0.3))
        c.setLineWidth(0.5)
        c.rect(bx, by, bw, bh, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 5.5)
        c.setFillColor(CMYKColor(0,0,0,0.6))
        c.drawCentredString(bx+bw/2, by+bh/2+3, "RESERVADO — KDP BARCODE")
        c.setFont("Helvetica", 4.5)
        c.drawCentredString(bx+bw/2, by+bh/2-4, "50×30mm — DEIXAR BRANCO")

    # Legendas
    c.setFont("Helvetica", 4)
    c.setFillColor(CMYKColor(0,0,0,0.35))
    info = (f"PDF: {larg_total:.1f}×{alt_total:.1f}mm  |  "
            f"SANGRIA: {sangria_mm}mm  |  LOMBADA: {lombada_mm:.1f}mm")
    c.drawString(sangria_mm*mm, (sangria_mm*0.3)*mm, info)

    c.save()

    # Limpa temporários
    for p in tmp_files:
        try: os.remove(p)
        except: pass

    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════
#  INTERFACE STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════

# — Header
st.markdown('<div class="main-title">Gerador de Capa de Livro</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Arquivo profissional pronto para gráfica · CMYK · 300 DPI</div>', unsafe_allow_html=True)

# — Layout: sidebar + conteúdo principal
col_main, col_preview = st.columns([1.1, 1])

with col_main:

    # ── DIMENSÕES
    st.markdown('<div class="section-header">📐 Dimensões do Livro</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        largura = st.number_input("Largura (mm)", min_value=80, max_value=300, value=160, step=1)
    with c2:
        altura = st.number_input("Altura (mm)", min_value=100, max_value=400, value=230, step=1)

    # ── MIOLO
    st.markdown('<div class="section-header">📄 Miolo do Livro</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        num_paginas = st.number_input("Nº de páginas", min_value=8, max_value=2000, value=20, step=2,
                                       help="Use sempre número par (frente e verso)")
    with c4:
        tipo_papel = st.selectbox("Tipo de papel", list(ESPESSURA_PAPEL.keys()))

    # ── SANGRIA E OPÇÕES
    st.markdown('<div class="section-header">⚙️ Configurações</div>', unsafe_allow_html=True)
    c5, c6 = st.columns(2)
    with c5:
        sangria = st.selectbox("Sangria (bleed)", [3, 5], index=0,
                               format_func=lambda x: f"{x} mm {'(padrão BR)' if x==3 else '(offset/exigente)'}")
    with c6:
        lombada_manual = st.number_input("Lombada manual (mm)", min_value=1.0, max_value=100.0,
                                          value=0.0, step=0.5,
                                          help="Deixe 0 para calcular automaticamente")

    col_opt1, col_opt2, col_opt3 = st.columns(3)
    with col_opt1:
        marcas_corte = st.checkbox("Marcas de corte", value=True)
    with col_opt2:
        guia_lombada = st.checkbox("Guia da lombada", value=True)
    with col_opt3:
        kdp_barcode  = st.checkbox("Reserva KDP", value=False)

    # ── IMAGENS
    st.markdown('<div class="section-header">🖼️ Imagens</div>', unsafe_allow_html=True)
    st.markdown('<p class="upload-hint">Formatos aceitos: JPG, PNG, WEBP · Recomendado: 300 DPI ou maior</p>',
                unsafe_allow_html=True)

    up_capa   = st.file_uploader("Capa Frontal",  type=["jpg","jpeg","png","webp"], key="capa")
    up_contra = st.file_uploader("Contracapa",    type=["jpg","jpeg","png","webp"], key="contra")
    up_lomb   = st.file_uploader("Lombada",       type=["jpg","jpeg","png","webp"], key="lomb",
                                  help="Opcional — se não enviar, será gerado um placeholder")

    # ── CÁLCULOS
    lombada_calc = calcular_lombada(num_paginas, tipo_papel)
    lombada_final = lombada_manual if lombada_manual > 0 else lombada_calc
    larg_total = (largura * 2) + lombada_final + (sangria * 2)
    alt_total  = altura + (sangria * 2)

with col_preview:
    # ── RESUMO TÉCNICO
    st.markdown('<div class="section-header">📊 Resumo Técnico</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Lombada Calculada</div>
      <div class="metric-value">{lombada_calc:.2f} mm
        <span style="font-size:0.7rem;color:#9ca3af;font-weight:400">
          ({ESPESSURA_PAPEL[tipo_papel]:.3f} mm/folha × {num_paginas//2} folhas)
        </span>
      </div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Lombada Final Usada</div>
      <div class="metric-value">{lombada_final:.2f} mm
        <span style="font-size:0.7rem;color:#9ca3af;font-weight:400">
          {'(manual)' if lombada_manual > 0 else '(automático)'}
        </span>
      </div>
    </div>
    <div class="metric-card">
      <div class="metric-label">PDF Total (com sangria)</div>
      <div class="metric-value">{larg_total:.2f} × {alt_total:.2f} mm</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Contracapa · Lombada · Capa</div>
      <div class="metric-value">{largura} · {lombada_final:.1f} · {largura} mm</div>
    </div>
    """, unsafe_allow_html=True)

    # Aviso lombada fina
    if lombada_calc < 6:
        st.markdown(f"""
        <div class="warning-box" style="margin-top:12px">
          ⚠️ Lombada de {lombada_calc:.1f}mm é muito fina para texto.
          O KDP exige mínimo de 3,175mm e recomenda 6mm para imprimir título na lombada.
        </div>
        """, unsafe_allow_html=True)

    # Preview das imagens enviadas
    if up_capa or up_contra:
        st.markdown('<div class="section-header">👁️ Preview</div>', unsafe_allow_html=True)
        prev_cols = st.columns(3)
        labels = ["Contracapa", "Lombada", "Capa Frontal"]
        uploads = [up_contra, up_lomb, up_capa]
        for i, (lbl, up) in enumerate(zip(labels, uploads)):
            with prev_cols[i]:
                if up:
                    img = Image.open(up)
                    st.image(img, caption=lbl, use_container_width=True)
                    up.seek(0)
                else:
                    st.markdown(f"<div style='background:#f3f4f6;border-radius:4px;padding:20px;text-align:center;color:#9ca3af;font-size:0.7rem'>{lbl}<br>sem imagem</div>",
                                unsafe_allow_html=True)

# ── BOTÃO GERAR
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
with col_btn2:
    gerar = st.button("⬇  Gerar e Baixar PDF para Gráfica", use_container_width=True)

if gerar:
    img_capa_bytes   = up_capa.read()   if up_capa   else None
    img_contra_bytes = up_contra.read() if up_contra else None
    img_lomb_bytes   = up_lomb.read()   if up_lomb   else None

    with st.spinner("Gerando PDF profissional..."):
        pdf_bytes = gerar_pdf(
            largura_mm=largura,
            altura_mm=altura,
            lombada_mm=lombada_final,
            sangria_mm=sangria,
            img_capa_bytes=img_capa_bytes,
            img_contra_bytes=img_contra_bytes,
            img_lombada_bytes=img_lomb_bytes,
            kdp=kdp_barcode,
            marcas=marcas_corte,
            guias=guia_lombada,
            linha_sangria=True,
        )

    st.markdown(f"""
    <div class="success-box">
      ✅ PDF gerado com sucesso!
      Tamanho: {larg_total:.1f} × {alt_total:.1f} mm · CMYK · 300 DPI · Pronto para gráfica
    </div>
    """, unsafe_allow_html=True)

    st.download_button(
        label="📥 Clique aqui para baixar o PDF",
        data=pdf_bytes,
        file_name="capa_livro_grafica.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ── RODAPÉ
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#9ca3af;font-size:0.7rem;padding:8px 0">
  Gerador de Capa de Livro · CMYK · 300 DPI · Compatível com gráficas brasileiras e KDP Amazon
</div>
""", unsafe_allow_html=True)
