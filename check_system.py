#!/usr/bin/env python3
"""
🔧 VERIFICADOR DO SISTEMA
Checklist automático para garantir que tudo está funcionando
"""

import os
import sys
import subprocess
from pathlib import Path

def check_system():
    """Verifica se o sistema está pronto para produção"""
    
    print("🔧 VERIFICAÇÃO DO SISTEMA DE PRODUÇÃO")
    print("=" * 60)
    
    checks = []
    
    # 1. Verificar diretório
    current_dir = os.getcwd()
    expected_dir = "automacao-midia"
    
    if expected_dir in current_dir:
        checks.append(("📁 Diretório correto", True, current_dir))
    else:
        checks.append(("📁 Diretório correto", False, f"Execute: cd .../automacao-midia"))
    
    # 2. Verificar ambiente virtual
    venv_path = "./venv"
    if os.path.exists(venv_path):
        checks.append(("🐍 Ambiente virtual", True, "venv/ encontrado"))
    else:
        checks.append(("🐍 Ambiente virtual", False, "Execute: python3 -m venv venv"))
    
    # 3. Verificar MoviePy
    try:
        import moviepy
        checks.append(("🎬 MoviePy", True, f"v{moviepy.__version__}"))
    except ImportError:
        checks.append(("🎬 MoviePy", False, "Execute: pip install moviepy"))
    
    # 4. Verificar YouTube uploader
    youtube_uploader_exists = os.path.exists("youtube_uploader.py")
    if youtube_uploader_exists:
        checks.append(("📺 YouTube Uploader", True, "youtube_uploader.py"))
    else:
        checks.append(("📺 YouTube Uploader", False, "Arquivo não encontrado"))
    
    # 5. Verificar scripts principais
    scripts = [
        ("production_script.py", "Script de produção"),
        ("upload_shorts.py", "Upload inteligente"),
        ("validate_and_convert.py", "Validador"),
        ("youtube_shorts_validator.py", "Conversor")
    ]
    
    for script, description in scripts:
        if os.path.exists(script):
            checks.append((f"📜 {description}", True, script))
        else:
            checks.append((f"📜 {description}", False, f"{script} não encontrado"))
    
    # 6. Verificar pastas necessárias
    folders = ["downloads", "shorts", "config"]
    for folder in folders:
        if os.path.exists(folder):
            checks.append((f"📂 Pasta {folder}", True, "Existe"))
        else:
            checks.append((f"📂 Pasta {folder}", False, f"Será criada automaticamente"))
    
    # 7. Verificar espaço em disco
    try:
        statvfs = os.statvfs('.')
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        free_gb = free_bytes / (1024**3)
        
        if free_gb > 2:
            checks.append((f"💾 Espaço em disco", True, f"{free_gb:.1f} GB livres"))
        else:
            checks.append((f"💾 Espaço em disco", False, f"Apenas {free_gb:.1f} GB (mín: 2GB)"))
    except:
        checks.append((f"💾 Espaço em disco", None, "Não foi possível verificar"))
    
    # 8. Verificar dependências Python
    dependencies = [
        ("yt-dlp", "Download de vídeos"),
        ("google-api-python-client", "API YouTube"),
        ("numpy", "Processamento numérico")
    ]
    
    for dep, desc in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            checks.append((f"📦 {desc}", True, dep))
        except ImportError:
            checks.append((f"📦 {desc}", False, f"pip install {dep}"))
    
    # Imprimir resultados
    print("\n📊 RESULTADO DA VERIFICAÇÃO:")
    print("-" * 60)
    
    success_count = 0
    warning_count = 0
    error_count = 0
    
    for check_name, status, details in checks:
        if status is True:
            print(f"✅ {check_name:<30} {details}")
            success_count += 1
        elif status is False:
            print(f"❌ {check_name:<30} {details}")
            error_count += 1
        else:
            print(f"⚠️ {check_name:<30} {details}")
            warning_count += 1
    
    # Resumo
    total_checks = len(checks)
    
    print(f"\n📈 RESUMO:")
    print(f"   ✅ Sucessos: {success_count}/{total_checks}")
    print(f"   ❌ Erros: {error_count}/{total_checks}")
    print(f"   ⚠️ Avisos: {warning_count}/{total_checks}")
    
    # Veredito final
    print(f"\n🎯 VEREDITO FINAL:")
    
    if error_count == 0:
        print("🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("✅ Todos os componentes estão funcionando")
        print("\n🚀 PRÓXIMOS PASSOS:")
        print("   1. python3 production_script.py URL_VIDEO QUANTIDADE")
        print("   2. python3 upload_shorts.py")
        return True
    elif error_count <= 2:
        print("⚠️ SISTEMA PARCIALMENTE PRONTO")
        print("🔧 Corrija os erros listados acima")
        print("\n🛠️ COMANDOS DE CORREÇÃO:")
        if not os.path.exists("venv"):
            print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   pip install moviepy yt-dlp google-api-python-client numpy")
        return False
    else:
        print("❌ SISTEMA NÃO ESTÁ PRONTO")
        print("🚨 Muitos problemas encontrados")
        print("💡 Consulte o GUIA_PRODUCAO.md para setup completo")
        return False

def quick_fix():
    """Tenta corrigir problemas comuns automaticamente"""
    
    print("\n🔧 CORREÇÃO AUTOMÁTICA")
    print("-" * 30)
    
    # Criar pastas necessárias
    folders = ["downloads", "shorts", "config", "temp"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)
            print(f"📁 Criada pasta: {folder}")
    
    # Verificar se está no venv
    if 'VIRTUAL_ENV' not in os.environ:
        print("⚠️ Ambiente virtual não ativo")
        print("💡 Execute: source venv/bin/activate")
    else:
        print("✅ Ambiente virtual ativo")
    
    print("🔧 Correções aplicadas!")

def main():
    """Função principal"""
    
    system_ok = check_system()
    
    if not system_ok:
        print(f"\n🔧 Tentar correção automática? [s/N]: ", end="")
        response = input().lower()
        
        if response in ['s', 'sim', 'y', 'yes']:
            quick_fix()
            print(f"\n🔄 Execute novamente para verificar:")
            print(f"   python3 check_system.py")
        else:
            print("📖 Consulte GUIA_PRODUCAO.md para instruções detalhadas")
    
    return system_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Verificação cancelada")
        sys.exit(1)