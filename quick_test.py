#!/usr/bin/env python3
"""
Teste rápido da automação - apenas análise e shorts
"""

import os
from video_processor import VideoProcessor
from short_creator import ShortCreator

def quick_test():
    """Teste rápido com vídeo já baixado"""
    
    # Verificar se o vídeo foi baixado
    downloads_dir = "./downloads"
    video_files = [f for f in os.listdir(downloads_dir) if f.endswith('.mp4')]
    
    if not video_files:
        print("❌ Nenhum vídeo encontrado na pasta downloads")
        return
    
    video_path = os.path.join(downloads_dir, video_files[0])
    print(f"📁 Usando vídeo: {video_files[0]}")
    
    try:
        # Processar vídeo
        processor = VideoProcessor()
        print("🔄 Carregando vídeo...")
        result = processor.load_video(video_path)
        
        if result and result['validation']['is_valid']:
            print(f"✅ Vídeo carregado: {result['duration']:.1f}s")
            
            # Criar shorts usando método simples
            print("🎬 Criando shorts...")
            creator = ShortCreator()
            
            # Criar 3 shorts de 60s cada
            shorts = creator.create_shorts_simple(
                video_path=video_path,
                num_shorts=3,
                duration=60,
                output_dir="./shorts"
            )
            
            if shorts:
                print(f"✅ {len(shorts)} shorts criados com sucesso!")
                for short in shorts:
                    print(f"   📁 {short['filename']}")
            else:
                print("❌ Falha na criação dos shorts")
                
        else:
            print("❌ Vídeo inválido ou não processado")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    quick_test()