#!/usr/bin/env python3
"""
Sistema Principal de Automação YouTube Shorts
Versão final otimizada e funcional
"""

import os
import sys
import logging
from datetime import datetime
from simple_processor import SimpleProcessor

# Configurar logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def show_menu():
    """Mostra menu principal"""
    print("\n" + "="*60)
    print("🎬 YOUTUBE SHORTS AUTOMATION - LEONARDO ZARELLI")
    print("="*60)
    print("📋 MENU PRINCIPAL:")
    print("1. 🚀 Processar vídeo do YouTube (criar shorts)")
    print("2. 📁 Listar shorts criados")
    print("3. 📊 Status do sistema")
    print("4. 🧪 Executar testes")
    print("5. 🧹 Limpar arquivos temporários")
    print("6. ❌ Sair")
    print("="*60)

def process_youtube_video():
    """Processa vídeo do YouTube"""
    print("\n🎬 PROCESSAMENTO DE VÍDEO")
    print("-" * 40)
    
    url = input("Digite a URL do YouTube: ").strip()
    
    if not url:
        print("❌ URL inválida!")
        return
    
    if not ("youtube.com" in url or "youtu.be" in url):
        print("❌ URL deve ser do YouTube!")
        return
    
    try:
        processor = SimpleProcessor()
        
        print(f"\n🔄 Processando: {url}")
        print("⏳ Aguarde... (pode levar alguns minutos)")
        
        result = processor.process_video_complete(url)
        
        if result["success"]:
            print("\n🎉 SUCESSO!")
            print(f"✅ Shorts criados: {result['shorts_created']}")
            print(f"⏱️  Tempo total: {result['processing_time']}")
            print(f"📁 Arquivos salvos em: ./shorts/")
            
            # Mostrar arquivos criados
            if result["created_files"]:
                print("\n📋 Arquivos criados:")
                for file in result["created_files"]:
                    size_mb = os.path.getsize(file) / (1024*1024)
                    print(f"  • {os.path.basename(file)} ({size_mb:.1f}MB)")
        else:
            print(f"\n❌ ERRO: {result.get('error', 'Falha no processamento')}")
            
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        logger.error(f"Erro no processamento: {e}")

def list_shorts():
    """Lista shorts criados"""
    print("\n📁 SHORTS CRIADOS")
    print("-" * 40)
    
    shorts_dir = "./shorts"
    
    if not os.path.exists(shorts_dir):
        print("❌ Diretório de shorts não existe")
        return
    
    files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    
    if not files:
        print("📁 Nenhum short encontrado")
        print("💡 Use a opção 1 para criar shorts")
        return
    
    print(f"📋 Encontrados {len(files)} shorts:")
    
    total_size = 0
    for i, file in enumerate(files, 1):
        file_path = os.path.join(shorts_dir, file)
        size_mb = os.path.getsize(file_path) / (1024*1024)
        total_size += size_mb
        
        # Data de criação
        creation_time = os.path.getctime(file_path)
        creation_date = datetime.fromtimestamp(creation_time).strftime("%d/%m %H:%M")
        
        print(f"  {i:2d}. {file}")
        print(f"      📊 {size_mb:.1f}MB • 📅 {creation_date}")
    
    print(f"\n📊 Total: {len(files)} arquivos • {total_size:.1f}MB")

def show_system_status():
    """Mostra status do sistema"""
    print("\n📊 STATUS DO SISTEMA")
    print("-" * 40)
    
    # Verificar dependências
    deps = [
        ("MoviePy", "moviepy.editor"),
        ("OpenCV", "cv2"),
        ("YouTube Downloader", "yt_dlp"),
        ("Google API", "googleapiclient.discovery"),
        ("Audio Processing", "pydub")
    ]
    
    print("🔧 Dependências:")
    for name, module in deps:
        try:
            __import__(module)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name}")
    
    # Verificar diretórios
    dirs = ["./downloads", "./shorts", "./logs", "./temp", "./config"]
    print("\n📁 Diretórios:")
    for dir_path in dirs:
        if os.path.exists(dir_path):
            files = len([f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))])
            print(f"  ✅ {dir_path} ({files} arquivos)")
        else:
            print(f"  ❌ {dir_path} (não existe)")
    
    # Verificar espaço em disco
    import shutil
    total, used, free = shutil.disk_usage(".")
    free_gb = free / (1024**3)
    print(f"\n💾 Espaço livre: {free_gb:.1f}GB")
    
    # Status dos arquivos
    downloads = len([f for f in os.listdir("./downloads") if f.endswith('.mp4')]) if os.path.exists("./downloads") else 0
    shorts = len([f for f in os.listdir("./shorts") if f.endswith('.mp4')]) if os.path.exists("./shorts") else 0
    
    print(f"\n📈 Estatísticas:")
    print(f"  📥 Vídeos baixados: {downloads}")
    print(f"  ✂️  Shorts criados: {shorts}")

def run_tests():
    """Executa testes do sistema"""
    print("\n🧪 EXECUTANDO TESTES")
    print("-" * 40)
    
    try:
        from test_simple import main as run_simple_tests
        
        print("🔍 Executando testes básicos...")
        success = run_simple_tests()
        
        if success:
            print("\n✅ Todos os testes passaram!")
        else:
            print("\n❌ Alguns testes falharam!")
            
    except Exception as e:
        print(f"\n❌ Erro nos testes: {e}")

def cleanup_temp_files():
    """Limpa arquivos temporários"""
    print("\n🧹 LIMPEZA DE ARQUIVOS TEMPORÁRIOS")
    print("-" * 40)
    
    temp_dirs = ["./temp", "./logs"]
    removed_count = 0
    
    for temp_dir in temp_dirs:
        if os.path.exists(temp_dir):
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        removed_count += 1
                        print(f"  🗑️  Removido: {file}")
                except Exception as e:
                    print(f"  ❌ Erro ao remover {file}: {e}")
    
    # Limpar cache do Python
    import subprocess
    try:
        subprocess.run(["find", ".", "-name", "__pycache__", "-type", "d", "-exec", "rm", "-rf", "{}", "+"], 
                      check=False, capture_output=True)
        print("  🗑️  Cache Python limpo")
    except:
        pass
    
    print(f"\n✅ Limpeza concluída: {removed_count} arquivos removidos")

def main():
    """Função principal"""
    # Criar diretórios necessários
    os.makedirs("logs", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    os.makedirs("shorts", exist_ok=True)
    os.makedirs("temp", exist_ok=True)
    
    logger.info("Sistema de automação iniciado")
    
    while True:
        try:
            show_menu()
            choice = input("\n👉 Escolha uma opção (1-6): ").strip()
            
            if choice == "1":
                process_youtube_video()
                
            elif choice == "2":
                list_shorts()
                
            elif choice == "3":
                show_system_status()
                
            elif choice == "4":
                run_tests()
                
            elif choice == "5":
                cleanup_temp_files()
                
            elif choice == "6":
                print("\n👋 Encerrando sistema...")
                logger.info("Sistema encerrado pelo usuário")
                break
                
            else:
                print("\n❌ Opção inválida! Use números de 1 a 6.")
                
            input("\n⏸️  Pressione Enter para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n🛑 Sistema interrompido (Ctrl+C)")
            logger.info("Sistema interrompido pelo usuário")
            break
            
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            logger.error(f"Erro inesperado: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)