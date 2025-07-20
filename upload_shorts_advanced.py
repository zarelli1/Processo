#!/usr/bin/env python3
"""
🚀 SISTEMA AVANÇADO DE UPLOAD DE SHORTS
Sistema com agendamento personalizado e múltiplos horários diários
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from youtube_uploader import YouTubeUploader
from upload_scheduler import UploadScheduler
from video_processor import VideoProcessor

def main():
    """Função principal com menu interativo avançado"""
    
    print("🚀 SISTEMA AVANÇADO DE UPLOAD - Leonardo Zarelli")
    print("=" * 60)
    
    # Verificar pasta de shorts
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        print("❌ Pasta 'shorts' não encontrada")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        sys.exit(1)
    
    # Listar arquivos disponíveis
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    shorts_files.sort()
    
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        sys.exit(1)
    
    print(f"📁 SHORTS DISPONÍVEIS ({len(shorts_files)}):")
    for i, file in enumerate(shorts_files, 1):
        size = os.path.getsize(os.path.join(shorts_dir, file)) / (1024*1024)
        print(f"   {i:2d}. {file} ({size:.1f} MB)")
    
    # Menu principal
    print(f"\n🎯 OPÇÕES DE UPLOAD:")
    print(f"   1 📊 Upload IMEDIATO (todos os shorts agora)")
    print(f"   2 📅 Upload AGENDADO (configurar dias e horários)")
    print(f"   3 🔢 Upload SELETIVO (escolher shorts específicos)")
    print(f"   4 ⬅️ Voltar ao menu principal")
    print(f"   5 ❌ Cancelar")
    
    while True:
        choice = input(f"\n👉 Escolha uma opção (1-5): ").strip()
        
        if choice == "1":
            # Upload imediato
            upload_immediate(shorts_files)
            break
            
        elif choice == "2":
            # Upload agendado
            config = configure_scheduled_upload()
            if config:
                upload_scheduled(shorts_files, config)
            elif config is None:  # Usuário escolheu voltar
                continue  # Volta ao menu principal
            break
            
        elif choice == "3":
            # Upload seletivo
            selected_videos = select_videos_interactive(shorts_files)
            if selected_videos:
                upload_immediate(selected_videos)
            elif selected_videos is None:  # Usuário escolheu voltar
                continue  # Volta ao menu principal
            break
            
        elif choice == "4":
            print("⬅️ Voltando ao menu principal...")
            main()  # Reinicia o menu principal
            return
            
        elif choice == "5":
            print("❌ Upload cancelado")
            sys.exit(0)
        else:
            print("❌ Opção inválida. Escolha 1, 2, 3, 4 ou 5")

def configure_scheduled_upload() -> Dict:
    """Configura upload agendado com múltiplos horários"""
    
    print("\n📅 CONFIGURAÇÃO DE UPLOAD AGENDADO")
    print("=" * 50)
    
    config = {}
    
    # 1. Duração em dias
    while True:
        try:
            print("\n🗓️ Por quantos DIAS você quer distribuir os uploads?")
            print("   💡 Padrão: 7 dias (1 semana)")
            print("   0️⃣ Digite '0' para voltar ao menu anterior")
            days_input = input("👉 Digite o número de dias (1-30) [7] ou 0 para voltar: ").strip()
            
            if days_input == "0":
                return None  # Sinal para voltar
                
            if not days_input:
                config['days_duration'] = 7
                break
            
            days = int(days_input)
            if 1 <= days <= 30:
                config['days_duration'] = days
                break
            else:
                print("❌ Digite um número entre 1 e 30")
                
        except ValueError:
            print("❌ Digite apenas números")
    
    # 2. Vídeos por dia
    while True:
        try:
            print(f"\n📊 Quantos VÍDEOS POR DIA você quer postar?")
            print("   💡 Padrão: 3 vídeos/dia")
            print("   💡 Máximo recomendado: 5 vídeos/dia")
            print("   0️⃣ Digite '0' para voltar ao menu anterior")
            videos_input = input("👉 Digite o número de vídeos por dia (1-10) [3] ou 0 para voltar: ").strip()
            
            if videos_input == "0":
                return None  # Sinal para voltar
                
            if not videos_input:
                config['videos_per_day'] = 3
                break
            
            videos = int(videos_input)
            if 1 <= videos <= 10:
                config['videos_per_day'] = videos
                break
            else:
                print("❌ Digite um número entre 1 e 10")
                
        except ValueError:
            print("❌ Digite apenas números")
    
    # 3. Horários diários
    videos_per_day = config['videos_per_day']
    
    print(f"\n⏰ CONFIGURAÇÃO DOS HORÁRIOS DIÁRIOS:")
    print(f"   Você precisa configurar {videos_per_day} horários por dia")
    
    # Horários padrão baseados na quantidade
    default_times = {
        1: ['08:00'],
        2: ['08:00', '18:30'],
        3: ['08:00', '12:00', '18:30'],
        4: ['08:00', '12:00', '16:00', '20:00'],
        5: ['08:00', '11:00', '14:00', '17:00', '20:00']
    }
    
    if videos_per_day <= 5:
        suggested_times = default_times[videos_per_day]
    else:
        # Gerar horários automáticos
        suggested_times = []
        start_hour = 8
        interval = (20 - 8) // (videos_per_day - 1)
        for i in range(videos_per_day):
            hour = start_hour + (i * interval)
            suggested_times.append(f"{hour:02d}:00")
    
    print(f"\n💡 HORÁRIOS SUGERIDOS: {', '.join(suggested_times)}")
    print("   • Primeiro shorts: 8:00 (manhã)")
    print("   • Segundo shorts: 12:00 (almoço)") 
    print("   • Terceiro shorts: 18:30 (tarde/noite)")
    print("   0️⃣ Digite '0' para voltar ao menu anterior")
    
    use_default = input("\n👉 Usar horários sugeridos? [S/n] ou 0 para voltar: ").strip().lower()
    
    if use_default == "0":
        return None  # Sinal para voltar
        
    if use_default in ['', 's', 'sim', 'y', 'yes']:
        config['daily_times'] = suggested_times
    else:
        # Configurar horários manualmente
        custom_times = []
        for i in range(videos_per_day):
            while True:
                print(f"\n⏰ Configurando horário {i+1}/{videos_per_day}")
                print("   0️⃣ Digite '0' para voltar ao menu anterior")
                time_input = input(f"👉 Horário do {i+1}º vídeo (HH:MM) ou 0 para voltar: ").strip()
                
                if time_input == "0":
                    return None  # Sinal para voltar
                    
                if validate_time_format(time_input):
                    custom_times.append(time_input)
                    break
                else:
                    print("❌ Formato inválido. Use HH:MM (ex: 08:00, 18:30)")
        
        config['daily_times'] = custom_times
    
    # 4. Data de início
    print(f"\n📅 QUANDO COMEÇAR OS UPLOADS?")
    print("   1. Amanhã")
    print("   2. Escolher data específica")
    print("   0. Voltar ao menu anterior")
    
    start_choice = input("👉 Escolha (1-2) [1] ou 0 para voltar: ").strip()
    
    if start_choice == "0":
        return None  # Sinal para voltar
        
    if start_choice == "2":
        while True:
            print("\n📅 Data de início personalizada:")
            print("   0️⃣ Digite '0' para voltar ao menu anterior")
            date_input = input("👉 Data de início (DD/MM/AAAA) ou 0 para voltar: ").strip()
            
            if date_input == "0":
                return None  # Sinal para voltar
                
            try:
                start_date = datetime.strptime(date_input, "%d/%m/%Y")
                if start_date.date() >= datetime.now().date():
                    config['start_date'] = start_date
                    break
                else:
                    print("❌ Data deve ser hoje ou no futuro")
            except ValueError:
                print("❌ Formato inválido. Use DD/MM/AAAA")
    else:
        config['start_date'] = datetime.now() + timedelta(days=1)
    
    # 5. Resumo da configuração
    print("\n" + "="*50)
    print("📋 RESUMO DA CONFIGURAÇÃO:")
    print("="*50)
    print(f"🗓️  Duração: {config['days_duration']} dias")
    print(f"📊 Vídeos/dia: {config['videos_per_day']}")
    print(f"⏰ Horários: {', '.join(config['daily_times'])}")
    print(f"📅 Início: {config['start_date'].strftime('%d/%m/%Y')}")
    
    total_slots = config['days_duration'] * config['videos_per_day']
    print(f"📈 Total de slots: {total_slots}")
    
    # Mostrar cronograma dos primeiros dias
    print(f"\n📅 CRONOGRAMA (primeiros 3 dias):")
    for day in range(min(3, config['days_duration'])):
        date = config['start_date'] + timedelta(days=day)
        print(f"   {date.strftime('%d/%m/%Y')}:")
        for i, time_str in enumerate(config['daily_times']):
            video_num = (day * config['videos_per_day']) + i + 1
            print(f"     • {time_str} - Vídeo {video_num}")
    
    print("\n📋 OPÇÕES FINAIS:")
    print("   S - Confirmar configuração")
    print("   N - Cancelar configuração")
    print("   0 - Voltar ao menu anterior")
    
    confirm = input(f"\n✅ Confirma, cancela ou volta? [S/n/0]: ").strip().lower()
    
    if confirm == "0":
        return None  # Sinal para voltar
    elif confirm in ['', 's', 'sim', 'y', 'yes']:
        return config
    else:
        print("❌ Configuração cancelada")
        return False  # Configuração cancelada (diferente de voltar)

def validate_time_format(time_str: str) -> bool:
    """Valida formato de horário HH:MM"""
    try:
        time_obj = datetime.strptime(time_str, "%H:%M")
        return True
    except ValueError:
        return False

def select_videos_interactive(shorts_files: List[str]) -> List[str]:
    """Seleção interativa de vídeos"""
    
    while True:
        print(f"\n📋 SELEÇÃO DE VÍDEOS:")
        print(f"   • Digite números separados por vírgula: 1,3,5")
        print(f"   • Use hífen para range: 1-4") 
        print(f"   • Combine ambos: 1,3,5-7")
        print(f"   • Digite '0' para voltar ao menu anterior")
        
        selection = input("👉 Sua seleção ou 0 para voltar: ").strip()
        
        if selection == "0":
            return None  # Sinal para voltar
        
        try:
            selected_indices = parse_selection(selection, len(shorts_files))
            selected_videos = [shorts_files[i-1] for i in selected_indices]
            
            print(f"✅ Selecionados {len(selected_videos)} shorts:")
            for video in selected_videos:
                print(f"   • {video}")
            
            # Confirmar seleção
            print(f"\n📋 OPÇÕES:")
            print(f"   S - Confirmar seleção")
            print(f"   N - Refazer seleção")
            print(f"   0 - Voltar ao menu anterior")
            
            confirm = input("👉 Confirma, refaz ou volta? [S/n/0]: ").strip().lower()
            
            if confirm == "0":
                return None  # Sinal para voltar
            elif confirm in ['', 's', 'sim', 'y', 'yes']:
                return selected_videos
            else:
                continue  # Refazer seleção
            
        except Exception as e:
            print(f"❌ Seleção inválida: {e}")
            print("\n🔄 Tente novamente ou digite '0' para voltar")
            retry = input("👉 Pressione Enter para tentar novamente ou 0 para voltar: ").strip()
            if retry == "0":
                return None
            continue

def parse_selection(selection: str, max_num: int) -> List[int]:
    """Parseia seleção de vídeos"""
    indices = set()
    parts = [part.strip() for part in selection.split(',')]
    
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            if 1 <= start <= max_num and 1 <= end <= max_num and start <= end:
                indices.update(range(start, end + 1))
            else:
                raise ValueError(f"Range inválido: {part}")
        else:
            num = int(part)
            if 1 <= num <= max_num:
                indices.add(num)
            else:
                raise ValueError(f"Número fora do range: {num}")
    
    return sorted(list(indices))

def upload_immediate(videos_to_upload: List[str]) -> bool:
    """Upload imediato dos vídeos selecionados"""
    
    print(f"\n🔧 UPLOAD IMEDIATO...")
    print("=" * 50)
    
    # Confirmação
    print(f"📊 Resumo:")
    print(f"   • Vídeos: {len(videos_to_upload)}")
    print(f"   • Tempo estimado: {len(videos_to_upload) * 0.5:.1f} minutos")
    print(f"   • Tipo: Upload imediato")
    
    print(f"\n📋 OPÇÕES FINAIS:")
    print(f"   S - Confirmar upload")
    print(f"   N - Cancelar upload")
    print(f"   0 - Voltar ao menu anterior")
    
    confirm = input(f"\n✅ Confirma, cancela ou volta? [s/N/0]: ").lower()
    
    if confirm == "0":
        main()  # Volta ao menu principal
        return False
    elif confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Upload cancelado")
        return False
    
    # Fazer upload
    from upload_shorts import upload_selected_shorts
    success = upload_selected_shorts(videos_to_upload)
    
    if success:
        print(f"\n🎉 UPLOAD IMEDIATO CONCLUÍDO!")
        print(f"📺 Acesse: https://youtube.com/@leonardo_zarelli")
    
    return success

def upload_scheduled(videos_to_upload: List[str], config: Dict) -> bool:
    """Upload agendado NATIVO do YouTube com publishAt"""
    
    print(f"\n📅 CONFIGURANDO UPLOAD AGENDADO NO YOUTUBE...")
    print("=" * 50)
    
    try:
        # Configurar uploader
        uploader = YouTubeUploader()
        if not uploader.authenticate():
            print("❌ Falha na autenticação do YouTube")
            return False
        
        print("✅ Autenticação YouTube configurada")
        
        # Preparar shorts para upload direto com agendamento
        shorts_dir = 'shorts'
        uploaded_videos = []
        
        video_index = 0
        for day in range(config['days_duration']):
            if video_index >= len(videos_to_upload):
                break
                
            current_date = config['start_date'] + timedelta(days=day)
            
            for time_slot in range(config['videos_per_day']):
                if video_index >= len(videos_to_upload):
                    break
                    
                # Obter horário para este slot
                time_str = config['daily_times'][time_slot % len(config['daily_times'])]
                hour, minute = map(int, time_str.split(':'))
                
                # Calcular datetime do agendamento
                publish_datetime = current_date.replace(
                    hour=hour,
                    minute=minute,
                    second=0,
                    microsecond=0
                )
                
                # Converter para formato ISO 8601 do YouTube
                publish_at = publish_datetime.isoformat() + 'Z'
                
                # Obter arquivo
                filename = videos_to_upload[video_index]
                file_path = os.path.join(shorts_dir, filename)
                
                if os.path.exists(file_path):
                    # Gerar metadados
                    from upload_shorts import generate_title, generate_description, generate_tags
                    
                    title = generate_title(filename)
                    description = generate_description(filename)
                    tags = generate_tags(filename)
                    
                    print(f"\n📤 Agendando vídeo {video_index + 1}/{len(videos_to_upload)}")
                    print(f"   📅 Data: {publish_datetime.strftime('%d/%m/%Y %H:%M')}")
                    print(f"   📺 Título: {title[:50]}...")
                    
                    # Fazer upload com agendamento NATIVO
                    result = uploader.upload_video(
                        file_path=file_path,
                        title=title,
                        description=description,
                        tags=tags,
                        category='22',
                        privacy='private',  # Privado até a data agendada
                        publish_at=publish_at  # 🎯 AGENDAMENTO NATIVO DO YOUTUBE!
                    )
                    
                    if result['success']:
                        uploaded_videos.append({
                            'filename': filename,
                            'title': title,
                            'video_id': result.get('video_id'),
                            'video_url': result.get('video_url'),
                            'publish_at': publish_datetime.strftime('%d/%m/%Y %H:%M'),
                            'day': day + 1,
                            'slot': time_slot + 1
                        })
                        
                        print(f"   ✅ Agendado com sucesso!")
                        print(f"   🔗 URL: {result.get('video_url')}")
                        
                        # Remover arquivo após upload
                        try:
                            os.remove(file_path)
                            print(f"   🗑️ Arquivo removido: {filename}")
                        except:
                            pass
                    else:
                        print(f"   ❌ Erro: {result.get('error')}")
                
                video_index += 1
        
        if uploaded_videos:
            print(f"\n🎉 AGENDAMENTO NATIVO CONCLUÍDO!")
            print(f"✅ {len(uploaded_videos)} shorts agendados DIRETO NO YOUTUBE")
            
            print(f"\n📅 CRONOGRAMA DE PUBLICAÇÃO:")
            for video in uploaded_videos:
                print(f"   {video['publish_at']} - {video['title'][:40]}...")
            
            print(f"\n🚀 VÍDEOS AGENDADOS NO YOUTUBE STUDIO!")
            print(f"   • Acesse: https://studio.youtube.com/channel/uploads")
            print(f"   • Os vídeos aparecerão automaticamente nas datas programadas")
            print(f"   • Não precisa deixar o sistema rodando!")
            
            # Salvar informações do agendamento
            save_native_schedule_info(config, uploaded_videos)
            
            return True
        else:
            print("❌ Nenhum vídeo foi agendado")
            return False
            
    except Exception as e:
        print(f"❌ Erro no upload agendado: {e}")
        return False

def save_schedule_info(config: Dict, scheduled_ids: List[str], upcoming: List[Dict]):
    """Salva informações do agendamento"""
    try:
        import json
        
        schedule_info = {
            'created_at': datetime.now().isoformat(),
            'config': {
                **config,
                'start_date': config['start_date'].isoformat()
            },
            'scheduled_ids': scheduled_ids,
            'upcoming_uploads': upcoming,
            'total_scheduled': len(scheduled_ids)
        }
        
        os.makedirs('temp', exist_ok=True)
        with open('temp/last_schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule_info, f, indent=2, ensure_ascii=False)
        
        print("📄 Informações do agendamento salvas em: temp/last_schedule.json")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar informações: {e}")

def save_native_schedule_info(config: Dict, uploaded_videos: List[Dict]):
    """Salva informações do agendamento nativo do YouTube"""
    try:
        import json
        
        schedule_info = {
            'created_at': datetime.now().isoformat(),
            'type': 'native_youtube_scheduling',
            'config': {
                **config,
                'start_date': config['start_date'].isoformat()
            },
            'uploaded_videos': uploaded_videos,
            'total_scheduled': len(uploaded_videos),
            'youtube_studio_url': 'https://studio.youtube.com/channel/uploads'
        }
        
        os.makedirs('temp', exist_ok=True)
        with open('temp/native_schedule.json', 'w', encoding='utf-8') as f:
            json.dump(schedule_info, f, indent=2, ensure_ascii=False)
        
        print("📄 Informações do agendamento salvas em: temp/native_schedule.json")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar informações: {e}")

if __name__ == "__main__":
    main()