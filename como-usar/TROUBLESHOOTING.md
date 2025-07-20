# 🛠️ Guia de Solução de Problemas

## 🔍 Diagnóstico Inicial

### Verificar Ambiente
```bash
# Verificar se ambiente virtual está ativo
which python3
# Deve mostrar: /caminho/para/venv/bin/python3

# Verificar versão do Python
python3 --version
# Deve ser 3.8 ou superior

# Verificar dependências
pip list | grep -E "(moviepy|yt-dlp)"
```

## ❌ Problemas Comuns

### 1. Erro: "ModuleNotFoundError: No module named 'moviepy'"

**Causa**: Dependências não instaladas ou ambiente virtual não ativado

**Solução**:
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
python3 -c "import moviepy; print('MoviePy OK')"
```

### 2. Erro: "❌ Falha no download"

**Causa**: Problemas com URL ou conexão

**Diagnóstico**:
```bash
# Testar URL manualmente
yt-dlp --list-formats "https://youtu.be/VIDEO_ID"
```

**Soluções**:
- Verificar se URL está correta
- Testar com vídeo público
- Verificar conexão com internet
- Usar URL completa: `https://www.youtube.com/watch?v=VIDEO_ID`

### 3. Erro: "❌ Falha na análise"

**Causa**: Vídeo sem áudio ou muito curto

**Diagnóstico**:
```bash
# Verificar informações do vídeo
yt-dlp --get-duration "https://youtu.be/VIDEO_ID"
yt-dlp --get-title "https://youtu.be/VIDEO_ID"
```

**Soluções**:
- Usar vídeo com pelo menos 2 minutos
- Verificar se vídeo tem áudio
- Testar com vídeo diferente

### 4. Erro: "externally-managed-environment"

**Causa**: Tentativa de instalar globalmente em sistema protegido

**Solução**:
```bash
# Sempre usar ambiente virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5. Erro: "EOF when reading a line"

**Causa**: Entrada interativa sem terminal

**Solução**:
```bash
# Usar formato específico
python3 production_script.py URL 7 screen
# Em vez de deixar o menu interativo
```

## 🔧 Soluções Específicas

### Problema: Vídeo não processa
```bash
# Verificar se arquivo foi baixado
ls -la downloads/

# Verificar logs
python3 production_script.py URL 2>&1 | tee debug.log

# Testar com vídeo simples
python3 production_script.py "https://youtu.be/dQw4w9WgXcQ" 1 normal
```

### Problema: Layout screen não funciona
```bash
# Testar funcionalidade
python3 test_split_screen.py

# Verificar se vídeo é adequado para split-screen
# (deve ter webcam + conteúdo)
```

### Problema: Arquivos muito grandes
```bash
# Verificar tamanho
du -h shorts/*.mp4

# Reduzir qualidade se necessário
# (editar config.json se existir)
```

### Problema: Processo muito lento
```bash
# Verificar recursos do sistema
top
free -h

# Reduzir número de shorts
python3 production_script.py URL 3 screen
```

## 🔍 Ferramentas de Diagnóstico

### Script de Diagnóstico Completo
```bash
#!/bin/bash
echo "=== DIAGNÓSTICO DO SISTEMA ==="
echo "Python: $(python3 --version)"
echo "Ambiente virtual: $(which python3)"
echo "Espaço em disco: $(df -h . | tail -1)"
echo "Memória: $(free -h | grep Mem)"
echo

echo "=== VERIFICANDO DEPENDÊNCIAS ==="
python3 -c "
try:
    import moviepy
    print('✅ MoviePy:', moviepy.__version__)
except ImportError:
    print('❌ MoviePy não instalado')

try:
    import yt_dlp
    print('✅ yt-dlp disponível')
except ImportError:
    print('❌ yt-dlp não instalado')

try:
    import numpy
    print('✅ NumPy:', numpy.__version__)
except ImportError:
    print('❌ NumPy não instalado')
"

echo "=== VERIFICANDO ESTRUTURA ==="
ls -la | grep -E "(downloads|shorts|config)"
echo

echo "=== TESTANDO FUNCIONALIDADE ==="
python3 production_script.py 2>&1 | head -5
```

### Teste de Conectividade
```bash
# Testar download simples
yt-dlp --extract-flat "https://youtu.be/dQw4w9WgXcQ"
```

### Verificar Logs
```bash
# Executar com logs detalhados
python3 production_script.py URL 5 screen 2>&1 | tee production.log
```

## 🚨 Problemas Críticos

### Sistema Trava Durante Processamento
```bash
# Verificar processos
ps aux | grep python3

# Matar processo se necessário
pkill -f production_script.py

# Verificar memória
free -h
```

### Sem Espaço em Disco
```bash
# Verificar espaço
df -h

# Limpar arquivos temporários
rm downloads/*.mp4
rm shorts/*.mp4
```

### Dependências Quebradas
```bash
# Recriar ambiente virtual
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Monitoramento

### Monitorar Progresso
```bash
# Em terminal separado
watch -n 1 "ls -la shorts/ | wc -l"
```

### Verificar Uso de Recursos
```bash
# Monitorar processo
htop
# ou
top
```

## 🔄 Procedimentos de Recuperação

### Recuperação Padrão
```bash
# 1. Parar processos
pkill -f production_script.py

# 2. Limpar arquivos temporários
rm -f downloads/*.part
rm -f shorts/*.tmp

# 3. Verificar integridade
ls -la shorts/
```

### Recuperação Completa
```bash
# 1. Backup de configurações
cp -r config/ config_backup/

# 2. Limpar tudo
rm -rf downloads/* shorts/*

# 3. Recriar ambiente
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Teste simples
python3 test_split_screen.py
```

## 📞 Quando Buscar Ajuda

### Antes de Buscar Suporte
- [ ] Executar diagnóstico completo
- [ ] Verificar logs de erro
- [ ] Testar com vídeo diferente
- [ ] Verificar espaço em disco
- [ ] Confirmar dependências instaladas

### Informações para Suporte
```bash
# Gerar relatório de sistema
echo "=== RELATÓRIO DE ERRO ===" > error_report.txt
echo "Data: $(date)" >> error_report.txt
echo "Sistema: $(uname -a)" >> error_report.txt
echo "Python: $(python3 --version)" >> error_report.txt
echo "Ambiente: $(which python3)" >> error_report.txt
echo "Erro:" >> error_report.txt
python3 production_script.py PROBLEMA_URL 2>&1 >> error_report.txt
```

## 🎯 Prevenção de Problemas

### Checklist Antes de Usar
- [ ] Ambiente virtual ativado
- [ ] Dependências atualizadas
- [ ] Espaço em disco suficiente (> 5GB)
- [ ] Conexão estável
- [ ] URL válida e acessível

### Manutenção Regular
```bash
# Limpar arquivos antigos (semanal)
find downloads/ -name "*.mp4" -mtime +7 -delete
find shorts/ -name "*.mp4" -mtime +30 -delete

# Atualizar dependências (mensal)
pip install --upgrade -r requirements.txt
```