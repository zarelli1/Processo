# 🎬 Como Usar o Sistema de Automação de Shorts

Este guia explica como usar o sistema melhorado de criação de YouTube Shorts com menu simplificado.

## 📋 Índice

1. [Instalação](#instalação)
2. [Configuração](#configuração)
3. [Uso Básico](#uso-básico)
4. [Formatos Disponíveis](#formatos-disponíveis)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Solução de Problemas](#solução-de-problemas)

## 🚀 Instalação

### 1. Criar Ambiente Virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 3. Verificar Instalação
```bash
python3 production_script.py
```

## ⚙️ Configuração

### Estrutura de Pastas
```
automacao-midia/
├── config/
│   └── config.json
├── downloads/
├── shorts/
└── production_script.py
```

### Configuração Básica
O sistema cria automaticamente as pastas necessárias na primeira execução.

## 🎯 Uso Básico

### Comando Principal
```bash
python3 production_script.py <URL_YOUTUBE> [num_shorts] [formato]
```

### Parâmetros
- `<URL_YOUTUBE>`: URL do vídeo do YouTube (obrigatório)
- `[num_shorts]`: Número de shorts a criar (padrão: 7)
- `[formato]`: Formato do vídeo - "normal" ou "screen" (opcional)

## 📱 Formatos Disponíveis

### 1. Normal
- **Descrição**: Mantém o formato original do vídeo
- **Uso**: Para vídeos já otimizados ou conteúdo tradicional
- **Comando**: `python3 production_script.py URL 7 normal`

### 2. Screen
- **Descrição**: Layout otimizado com câmera no topo e tela embaixo
- **Proporções**: 45% superior (câmera) + 55% inferior (conteúdo)
- **Resolução**: 1080x1920 (perfeito para YouTube Shorts)
- **Uso**: Para gravações de tela com webcam, apresentações, tutoriais
- **Comando**: `python3 production_script.py URL 7 screen`

## 🔧 Exemplos Práticos

### Exemplo 1: Uso Interativo
```bash
python3 production_script.py https://youtu.be/dQw4w9WgXcQ
```
O sistema perguntará:
```
📱 ESCOLHA O FORMATO DOS SHORTS:
   1. Normal - Formato original do vídeo
   2. Screen - Câmera no topo, tela embaixo

👉 Escolha o formato (1 ou 2):
```

### Exemplo 2: Formato Normal
```bash
python3 production_script.py https://youtu.be/dQw4w9WgXcQ 5 normal
```

### Exemplo 3: Formato Screen
```bash
python3 production_script.py https://youtu.be/dQw4w9WgXcQ 10 screen
```

### Exemplo 4: Apenas 3 Shorts
```bash
python3 production_script.py https://youtu.be/dQw4w9WgXcQ 3
```

## 📊 Processo de Criação

### Etapas Automáticas
1. **Download**: Baixa o vídeo do YouTube
2. **Análise**: Identifica os melhores momentos
3. **Criação**: Gera os shorts no formato escolhido
4. **Salvamento**: Armazena na pasta `shorts/`

### Saída Esperada
```
🎉 PROCESSAMENTO CONCLUÍDO!
📊 RESULTADOS:
   • Vídeo processado: video.mp4
   • Shorts criados: 7
   • Localização: ./shorts/

📁 ARQUIVOS CRIADOS:
   1. short_1.mp4 (15.2MB)
   2. short_2.mp4 (14.8MB)
   ...
```

## 🛠️ Solução de Problemas

### Erro: "ModuleNotFoundError"
```bash
# Ative o ambiente virtual
source venv/bin/activate
pip install -r requirements.txt
```

### Erro: "Falha no download"
- Verifique se a URL está correta
- Teste com um vídeo público
- Verifique sua conexão com a internet

### Erro: "Falha na análise"
- Certifique-se de que o vídeo tem áudio
- Verifique se o vídeo não está muito curto (< 60s)

### Problemas de Qualidade
- Para vídeos com webcam, use o formato "screen"
- Para conteúdo tradicional, use o formato "normal"

## 🎮 Comandos Úteis

### Testar Funcionalidade
```bash
source venv/bin/activate
python3 test_split_screen.py
```

### Listar Shorts Criados
```bash
ls -la shorts/
```

### Verificar Tamanho dos Arquivos
```bash
du -h shorts/*
```

## 📈 Dicas de Uso

1. **Para Tutoriais**: Use formato "screen" para melhor visualização
2. **Para Podcasts**: Use formato "normal" 
3. **Para Apresentações**: Use formato "screen" com 5-10 shorts
4. **Para Conteúdo Longo**: Comece com 3-5 shorts para testar

## 🔄 Próximos Passos

Após criar os shorts, você pode:
1. Revisar os arquivos na pasta `shorts/`
2. Fazer upload manual para o YouTube
3. Usar o sistema de upload automático (se configurado)

## 📞 Suporte

Para problemas ou dúvidas, verifique:
- Logs do sistema
- Arquivos de configuração
- Dependências instaladas