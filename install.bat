@echo off
echo ========================================
echo    INSTALANDO EMAIL CLASSIFIER
echo ========================================

echo.
echo 1. Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado! Instale o Python primeiro.
    pause
    exit /b 1
)

echo.
echo 2. Criando ambiente virtual...
python -m venv .venv

echo.
echo 3. Ativando ambiente virtual...
call .venv\Scripts\activate.bat

echo.
echo 4. Instalando dependencias basicas...
pip install flask python-dotenv nltk PyPDF2

echo.
echo 5. Baixando stopwords do NLTK...
python -c "import nltk; nltk.download('stopwords')"

echo.
echo 6. Testando instalacao...
python -c "import flask; print('Flask OK')"
python -c "import nltk; print('NLTK OK')"
python -c "import PyPDF2; print('PyPDF2 OK')"

echo.
echo ========================================
echo    INSTALACAO CONCLUIDA!
echo ========================================
echo.
echo Para rodar o projeto:
echo 1. .venv\Scripts\activate.bat
echo 2. python app.py
echo 3. Acesse: http://localhost:5000
echo.
pause

