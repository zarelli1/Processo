#!/usr/bin/env python3
"""
Script de configuração e teste de dependências
YouTube Shorts Automation - Leonardo_Zarelli
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Executa comando e trata erros"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - ERRO: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - EXCEÇÃO: {e}")
        return False

def test_import(module_name, package_name=None):
    """Testa importação de módulo"""
    try:
        __import__(module_name)
        print(f"✅ {package_name or module_name}")
        return True
    except ImportError as e:
        print(f"❌ {package_name or module_name}: {e}")
        return False

def main():
    print("🎬 YouTube Shorts Automation - Setup de Dependências")
    print("Canal: Leonardo_Zarelli")
    print("=" * 60)
    
    # 1. Atualizar pip
    run_command("pip install --upgrade pip setuptools wheel", "Atualizando ferramentas")
    
    # 2. Desinstalar MoviePy quebrado
    run_command("pip uninstall moviepy -y", "Removendo MoviePy antigo")
    
    # 3. Limpar cache
    run_command("pip cache purge", "Limpando cache")
    
    # 4. Instalar dependências uma por uma
    dependencies = [
        ("moviepy>=2.0.0", "MoviePy"),
        ("opencv-python", "OpenCV"),
        ("yt-dlp", "YouTube Downloader"),
        ("google-api-python-client", "Google API"),
        ("google-auth-oauthlib", "Google OAuth"),
        ("SpeechRecognition", "Speech Recognition"),
        ("pydub", "Audio Processing"),
        ("numpy", "NumPy"),
        ("schedule", "Scheduler"),
        ("psutil", "System Utils"),
        ("matplotlib", "Plotting"),
        ("Pillow", "Image Processing"),
        ("requests", "HTTP Client"),
        ("python-dotenv", "Environment Variables")
    ]
    
    print("\n📦 Instalando dependências...")
    for package, name in dependencies:
        run_command(f"pip install {package}", f"Instalando {name}")
    
    # 5. Testar importações
    print("\n🧪 Testando importações...")
    imports_test = [
        ("moviepy", "MoviePy"),
        ("cv2", "OpenCV"),
        ("yt_dlp", "YouTube DL"),
        ("googleapiclient.discovery", "Google API Client"),
        ("google_auth_oauthlib.flow", "Google OAuth"),
        ("speech_recognition", "Speech Recognition"),
        ("pydub", "PyDub"),
        ("numpy", "NumPy"),
        ("schedule", "Schedule"),
        ("psutil", "PSUtil"),
        ("matplotlib", "Matplotlib"),
        ("PIL", "Pillow"),
        ("requests", "Requests")
    ]
    
    failed_imports = []
    for module, name in imports_test:
        if not test_import(module, name):
            failed_imports.append(name)
    
    # 6. Teste específico do MoviePy
    print("\n🎬 Teste específico do MoviePy...")
    try:
        from moviepy import VideoFileClip
        print("✅ MoviePy VideoFileClip importado com sucesso")
    except Exception as e:
        print(f"❌ Erro no MoviePy: {e}")
        failed_imports.append("MoviePy VideoFileClip")
    
    # 7. Resultado final
    print("\n" + "=" * 60)
    if failed_imports:
        print(f"❌ FALHAS: {len(failed_imports)} dependências com problema:")
        for fail in failed_imports:
            print(f"   • {fail}")
        print("\n🔧 Execute novamente ou instale manualmente as que falharam")
        return False
    else:
        print("✅ SUCESSO: Todas as dependências instaladas e funcionando!")
        print("\n🚀 Próximo passo: python3 main.py --validate")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
