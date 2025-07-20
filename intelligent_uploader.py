#!/usr/bin/env python3
"""
Sistema Inteligente de Upload
Combina análise de conteúdo + agendamento inteligente + upload automático
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from content_analyzer import ContentAnalyzer
from smart_scheduler import SmartScheduler
from youtube_uploader import YouTubeUploader

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentUploader:
    """Sistema inteligente que combina análise de conteúdo e agendamento otimizado"""
    
    def __init__(self, original_video_info: Dict = None):
        self.content_analyzer = ContentAnalyzer()
        self.scheduler = SmartScheduler()
        self.youtube_uploader = YouTubeUploader()
        self.original_video_info = original_video_info or {}
        
        # Configurações
        self.shorts_dir = "shorts"
        self.config_file = "config/upload_config.json"
        self.schedule_file = "config/upload_schedule.json"
        
        logger.info("Sistema Inteligente de Upload inicializado")
    
    def process_all_shorts(self, strategy: str = "balanced") -> Dict:
        """
        Processa todos os shorts na pasta com conteúdo inteligente e agendamento
        
        Args:
            strategy: "aggressive", "balanced", ou "conservative"
            
        Returns:
            Dict com resultado do processamento
        """
        logger.info(f"Iniciando processamento inteligente - estratégia: {strategy}")
        
        # 1. Verificar arquivos
        shorts_files = self._get_shorts_files()
        if not shorts_files:
            return {"error": "Nenhum short encontrado"}
        
        # 2. Analisar conteúdo original
        content_analysis = self._analyze_original_content()
        
        # 3. Gerar metadados únicos para cada short
        video_metadata = []
        for i, filename in enumerate(shorts_files, 1):
            metadata = self.content_analyzer.generate_video_metadata(
                video_title=self.original_video_info.get("title", "Conteúdo Tech"),
                video_description=self.original_video_info.get("description", ""),
                part_number=i,
                original_url=self.original_video_info.get("url", "")
            )
            metadata["filename"] = filename
            metadata["filepath"] = os.path.join(self.shorts_dir, filename)
            video_metadata.append(metadata)
        
        # 4. Gerar cronograma inteligente
        schedule = self.scheduler.get_optimal_schedule(
            num_videos=len(shorts_files),
            strategy=strategy
        )
        
        # 5. Combinar metadados com cronograma
        upload_plan = []
        for i, (metadata, schedule_item) in enumerate(zip(video_metadata, schedule)):
            upload_item = {
                **metadata,
                **schedule_item,
                "upload_status": "pending"
            }
            upload_plan.append(upload_item)
        
        # 6. Salvar plano
        self._save_upload_plan(upload_plan)
        
        # 7. Mostrar preview
        preview = self._generate_upload_preview(upload_plan)
        
        return {
            "success": True,
            "total_videos": len(upload_plan),
            "strategy": strategy,
            "upload_plan": upload_plan,
            "preview": preview,
            "schedule_report": self.scheduler.generate_schedule_report(schedule)
        }
    
    def _get_shorts_files(self) -> List[str]:
        """Retorna lista de arquivos de shorts"""
        if not os.path.exists(self.shorts_dir):
            return []
        
        files = [f for f in os.listdir(self.shorts_dir) if f.endswith('.mp4')]
        return sorted(files)
    
    def _analyze_original_content(self) -> Dict:
        """Analisa o conteúdo do vídeo original"""
        return self.content_analyzer.analyze_video_content(
            video_title=self.original_video_info.get("title", ""),
            video_description=self.original_video_info.get("description", ""),
            video_tags=self.original_video_info.get("tags", [])
        )
    
    def _save_upload_plan(self, upload_plan: List[Dict]):
        """Salva plano de upload em arquivo"""
        os.makedirs(os.path.dirname(self.schedule_file), exist_ok=True)
        
        plan_data = {
            "created_at": datetime.now().isoformat(),
            "original_video": self.original_video_info,
            "upload_plan": upload_plan
        }
        
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"Plano de upload salvo: {self.schedule_file}")
    
    def _generate_upload_preview(self, upload_plan: List[Dict]) -> str:
        """Gera preview do plano de upload"""
        preview = "🎬 PREVIEW DO PLANO DE UPLOAD\n"
        preview += "=" * 50 + "\n\n"
        
        for item in upload_plan[:5]:  # Mostrar apenas primeiros 5
            preview += f"📅 {item['scheduled_time'].strftime('%d/%m %H:%M')} - "
            preview += f"Vídeo {item['video_number']}\n"
            preview += f"   📝 {item['title']}\n"
            preview += f"   🏷️ {', '.join(item['tags'][:3])}...\n"
            preview += f"   📊 Score: {item['engagement_score']}\n\n"
        
        if len(upload_plan) > 5:
            preview += f"... e mais {len(upload_plan) - 5} vídeos\n"
        
        return preview
    
    def execute_upload_plan(self, immediate: bool = False) -> Dict:
        """
        Executa o plano de upload
        
        Args:
            immediate: Se True, faz upload imediato. Se False, agenda uploads
        """
        logger.info(f"Executando plano de upload - imediato: {immediate}")
        
        # Carregar plano
        if not os.path.exists(self.schedule_file):
            return {"error": "Nenhum plano de upload encontrado"}
        
        with open(self.schedule_file, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        
        upload_plan = plan_data["upload_plan"]
        results = {"success": 0, "failed": 0, "scheduled": 0, "errors": []}
        
        # Autenticar YouTube
        if not self.youtube_uploader.authenticate():
            return {"error": "Falha na autenticação do YouTube"}
        
        for item in upload_plan:
            try:
                if immediate:
                    # Upload imediato
                    result = self._upload_video_now(item)
                    if result["success"]:
                        results["success"] += 1
                        item["upload_status"] = "uploaded"
                        item["video_id"] = result["video_id"]
                        item["uploaded_at"] = datetime.now().isoformat()
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Vídeo {item['video_number']}: {result['error']}")
                else:
                    # Agendar upload direto no YouTube
                    result = self._schedule_video_upload(item)
                    if result["success"]:
                        results["scheduled"] += 1
                        item["upload_status"] = "scheduled_youtube"
                        item["video_id"] = result.get("video_id")
                        item["video_url"] = result.get("video_url")
                        item["scheduled_for"] = result.get("scheduled_for")
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Vídeo {item['video_number']}: {result['error']}")
                
            except Exception as e:
                logger.error(f"Erro no upload do vídeo {item['video_number']}: {e}")
                results["failed"] += 1
                results["errors"].append(f"Vídeo {item['video_number']}: {str(e)}")
        
        # Salvar plano atualizado
        plan_data["upload_plan"] = upload_plan
        plan_data["last_execution"] = datetime.now().isoformat()
        
        with open(self.schedule_file, 'w', encoding='utf-8') as f:
            json.dump(plan_data, f, ensure_ascii=False, indent=2, default=str)
        
        return results
    
    def _upload_video_now(self, video_item: Dict) -> Dict:
        """Faz upload imediato de um vídeo"""
        try:
            upload_data = {
                "file_path": video_item["filepath"],
                "title": video_item["title"],
                "description": video_item["description"],
                "tags": video_item["tags"],
                "category_id": "22",  # People & Blogs
                "privacy_status": "public"
            }
            
            result = self.youtube_uploader.upload_video(upload_data)
            return result
            
        except Exception as e:
            logger.error(f"Erro no upload: {e}")
            return {"success": False, "error": str(e)}
    
    def _schedule_video_upload(self, video_item: Dict) -> Dict:
        """Agenda upload direto no YouTube para o horário especificado"""
        try:
            # Converter datetime para formato ISO 8601 UTC
            scheduled_time = video_item['scheduled_time']
            if isinstance(scheduled_time, str):
                scheduled_time = datetime.fromisoformat(scheduled_time)
            
            # Converter para UTC (YouTube API exige UTC)
            utc_time = scheduled_time.strftime('%Y-%m-%dT%H:%M:%SZ')
            
            logger.info(f"Agendando no YouTube: {video_item['title']} para {utc_time}")
            
            # Fazer upload com agendamento direto no YouTube
            result = self.youtube_uploader.upload_video_scheduled(
                file_path=video_item["filepath"],
                title=video_item["title"],
                description=video_item["description"],
                tags=video_item["tags"],
                category="22",  # People & Blogs
                publish_at=utc_time
            )
            
            if result["success"]:
                logger.info(f"✅ Vídeo agendado no YouTube: {result['video_url']}")
                logger.info(f"📅 Será publicado automaticamente em: {utc_time}")
                return {
                    "success": True, 
                    "video_id": result["video_id"],
                    "video_url": result["video_url"],
                    "scheduled_for": utc_time,
                    "message": "Agendado diretamente no YouTube"
                }
            else:
                return {"success": False, "error": result.get("error", "Erro desconhecido")}
            
        except Exception as e:
            logger.error(f"Erro no agendamento direto: {e}")
            return {"success": False, "error": str(e)}
    
    def show_upload_summary(self) -> str:
        """Mostra resumo dos uploads planejados/executados"""
        
        if not os.path.exists(self.schedule_file):
            return "❌ Nenhum plano de upload encontrado"
        
        with open(self.schedule_file, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
        
        upload_plan = plan_data["upload_plan"]
        
        summary = "📊 RESUMO DO PLANO DE UPLOAD\n"
        summary += "=" * 40 + "\n\n"
        
        # Estatísticas
        total = len(upload_plan)
        uploaded = sum(1 for item in upload_plan if item.get("upload_status") == "uploaded")
        scheduled_youtube = sum(1 for item in upload_plan if item.get("upload_status") == "scheduled_youtube")
        scheduled_local = sum(1 for item in upload_plan if item.get("upload_status") == "scheduled")
        pending = sum(1 for item in upload_plan if item.get("upload_status") == "pending")
        
        summary += f"📈 ESTATÍSTICAS:\n"
        summary += f"   • Total de vídeos: {total}\n"
        summary += f"   • ✅ Já publicados: {uploaded}\n"
        summary += f"   • 📅 Agendados no YouTube: {scheduled_youtube}\n"
        summary += f"   • ⏳ Agendados localmente: {scheduled_local}\n"
        summary += f"   • 🔄 Pendentes: {pending}\n\n"
        
        # Próximos uploads
        now = datetime.now()
        upcoming = [
            item for item in upload_plan 
            if item.get("upload_status") == "scheduled" 
            and datetime.fromisoformat(item["scheduled_time"]) > now
        ]
        
        if upcoming:
            summary += f"🔜 PRÓXIMOS UPLOADS:\n"
            for item in upcoming[:3]:
                scheduled_time = datetime.fromisoformat(item["scheduled_time"])
                summary += f"   📅 {scheduled_time.strftime('%d/%m %H:%M')} - {item['title'][:50]}...\n"
            
            if len(upcoming) > 3:
                summary += f"   ... e mais {len(upcoming) - 3} agendados\n"
        
        return summary

def main():
    """Função principal com menu interativo"""
    
    print("🤖 SISTEMA INTELIGENTE DE UPLOAD")
    print("=" * 50)
    
    # Verificar se há shorts para processar
    shorts_dir = "shorts"
    if not os.path.exists(shorts_dir):
        print("❌ Pasta 'shorts' não encontrada")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        sys.exit(1)
    
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        sys.exit(1)
    
    print(f"📁 Encontrados {len(shorts_files)} shorts para upload")
    
    # Solicitar informações do vídeo original
    print("\n🎬 INFORMAÇÕES DO VÍDEO ORIGINAL:")
    original_url = input("🔗 URL do vídeo original (opcional): ").strip()
    original_title = input("📝 Título do vídeo original: ").strip() or "Conteúdo Tech"
    
    original_video_info = {
        "url": original_url,
        "title": original_title,
        "description": "",
        "tags": []
    }
    
    # Inicializar sistema
    uploader = IntelligentUploader(original_video_info)
    
    # Menu principal
    while True:
        print(f"\n🎯 OPÇÕES DISPONÍVEIS:")
        print(f"   1 🧠 GERAR PLANO INTELIGENTE (análise + agendamento)")
        print(f"   2 🚀 UPLOAD IMEDIATO (todos agora)")
        print(f"   3 📅 AGENDAR NO YOUTUBE (automático nos horários ótimos)")
        print(f"   4 📊 VER RESUMO DO PLANO")
        print(f"   5 ❌ Sair")
        
        choice = input("\n👉 Escolha uma opção (1-5): ").strip()
        
        if choice == "1":
            print("\n📋 ESTRATÉGIAS DISPONÍVEIS:")
            print("   • conservative: 1 vídeo/dia, maior espaçamento")
            print("   • balanced: 2 vídeos/dia, equilibrado (recomendado)")
            print("   • aggressive: 4 vídeos/dia, máximo alcance")
            
            strategy = input("\n🎯 Estratégia (conservative/balanced/aggressive): ").strip() or "balanced"
            
            print(f"\n🧠 Gerando plano inteligente...")
            result = uploader.process_all_shorts(strategy)
            
            if result.get("success"):
                print("✅ Plano gerado com sucesso!")
                print(f"\n{result['preview']}")
                print(f"\n{result['schedule_report']}")
            else:
                print(f"❌ Erro: {result.get('error')}")
        
        elif choice == "2":
            print(f"\n🚀 Iniciando upload imediato...")
            result = uploader.execute_upload_plan(immediate=True)
            
            print(f"\n📊 RESULTADO:")
            print(f"   ✅ Sucessos: {result.get('success', 0)}")
            print(f"   ❌ Falhas: {result.get('failed', 0)}")
            
            if result.get('errors'):
                print(f"\n❌ ERROS:")
                for error in result['errors']:
                    print(f"   • {error}")
        
        elif choice == "3":
            print(f"\n📅 Agendando diretamente no YouTube...")
            print(f"⚡ Os vídeos serão enviados agora e publicados automaticamente nos horários ótimos!")
            
            result = uploader.execute_upload_plan(immediate=False)
            
            print(f"\n📊 RESULTADO:")
            print(f"   📅 Agendados no YouTube: {result.get('scheduled', 0)}")
            print(f"   ❌ Falhas: {result.get('failed', 0)}")
            
            if result.get('scheduled', 0) > 0:
                print(f"\n✅ SUCESSO!")
                print(f"   🎬 Vídeos enviados para o YouTube")
                print(f"   📅 Serão publicados automaticamente nos horários programados")
                print(f"   🔔 Você receberá notificações quando forem publicados")
        
        elif choice == "4":
            summary = uploader.show_upload_summary()
            print(f"\n{summary}")
        
        elif choice == "5":
            print("👋 Até logo!")
            break
        
        else:
            print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()