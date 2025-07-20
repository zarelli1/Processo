#!/usr/bin/env python3
"""
Debug das configurações OAuth
"""

import json
import os

def debug_oauth():
    """Debug completo da configuração OAuth"""
    
    print("🔍 DEBUG CONFIGURAÇÃO OAUTH")
    print("=" * 50)
    
    # Verificar arquivo de credenciais
    client_file = 'config/client_secrets.json'
    if not os.path.exists(client_file):
        print(f"❌ Arquivo não encontrado: {client_file}")
        return
    
    # Carregar e mostrar configurações
    with open(client_file, 'r') as f:
        config = json.load(f)
    
    print("📋 CONFIGURAÇÕES ATUAIS:")
    if 'installed' in config:
        installed = config['installed']
        print(f"Client ID: {installed.get('client_id', 'NÃO ENCONTRADO')}")
        print(f"Project ID: {installed.get('project_id', 'NÃO ENCONTRADO')}")
        print(f"Client Secret: {installed.get('client_secret', 'NÃO ENCONTRADO')[:10]}...")
        print(f"Redirect URIs: {installed.get('redirect_uris', 'NÃO ENCONTRADO')}")
        
        # Gerar URL de teste manual
        client_id = installed.get('client_id')
        if client_id:
            test_url = f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={client_id}&redirect_uri=http://localhost:8080&scope=https://www.googleapis.com/auth/youtube.upload&access_type=offline&prompt=consent"
            
            print("\n🧪 URL DE TESTE MANUAL:")
            print(test_url)
            print("\n📋 TESTE ESTA URL NO NAVEGADOR")
            
    else:
        print("❌ Estrutura 'installed' não encontrada no arquivo")
        print("📄 Conteúdo do arquivo:")
        print(json.dumps(config, indent=2))

if __name__ == "__main__":
    debug_oauth()