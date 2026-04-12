# 📚 Gerador de Capa de Livro

Aplicativo web para gerar capas de livros prontas para gráfica (CMYK · 300 DPI).

## Funcionalidades

- Cálculo automático da lombada por tipo de papel brasileiro
- Upload de imagens de capa, contracapa e lombada
- Marcas de corte e guias técnicas
- Reserva de área para código de barras KDP Amazon
- Download do PDF pronto para gráfica

## Como hospedar gratuitamente no Streamlit Cloud

1. Crie uma conta gratuita em **share.streamlit.io**
2. Crie um repositório no GitHub e envie os arquivos:
   - `app.py`
   - `requirements.txt`
3. No Streamlit Cloud, clique em **"New app"**
4. Escolha seu repositório e o arquivo `app.py`
5. Clique em **Deploy** — em 2 minutos o link estará pronto!

## Como rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Papéis suportados

| Papel         | mm/folha |
|---------------|----------|
| Pólen 80g     | 0,113    |
| Offset 75g    | 0,095    |
| Offset 90g    | 0,110    |
| Couchê 90g    | 0,092    |
| Couchê 115g   | 0,108    |
