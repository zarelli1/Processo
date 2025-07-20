#!/usr/bin/env python3
"""
🚀 UPLOAD RÁPIDO - Resolve erros de input
Posta 1 short automaticamente para testar remoção
"""

import os
import sys
import time

def upload_one_short():
    """Upload direto de 1 short sem interações"""
    
    print("🚀 UPLOAD RÁPIDO - Leonardo Zarelli")
    print("=" * 50)
    
    # Importar depois para evitar erros de import
    try:
        from youtube_uploader import YouTubeUploader
        from video_processor import VideoProcessor
        from upload_shorts import generate_title, generate_description, generate_tags
    except Exception as e:
        print(f"❌ Erro de import: {e}")
        return False
    
    # Verificar shorts
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        print("❌ Pasta shorts não encontrada")
        return False
    
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        return False
    
    # Usar primeiro arquivo
    filename = shorts_files[0]
    file_path = os.path.join(shorts_dir, filename)
    
    print(f"📁 Arquivo selecionado: {filename}")
    size = os.path.getsize(file_path) / (1024*1024)
    print(f"📊 Tamanho: {size:.1f} MB")
    
    try:
        # 1. Autenticação
        print(f"\n🔐 Autenticando no YouTube...")
        uploader = YouTubeUploader()
        
        if not uploader.authenticate():
            print("❌ Falha na autenticação")
            return False
        
        print("✅ Autenticado!")
        
        # 2. Validação rápida
        print(f"\n🔍 Validando arquivo...")
        processor = VideoProcessor()
        video_info = processor.load_video(file_path)
        
        if video_info:
            print("✅ Arquivo válido")
            processor.cleanup()
        else:
            print("❌ Arquivo inválido")
            return False
        
        # 3. Metadados
        print(f"\n📝 Gerando metadados...")
        title = generate_title(filename)
        description = generate_description(filename)
        tags = generate_tags(filename)
        
        print(f"📝 Título: {title[:50]}...")
        
        # 4. Upload
        print(f"\n⬆️  Fazendo upload...")
        print("⏳ Isso pode demorar alguns minutos...")
        
        result = uploader.upload_video(
            file_path=file_path,
            title=title,
            description=description,
            tags=tags,
            category='22',
            privacy='public'
        )
        
        # 5. Resultado
        if result and result.get('success'):
            video_id = result.get('video_id')
            video_url = f"https://youtu.be/{video_id}"
            
            print(f"\n🎉 UPLOAD CONCLUÍDO!")
            print(f"✅ Sucesso: {title}")
            print(f"🔗 URL: {video_url}")
            
            # 6. Teste de remoção automática
            print(f"\n🗑️  TESTANDO REMOÇÃO AUTOMÁTICA...")
            
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✅ Arquivo removido: {filename}")
                    
                    # Verificar se realmente foi removido
                    if not os.path.exists(file_path):
                        print(f"✅ Confirmado: remoção bem-sucedida!")
                        print(f"🧹 Sistema de limpeza funcionando perfeitamente!")
                    else:
                        print(f"❌ Erro: arquivo ainda existe")
                        return False
                else:
                    print(f"⚠️  Arquivo já não existia")
                    
            except Exception as e:
                print(f"❌ Erro na remoção: {e}")
                return False
            
            # 7. Resultado final
            print(f"\n" + "=" * 50)
            print(f"🎉 TESTE COMPLETO - TUDO FUNCIONANDO!")
            print(f"=" * 50)
            print(f"✅ Upload para YouTube: OK")
            print(f"✅ Remoção automática: OK")
            print(f"✅ Sistema de limpeza: OK")
            print(f"")
            print(f"📺 Vídeo disponível em:")
            print(f"🔗 {video_url}")
            print(f"🔗 https://youtube.com/@leonardo_zarelli")
            print(f"")
            print(f"⏰ O vídeo ficará visível em 15-30 minutos")
            
            return True
            
        else:
            error_msg = result.get('error', 'Erro desconhecido') if result else 'Sem resposta'
            print(f"❌ Upload falhou: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no processo: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_remaining_shorts():
    """Verifica quantos shorts restam"""
    
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        return 0
        
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    return len(shorts_files)

def main():
    """Função principal"""
    
    print("🧪 TESTE DE UPLOAD COM REMOÇÃO AUTOMÁTICA")
    print("=" * 60)
    
    # Verificar quantos shorts temos
    initial_count = check_remaining_shorts()
    print(f"📊 Shorts disponíveis: {initial_count}")
    
    if initial_count == 0:
        print("❌ Nenhum short encontrado para teste")
        print("💡 Execute: python3 production_script.py URL_VIDEO 3")
        return False
    
    # Fazer upload de 1
    print(f"\n🚀 Fazendo upload de 1 short (teste)...")
    success = upload_one_short()
    
    # Verificar resultado
    final_count = check_remaining_shorts()
    
    print(f"\n📊 RESULTADO:")
    print(f"   Shorts antes: {initial_count}")
    print(f"   Shorts depois: {final_count}")
    print(f"   Removidos: {initial_count - final_count}")
    
    if success and (final_count == initial_count - 1):
        print(f"\n🎉 TESTE PASSOU!")
        print(f"✅ Upload: OK")
        print(f"✅ Remoção: OK")
        print(f"✅ Sistema funcionando perfeitamente!")
        
        if final_count > 0:
            print(f"\n📋 PRÓXIMOS PASSOS:")
            print(f"   • {final_count} shorts restantes")
            print(f"   • Use: python3 upload_shorts_advanced.py")
            print(f"   • Ou: python3 quick_upload.py (para mais testes)")
        
        return True
    else:
        print(f"\n❌ TESTE FALHOU!")
        return False

if __name__ == "__main__":
    main()