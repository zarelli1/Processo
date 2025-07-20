#!/usr/bin/env python3
"""
Autenticação manual OAuth para WSL/ambientes sem navegador
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def manual_auth():
    """Autenticação manual via código"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    CLIENT_SECRETS_FILE = 'config/client_secrets.json'
    CREDENTIALS_FILE = 'config/youtube_credentials.pickle'
    
    print("🔐 AUTENTICAÇÃO MANUAL PARA YOUTUBE")
    print("=" * 50)
    
    # Verificar credenciais existentes
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)
            if credentials and credentials.valid:
                print("✅ Já autenticado! Credenciais válidas encontradas.")
                return True
    
    # Nova autenticação
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    
    # Obter URL de autorização
    auth_url, _ = flow.authorization_url(prompt='consent')
    
    print("\n📋 INSTRUÇÕES:")
    print("1. Copie esta URL e cole no seu navegador:")
    print(f"\n{auth_url}\n")
    print("2. Faça login na sua conta Google")
    print("3. Autorize a aplicação")
    print("4. Copie o código que aparece na página")
    print("5. Cole o código aqui:")
    
    # Aguardar código do usuário
    auth_code = input("\n🔑 Cole o código aqui: ").strip()
    
    if not auth_code:
        print("❌ Código não fornecido")
        return False
    
    try:
        # Trocar código por token
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Salvar credenciais
        os.makedirs('config', exist_ok=True)
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        print("✅ Autenticação concluída com sucesso!")
        print(f"📁 Credenciais salvas em: {CREDENTIALS_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        return False

if __name__ == "__main__":
    success = manual_auth()
    if success:
        print("\n🎉 SISTEMA PRONTO!")
        print("🚀 Agora você pode fazer upload automático:")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID 5")
    else:
        print("❌ Falha na autenticação")