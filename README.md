# PDF → Apresentação (Gamma API)

Aplicação web simples (Flask + HTML/JS) que recebe um PDF, extrai o texto e usa a
[Gamma API](https://developers.gamma.app) para gerar uma apresentação automaticamente.

> **Importante:** a Gamma API não recebe arquivos PDF diretamente — ela gera conteúdo a
> partir de **texto**. Por isso esta aplicação extrai o texto do PDF no servidor
> (com `pypdf`) e envia esse texto como `inputText` para a API.

## Como funciona

1. Você faz upload do PDF na página.
2. O backend extrai o texto de todas as páginas.
3. O backend chama `POST /v1.0/generations` na Gamma API (`format: presentation`,
   `exportAs: pptx`) e recebe um `generationId`.
4. O frontend consulta `GET /v1.0/generations/{generationId}` a cada 5 segundos até o
   status ficar `completed`.
5. Ao concluir, você recebe o link para abrir na Gamma (`gammaUrl`) e o link de
   download do `.pptx` (`exportUrl`).

## Pré-requisitos

- Conta Gamma em plano **Pro, Ultra, Team ou Business** (a API exige um desses planos).
- Uma API key gerada em **Gamma → Account Settings → API Keys**.
- Python 3.10+.

## Instalação

```bash
cd gamma-pdf-app
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração da API Key

A Gamma API Key agora é informada **direto na página**, no campo no topo — ela fica
salva apenas no `localStorage` do seu navegador e é enviada a cada geração. Não é mais
necessário definir variável de ambiente.

(Opcionalmente, se quiser um valor padrão do lado do servidor — por exemplo, para não
depender do navegador — ainda é possível definir `GAMMA_API_KEY` como variável de
ambiente; ela só é usada como *fallback* quando o campo da página estiver vazio.)

## Rodando

```bash
python app.py
```

Acesse **http://localhost:5000** no navegador, envie um PDF e aguarde a geração.

## Parâmetros ajustáveis na interface

- **Gamma API Key**: obrigatória, informada no topo da página.
- **Idioma da apresentação**: enviado como `textOptions.language`. Por padrão a Gamma
  gera em inglês (`en`) se esse parâmetro não for informado — por isso o padrão aqui é
  `pt-br` (Português do Brasil). Também dá pra escolher `pt-pt`, `en`, `es`, `fr` no
  seletor (a Gamma aceita bem mais idiomas — veja a lista completa em
  [Output languages](https://developers.gamma.app/reference/output-language-accepted-values)
  e adicione outras opções no `<select id="language">` do `index.html` se precisar).
- **Nº de slides**: força uma quantidade específica de cards (1–75). Deixe em branco
  para a Gamma decidir automaticamente.
- **Modo do texto**:
  - `condense` (padrão): resume o conteúdo do PDF nos slides.
  - `preserve`: mantém o texto praticamente como está, só organizando em slides.
  - `generate`: usa o texto como ponto de partida e deixa a IA expandir mais.
- **Tom** e **Público-alvo**: textos livres passados como `textOptions.tone` e
  `textOptions.audience` para orientar o estilo da apresentação.

## Limitações conhecidas

- PDFs **escaneados/imagem** (sem camada de texto) não terão texto extraído. Seria
  necessário adicionar OCR (ex.: `pytesseract`) para esses casos.
- O texto enviado é limitado a ~120.000 caracteres (variável `MAX_CHARS` em `app.py`)
  para respeitar o limite de contexto da API.
- A chamada é síncrona por PDF: para uso em produção com múltiplos usuários
  simultâneos, considere uma fila (Celery/RQ) em vez de chamar a Gamma diretamente
  na requisição HTTP.

## Estrutura do projeto

```
gamma-pdf-app/
├── app.py                 # Backend Flask: extração de PDF + integração Gamma API
├── requirements.txt
├── templates/
│   └── index.html         # Interface de upload e acompanhamento
└── README.md
```
