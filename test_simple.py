#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste simples do EmailClassifier
"""

def test_heuristic_classification():
    """Testa a classificação heurística"""
    print("🔍 Testando classificação heurística...")
    
    # Palavras-chave produtivas
    productive_keywords = {
        "reuni": 3, "cronograma": 3, "prazo": 3, "entrega": 3, "alinhamento": 3,
        "orçamento": 3, "proposta": 3, "contrato": 3, "briefing": 3, "escopo": 3,
        "documenta": 2, "status": 2, "retorno": 2, "agenda": 2, "projeto": 3,
        "cliente": 2, "empresa": 2, "trabalho": 2, "colaboração": 2, "parceria": 2,
    }
    
    # Palavras-chave improdutivas
    unproductive_keywords = {
        "spam": -3, "oferta": -2, "ganhe": -3, "promo": -2, "desconto": -2,
        "sorteio": -3, "bitcoin": -2, "cripto": -2, "investimento": -1,
    }
    
    def classify_text(text):
        text_lower = text.lower()
        score = 0
        found_productive = []
        found_unproductive = []
        
        for kw, weight in productive_keywords.items():
            if kw in text_lower:
                score += weight
                found_productive.append(kw)
        
        for kw, weight in unproductive_keywords.items():
            if kw in text_lower:
                score += weight
                found_unproductive.append(kw)
        
        if len(text.strip()) < 50:
            score -= 2
        
        if score >= 3:
            return "Produtivo", f"Score: {score}. Palavras: {', '.join(found_productive[:3])}"
        else:
            return "Improdutivo", f"Score: {score}. Não apresenta contexto profissional suficiente."
    
    # Testes
    test_emails = [
        "Olá, gostaria de agendar uma reunião para discutir o projeto de desenvolvimento do sistema.",
        "Ganhe dinheiro fácil! Oferta imperdível de investimento em criptomoedas!",
        "Preciso do status do relatório que enviei ontem. Podemos alinhar o cronograma?",
        "Promoção especial! Desconto de 50% em todos os produtos!",
        "Bom dia, envio em anexo a proposta comercial para análise.",
    ]
    
    print("\n📧 Testando e-mails:")
    print("=" * 60)
    
    for i, email in enumerate(test_emails, 1):
        categoria, motivo = classify_text(email)
        print(f"\n{i}. {email[:50]}...")
        print(f"   Categoria: {categoria}")
        print(f"   Motivo: {motivo}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_heuristic_classification()

