import os
import re
import json
from typing import Dict, Any, List, Tuple

from flask import Flask, request, jsonify, render_template
from werkzeug.datastructures import FileStorage
from dotenv import load_dotenv

import nltk
from nltk.corpus import stopwords

from PyPDF2 import PdfReader

# OpenAI SDK
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Hugging Face (gratuito)
try:
    from transformers import pipeline
    HF_AVAILABLE = True
except Exception:
    HF_AVAILABLE = False


load_dotenv()

# Importar configuração
try:
    from config import CLASSIFICATION_METHOD, HF_MODEL, OPENAI_MODEL
except ImportError:
    CLASSIFICATION_METHOD = "heuristic"
    HF_MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    OPENAI_MODEL = "gpt-4o-mini"

app = Flask(__name__)


# histórico de e-mails processados
HISTORY_MAX = 20
processed_history: List[Dict[str, Any]] = []
counts = {"Produtivo": 0, "Improdutivo": 0}



def ensure_nltk() -> None:
    try:
        _ = stopwords.words("english")
    except LookupError:
        nltk.download("stopwords")


def extract_text_from_file(upload: FileStorage) -> str:
    filename = (upload.filename or "").lower()
    if filename.endswith(".txt"):
        content = upload.read()
        try:
            return content.decode("utf-8", errors="ignore")
        finally:
            upload.close()
    if filename.endswith(".pdf"):
        reader = PdfReader(upload)
        text_parts: List[str] = []
        for page in reader.pages:
            try:
                text_parts.append(page.extract_text() or "")
            except Exception:
                continue
        upload.close()
        return "\n".join(text_parts)
    raise ValueError("Formato de arquivo não suportado. Envie .txt ou .pdf.")


def generate_contextual_response(response_type: str, email_original: str, context_data: List[str]) -> str:
    """Gera respostas dinâmicas baseadas no contexto do email"""
    
    # Extrair informações do email para personalizar a resposta
    email_lower = email_original.lower()
    
    # Detectar se mencionam nome/empresa
    has_name_mention = any(word in email_lower for word in ["meu nome", "me chamo", "sou", "empresa"])
    
    # Detectar urgência
    is_urgent = any(word in email_lower for word in ["urgente", "rápido", "hoje", "amanhã", "prazo"])
    
    # Detectar se é primeira interação
    is_first_contact = any(word in email_lower for word in ["primeira vez", "conheci", "indicação", "recomendação"])
    
    if response_type == "business_strong":
        if "meetings" in context_data:
            if is_urgent:
                return "Olá! Vejo que há urgência para a reunião. Posso disponibilizar um horário ainda hoje ou amanhã. Qual seria o melhor período para você?"
            else:
                return "Olá! Fico feliz em agendar uma reunião. Tenho disponibilidade na próxima semana. Poderia me enviar alguns horários que funcionam para você?"
                
        elif "projects" in context_data:
            return "Olá! Obrigado pelo interesse no projeto. Vou analisar os detalhes e preparar uma proposta inicial. Podemos agendar uma conversa para alinhar expectativas e cronograma?"
            
        elif "business" in context_data:
            return "Olá! Recebi sua solicitação comercial. Vou revisar os detalhes e retornar com feedback em breve. Caso tenha documentação adicional, fique à vontade para enviar."
            
        else:
            return "Olá! Obrigado pelo contato profissional. Vou analisar sua mensagem e retornar com uma resposta detalhada em breve."
    
    elif response_type == "business_moderate":
        if is_first_contact:
            return "Olá! Obrigado pelo primeiro contato. Vou analisar sua proposta e retornar em breve. Caso tenha materiais complementares, pode enviar."
        else:
            return "Olá! Recebi sua mensagem e vou analisar os pontos mencionados. Retorno em breve com mais informações."
    
    elif response_type == "business_light":
        return "Olá! Obrigado pelo contato. Vou verificar internamente e retornar com uma posição. Aguarde meu retorno."
    
    elif response_type == "spam":
        if "bitcoin" in context_data or "cripto" in context_data:
            return "Obrigado pelo contato, mas não temos interesse em investimentos ou criptomoedas no momento."
        elif "oferta" in context_data or "promoção" in context_data:
            return "Obrigado pela oferta, mas no momento não temos interesse em serviços promocionais."
        else:
            return "Obrigado pelo contato, mas no momento não temos interesse neste tipo de proposta."
    
    elif response_type == "generic":
        return "Olá! Obrigado pela mensagem. Para melhor atendê-lo, poderia ser mais específico sobre o assunto de interesse?"
    
    else:  # unclear
        return "Olá! Obrigado pelo contato. No momento não conseguimos identificar como podemos ajudar. Caso tenha uma solicitação específica, fique à vontade para detalhar."


def basic_preprocess(text: str) -> str:
    ensure_nltk()

    # Normalize whitespace and lowercase
    text = text.replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip().lower()

    # Remove URLs, emails
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"\b\S+@\S+\.[a-z]{2,}\b", " ", text)

    # Remove numbers and punctuation (keep letters and spaces)
    text = re.sub(r"[^a-zá-úà-ùâ-ûãõç\s]", " ", text)

    # Stopwords (Portuguese + English)
    sw_pt = set()
    sw_en = set()
    try:
        sw_pt = set(stopwords.words("portuguese"))
    except Exception:
        pass
    try:
        sw_en = set(stopwords.words("english"))
    except Exception:
        pass
    sw_all = sw_pt | sw_en

    tokens = [t for t in text.split() if t and t not in sw_all]
    return " ".join(tokens)


def classify_with_huggingface(email_original: str, email_preprocessed: str) -> Dict[str, Any]:
    """Classificação usando Hugging Face (gratuito) - IA inteligente e flexível"""
    if not HF_AVAILABLE:
        print("⚠️ Hugging Face não disponível, usando heurística")
        return heuristic_classification(email_original, email_preprocessed)
    
    try:
        print("🤗 Iniciando classificação inteligente com IA...")
        
        # Usar modelo de sentimento
        classifier = pipeline("sentiment-analysis", 
                           model="nlptown/bert-base-multilingual-uncased-sentiment",
                           return_all_scores=True)
        
        # Analisar tanto o texto original quanto o pré-processado
        text_to_analyze = email_original[:512] if len(email_original) > 512 else email_original
        results = classifier(text_to_analyze)
        
        # Extrair scores
        positive_score = 0
        negative_score = 0
        neutral_score = 0
        
        for result in results[0]:
            label = result['label']
            score = result['score']
            
            if label in ['5 stars', '4 stars']:
                positive_score = max(positive_score, score)
            elif label in ['1 star', '2 stars']:
                negative_score = max(negative_score, score)
            elif label in ['3 stars']:
                neutral_score = max(neutral_score, score)
        
        print(f"📊 Sentimento IA - Positivo: {positive_score:.2f}, Negativo: {negative_score:.2f}, Neutro: {neutral_score:.2f}")
        
        # Análise contextual mais rigorosa
        business_indicators = {
            "meetings": ["reunião", "reuni", "encontro", "call", "videochamada", "zoom", "teams"],
            "projects": ["projeto", "desenvolvimento", "implementação", "sistema", "aplicação", "software"],
            "business": ["proposta", "orçamento", "contrato", "briefing", "escopo", "cronograma", "prazo"],
            "professional": ["empresa", "cliente", "parceria", "colaboração", "trabalho", "serviço"],
            "communication": ["retorno", "feedback", "alinhamento", "status", "atualização", "informações"]
        }
        
        # Indicadores de spam/improdutivo (mais rigoroso)
        spam_indicators = {
            "promotional": ["oferta", "promoção", "desconto", "grátis", "ganhe", "sorteio", "prêmio"],
            "financial_scam": ["bitcoin", "cripto", "investimento", "lucro", "dinheiro fácil", "renda extra"],
            "generic_sales": ["vendas", "marketing", "anúncio", "propaganda", "divulgação"],
            "suspicious": ["clique aqui", "limitado", "exclusivo", "imperdível"]
        }
        
        # Calcular scores contextuais
        business_score = 0
        spam_score = 0
        found_business = []
        found_spam = []
        
        # Verificar indicadores de negócio
        for category, keywords in business_indicators.items():
            category_found = False
            for keyword in keywords:
                if keyword.lower() in email_original.lower() or keyword in email_preprocessed:
                    business_score += 1
                    if not category_found:
                        found_business.append(category)
                        category_found = True
        
        # Verificar indicadores de spam (com contexto inteligente)
        for category, keywords in spam_indicators.items():
            for keyword in keywords:
                if keyword.lower() in email_original.lower():
                    spam_score += 2  # Peso maior para spam
                    found_spam.append(keyword)
        
        # Verificar "urgente" com contexto - só é spam se não tiver contexto profissional
        if "urgente" in email_original.lower():
            if business_score == 0:  # Sem contexto profissional = provável spam
                spam_score += 2
                found_spam.append("urgente")
            # Se tem contexto profissional, "urgente" é legítimo
        
        # Análise estrutural do email
        email_lines = email_original.strip().split('\n')
        has_proper_greeting = any(greeting in email_original.lower() for greeting in 
                                ["prezado", "caro", "olá", "bom dia", "boa tarde", "boa noite"])
        has_signature = len(email_lines) > 2 and any(line.strip() for line in email_lines[-2:])
        is_structured = len(email_lines) >= 3
        is_substantial = len(email_original.strip()) >= 80
        
        # Verificar se é muito genérico/vago
        generic_phrases = ["tudo bem", "como vai", "e aí", "oi", "tchau", "até mais", "falou"]
        generic_count = sum(1 for phrase in generic_phrases if phrase in email_original.lower())
        
        print(f"🔍 Análise contextual - Business: {business_score}, Spam: {spam_score}, Genérico: {generic_count}")
        
        # Lógica de classificação mais inteligente
        if spam_score >= 2:  # Spam detectado
            categoria = "Improdutivo"
            motivo = f"IA detectou indicadores de spam/promoção (score: {spam_score}). Palavras: {found_spam[:3]}"
            resposta = generate_contextual_response("spam", email_original, found_spam)
            
        elif business_score >= 3 and spam_score == 0:  # Contexto profissional forte
            categoria = "Produtivo"
            motivo = f"IA identificou contexto profissional sólido (business_score: {business_score}, categorias: {found_business})"
            resposta = generate_contextual_response("business_strong", email_original, found_business)
            
        elif business_score >= 2 and is_structured and is_substantial and spam_score == 0:
            categoria = "Produtivo"
            motivo = f"IA detectou email profissional estruturado (business_score: {business_score}, estruturado e substancial)"
            resposta = generate_contextual_response("business_moderate", email_original, found_business)
            
        elif business_score >= 1 and positive_score > 0.4 and spam_score == 0 and is_substantial:
            categoria = "Produtivo"
            motivo = f"IA identificou contexto profissional com sentimento positivo (business: {business_score}, sentimento: {positive_score:.2f})"
            resposta = generate_contextual_response("business_light", email_original, found_business)
            
        elif generic_count >= 2 or not is_substantial:
            categoria = "Improdutivo"
            motivo = f"IA detectou email muito genérico ou insubstancial (genérico: {generic_count}, tamanho: {len(email_original)})"
            resposta = generate_contextual_response("generic", email_original, [])
            
        else:
            categoria = "Improdutivo"
            motivo = f"IA não identificou contexto profissional suficiente (business: {business_score}, spam: {spam_score}, sentimento: pos={positive_score:.2f})"
            resposta = generate_contextual_response("unclear", email_original, [])
        
        print(f"✅ Classificação IA: {categoria}")
        return {"categoria": categoria, "motivo": motivo, "resposta_sugerida": resposta}
        
    except Exception as e:
        print(f"❌ Erro no Hugging Face: {e}")
        print("🔄 Fallback para classificação heurística...")
        return heuristic_classification(email_original, email_preprocessed)


def classify_and_respond_with_openai(email_original: str, email_preprocessed: str) -> Dict[str, Any]:
    """Classificação e resposta contextual inteligente com OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    print(f"🔍 Debug OpenAI - API Key existe: {'✅' if api_key else '❌'}")
    print(f"🔍 Debug OpenAI - OpenAI disponível: {'✅' if OpenAI else '❌'}")
    
    if not api_key or OpenAI is None:
        print("⚠️ OpenAI não configurado, usando Hugging Face como fallback")
        return classify_with_huggingface(email_original, email_preprocessed)

    client = OpenAI(api_key=api_key)

    system_prompt = """Você é um assistente especializado em análise e resposta de emails profissionais.

TAREFA: Analise o email e forneça:
1) Classificação: "Produtivo" ou "Improdutivo"
2) Motivo detalhado da classificação
3) Resposta contextual que responda EXATAMENTE ao conteúdo do email

CRITÉRIOS PARA CLASSIFICAÇÃO:
- PRODUTIVO: Emails sobre trabalho, projetos, reuniões, propostas, colaborações, feedbacks, solicitações profissionais
- IMPRODUTIVO: Spam, ofertas genéricas, emails muito vagos, conteúdo irrelevante

INSTRUÇÕES PARA RESPOSTA:
- Leia CUIDADOSAMENTE o conteúdo do email
- Responda de forma ESPECÍFICA ao que foi mencionado
- Se mencionam prazo, reconheça o prazo
- Se pedem reunião, responda sobre reunião
- Se é mudança de requisito, responda sobre a mudança
- Se é proposta, responda sobre a proposta
- Seja profissional, educado e direto
- Use tom apropriado (formal/informal baseado no email recebido)

FORMATO DE RESPOSTA: JSON válido com exatamente estes campos:
{
  "categoria": "Produtivo" ou "Improdutivo",
  "motivo": "explicação detalhada da classificação",
  "resposta_sugerida": "resposta contextual específica"
}"""

    user_prompt = f"""Analise este email e forneça classificação + resposta contextual:

EMAIL RECEBIDO:
{email_original.strip()}

Gere a resposta em JSON considerando:
- O contexto específico mencionado no email
- Qualquer prazo ou urgência mencionada
- O tipo de solicitação ou informação
- O tom apropriado para responder

Responda APENAS com o JSON válido."""

    try:
        print("🤖 Gerando resposta contextual com OpenAI...")
        completion = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,  # Pouca criatividade para manter consistência
            max_tokens=500,   # Limite para respostas concisas
        )
        
        content = completion.choices[0].message.content or "{}"
        print(f"📝 Resposta OpenAI: {content[:150]}...")
        
        # Limpar possível markdown do JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        data = json.loads(content)
        categoria = str(data.get("categoria", "Improdutivo")).strip()
        
        # Validar categoria
        if categoria not in ("Produtivo", "Improdutivo"):
            categoria = "Improdutivo"
            
        motivo = str(data.get("motivo", "Classificação automática")).strip()
        resposta = str(data.get("resposta_sugerida", "Obrigado pelo contato.")).strip()
        
        print(f"✅ OpenAI Classificou: {categoria}")
        return {"categoria": categoria, "motivo": motivo, "resposta_sugerida": resposta}
        
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar JSON da OpenAI: {e}")
        print(f"Conteúdo recebido: {content}")
        return classify_with_huggingface(email_original, email_preprocessed)
    except Exception as e:
        print(f"❌ Erro na OpenAI API: {e}")
        return classify_with_huggingface(email_original, email_preprocessed)


def heuristic_classification(email_original: str, email_preprocessed: str) -> Dict[str, Any]:
    """Classificação heurística melhorada (gratuita)"""
    print("🔍 Usando classificação heurística...")
    
    # Palavras-chave produtivas (peso maior)
    productive_keywords = {
        "reuni": 3, "cronograma": 3, "prazo": 3, "entrega": 3, "alinhamento": 3,
        "orçamento": 3, "proposta": 3, "contrato": 3, "briefing": 3, "escopo": 3,
        "documenta": 2, "status": 2, "retorno": 2, "agenda": 2, "projeto": 3,
        "cliente": 2, "empresa": 2, "trabalho": 2, "colaboração": 2, "parceria": 2,
        "desenvolvimento": 2, "implementação": 2, "apresentação": 2, "relatório": 2
    }
    
    # Palavras-chave improdutivas (peso negativo)
    unproductive_keywords = {
        "spam": -3, "oferta": -2, "ganhe": -3, "promo": -2, "desconto": -2,
        "sorteio": -3, "bitcoin": -2, "cripto": -2, "investimento": -1,
        "marketing": -1, "vendas": -1, "propaganda": -2, "anúncio": -2
    }
    
    # Calcular score
    score = 0
    found_productive = []
    found_unproductive = []
    
    for kw, weight in productive_keywords.items():
        if kw in email_preprocessed:
            score += weight
            found_productive.append(kw)
    
    for kw, weight in unproductive_keywords.items():
        if kw in email_preprocessed:
            score += weight
            found_unproductive.append(kw)
    
    # Verificar tamanho do e-mail (e-mails muito curtos tendem a ser improdutivos)
    if len(email_original.strip()) < 50:
        score -= 2
    
    # Verificar se tem estrutura de e-mail profissional
    professional_indicators = ["assunto:", "para:", "de:", "data:", "horário:", "local:"]
    has_structure = any(indicator in email_original.lower() for indicator in professional_indicators)
    if has_structure:
        score += 1
    
    # Classificar
    if score >= 3:
        categoria = "Produtivo"
        motivo = f"Score: {score}. Palavras-chave encontradas: {', '.join(found_productive[:3])}"
        resposta = (
            "Olá, obrigado pelo contato. Podemos agendar uma reunião para alinhar os próximos passos? "
            "Envie, por favor, sua disponibilidade e eventuais materiais relevantes."
        )
    else:
        categoria = "Improdutivo"
        motivo = f"Score: {score}. Não apresenta contexto profissional suficiente."
        if found_unproductive:
            motivo += f" Palavras improdutivas: {', '.join(found_unproductive[:2])}"
        resposta = (
            "Olá, obrigado pela mensagem. No momento, não temos interesse. Caso deseje, mantenha-nos "
            "informados sobre novidades mais alinhadas às nossas necessidades."
        )

    return {"categoria": categoria, "motivo": motivo, "resposta_sugerida": resposta}


def update_history(entry: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    processed_history.insert(0, entry)
    if len(processed_history) > HISTORY_MAX:
        processed_history.pop()
    cat = entry.get("categoria")
    if cat in counts:
        counts[cat] += 1
    return processed_history, counts


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def index():
    return render_template("index.html", counts=counts, history=processed_history)


@app.post("/process")
def process_email():
    try:
        email_text = (request.form.get("email_text") or "").strip()
        file = request.files.get("file")

        if not email_text and file and getattr(file, "filename", ""):
            email_text = extract_text_from_file(file)

        if not email_text:
            return jsonify({"error": "Forneça texto do e-mail ou envie um arquivo .txt/.pdf."}), 400

        preprocessed = basic_preprocess(email_text)
        
        # Usar método configurado
        if CLASSIFICATION_METHOD == "openai":
            print("🤖 Usando OpenAI...")
            result = classify_and_respond_with_openai(email_text, preprocessed)
        elif CLASSIFICATION_METHOD == "huggingface" and HF_AVAILABLE:
            print("🤗 Usando Hugging Face (gratuito)...")
            result = classify_with_huggingface(email_text, preprocessed)
        else:
            print("🔍 Usando classificação heurística (gratuito)...")
            result = heuristic_classification(email_text, preprocessed)

        entry = {
            "categoria": result.get("categoria"),
            "motivo": result.get("motivo"),
            "resposta_sugerida": result.get("resposta_sugerida"),
            "preview": email_text[:220] + ("..." if len(email_text) > 220 else ""),
        }
        history, totals = update_history(entry)

        return jsonify({
            "categoria": entry["categoria"],
            "motivo": entry["motivo"],
            "resposta_sugerida": entry["resposta_sugerida"],
            "counts": totals,
            "history": history[:10],  # send a short recent history snapshot
        })
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as exc:  # pragma: no cover
        return jsonify({"error": f"Falha no processamento: {exc}"}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)