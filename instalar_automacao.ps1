# ========================================
# INSTALADOR AUTOMAÇÃO ESL CLOUD
# ========================================
# Este script instala todas as dependências necessárias

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " INSTALADOR - AUTOMAÇÃO ESL CLOUD" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Instalar bibliotecas Python
Write-Host "📦 Instalando dependências Python..." -ForegroundColor Yellow
pip install selenium python-dotenv webdriver-manager

Write-Host ""
Write-Host "✅ Dependências instaladas com sucesso!" -ForegroundColor Green
Write-Host ""

# 2. Criar arquivo .env se não existir
if (-Not (Test-Path ".env")) {
    Write-Host "📝 Criando arquivo de configuração .env..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✅ Arquivo .env criado!" -ForegroundColor Green
    Write-Host ""
    Write-Host "⚠️  ATENÇÃO: Edite o arquivo .env e adicione suas credenciais!" -ForegroundColor Red
    Write-Host "   ESL_EMAIL=seu_email@empresa.com" -ForegroundColor Gray
    Write-Host "   ESL_SENHA=sua_senha" -ForegroundColor Gray
} else {
    Write-Host "ℹ️  Arquivo .env já existe" -ForegroundColor Blue
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " INSTALAÇÃO CONCLUÍDA!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host "   1. Edite o arquivo .env com suas credenciais" -ForegroundColor White
Write-Host "   2. Execute: python automacao_eslcloud.py" -ForegroundColor White
Write-Host ""
