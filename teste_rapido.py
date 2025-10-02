#!/usr/bin/env python3
"""
Teste rápido para verificar se OpenAI está funcionando
"""

import requests
import json

def testar_openai():
    url = "http://localhost:5000/process"
    
    email_teste = """Assunto: Mudança de Requisito no Projeto X - Prazo Imediato

Caro Desenvolvedor,

A diretoria aprovou uma mudança no requisito de cálculo de juros do sistema. A nova regra deve ser implementada até o final do dia de hoje para que o próximo ciclo de processamento funcione corretamente.

O documento detalhando a alteração está no link do SharePoint. Confirme que entendeu a urgência.

Obrigado,
Gerência de Projetos"""
    
    print("🧪 TESTE RÁPIDO - VERIFICANDO OPENAI")
    print("=" * 50)
    
    try:
        response = requests.post(url, data={"email_text": email_teste}, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Status: {response.status_code}")
            print(f"📧 Categoria: {result.get('categoria')}")
            print(f"📝 Motivo: {result.get('motivo')}")
            print(f"💬 Resposta: {result.get('resposta_sugerida')}")
            
            # Verificar se é contextual
            resposta = result.get('resposta_sugerida', '').lower()
            contextual_words = ['mudança', 'requisito', 'sharepoint', 'urgência', 'hoje', 'prazo']
            
            found_context = [word for word in contextual_words if word in resposta]
            
            print(f"\n🔍 Análise Contextual:")
            print(f"Palavras contextuais encontradas: {found_context}")
            
            if len(found_context) >= 2:
                print("✅ RESPOSTA CONTEXTUAL - OpenAI funcionando!")
            else:
                print("❌ Resposta genérica - OpenAI não está sendo usado")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            print(f"Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    testar_openai()
