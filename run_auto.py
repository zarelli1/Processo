#!/usr/bin/env python3
"""
Script automatizado para testar o sistema sem entrada interativa
"""

import sys
from main import YouTubeAutomation

def run_automation():
    """Executa automação com vídeo de teste"""
    
    # URL de teste do Rick Roll (vídeo público conhecido)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        print("🚀 Iniciando automação YouTube...")
        
        # Inicializar sistema
        automation = YouTubeAutomation()
        print("✅ Sistema inicializado")
        
        # Processar vídeo de teste
        print(f"📹 Processando vídeo: {test_url}")
        result = automation.process_video(test_url)
        
        if result:
            print(f"✅ Vídeo processado: {result.title}")
            print(f"📊 Duração: {result.duration:.1f}s")
            print(f"📁 Arquivo: {result.local_path}")
        else:
            print("❌ Falha no processamento")
            
        return result is not None
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False
    finally:
        if 'automation' in locals():
            automation.cleanup()

if __name__ == "__main__":
    success = run_automation()
    sys.exit(0 if success else 1)