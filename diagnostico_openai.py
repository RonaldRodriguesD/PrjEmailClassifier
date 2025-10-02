#!/usr/bin/env python3
"""
Diagnóstico para verificar configuração OpenAI
"""

import os
from dotenv import load_dotenv

def diagnosticar_openai():
    print("🔍 DIAGNÓSTICO OPENAI")
    print("=" * 40)
    
    # Carregar .env
    load_dotenv()
    
    # Verificar chave
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    print(f"1. Arquivo .env encontrado: {'✅' if os.path.exists('.env') else '❌'}")
    print(f"2. OPENAI_API_KEY definida: {'✅' if api_key else '❌'}")
    
    if api_key:
        print(f"3. Chave começa com 'sk-': {'✅' if api_key.startswith('sk-') else '❌'}")
        print(f"4. Tamanho da chave: {len(api_key)} caracteres")
        print(f"5. Modelo configurado: {model}")
        
        # Testar importação OpenAI
        try:
            from openai import OpenAI
            print("6. Biblioteca OpenAI: ✅ Importada")
            
            # Testar cliente
            try:
                client = OpenAI(api_key=api_key)
                print("7. Cliente OpenAI: ✅ Criado")
            except Exception as e:
                print(f"7. Cliente OpenAI: ❌ Erro: {e}")
                
        except ImportError as e:
            print(f"6. Biblioteca OpenAI: ❌ Erro: {e}")
    else:
        print("3. ❌ Chave não encontrada")
        print("\n💡 SOLUÇÃO:")
        print("1. Crie um arquivo .env na raiz do projeto")
        print("2. Adicione: OPENAI_API_KEY=sk-sua-chave-aqui")
        print("3. Reinicie o servidor")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    diagnosticar_openai()
