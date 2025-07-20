#!/usr/bin/env python3
"""
Script simples para autenticação OAuth do YouTube
"""

import os
import sys
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def authenticate_youtube():
    """Autentica com OAuth 2.0 do YouTube"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    CLIENT_SECRETS_FILE = 'config/client_secrets.json'
    CREDENTIALS_FILE = 'config/youtube_credentials.pickle'
    
    credentials = None
    
    # Verificar se já existe token salvo
    if os.path.exists(CREDENTIALS_FILE):
        print("🔍 Carregando credenciais existentes...")
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)
    
    # Se não existir ou expirou, fazer nova autenticação
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("🔄 Renovando token expirado...")
            credentials.refresh(Request())
        else:
            print("🔐 Iniciando nova autenticação OAuth...")
            print("📌 Seu navegador será aberto para autorização")
            
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"❌ Arquivo não encontrado: {CLIENT_SECRETS_FILE}")
                return False
                
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            credentials = flow.run_local_server(port=8080)
        
        # Salvar as credenciais
        print("💾 Salvando credenciais...")
        os.makedirs('config', exist_ok=True)
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)
    
    print("✅ Autenticação OAuth concluída com sucesso!")
    print(f"📁 Credenciais salvas em: {CREDENTIALS_FILE}")
    return True

if __name__ == "__main__":
    success = authenticate_youtube()
    if success:
        print("\n🎉 Pronto! Agora você pode fazer upload automático no YouTube")
        print("💡 Use: python3 production_script.py URL 5")
    else:
        print("\n❌ Erro na autenticação")
        sys.exit(1)