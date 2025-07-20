#!/usr/bin/env python3
"""
Autenticação OAuth mais simples para YouTube
"""

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

def simple_auth():
    """Autenticação simples com redirect_uri correto"""
    
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    CLIENT_SECRETS_FILE = 'config/client_secrets.json'
    CREDENTIALS_FILE = 'config/youtube_credentials.pickle'
    
    print("🔐 AUTENTICAÇÃO YOUTUBE - VERSÃO SIMPLES")
    print("=" * 50)
    
    # Verificar credenciais existentes
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'rb') as token:
            credentials = pickle.load(token)
            if credentials and credentials.valid:
                print("✅ Já autenticado! Credenciais válidas.")
                return True
    
    try:
        # Configurar fluxo OAuth
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, 
            SCOPES,
            redirect_uri='urn:ietf:wg:oauth:2.0:oob'
        )
        
        # Obter URL de autorização
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        
        print("📋 INSTRUÇÕES:")
        print("1. Copie e cole esta URL no navegador:")
        print(f"\n{auth_url}\n")
        print("2. Faça login e autorize a aplicação")
        print("3. Copie o código de autorização")
        print("4. Cole o código aqui:")
        
        # Solicitar código
        auth_code = input("\n🔑 Cole o código: ").strip()
        
        if not auth_code:
            print("❌ Código não fornecido")
            return False
        
        # Trocar código por token
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        
        # Salvar credenciais
        os.makedirs('config', exist_ok=True)
        with open(CREDENTIALS_FILE, 'wb') as token:
            pickle.dump(credentials, token)
        
        print("✅ Autenticação concluída!")
        print(f"📁 Credenciais salvas: {CREDENTIALS_FILE}")
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = simple_auth()
    if success:
        print("\n🎉 PRONTO PARA UPLOAD AUTOMÁTICO!")
        print("🚀 Comando: python3 production_script.py URL 5")
    else:
        print("❌ Falha na autenticação")