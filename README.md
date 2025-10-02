## EmailClassifier (Flask + IA)

App simples para:
- Colar texto ou enviar .txt/.pdf
- Classificar e-mails como "Produtivo" ou "Improdutivo"
- Sugerir resposta automática
- Histórico in-memory e mini dashboard

### Métodos de Classificação (3 opções)

1. **Heurística (Gratuito)** - Sempre funciona, baseado em palavras-chave
2. **Hugging Face (Gratuito)** - IA gratuita, precisa instalar transformers
3. **OpenAI (Pago)** - GPT-4, precisa de chave API

### Requisitos
- Python 3.10+
- Para OpenAI: chave API (`OPENAI_API_KEY`)
- Para Hugging Face: `pip install transformers torch`

### Setup local (Windows PowerShell)

#### Opção 1: Heurística (Gratuito - Recomendado para começar)
```powershell
cd C:\Caminho\do\Projeto

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install flask python-dotenv nltk PyPDF2

python app.py
```

#### Opção 2: Hugging Face (Gratuito - IA)
```powershell
# Instalar dependências extras
pip install transformers torch

# Editar config.py e mudar para:
# CLASSIFICATION_METHOD = "huggingface"

python app.py
```

#### Opção 3: OpenAI (Pago - Melhor qualidade)
```powershell
pip install -r requirements.txt

copy .env.example .env
# Abra .env e preencha OPENAI_API_KEY

# Editar config.py e mudar para:
# CLASSIFICATION_METHOD = "openai"

python app.py
```

Depois acesse: http://localhost:5000

### Configuração
Edite `config.py` para escolher o método:
- `CLASSIFICATION_METHOD = "heuristic"` - Heurística (padrão)
- `CLASSIFICATION_METHOD = "huggingface"` - Hugging Face
- `CLASSIFICATION_METHOD = "openai"` - OpenAI

### Notas
- **Heurística**: Sempre funciona, baseado em palavras-chave inteligentes
- **Hugging Face**: Primeira execução baixa o modelo (pode demorar)
- **OpenAI**: Precisa de chave válida e tem custo por uso
- Primeira execução baixa `nltk` stopwords (PT/EN)
- Histórico e contadores ficam na memória (reiniciar zera)