# 🎬 YouTube Shorts Automation

Sistema automatizado para transformar vídeos longos em 7 shorts e agendar uploads diários.

**Canal:** Leonardo_Zarelli  
**URL:** https://www.youtube.com/@Leonardo_Zarelli

## 🎯 Objetivo

Automatizar a criação de 7 shorts (60s cada) a partir de vídeos longos do canal, com upload diário às 07:00 (horário de Brasília).

## 🚀 Funcionalidades

- ✅ Download automático de vídeos do YouTube
- ✅ Análise inteligente para identificar melhores momentos
- ✅ Criação automática de 7 shorts em 720p
- ✅ Agendamento de uploads diários
- ✅ Hashtags personalizadas: #IA #thedreamjob #crypto #automacao #claudecode
- ✅ Logs detalhados de todo o processo

## 📋 Pré-requisitos

- Python 3.8+
- FFmpeg
- Conta Google Cloud com YouTube Data API v3 ativada
- Credenciais OAuth 2.0 configuradas

## 🔧 Instalação

### 1. Clone e configure o projeto:
```bash
git clone <repository>
cd automacao-midia
chmod +x install.sh
./install.sh
```

### 2. Ative o ambiente virtual:
```bash
# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Configure suas credenciais:
- As credenciais OAuth já estão configuradas no arquivo `config/client_secrets.json`
- Primeira execução solicitará autorização OAuth

## 📁 Estrutura do Projeto

```
automacao-midia/
├── main.py                    # Arquivo principal
├── requirements.txt           # Dependências Python
├── install.sh                # Script de instalação
├── README.md                 # Documentação
├── config/
│   ├── config.json           # Configurações principais
│   └── client_secrets.json   # Credenciais OAuth
├── downloads/                # Vídeos baixados
├── shorts/                   # Shorts criados
├── logs/                     # Logs do sistema
└── temp/                     # Arquivos temporários
```

## ⚙️ Configuração

### config.json - Principais configurações:

```json
{
  "channel_info": {
    "name": "Leonardo_Zarelli",
    "url": "https://www.youtube.com/@Leonardo_Zarelli"
  },
  "shorts_config": {
    "duration": 60,
    "resolution": "720x1280",
    "count_per_video": 7
  },
  "upload_schedule": {
    "time": "07:00",
    "timezone": "America/Sao_Paulo"
  },
  "hashtags": [
    "#IA", "#thedreamjob", "#crypto", 
    "#automacao", "#claudecode", "#shorts", "#tech"
  ]
}
```

## 🎮 Como Usar

### 1. Processar um vídeo específico:
```python
from main import YouTubeAutomation

automation = YouTubeAutomation()
automation.process_video("https://www.youtube.com/watch?v=VIDEO_ID")
```

### 2. Executar agendador diário:
```bash
python3 main.py
```

### 3. Processar vídeo mais recente do canal:
```python
# Implementação futura - detectar vídeo mais recente automaticamente
```

## 📊 Processo de Automação

1. **Download**: Baixa vídeo original do YouTube
2. **Análise**: Identifica os melhores momentos usando:
   - Análise de áudio (picos, pausas)
   - Reconhecimento de fala
   - Detecção de movimento visual
3. **Criação**: Gera 7 shorts de 60s cada
4. **Agendamento**: Programa uploads diários às 07:00
5. **Upload**: Publica automaticamente com hashtags

## 🔐 Autenticação OAuth 2.0

### Credenciais já configuradas:
- **Client ID**: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- **Client Secret**: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
- **Redirect URI**: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

### Primeira execução:
1. Sistema abrirá navegador para autorização
2. Faça login com conta do canal Leonardo_Zarelli
3. Autorize acesso ao YouTube
4. Token será salvo automaticamente

## 📝 Logs

Logs são salvos em `logs/automation.log` com informações detalhadas:
- Timestamp de cada operação
- Status de downloads
- Progresso de criação de shorts
- Resultados de uploads
- Erros e debugging

## 🎯 Hashtags Padrão

Cada short será publicado com as hashtags:
- #IA
- #thedreamjob  
- #crypto
- #automacao
- #claudecode
- #shorts
- #tech

## 🔄 Agendamento

- **Horário**: 07:00 (UTC-3 - Brasília)
- **Frequência**: Diário
- **Processo**: 1 short por dia de cada lote de 7

## 🛠️ Dependências Principais

- **moviepy**: Processamento de vídeo
- **opencv-python**: Análise visual
- **yt-dlp**: Download YouTube
- **google-api-python-client**: YouTube API
- **speech_recognition**: Transcrição
- **pydub**: Processamento áudio

## 📞 Suporte

Para dúvidas ou problemas:
- Verifique logs em `logs/automation.log`
- Certifique-se que FFmpeg está instalado
- Confirme credenciais OAuth válidas
- Execute `./install.sh` novamente se necessário

## 📈 Roadmap

- [ ] Interface web para monitoramento
- [ ] Análise automática de performance
- [ ] Detecção automática de novos vídeos
- [ ] Múltiplos formatos de saída
- [ ] Integração com outras plataformas

---

**Desenvolvido para o canal Leonardo_Zarelli**  
Sistema de automação de conteúdo YouTube Shorts
