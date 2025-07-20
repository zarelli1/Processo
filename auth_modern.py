#!/usr/bin/env python3
"""
Autenticação OAuth Moderna para YouTube API
Usa apenas http://localhost:8080 (padrão atual do Google)
"""

import os
import pickle
import webbrowser
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def modern_auth():
    """Autenticação OAuth moderna com localhost:8080"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    CLIENT_SECRETS_FILE = 'config/client_secrets.json'
    CREDENTIALS_FILE = 'config/youtube_credentials.pickle'
    
    print("🔐 AUTENTICAÇÃO YOUTUBE - PADRÃO MODERNO")
    print("=" * 50)
    
    credentials = None
    
    # Verificar credenciais existentes
    if os.path.exists(CREDENTIALS_FILE):
        print("🔍 Verificando credenciais existentes...")
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)
    
    # Se não existe ou expirou, fazer nova autenticação
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("🔄 Renovando token expirado...")
            try:
                credentials.refresh(Request())
            except Exception as e:
                print(f"⚠️  Erro ao renovar token: {e}")
                credentials = None
        
        if not credentials:
            print("🆕 Iniciando nova autenticação...")
            print("📌 O navegador será aberto automaticamente")
            print("📌 Se não abrir, copie a URL que aparecerá")
            
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"❌ Arquivo não encontrado: {CLIENT_SECRETS_FILE}")
                return False
            
            try:
                # Configurar fluxo OAuth com localhost
                flow = InstalledAppFlow.from_client_secrets_file(
                    CLIENT_SECRETS_FILE, 
                    SCOPES
                )
                
                # Executar servidor local na porta 8080
                print("🌐 Iniciando servidor local na porta 8080...")
                credentials = flow.run_local_server(
                    port=8080,
                    prompt='consent',
                    authorization_prompt_message='🔐 Autorize a aplicação no navegador que abriu...',
                    success_message='✅ Autorização concluída! Você pode fechar esta aba.',
                    open_browser=True
                )
                
            except Exception as e:
                print(f"❌ Erro na autenticação: {e}")
                print("💡 Certifique-se que a porta 8080 está disponível")
                return False
        
        # Salvar as credenciais
        print("💾 Salvando credenciais...")
        os.makedirs('config', exist_ok=True)
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)
    
    print("✅ Autenticação OAuth concluída com sucesso!")
    print(f"📁 Credenciais salvas em: {CREDENTIALS_FILE}")
    
    # Testar se as credenciais funcionam
    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Fazer uma chamada simples para testar
        channels = youtube.channels().list(part='snippet', mine=True).execute()
        channel_name = channels['items'][0]['snippet']['title']
        
        print(f"🎬 Canal autenticado: {channel_name}")
        print("🎉 Sistema pronto para upload automático!")
        
    except Exception as e:
        print(f"⚠️  Aviso: Não foi possível testar a conexão: {e}")
        print("✅ Mas as credenciais foram salvas com sucesso!")
    
    return True

if __name__ == "__main__":
    print("🚀 AUTENTICAÇÃO YOUTUBE API - VERSÃO 2024")
    print("📋 Requisitos:")
    print("   • Google Console configurado com http://localhost:8080")
    print("   • Porta 8080 disponível")
    print("   • Navegador padrão funcionando")
    print()
    
    success = modern_auth()
    
    if success:
        print("\n" + "="*50)
        print("🎉 SISTEMA TOTALMENTE CONFIGURADO!")
        print("🚀 Próximo passo:")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID 5")
        print("="*50)
    else:
        print("\n❌ Falha na autenticação")
        print("💡 Verifique se configurou http://localhost:8080 no Google Console")