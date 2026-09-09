import os
import requests
from flask import Flask, request, jsonify, render_template
from pypdf import PdfReader

app = Flask(__name__)

# Usada apenas como fallback caso o campo de API key na página fique em branco.
GAMMA_API_KEY_ENV = os.environ.get("GAMMA_API_KEY", "")
GAMMA_BASE_URL = "https://public-api.gamma.app/v1.0"

# Limite de caracteres de texto enviado à Gamma (a API aceita até ~100.000 tokens)
MAX_CHARS = 120000


def extrair_texto_pdf(arquivo) -> str:
    """Extrai o texto de um PDF enviado via upload."""
    leitor = PdfReader(arquivo)
    partes = []
    for pagina in leitor.pages:
        texto = pagina.extract_text() or ""
        if texto.strip():
            partes.append(texto)
    texto_completo = "\n\n".join(partes).strip()
    if len(texto_completo) > MAX_CHARS:
        texto_completo = texto_completo[:MAX_CHARS]
    return texto_completo


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def gerar_apresentacao():
    api_key = request.form.get("apiKey") or GAMMA_API_KEY_ENV
    if not api_key:
        return jsonify({"erro": "Informe sua Gamma API Key no campo no topo da página."}), 400

    if "pdf" not in request.files:
        return jsonify({"erro": "Nenhum arquivo PDF enviado."}), 400

    arquivo = request.files["pdf"]
    if arquivo.filename == "":
        return jsonify({"erro": "Nenhum arquivo selecionado."}), 400

    if not arquivo.filename.lower().endswith(".pdf"):
        return jsonify({"erro": "Envie um arquivo .pdf."}), 400

    try:
        texto = extrair_texto_pdf(arquivo)
    except Exception as e:
        return jsonify({"erro": f"Falha ao ler o PDF: {e}"}), 400

    if not texto:
        return jsonify({"erro": "Não foi possível extrair texto do PDF (pode ser um PDF escaneado/imagem)."}), 400

    # Parâmetros opcionais vindos do formulário
    num_cards = request.form.get("numCards", type=int)
    tom = request.form.get("tone") or None
    publico = request.form.get("audience") or None
    text_mode = request.form.get("textMode", "condense")
    idioma = request.form.get("language") or "pt-br"

    payload = {
        "inputText": texto,
        "format": "presentation",
        "textMode": text_mode,
        "exportAs": "pptx",
        "textOptions": {
            "language": idioma,
        },
    }
    if num_cards:
        payload["numCards"] = num_cards
    if tom:
        payload["textOptions"]["tone"] = tom
    if publico:
        payload["textOptions"]["audience"] = publico

    resp = requests.post(
        f"{GAMMA_BASE_URL}/generations",
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=30,
    )

    if resp.status_code >= 400:
        return jsonify({"erro": f"Erro da API Gamma ({resp.status_code}): {resp.text}"}), 502

    dados = resp.json()
    return jsonify({"generationId": dados.get("generationId")})


@app.route("/api/status/<generation_id>", methods=["GET"])
def status_geracao(generation_id):
    api_key = request.args.get("apiKey") or GAMMA_API_KEY_ENV
    if not api_key:
        return jsonify({"erro": "Informe sua Gamma API Key no campo no topo da página."}), 400

    resp = requests.get(
        f"{GAMMA_BASE_URL}/generations/{generation_id}",
        headers={"X-API-KEY": api_key},
        timeout=30,
    )

    if resp.status_code >= 400:
        return jsonify({"erro": f"Erro da API Gamma ({resp.status_code}): {resp.text}"}), 502

    return jsonify(resp.json())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
