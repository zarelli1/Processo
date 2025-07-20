#!/usr/bin/env python3
"""
🚀 SCRIPT DE PRODUÇÃO - LEONARDO ZARELLI
Sistema automatizado para criação de shorts a partir de vídeos longos
"""

import sys
import os
from simple_processor import SimpleProcessor

def main():
    print("🎬 YOUTUBE SHORTS AUTOMATION - LEONARDO ZARELLI")
    print("=" * 60)
    
    # Verificar argumentos
    if len(sys.argv) < 2:
        print("❌ Uso: python3 production_script.py <URL_YOUTUBE> [num_shorts] [formato]")
        print("📋 Exemplos:")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID 7")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID 7 normal")
        print("   python3 production_script.py https://youtu.be/VIDEO_ID 7 screen")
        print("\n📱 Formatos disponíveis:")
        print("   • normal  - Formato original do vídeo")
        print("   • screen  - Câmera no topo, tela embaixo")
        sys.exit(1)
    
    url = sys.argv[1]
    num_shorts = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    format_arg = sys.argv[3] if len(sys.argv) > 3 else None
    
    try:
        # Determinar formato
        if format_arg:
            if format_arg.lower() in ['normal', 'n']:
                format_type = "normal"
                format_name = "Normal (formato original)"
            elif format_arg.lower() in ['shorts', 's', 'youtube_shorts']:
                format_type = "youtube_shorts"
                format_name = "YouTube Shorts (1080x1920, 9:16)"
            elif format_arg.lower() in ['screen', 'split', 'split_screen', 'splitscreen']:
                format_type = "split_screen"
                format_name = "Screen (câmera no topo, tela embaixo)"
            else:
                print(f"❌ Formato inválido: {format_arg}")
                print("💡 Use 'normal' ou 'screen'")
                sys.exit(1)
        else:
            # Menu interativo simplificado para escolher formato
            print("\n📱 ESCOLHA O FORMATO DOS SHORTS:")
            print("   1. Normal - Formato original do vídeo")
            print("   2. Screen - Câmera no topo, tela embaixo")
            
            while True:
                choice = input("\n👉 Escolha o formato (1 ou 2): ").strip()
                if choice == "1":
                    format_type = "normal"
                    format_name = "Normal (formato original)"
                    break
                elif choice == "2":
                    format_type = "split_screen"
                    format_name = "Screen (câmera no topo, tela embaixo)"
                    break
                else:
                    print("❌ Opção inválida. Digite 1 ou 2")
        
        print(f"🎯 URL: {url}")
        print(f"🎬 Criando {num_shorts} shorts")
        print(f"📱 Formato: {format_name}")
        print("=" * 60)
        
        # Inicializar processador com formato escolhido
        processor = SimpleProcessor(format_type=format_type)
        processor.config['shorts_config']['count_per_video'] = num_shorts
        
        # 1. Download
        print("\n📥 ETAPA 1: Download do vídeo...")
        video_path = processor.download_video(url)
        if not video_path:
            print("❌ Falha no download")
            sys.exit(1)
        
        print(f"✅ Download concluído: {os.path.basename(video_path)}")
        
        # 2. Análise
        print(f"\n🔍 ETAPA 2: Análise para {num_shorts} shorts...")
        segments = processor.analyze_video_simple(video_path)
        if not segments:
            print("❌ Falha na análise")
            sys.exit(1)
            
        print(f"✅ Análise concluída: {len(segments)} segmentos encontrados")
        
        # 3. Criação de shorts
        print(f"\n✂️ ETAPA 3: Criação de {num_shorts} shorts...")
        shorts = processor.create_shorts(video_path, segments[:num_shorts])
        
        # 4. Resultado
        print("\n" + "=" * 60)
        print("🎉 PROCESSAMENTO CONCLUÍDO!")
        print("=" * 60)
        print(f"📊 RESULTADOS:")
        print(f"   • Vídeo processado: {os.path.basename(video_path)}")
        print(f"   • Shorts criados: {len(shorts)}")
        print(f"   • Localização: ./shorts/")
        
        if shorts:
            print(f"\n📁 ARQUIVOS CRIADOS:")
            for i, short in enumerate(shorts, 1):
                if os.path.exists(short):
                    size_mb = os.path.getsize(short) / (1024*1024)
                    print(f"   {i}. {os.path.basename(short)} ({size_mb:.1f}MB)")
                else:
                    print(f"   {i}. ERRO: {short}")
        
        print(f"\n🚀 PRONTO PARA UPLOAD!")
        print(f"📋 Use os arquivos da pasta 'shorts/' para publicar no YouTube")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()