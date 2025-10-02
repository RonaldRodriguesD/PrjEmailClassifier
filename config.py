# Configuração do EmailClassifier
# Escolha o método de classificação (gratuito)

# Opções disponíveis:
# 1. "heuristic" - Apenas heurística (sempre funciona, gratuito)
# 2. "huggingface" - Hugging Face (gratuito, precisa instalar transformers)
# 3. "openai" - OpenAI API (pago, precisa de chave)

CLASSIFICATION_METHOD = "openai"  # Usando OpenAI para respostas contextuais inteligentes

# Configurações do Hugging Face
HF_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"

# Configurações da OpenAI
OPENAI_MODEL = "gpt-4o-mini"

