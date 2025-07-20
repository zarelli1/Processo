#!/usr/bin/env python3
"""
Visualizador de Vídeos Agendados
Sistema para ver status dos uploads e agendamentos em tempo real
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class ScheduleViewer:
    """Visualizador de agendamentos e status dos vídeos"""
    
    def __init__(self):
        self.schedule_file = "config/upload_schedule.json"
        self.refresh_interval = 5  # segundos
        
    def load_schedule_data(self) -> Dict:
        """Carrega dados do cronograma"""
        if not os.path.exists(self.schedule_file):
            return {"error": "Nenhum agendamento encontrado"}
        
        try:
            with open(self.schedule_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            return {"error": f"Erro ao carregar: {e}"}
    
    def format_time_remaining(self, scheduled_time: str) -> str:
        """Calcula tempo restante até publicação"""
        try:
            if isinstance(scheduled_time, str):
                # Tentar diferentes formatos
                try:
                    dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                except:
                    dt = datetime.fromisoformat(scheduled_time)
            else:
                dt = scheduled_time
                
            now = datetime.now()
            
            # Se scheduled_time está em UTC, ajustar
            if 'Z' in str(scheduled_time):
                # É UTC, converter now para UTC para comparação
                import pytz
                now = now.replace(tzinfo=pytz.timezone('America/Sao_Paulo')).astimezone(pytz.UTC).replace(tzinfo=None)
            
            diff = dt - now
            
            if diff.total_seconds() <= 0:
                return "🔴 JÁ DEVERIA TER SIDO PUBLICADO"
            
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            if days > 0:
                return f"⏳ {days}d {hours}h {minutes}m"
            elif hours > 0:
                return f"⏳ {hours}h {minutes}m"
            else:
                return f"⏳ {minutes}m"
                
        except Exception as e:
            return f"❓ Erro: {e}"
    
    def get_status_emoji(self, status: str) -> str:
        """Retorna emoji baseado no status"""
        status_emojis = {
            "pending": "⏳",
            "scheduled": "📅", 
            "scheduled_youtube": "🎬",
            "uploaded": "✅",
            "failed": "❌",
            "published": "🔥"
        }
        return status_emojis.get(status, "❓")
    
    def show_current_status(self) -> str:
        """Mostra status atual dos vídeos"""
        data = self.load_schedule_data()
        
        if "error" in data:
            return f"❌ {data['error']}"
        
        upload_plan = data.get("upload_plan", [])
        if not upload_plan:
            return "📭 Nenhum vídeo no plano atual"
        
        now = datetime.now()
        
        output = "🎬 STATUS DOS VÍDEOS AGENDADOS\n"
        output += "=" * 50 + "\n\n"
        
        # Estatísticas rápidas
        total = len(upload_plan)
        published = sum(1 for v in upload_plan if v.get("upload_status") == "uploaded")
        scheduled_yt = sum(1 for v in upload_plan if v.get("upload_status") == "scheduled_youtube")
        pending = sum(1 for v in upload_plan if v.get("upload_status") == "pending")
        
        output += f"📊 RESUMO RÁPIDO:\n"
        output += f"   Total: {total} | ✅ Publicados: {published} | 🎬 Agendados: {scheduled_yt} | ⏳ Pendentes: {pending}\n\n"
        
        # Próximos vídeos (próximas 24h)
        upcoming = []
        for video in upload_plan:
            if video.get("upload_status") in ["scheduled_youtube", "scheduled"]:
                try:
                    scheduled_time = video.get("scheduled_time")
                    if scheduled_time:
                        if isinstance(scheduled_time, str):
                            dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                        else:
                            dt = scheduled_time
                        
                        if dt > now and dt <= now + timedelta(hours=24):
                            upcoming.append((video, dt))
                except:
                    continue
        
        upcoming.sort(key=lambda x: x[1])
        
        if upcoming:
            output += "🔜 PRÓXIMAS 24 HORAS:\n"
            for video, dt in upcoming[:5]:
                time_remaining = self.format_time_remaining(video["scheduled_time"])
                status_emoji = self.get_status_emoji(video.get("upload_status", "pending"))
                
                output += f"   {status_emoji} {dt.strftime('%H:%M')} - {video.get('title', 'Sem título')[:40]}...\n"
                output += f"      {time_remaining}\n"
            output += "\n"
        
        # Todos os vídeos
        output += "📋 TODOS OS VÍDEOS:\n"
        output += "-" * 30 + "\n"
        
        current_date = None
        for video in sorted(upload_plan, key=lambda x: x.get("scheduled_time", "")):
            try:
                scheduled_time = video.get("scheduled_time")
                if scheduled_time:
                    if isinstance(scheduled_time, str):
                        dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    else:
                        dt = scheduled_time
                    
                    # Cabeçalho do dia
                    date_str = dt.strftime('%d/%m/%Y')
                    if current_date != date_str:
                        current_date = date_str
                        day_name = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'][dt.weekday()]
                        output += f"\n📅 {day_name}, {date_str}:\n"
                    
                    # Detalhes do vídeo
                    status_emoji = self.get_status_emoji(video.get("upload_status", "pending"))
                    time_str = dt.strftime('%H:%M')
                    title = video.get("title", "Sem título")[:45]
                    
                    output += f"   {status_emoji} {time_str} - {title}\n"
                    
                    # Informações extras
                    if video.get("video_url"):
                        output += f"      🔗 {video['video_url']}\n"
                    
                    time_remaining = self.format_time_remaining(scheduled_time)
                    output += f"      {time_remaining}\n"
                    
                    if video.get("engagement_score"):
                        score = video["engagement_score"]
                        score_emoji = "🔥" if score >= 90 else "⚡" if score >= 75 else "📈"
                        output += f"      {score_emoji} Score: {score}\n"
                    
                    output += "\n"
            except Exception as e:
                output += f"   ❌ Vídeo {video.get('video_number', '?')}: Erro na data\n"
        
        return output
    
    def show_live_dashboard(self):
        """Dashboard em tempo real"""
        print("🎬 DASHBOARD AO VIVO - YouTube Scheduler")
        print("Pressione Ctrl+C para sair")
        print("=" * 60)
        
        try:
            while True:
                # Limpar tela (funciona no Linux/Mac)
                os.system('clear' if os.name == 'posix' else 'cls')
                
                print("🎬 YOUTUBE SCHEDULER - DASHBOARD AO VIVO")
                print(f"⏰ Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                print("=" * 60)
                
                status = self.show_current_status()
                print(status)
                
                print(f"\n🔄 Próxima atualização em {self.refresh_interval}s (Ctrl+C para sair)")
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard encerrado!")
    
    def show_video_details(self, video_number: int = None):
        """Mostra detalhes de um vídeo específico"""
        data = self.load_schedule_data()
        
        if "error" in data:
            return f"❌ {data['error']}"
        
        upload_plan = data.get("upload_plan", [])
        
        if video_number:
            # Buscar vídeo específico
            video = None
            for v in upload_plan:
                if v.get("video_number") == video_number:
                    video = v
                    break
            
            if not video:
                return f"❌ Vídeo #{video_number} não encontrado"
            
            output = f"🎬 DETALHES DO VÍDEO #{video_number}\n"
            output += "=" * 40 + "\n\n"
            
            output += f"📝 Título: {video.get('title', 'Sem título')}\n"
            output += f"📅 Agendado: {video.get('scheduled_time', 'Não definido')}\n"
            output += f"🎯 Status: {self.get_status_emoji(video.get('upload_status', 'pending'))} {video.get('upload_status', 'pending')}\n"
            
            if video.get("video_url"):
                output += f"🔗 URL: {video['video_url']}\n"
            
            if video.get("engagement_score"):
                output += f"📊 Score: {video['engagement_score']}\n"
            
            if video.get("scheduled_time"):
                time_remaining = self.format_time_remaining(video["scheduled_time"])
                output += f"⏰ Tempo restante: {time_remaining}\n"
            
            output += f"\n📋 Descrição:\n{video.get('description', 'Sem descrição')[:200]}...\n"
            output += f"\n🏷️ Tags: {', '.join(video.get('tags', [])[:5])}\n"
            
            return output
        else:
            return self.show_current_status()

def main():
    """Menu principal do visualizador"""
    viewer = ScheduleViewer()
    
    print("👁️ VISUALIZADOR DE AGENDAMENTOS")
    print("=" * 40)
    
    while True:
        print(f"\n🎯 OPÇÕES:")
        print(f"   1 📊 Ver status atual")
        print(f"   2 🔴 Dashboard ao vivo")
        print(f"   3 🔍 Detalhes de vídeo específico")
        print(f"   4 📋 Listar todos")
        print(f"   5 ❌ Sair")
        
        choice = input("\n👉 Escolha (1-5): ").strip()
        
        if choice == "1":
            print("\n" + viewer.show_current_status())
            
        elif choice == "2":
            viewer.show_live_dashboard()
            
        elif choice == "3":
            try:
                video_num = int(input("🎬 Número do vídeo: "))
                print("\n" + viewer.show_video_details(video_num))
            except ValueError:
                print("❌ Digite um número válido")
                
        elif choice == "4":
            print("\n" + viewer.show_current_status())
            
        elif choice == "5":
            print("👋 Até logo!")
            break
            
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()