#!/usr/bin/env python3
"""
Autenticação final usando requests direto
"""

import os
import json
import pickle
import requests
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def final_auth_manual():
    """Autenticação manual com requests"""
    
    CLIENT_SECRETS_FILE = 'config/client_secrets.json'
    CREDENTIALS_FILE = 'config/youtube_credentials.pickle'
    
    # Carregar configurações
    with open(CLIENT_SECRETS_FILE, 'r') as f:
        config = json.load(f)['installed']
    
    # Código recebido
    auth_code = "4/0AVMBsJhYpriX-RZvXkXjQ8fMK1P2WWW3VPlyoRszDkMtefydf8_MKtzbKB4cmnFww9-9qQ"
    
    print("🔐 AUTENTICAÇÃO FINAL - MÉTODO DIRETO")
    print("=" * 50)
    
    # Parâmetros para trocar código por token
    token_data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': 'http://localhost:8080'
    }
    
    try:
        print("🔄 Trocando código por token...")
        
        # Fazer requisição para trocar código
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data
        )
        
        if response.status_code == 200:
            token_info = response.json()
            print("✅ Token recebido com sucesso!")
            
            # Criar objeto de credenciais
            credentials = Credentials(
                token=token_info['access_token'],
                refresh_token=token_info.get('refresh_token'),
                token_uri=config['token_uri'],
                client_id=config['client_id'],
                client_secret=config['client_secret'],
                scopes=['https://www.googleapis.com/auth/youtube.upload']
            )
            
            # Salvar credenciais
            print("💾 Salvando credenciais...")
            os.makedirs('config', exist_ok=True)
            with open(CREDENTIALS_FILE, 'wb') as token:
                pickle.dump(credentials, token)
            
            # Testar conexão
            print("🧪 Testando conexão com YouTube...")
            youtube = build('youtube', 'v3', credentials=credentials)
            
            channels_response = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if channels_response['items']:
                channel = channels_response['items'][0]
                channel_name = channel['snippet']['title']
                subscriber_count = channel['statistics'].get('subscriberCount', 'N/A')
                
                print(f"🎬 Canal: {channel_name}")
                print(f"👥 Inscritos: {subscriber_count}")
                
                print("\n" + "="*50)
                print("🎉 SISTEMA 100% PRONTO!")
                print("🚀 Upload automático configurado!")
                print("="*50)
                
                return True
            else:
                print("⚠️  Canal não encontrado")
                return True
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = final_auth_manual()
    
    if success:
        print("\n🎯 AGORA VOCÊ PODE:")
        print("python3 production_script.py https://youtu.be/VIDEO_ID 5")
        print("• Download automático")
        print("• Criação de shorts")
        print("• Upload automático no YouTube!")
    else:
        print("❌ Autenticação falhou")