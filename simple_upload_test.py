#!/usr/bin/env python3
"""
Teste simples com API Key e credenciais manuais
"""

import os
import json
import pickle
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

def create_manual_credentials():
    """Criar credenciais manualmente para teste"""
    
    print("🔧 CONFIGURAÇÃO MANUAL DE CREDENCIAIS")
    print("=" * 50)
    
    # Carregar configurações
    with open('config/client_secrets.json', 'r') as f:
        secrets = json.load(f)['installed']
    
    with open('config/api_key.json', 'r') as f:
        api_config = json.load(f)
    
    print("📋 Configurações carregadas:")
    print(f"   • Project ID: {secrets['project_id']}")
    print(f"   • Client ID: {secrets['client_id'][:20]}...")
    print(f"   • API Key: {api_config['youtube_api_key'][:20]}...")
    
    # Vamos usar a API Key para operações simples primeiro
    print("\n🧪 TESTANDO API KEY...")
    
    try:
        # Criar serviço YouTube com API Key
        youtube = build('youtube', 'v3', developerKey=api_config['youtube_api_key'])
        
        # Testar uma chamada simples (não precisa OAuth)
        search_response = youtube.search().list(
            q='teste',
            part='snippet',
            maxResults=1,
            type='video'
        ).execute()
        
        print("✅ API Key funcionando!")
        print(f"   • Encontrados: {len(search_response['items'])} resultados")
        
        # Agora vamos tentar usar as credenciais OAuth para upload
        credentials_file = 'config/youtube_credentials.pickle'
        
        if os.path.exists(credentials_file):
            print("\n🔐 TESTANDO CREDENCIAIS OAUTH...")
            
            with open(credentials_file, 'rb') as token:
                credentials = pickle.load(token)
            
            if credentials and credentials.valid:
                print("✅ Credenciais OAuth válidas!")
                
                # Criar serviço autenticado
                youtube_auth = build('youtube', 'v3', credentials=credentials)
                
                # Testar acesso ao canal
                channels = youtube_auth.channels().list(part='snippet', mine=True).execute()
                
                if channels['items']:
                    channel_name = channels['items'][0]['snippet']['title']
                    print(f"🎬 Canal autenticado: {channel_name}")
                    print("🎉 SISTEMA COMPLETO FUNCIONANDO!")
                    return True
                else:
                    print("⚠️  Nenhum canal encontrado")
            else:
                print("❌ Credenciais OAuth inválidas")
        else:
            print("❌ Arquivo de credenciais não encontrado")
        
        print("\n💡 Para upload, você precisa:")
        print("1. Fazer OAuth uma vez")
        print("2. Sistema salva automaticamente")
        print("3. Uploads futuros são automáticos")
        
        return False
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_shorts_availability():
    """Verificar se há shorts prontos para upload"""
    
    print("\n📁 VERIFICANDO SHORTS DISPONÍVEIS...")
    
    shorts_dir = 'shorts'
    if os.path.exists(shorts_dir):
        files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
        print(f"✅ Encontrados {len(files)} shorts prontos:")
        for i, file in enumerate(files[:3], 1):
            size = os.path.getsize(os.path.join(shorts_dir, file)) / (1024*1024)
            print(f"   {i}. {file} ({size:.1f} MB)")
        
        if files:
            print("🚀 Prontos para upload automático!")
            return True
    else:
        print("❌ Pasta 'shorts' não encontrada")
        print("💡 Execute: python3 production_script.py URL 5")
    
    return False

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO COMPLETO DO SISTEMA")
    print("=" * 60)
    
    # Teste 1: API Key e configurações
    api_working = create_manual_credentials()
    
    # Teste 2: Shorts disponíveis
    shorts_ready = test_shorts_availability()
    
    print("\n" + "="*60)
    print("📊 RESULTADO FINAL:")
    print(f"   • API configurada: {'✅' if api_working else '❌'}")
    print(f"   • Shorts prontos: {'✅' if shorts_ready else '❌'}")
    
    if api_working and shorts_ready:
        print("\n🎉 SISTEMA 100% OPERACIONAL!")
        print("🚀 Execute: python3 production_script.py URL 5")
    else:
        print("\n🔧 Configuração adicional necessária")