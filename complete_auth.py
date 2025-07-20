#!/usr/bin/env python3
"""
Completar autenticação OAuth com código recebido
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

def complete_auth_with_code():
    """Finalizar autenticação com código do usuário"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CLIENT_SECRETS_FILE = 'config/client_secrets.json'
    CREDENTIALS_FILE = 'config/youtube_credentials.pickle'
    
    # Código de autorização recebido
    auth_code = "4/0AVMBsJhYpriX-RZvXkXjQ8fMK1P2WWW3VPlyoRszDkMtefydf8_MKtzbKB4cmnFww9-9qQ"
    
    print("🔐 FINALIZANDO AUTENTICAÇÃO OAUTH")
    print("=" * 50)
    print(f"📥 Código recebido: {auth_code[:20]}...")
    
    try:
        # Configurar fluxo OAuth
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, 
            SCOPES
        )
        
        # Trocar código por credenciais
        print("🔄 Trocando código por token de acesso...")
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Salvar credenciais
        print("💾 Salvando credenciais...")
        os.makedirs('config', exist_ok=True)
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        print("✅ Credenciais salvas com sucesso!")
        
        # Testar a conexão
        print("🧪 Testando conexão com YouTube API...")
        youtube = build('youtube', 'v3', credentials=credentials)
        
        # Obter informações do canal
        channels_response = youtube.channels().list(
            part='snippet,statistics',
            mine=True
        ).execute()
        
        if channels_response['items']:
            channel = channels_response['items'][0]
            channel_name = channel['snippet']['title']
            subscriber_count = channel['statistics'].get('subscriberCount', 'N/A')
            
            print(f"🎬 Canal autenticado: {channel_name}")
            print(f"👥 Inscritos: {subscriber_count}")
            print("✅ Conexão com YouTube API funcionando!")
        else:
            print("⚠️  Nenhum canal encontrado para esta conta")
        
        print("\n" + "="*50)
        print("🎉 AUTENTICAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🚀 Sistema pronto para upload automático!")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao finalizar autenticação: {e}")
        return False

if __name__ == "__main__":
    success = complete_auth_with_code()
    
    if success:
        print("\n🎯 PRÓXIMOS PASSOS:")
        print("1. Processar um vídeo:")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID 5")
        print("2. Sistema fará automaticamente:")
        print("   • Download do vídeo")
        print("   • Criação de 5 shorts")
        print("   • Upload automático no YouTube")
    else:
        print("❌ Falha na autenticação final")