#!/usr/bin/env python3
"""
🧪 TESTE DE UPLOAD - Sistema não-interativo
"""

import os
import sys
from youtube_uploader import YouTubeUploader
from video_processor import VideoProcessor

def test_upload_one_short():
    """Testa upload de apenas 1 short"""
    
    print("🧪 TESTE DE UPLOAD - Leonardo Zarelli")
    print("=" * 50)
    
    # Verificar pasta de shorts
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        print("❌ Pasta 'shorts' não encontrada")
        return False
    
    # Listar arquivos disponíveis
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    shorts_files.sort()
    
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        return False
    
    print(f"📁 SHORTS DISPONÍVEIS ({len(shorts_files)}):")
    for i, file in enumerate(shorts_files, 1):
        size = os.path.getsize(os.path.join(shorts_dir, file)) / (1024*1024)
        print(f"   {i:2d}. {file} ({size:.1f} MB)")
    
    # Selecionar primeiro arquivo para teste
    test_file = shorts_files[0]
    file_path = os.path.join(shorts_dir, test_file)
    
    print(f"\n🧪 TESTANDO COM: {test_file}")
    print("=" * 50)
    
    try:
        # Inicializar uploader
        print("🔐 Inicializando autenticação YouTube...")
        uploader = YouTubeUploader()
        
        if not uploader.authenticate():
            print("❌ Falha na autenticação do YouTube")
            return False
        
        print("✅ Autenticação YouTube OK!")
        
        # Validar formato
        print(f"\n🔍 Validando formato do arquivo...")
        processor = VideoProcessor()
        video_info = processor.load_video(file_path)
        
        if not video_info:
            print("❌ Erro ao carregar vídeo")
            processor.cleanup()
            return False
        
        shorts_format = video_info['validation']['shorts_format']
        
        if shorts_format['is_shorts_format']:
            print("✅ Formato perfeito para YouTube Shorts!")
        else:
            print(f"⚠️  Formato será aceito: {video_info['width']}x{video_info['height']}")
        
        processor.cleanup()
        
        # Gerar metadados
        print(f"\n📝 Gerando metadados...")
        
        from upload_shorts import generate_title, generate_description, generate_tags
        
        title = generate_title(test_file)
        description = generate_description(test_file)
        tags = generate_tags(test_file)
        
        print(f"📝 Título: {title}")
        print(f"📝 Tags: {', '.join(tags[:5])}...")
        
        # Confirmar upload
        print(f"\n🚀 INICIANDO UPLOAD DE TESTE...")
        print("-" * 40)
        
        # Upload
        result = uploader.upload_video(
            file_path=file_path,
            title=title,
            description=description,
            tags=tags,
            category='22',
            privacy='public'
        )
        
        if result and result.get('success'):
            video_id = result.get('video_id')
            print(f"✅ Upload concluído!")
            print(f"🔗 https://youtu.be/{video_id}")
            
            # 🗑️ Testar remoção automática
            print(f"\n🗑️ Testando remoção automática...")
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✅ Arquivo removido: {test_file}")
                    print(f"🧹 Sistema de limpeza funcionando!")
                else:
                    print(f"⚠️  Arquivo já não existe: {test_file}")
            except Exception as e:
                print(f"❌ Erro ao remover arquivo: {e}")
                return False
            
            # Verificar se arquivo foi realmente removido
            if not os.path.exists(file_path):
                print(f"✅ Confirmado: arquivo removido com sucesso!")
            else:
                print(f"❌ Erro: arquivo ainda existe")
                return False
            
            print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
            print(f"✅ Upload: OK")
            print(f"✅ Remoção automática: OK")
            print(f"✅ Vídeo disponível em: https://youtube.com/@leonardo_zarelli")
            
            return True
        else:
            error_msg = result.get('error', 'Erro desconhecido') if result else 'Sem resposta'
            print(f"❌ Upload falhou: {error_msg}")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def test_scheduler_system():
    """Testa sistema de agendamento"""
    
    print("\n🧪 TESTE DO SISTEMA DE AGENDAMENTO")
    print("=" * 50)
    
    try:
        from upload_scheduler import UploadScheduler
        from datetime import datetime, timedelta
        
        # Verificar shorts restantes
        shorts_dir = 'shorts'
        shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
        
        if not shorts_files:
            print("📝 Nenhum short restante para agendar (todos foram enviados)")
            return True
        
        print(f"📁 Shorts restantes para agendar: {len(shorts_files)}")
        
        # Configurar scheduler
        scheduler_config = {
            'upload_time': '08:00',
            'timezone': 'America/Sao_Paulo',
            'daily_uploads': True,
            'max_concurrent_uploads': 1,
            'check_interval': 60
        }
        
        scheduler = UploadScheduler(scheduler_config)
        print("✅ Scheduler configurado")
        
        # Preparar shorts info
        shorts_info = []
        for filename in shorts_files[:3]:  # Agendar apenas 3 para teste
            file_path = os.path.join(shorts_dir, filename)
            if os.path.exists(file_path):
                
                from upload_shorts import generate_title, generate_description, generate_tags
                
                title = generate_title(filename)
                description = generate_description(filename)
                tags = generate_tags(filename)
                
                short_info = {
                    'output_path': file_path,
                    'filename': filename,
                    'title': title,
                    'created_successfully': True,
                    'metadata': {
                        'title': title,
                        'description': description,
                        'tags': tags,
                        'category': '22',
                        'privacy_status': 'public'
                    }
                }
                shorts_info.append(short_info)
        
        print(f"✅ {len(shorts_info)} shorts preparados para agendamento")
        
        # Configurar uploader
        uploader = YouTubeUploader()
        if not uploader.authenticate():
            print("❌ Falha na autenticação para agendamento")
            return False
        
        scheduler.set_uploader(uploader)
        print("✅ Uploader configurado no scheduler")
        
        # Agendar shorts (teste: 2 dias, 2 vídeos/dia)
        scheduled_ids = scheduler.schedule_shorts(
            shorts_info=shorts_info,
            start_date=datetime.now() + timedelta(days=1),
            days_duration=2,
            videos_per_day=2,
            daily_times=['08:00', '18:30']
        )
        
        if scheduled_ids:
            print(f"✅ {len(scheduled_ids)} shorts agendados com sucesso")
            
            # Mostrar status
            status = scheduler.get_scheduler_status()
            upcoming = status.get('upcoming_uploads', [])
            
            print(f"\n📅 PRÓXIMOS UPLOADS AGENDADOS:")
            for i, upload in enumerate(upcoming[:3], 1):
                day_info = f"(Dia {upload['day_number']}, Slot {upload['time_slot']})" if upload.get('day_number') else ""
                print(f"   {i}. {upload['formatted_time']} - {upload['title'][:40]}... {day_info}")
            
            # Iniciar scheduler
            scheduler.start_scheduler()
            print(f"🚀 SCHEDULER INICIADO E FUNCIONANDO!")
            
            print(f"\n🎯 TESTE DE AGENDAMENTO CONCLUÍDO!")
            print(f"✅ Sistema funcionando automaticamente")
            print(f"✅ Próximo upload: {upcoming[0]['formatted_time'] if upcoming else 'Nenhum'}")
            
            return True
        else:
            print("❌ Erro no agendamento")
            return False
            
    except Exception as e:
        print(f"❌ Erro no teste de agendamento: {e}")
        return False

def main():
    """Executa testes do sistema"""
    
    print("🧪 SISTEMA DE TESTES - YouTube Shorts Automation")
    print("=" * 60)
    print("🎯 Testando funcionalidades principais...")
    
    # Teste 1: Upload de um short com remoção automática
    print("\n🚀 TESTE 1: Upload + Remoção Automática")
    success_upload = test_upload_one_short()
    
    if success_upload:
        print("\n✅ TESTE 1 PASSOU!")
    else:
        print("\n❌ TESTE 1 FALHOU!")
        return False
    
    # Teste 2: Sistema de agendamento
    print("\n🚀 TESTE 2: Sistema de Agendamento")
    success_scheduler = test_scheduler_system()
    
    if success_scheduler:
        print("\n✅ TESTE 2 PASSOU!")
    else:
        print("\n❌ TESTE 2 FALHOU!")
        return False
    
    # Resultado final
    print("\n" + "=" * 60)
    print("🎉 TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print("✅ Upload imediato + remoção automática: OK")
    print("✅ Sistema de agendamento: OK")
    print("✅ Autenticação YouTube: OK")
    print("✅ Processamento de vídeos: OK")
    
    print("\n🚀 Sistema pronto para uso em produção!")
    print("📺 Acesse: https://youtube.com/@leonardo_zarelli")
    
    return True

if __name__ == "__main__":
    main()