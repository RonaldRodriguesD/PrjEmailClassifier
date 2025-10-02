# 🔑 CONFIGURAÇÃO DA OPENAI

## PASSO 1: Obter Chave API

1. Acesse: https://platform.openai.com/api-keys
2. Faça login ou crie uma conta
3. Clique em "Create new secret key"
4. Copie a chave (começa com `sk-`)

## PASSO 2: Configurar no Projeto

Crie um arquivo `.env` na raiz do projeto com:

```
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
PORT=5000
```

## PASSO 3: Custo

- **Modelo recomendado:** `gpt-4o-mini`
- **Custo por email:** ~$0.002 (R$ 0,01)
- **100 emails:** ~$0.20 (R$ 1,00)
- **Muito barato para uso profissional!**

## PASSO 4: Testar

Após configurar, reinicie o servidor:
```bash
python app.py
```

A IA agora gerará respostas contextuais inteligentes!

## EXEMPLO DE RESULTADO

**Email:** "Mudança urgente no projeto X - implementar até hoje"
**Resposta IA:** "Olá! Recebi a informação sobre a mudança no projeto X. Vou implementar a alteração até o final do dia conforme solicitado. Confirmo que entendi a urgência."

**Muito melhor que templates fixos!** 🎉
