#!/bin/bash

# YouTube Shorts Automation - Script de Instalação
# Canal: Leonardo_Zarelli

echo "🚀 Iniciando instalação do YouTube Shorts Automation..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para logs
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Python está instalado
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        log_info "Python $PYTHON_VERSION encontrado"
    else
        log_error "Python 3 não encontrado. Instale Python 3.8+ primeiro."
        exit 1
    fi
}

# Verificar se pip está instalado
check_pip() {
    if command -v pip3 &> /dev/null; then
        log_info "pip3 encontrado"
    else
        log_error "pip3 não encontrado. Instale pip primeiro."
        exit 1
    fi
}

# Verificar FFmpeg
check_ffmpeg() {
    if command -v ffmpeg &> /dev/null; then
        log_info "FFmpeg encontrado"
    else
        log_warn "FFmpeg não encontrado. Tentando instalar..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt update && sudo apt install -y ffmpeg
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install ffmpeg
        elif [[ "$OSTYPE" == "msys" ]]; then
            log_error "No Windows, baixe FFmpeg de https://ffmpeg.org/download.html"
            exit 1
        fi
    fi
}

# Criar ambiente virtual
create_venv() {
    log_info "Criando ambiente virtual..."
    if [ -d "venv" ]; then
        log_warn "Ambiente virtual já existe. Removendo..."
        rm -rf venv
    fi
    
    python3 -m venv venv
    
    # Ativar ambiente virtual
    if [[ "$OSTYPE" == "msys" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    log_info "Ambiente virtual criado e ativado"
}

# Instalar dependências
install_dependencies() {
    log_info "Instalando dependências Python..."
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Instalar dependências
    pip install -r requirements.txt
    
    log_info "Dependências instaladas com sucesso"
}

# Criar diretórios necessários
create_directories() {
    log_info "Criando diretórios necessários..."
    
    mkdir -p downloads
    mkdir -p shorts
    mkdir -p logs
    mkdir -p temp
    
    # Criar diretório Windows se necessário
    if [[ "$OSTYPE" == "msys" ]]; then
        mkdir -p "/c/Users/leona/OneDrive/Gravações/Shorts"
    fi
    
    log_info "Diretórios criados"
}

# Configurar permissões
set_permissions() {
    log_info "Configurando permissões..."
    
    chmod +x main.py
    chmod +x install.sh
    
    log_info "Permissões configuradas"
}

# Verificar configuração
verify_config() {
    log_info "Verificando configuração..."
    
    if [ -f "config/config.json" ]; then
        log_info "Arquivo de configuração encontrado"
    else
        log_error "Arquivo config/config.json não encontrado"
        exit 1
    fi
    
    if [ -f "config/client_secrets.json" ]; then
        log_info "Credenciais OAuth encontradas"
    else
        log_error "Arquivo config/client_secrets.json não encontrado"
        exit 1
    fi
}

# Teste básico
test_installation() {
    log_info "Testando instalação..."
    
    python3 -c "
import sys
try:
    import moviepy
    import cv2
    import yt_dlp
    import googleapiclient
    print('✅ Todas as dependências principais importadas com sucesso')
except ImportError as e:
    print(f'❌ Erro na importação: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        log_info "Teste de instalação passou!"
    else
        log_error "Teste de instalação falhou"
        exit 1
    fi
}

# Função principal
main() {
    echo "📺 YouTube Shorts Automation - Leonardo_Zarelli"
    echo "================================================"
    
    check_python
    check_pip
    check_ffmpeg
    create_venv
    install_dependencies
    create_directories
    set_permissions
    verify_config
    test_installation
    
    echo ""
    log_info "🎉 Instalação concluída com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "1. Ative o ambiente virtual: source venv/bin/activate (Linux/Mac) ou venv\\Scripts\\activate (Windows)"
    echo "2. Execute: python3 main.py"
    echo "3. Configure suas credenciais OAuth na primeira execução"
    echo ""
    echo "📁 Diretórios criados:"
    echo "  - downloads/  : Vídeos baixados"
    echo "  - shorts/     : Shorts criados"
    echo "  - logs/       : Logs do sistema"
    echo "  - temp/       : Arquivos temporários"
    echo ""
    echo "🔧 Configuração:"
    echo "  - config/config.json        : Configurações principais"
    echo "  - config/client_secrets.json : Credenciais OAuth"
    echo ""
}

# Executar instalação
main