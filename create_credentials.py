#!/usr/bin/env python3
"""
Criar credenciais OAuth automaticamente
"""

import os
import json
import pickle
import requests
from google.oauth2.credentials import Credentials

def create_oauth_credentials():
    """Criar credenciais OAuth usando método simplificado"""
    
    print("🔐 CRIANDO CREDENCIAIS OAUTH")
    print("=" * 50)
    
    # Carregar configurações
    with open('config/client_secrets.json', 'r') as f:
        secrets = json.load(f)['installed']
    
    print("📋 Usando configurações do projeto:")
    print(f"   • Project: {secrets['project_id']}")
    print(f"   • Client ID: ...{secrets['client_id'][-10:]}")
    
    # URL de autorização simples
    auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"response_type=code&"
        f"client_id={secrets['client_id']}&"
        f"redirect_uri=http://localhost:8080&"
        f"scope=https://www.googleapis.com/auth/youtube&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    print("\n🌐 URL DE AUTORIZAÇÃO:")
    print(auth_url)
    print("\n📋 INSTRUÇÕES:")
    print("1. Copie a URL acima")
    print("2. Cole no navegador")
    print("3. Autorize a aplicação")
    print("4. Copie APENAS o código da URL de retorno")
    print("   Exemplo: http://localhost:8080/?code=ESTE_CÓDIGO")
    
    # Aguardar código do usuário
    print("\n" + "="*50)
    auth_code = input("🔑 Cole APENAS o código aqui: ").strip()
    
    if not auth_code:
        print("❌ Código não fornecido")
        return False
    
    # Trocar código por token
    print(f"\n🔄 Processando código: {auth_code[:20]}...")
    
    token_data = {
        'client_id': secrets['client_id'],
        'client_secret': secrets['client_secret'],
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8080'
    }
    
    try:
        response = requests.post('https://oauth2.googleapis.com/token', data=token_data)
        
        if response.status_code == 200:
            token_info = response.json()
            print("✅ Token recebido com sucesso!")
            
            # Criar credenciais
            credentials = Credentials(
                token=token_info['access_token'],
                refresh_token=token_info.get('refresh_token'),
                token_uri=secrets['token_uri'],
                client_id=secrets['client_id'],
                client_secret=secrets['client_secret'],
                scopes=['https://www.googleapis.com/auth/youtube']
            )
            
            # Salvar credenciais
            credentials_file = 'config/youtube_credentials.pickle'
            os.makedirs('config', exist_ok=True)
            
            with open(credentials_file, 'wb') as token:
                pickle.dump(credentials, token)
            
            print(f"💾 Credenciais salvas: {credentials_file}")
            
            # Testar conexão
            from googleapiclient.discovery import build
            
            youtube = build('youtube', 'v3', credentials=credentials)
            channels = youtube.channels().list(part='snippet', mine=True).execute()
            
            if channels['items']:
                channel_name = channels['items'][0]['snippet']['title']
                print(f"🎬 Canal autenticado: {channel_name}")
                
                print("\n" + "="*50)
                print("🎉 SISTEMA 100% OPERACIONAL!")
                print("🚀 Upload automático configurado!")
                print("="*50)
                
                return True
            else:
                print("⚠️  Canal não encontrado")
                return False
        
        else:
            print(f"❌ Erro na troca de token: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = create_oauth_credentials()
    
    if success:
        print("\n🎯 AGORA VOCÊ PODE FAZER UPLOAD AUTOMÁTICO:")
        print("python3 production_script.py https://youtu.be/VIDEO_ID 5")
        print("\n📋 OU FAZER UPLOAD DOS 5 SHORTS EXISTENTES:")
        print("python3 upload_existing_shorts.py")
    else:
        print("❌ Falha na criação das credenciais")