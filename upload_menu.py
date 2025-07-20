#!/usr/bin/env python3
"""
Menu Interativo Simplificado para Upload de Shorts
"""

import os
import sys
from datetime import datetime, timedelta
from upload_shorts_advanced import upload_scheduled

def show_menu():
    """Mostra o menu principal"""
    print("\n🚀 MENU DE UPLOAD DE SHORTS - Leonardo Zarelli")
    print("=" * 60)
    
    # Verificar shorts disponíveis
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        print("❌ Pasta 'shorts' não encontrada")
        return False
    
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        return False
    
    print(f"📁 SHORTS DISPONÍVEIS ({len(shorts_files)}):")
    for i, file in enumerate(shorts_files, 1):
        size = os.path.getsize(os.path.join(shorts_dir, file)) / (1024*1024)
        print(f"   {i}. {file[:60]}... ({size:.1f} MB)")
    
    print(f"\n🎯 OPÇÕES DE UPLOAD:")
    print(f"   1 📊 Upload IMEDIATO (todos os shorts agora)")
    print(f"   2 📅 Upload AGENDADO NO YOUTUBE (datas programadas)")
    print(f"   3 🔢 Upload SELETIVO (escolher shorts específicos)")
    print(f"   4 ❌ Sair")
    
    return shorts_files

def get_user_choice():
    """Obtém escolha do usuário"""
    while True:
        try:
            choice = input(f"\n👉 Digite sua escolha (1-4): ").strip()
            if choice in ['1', '2', '3', '4']:
                return int(choice)
            else:
                print("❌ Opção inválida. Digite 1, 2, 3 ou 4")
        except KeyboardInterrupt:
            print(f"\n❌ Operação cancelada")
            sys.exit(0)
        except:
            print("❌ Digite apenas números")

def configure_schedule():
    """Configura agendamento com valores padrão"""
    print(f"\n📅 CONFIGURAÇÃO RÁPIDA DE AGENDAMENTO")
    print("=" * 50)
    
    # Configuração padrão
    config = {
        'days_duration': 7,
        'videos_per_day': 2,
        'daily_times': ['08:00', '18:00'],
        'start_date': datetime.now() + timedelta(days=1)
    }
    
    print(f"📋 CONFIGURAÇÃO PADRÃO:")
    print(f"   • Duração: {config['days_duration']} dias")
    print(f"   • Vídeos por dia: {config['videos_per_day']}")
    print(f"   • Horários: {', '.join(config['daily_times'])}")
    print(f"   • Início: {config['start_date'].strftime('%d/%m/%Y')}")
    
    # Opção de personalizar
    print(f"\n📝 OPÇÕES:")
    print(f"   1 - Usar configuração padrão")
    print(f"   2 - Personalizar configuração")
    print(f"   3 - Voltar ao menu")
    
    choice = get_user_choice()
    
    if choice == 1:
        return config
    elif choice == 2:
        return customize_schedule(config)
    else:
        return None

def customize_schedule(config):
    """Permite personalizar configuração"""
    print(f"\n🛠️  PERSONALIZAÇÃO DE AGENDAMENTO")
    print("=" * 50)
    
    try:
        # Dias
        days = input(f"📅 Quantos dias? [7]: ").strip()
        if days and days.isdigit():
            config['days_duration'] = int(days)
        
        # Vídeos por dia
        videos = input(f"📊 Vídeos por dia? [2]: ").strip()
        if videos and videos.isdigit():
            config['videos_per_day'] = int(videos)
            
            # Ajustar horários
            if config['videos_per_day'] == 1:
                config['daily_times'] = ['08:00']
            elif config['videos_per_day'] == 2:
                config['daily_times'] = ['08:00', '18:00']
            elif config['videos_per_day'] == 3:
                config['daily_times'] = ['08:00', '12:00', '18:00']
            else:
                config['daily_times'] = ['08:00', '12:00', '16:00', '20:00']
        
        # Data início
        start = input(f"📅 Começar quando? [amanhã]: ").strip()
        if start.lower() in ['hoje', 'today']:
            config['start_date'] = datetime.now() + timedelta(hours=1)
        elif start.lower() in ['amanha', 'amanhã', 'tomorrow', '']:
            config['start_date'] = datetime.now() + timedelta(days=1)
        
        print(f"\n✅ CONFIGURAÇÃO PERSONALIZADA:")
        print(f"   • Duração: {config['days_duration']} dias")
        print(f"   • Vídeos por dia: {config['videos_per_day']}")
        print(f"   • Horários: {', '.join(config['daily_times'])}")
        print(f"   • Início: {config['start_date'].strftime('%d/%m/%Y')}")
        
        return config
        
    except:
        print("❌ Erro na configuração, usando padrão")
        return config

def upload_immediate(shorts_files):
    """Upload imediato"""
    print(f"\n🚀 UPLOAD IMEDIATO")
    print("=" * 50)
    
    confirm = input(f"✅ Confirma upload de {len(shorts_files)} shorts? [s/N]: ").strip().lower()
    
    if confirm in ['s', 'sim', 'y', 'yes']:
        print(f"📤 Iniciando upload imediato...")
        
        # Importar e usar upload_shorts
        from upload_shorts import upload_selected_shorts
        success = upload_selected_shorts(shorts_files)
        
        if success:
            print(f"🎉 Upload concluído com sucesso!")
            print(f"📺 Acesse: https://youtube.com/@leonardo_zarelli")
        else:
            print(f"❌ Erro no upload")
    else:
        print("❌ Upload cancelado")

def upload_selective(shorts_files):
    """Upload seletivo"""
    print(f"\n🔢 UPLOAD SELETIVO")
    print("=" * 50)
    
    print(f"📋 Selecione os shorts (exemplo: 1,3,5 ou 1-3):")
    selection = input(f"👉 Sua seleção: ").strip()
    
    try:
        selected_indices = []
        parts = selection.split(',')
        
        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                selected_indices.extend(range(start, end + 1))
            else:
                selected_indices.append(int(part))
        
        selected_files = [shorts_files[i-1] for i in selected_indices if 1 <= i <= len(shorts_files)]
        
        if selected_files:
            print(f"✅ Selecionados {len(selected_files)} shorts")
            upload_immediate(selected_files)
        else:
            print("❌ Nenhum short selecionado")
            
    except:
        print("❌ Seleção inválida")

def main():
    """Função principal"""
    try:
        while True:
            shorts_files = show_menu()
            
            if not shorts_files:
                break
            
            choice = get_user_choice()
            
            if choice == 1:
                # Upload imediato
                upload_immediate(shorts_files)
                
            elif choice == 2:
                # Upload agendado
                config = configure_schedule()
                if config:
                    print(f"\n🚀 INICIANDO AGENDAMENTO NO YOUTUBE...")
                    success = upload_scheduled(shorts_files, config)
                    if success:
                        print(f"🎉 Agendamento concluído!")
                    else:
                        print(f"❌ Erro no agendamento")
                
            elif choice == 3:
                # Upload seletivo
                upload_selective(shorts_files)
                
            elif choice == 4:
                # Sair
                print(f"👋 Até logo!")
                break
            
            # Perguntar se quer continuar
            continue_choice = input(f"\n🔄 Fazer outra operação? [s/N]: ").strip().lower()
            if continue_choice not in ['s', 'sim', 'y', 'yes']:
                print(f"👋 Até logo!")
                break
                
    except KeyboardInterrupt:
        print(f"\n👋 Operação cancelada. Até logo!")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()