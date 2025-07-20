#!/usr/bin/env python3
"""
YouTube Shorts Automation System
Transforma vídeos longos em 7 shorts automaticamente e agenda uploads diários.
Canal: Leonardo_Zarelli
"""

import os
import json
import logging
import schedule
import time
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# Importar nossos módulos
from video_downloader import VideoDownloader
from video_processor import VideoProcessor
from logging_config import setup_global_logger, get_logger
from system_validator import SystemValidator
from youtube_uploader import YouTubeUploader
from upload_scheduler import UploadScheduler
from system_monitor import SystemMonitor

@dataclass
class VideoData:
    """Estrutura de dados para informações de vídeo"""
    id: str
    title: str
    description: str
    duration: float
    local_path: str
    download_info: Dict
    processing_info: Dict
    validation_result: Dict
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'local_path': self.local_path,
            'download_info': self.download_info,
            'processing_info': self.processing_info,
            'validation_result': self.validation_result
        }

class YouTubeAutomation:
    """Classe principal para automação de YouTube Shorts"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Inicializa o sistema de automação"""
        self.config_path = config_path
        self.config = {}
        self.logger = None
        
        # Validar sistema primeiro
        self.validate_system()
        
        # Carregar configuração
        self.load_config()
        
        # Configurar logging avançado
        self.setup_advanced_logging()
        
        # Inicializar componentes
        self.downloader = VideoDownloader(self.config['directories']['downloads'])
        self.processor = VideoProcessor()
        
        # Componentes de upload e agendamento
        self.uploader = None
        self.scheduler = None
        self.monitor = None
        
        # Log inicial
        self.logger.info("YouTube Automation inicializado para Leonardo_Zarelli")
        
    def validate_system(self):
        """Valida sistema antes de inicializar"""
        print("🔍 Validando sistema...")
        
        validator = SystemValidator(self.config_path)
        results = validator.run_full_validation()
        
        if not results['summary']['success']:
            print("\n❌ Sistema possui problemas críticos:")
            for error in results['errors']:
                print(f"   • {error}")
            
            validator.print_validation_report()
            raise SystemExit("Corrija os problemas antes de continuar")
        
        print("✅ Sistema validado com sucesso!")
        
        # Mostrar avisos se houver
        if results['warnings']:
            print("\n⚠️  Avisos encontrados:")
            for warning in results['warnings']:
                print(f"   • {warning}")
        
    def load_config(self):
        """Carrega configurações do arquivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
    
    def setup_advanced_logging(self):
        """Configura sistema de logging avançado"""
        try:
            log_config = self.config.get('logging', {})
            
            # Configuração básica se não tiver avançada
            if not log_config:
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('logs/automation.log'),
                        logging.StreamHandler()
                    ]
                )
                self.logger = logging.getLogger('Main')
            else:
                # Configurar logger global
                from logging_config import AdvancedLogger
                logger_instance = AdvancedLogger(log_config)
                self.logger = logger_instance.get_logger('Main')
                
                # Adicionar métodos ao logger
                self.logger.log_process_start = logger_instance.log_process_start
                self.logger.log_process_end = logger_instance.log_process_end
                self.logger.log_step = logger_instance.log_step
                self.logger.log_error_details = logger_instance.log_error_details
                
        except Exception as e:
            # Fallback para logging básico
            logging.basicConfig(level=logging.INFO)
            self.logger = logging.getLogger('Main')
            self.logger.warning(f"Erro no logging avançado, usando básico: {e}")
            
            # Adicionar métodos dummy para compatibilidade
            def dummy_log_process_start(process_name: str, **kwargs):
                self.logger.info(f"INICIANDO: {process_name}")
                for key, value in kwargs.items():
                    self.logger.info(f"  {key}: {value}")
            
            def dummy_log_process_end(process_name: str, success: bool = True, **kwargs):
                status = "SUCESSO" if success else "ERRO"
                self.logger.info(f"FINALIZANDO: {process_name} - {status}")
                for key, value in kwargs.items():
                    self.logger.info(f"  {key}: {value}")
            
            def dummy_log_step(step_name: str, step_number: int = None, total_steps: int = None):
                if step_number and total_steps:
                    self.logger.info(f"ETAPA {step_number}/{total_steps}: {step_name}")
                else:
                    self.logger.info(f"ETAPA: {step_name}")
            
            def dummy_log_error_details(error: Exception, context: str = ""):
                self.logger.error(f"ERRO em {context}: {str(error)}")
                
            # Atribuir métodos dummy
            self.logger.log_process_start = dummy_log_process_start
            self.logger.log_process_end = dummy_log_process_end
            self.logger.log_step = dummy_log_step
            self.logger.log_error_details = dummy_log_error_details
        
    def download_video(self, url: str) -> Optional[VideoData]:
        """
        Baixa vídeo do YouTube e retorna estrutura VideoData
        
        Args:
            url: URL do vídeo YouTube
            
        Returns:
            VideoData com informações completas ou None se falhou
        """
        self.logger.info(f"Iniciando download: {url}")
        
        try:
            # Download do vídeo
            download_result = self.downloader.download_video(url)
            if not download_result:
                self.logger.error("Falha no download do vídeo")
                return None
            
            # Verificar se o arquivo existe no local especificado
            local_path = download_result['local_path']
            if not os.path.exists(local_path):
                self.logger.warning(f"Arquivo não encontrado no path: {local_path}")
                # Tentar encontrar o arquivo usando a função de busca
                found_path = self.downloader.find_downloaded_video(
                    title=download_result['title'],
                    video_id=download_result['id']
                )
                if found_path:
                    local_path = found_path
                    download_result['local_path'] = local_path
                    self.logger.info(f"Arquivo encontrado em: {local_path}")
                else:
                    self.logger.error("Arquivo não encontrado no sistema")
                    return None

            # Processar vídeo baixado
            processing_result = self.processor.load_video(local_path)
            if not processing_result:
                self.logger.error("Falha no processamento do vídeo")
                return None
            
            # Criar estrutura VideoData
            video_data = VideoData(
                id=download_result['id'],
                title=download_result['title'],
                description=download_result['description'],
                duration=download_result['duration'],
                local_path=local_path,
                download_info=download_result,
                processing_info=processing_result,
                validation_result=processing_result['validation']
            )
            
            # Log detalhado de download
            self.logger.info(f"Vídeo baixado: {download_result['title']}")
            self.logger.info(f"Duração: {download_result['duration']:.1f}s")
            self.logger.info(f"Arquivo: {download_result['local_path']}")
            
            # Verificar se vídeo é adequado
            if not processing_result['validation']['is_valid']:
                self.logger.error("Vídeo não atende aos requisitos mínimos")
                for error in processing_result['validation']['errors']:
                    self.logger.error(f"  • {error}")
                return None
            
            # Avisos se houver
            for warning in processing_result['validation']['warnings']:
                self.logger.warning(f"  • {warning}")
            
            self.logger.info(f"Download e processamento concluídos: {video_data.title}")
            return video_data
            
        except Exception as e:
            self.logger.log_error_details(e, "Download e processamento")
            return None
    
    def analyze_video(self, video_data: VideoData) -> Dict:
        """Analisa vídeo usando IA para identificar melhores momentos"""
        self.logger.log_step("Análise inteligente de vídeo")
        
        try:
            # Importar pipeline de análise
            from analysis_pipeline import AnalysisPipeline
            
            # Configurar pipeline
            pipeline_config = {
                'cache_enabled': True,
                'cache_dir': 'temp/cache',
                'max_workers': 3,
                'export_graphs': True,
                'analysis_interval': 1.0,
                'progress_callback': self._analysis_progress_callback
            }
            
            # Inicializar pipeline
            pipeline = AnalysisPipeline(pipeline_config)
            
            # Configurações dos shorts
            shorts_duration = self.config['shorts_config']['duration']
            shorts_count = self.config['shorts_config']['count_per_video']
            
            self.logger.info(f"Iniciando análise IA: {shorts_count} shorts de {shorts_duration}s")
            
            # Executar análise completa
            complete_analysis = pipeline.analyze_video_complete(
                video_path=video_data.local_path,
                shorts_duration=shorts_duration,
                shorts_count=shorts_count
            )
            
            # Extrair informações relevantes
            analysis_data = {
                'video_id': video_data.id,
                'analysis_method': 'ai_multimodal',
                'analysis_time': complete_analysis['summary']['total_analysis_time'],
                'segments_found': complete_analysis['summary']['segments_found'],
                'best_segments': complete_analysis['best_segments'],
                'audio_analysis': complete_analysis['analysis_results']['audio']['summary'],
                'visual_analysis': complete_analysis['analysis_results']['visual']['summary'],
                'speech_analysis': complete_analysis['analysis_results']['speech']['summary'],
                'analyzed_at': datetime.now().isoformat()
            }
            
            # Log resumo da análise
            self.logger.info(f"Análise IA concluída em {analysis_data['analysis_time']:.1f}s")
            self.logger.info(f"Encontrados {analysis_data['segments_found']} segmentos candidatos")
            
            # Log dos melhores segmentos
            for i, segment in enumerate(analysis_data['best_segments'][:3], 1):
                self.logger.info(f"Top {i}: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s "
                               f"(score: {segment['combined_score']:.3f})")
            
            # Limpeza do pipeline
            pipeline.cleanup()
            
            return analysis_data
            
        except Exception as e:
            self.logger.log_error_details(e, "Análise IA de vídeo")
            raise
    
    def _analysis_progress_callback(self, analysis_type: str, progress: float, status: str):
        """Callback para progresso da análise IA"""
        if progress >= 0:
            self.logger.info(f"[{analysis_type.upper()}] {progress:.0f}% - {status}")
        else:
            self.logger.error(f"[{analysis_type.upper()}] ERRO - {status}")
    
    def create_shorts(self, video_data: VideoData, analysis_data: Dict) -> List[Dict]:
        """Cria shorts a partir do vídeo analisado usando processamento em lote"""
        self.logger.log_step("Criação automática de shorts")
        
        try:
            # Importar processador de shorts
            from shorts_batch_processor import ShortsBatchProcessor
            
            # Extrair segmentos da análise
            best_segments = analysis_data.get('best_segments', [])
            
            if not best_segments:
                self.logger.error("Nenhum segmento encontrado para criar shorts")
                return []
            
            # Configurar processador
            processor_config = {
                'output_dir': self.config['directories']['shorts'],
                'backup_original': True,
                'backup_dir': 'backup',
                'max_parallel_jobs': 2,
                'create_thumbnails': True,
                'save_metadata_files': True,
                'progress_callback': self._shorts_progress_callback
            }
            
            # Inicializar processador
            processor = ShortsBatchProcessor(processor_config)
            
            # Configurar hashtags do canal
            hashtags = self.config.get('hashtags', [])
            
            self.logger.info(f"Iniciando criação de {len(best_segments)} shorts")
            
            # Processar lote de shorts
            batch_report = processor.create_shorts_batch(
                video_path=video_data.local_path,
                segments=best_segments,
                title=video_data.title,
                hashtags=hashtags,
                parallel=True  # Processamento paralelo
            )
            
            # Extrair informações dos shorts criados
            shorts_created = batch_report['results']['shorts_created']
            successful_shorts = [s for s in shorts_created if s.get('created_successfully', False)]
            
            # Log resumo
            total_shorts = len(shorts_created)
            success_count = len(successful_shorts)
            success_rate = batch_report['summary']['success_rate']
            
            self.logger.info(f"Criação concluída: {success_count}/{total_shorts} shorts ({success_rate:.1f}% sucesso)")
            
            # Log detalhes dos shorts criados
            for short in successful_shorts:
                self.logger.info(f"✓ {short['filename']} - {short['file_size']/1024/1024:.1f}MB")
            
            # Salvar relatório detalhado
            report_file = "temp/shorts_creation_report.json"
            os.makedirs(os.path.dirname(report_file), exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(batch_report, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Relatório detalhado salvo: {report_file}")
            
            # Limpeza
            processor.cleanup_temp_files()
            
            return shorts_created
            
        except Exception as e:
            self.logger.log_error_details(e, "Criação de shorts")
            return []
    
    def _shorts_progress_callback(self, step: str, progress: float, details: str):
        """Callback para progresso da criação de shorts"""
        self.logger.info(f"[SHORTS] {step}: {progress:.0f}% - {details}")
    
    def initialize_upload_system(self) -> bool:
        """
        Inicializa sistema de upload e agendamento
        
        Returns:
            True se inicialização bem-sucedida
        """
        try:
            self.logger.info("Inicializando sistema de upload")
            
            # Configurar uploader
            uploader_config = {
                'client_secrets_file': 'config/client_secrets.json',
                'credentials_file': 'config/youtube_credentials.pickle',
                'scopes': ['https://www.googleapis.com/auth/youtube.upload'],
                'api_service_name': 'youtube',
                'api_version': 'v3',
                'default_category': '22',  # People & Blogs
                'default_privacy': 'public'
            }
            
            self.uploader = YouTubeUploader(uploader_config)
            
            # Autenticar
            if not self.uploader.authenticate():
                self.logger.error("Falha na autenticação do YouTube")
                return False
            
            # Configurar scheduler
            scheduler_config = {
                'upload_time': self.config.get('upload_schedule', {}).get('time', '07:00'),
                'timezone': self.config.get('upload_schedule', {}).get('timezone', 'America/Sao_Paulo'),
                'daily_uploads': True,
                'max_concurrent_uploads': 1,
                'check_interval': 60
            }
            
            self.scheduler = UploadScheduler(scheduler_config)
            self.scheduler.set_uploader(self.uploader)
            
            # Configurar monitor
            monitor_config = {
                'monitor_interval': 30,
                'history_file': 'temp/system_history.json',
                'alert_cpu_threshold': 80,
                'alert_memory_threshold': 85,
                'dashboard_refresh': 5
            }
            
            self.monitor = SystemMonitor(monitor_config)
            self.monitor.set_components(scheduler=self.scheduler, uploader=self.uploader)
            
            self.logger.info("Sistema de upload inicializado com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao inicializar sistema de upload: {str(e)}")
            return False
    
    def schedule_shorts_uploads(self, shorts_created: List[Dict], custom_config: Dict = None) -> List[str]:
        """
        Agenda uploads dos shorts criados com configuração personalizada
        
        Args:
            shorts_created: Lista de shorts criados
            custom_config: Configuração personalizada de agendamento
            
        Returns:
            Lista de IDs dos uploads agendados
        """
        try:
            self.logger.log_step("Agendamento de uploads")
            
            # Verificar se sistema de upload está inicializado
            if not self.scheduler:
                self.logger.warning("Sistema de upload não inicializado, inicializando agora...")
                if not self.initialize_upload_system():
                    raise Exception("Falha ao inicializar sistema de upload")
            
            # Filtrar apenas shorts criados com sucesso
            successful_shorts = [s for s in shorts_created if s.get('created_successfully', False)]
            
            if not successful_shorts:
                self.logger.warning("Nenhum short válido para agendar")
                return []
            
            # Usar configuração personalizada ou padrão
            if custom_config:
                days_duration = custom_config.get('days_duration', 7)
                videos_per_day = custom_config.get('videos_per_day', 3)
                daily_times = custom_config.get('daily_times', ['08:00', '12:00', '18:30'])
                start_date = custom_config.get('start_date')
                
                self.logger.info(f"Agendando {len(successful_shorts)} shorts:")
                self.logger.info(f"  • Período: {days_duration} dias")
                self.logger.info(f"  • Vídeos/dia: {videos_per_day}")
                self.logger.info(f"  • Horários: {', '.join(daily_times)}")
                
                # Agendar shorts com configuração personalizada
                scheduled_ids = self.scheduler.schedule_shorts(
                    shorts_info=successful_shorts,
                    start_date=start_date,
                    days_duration=days_duration,
                    videos_per_day=videos_per_day,
                    daily_times=daily_times
                )
            else:
                self.logger.info(f"Agendando {len(successful_shorts)} shorts para upload diário (configuração padrão)")
                
                # Agendar shorts com configuração padrão
                scheduled_ids = self.scheduler.schedule_shorts(
                    shorts_info=successful_shorts,
                    start_date=None,  # Começar amanhã
                    upload_time=None  # Usar horário configurado
                )
            
            if scheduled_ids:
                self.logger.info(f"✅ {len(scheduled_ids)} shorts agendados com sucesso")
                
                # Iniciar scheduler se não estiver rodando
                if not self.scheduler.is_running:
                    self.scheduler.start_scheduler()
                    self.logger.info("Scheduler iniciado")
                
                # Iniciar monitor se não estiver rodando
                if not self.monitor.is_running:
                    self.monitor.start_monitoring()
                    self.logger.info("Monitor de sistema iniciado")
            
            return scheduled_ids
            
        except Exception as e:
            self.logger.error(f"Erro no agendamento: {str(e)}")
            return []
    
    def process_video(self, video_url: str) -> Optional[VideoData]:
        """
        Processo completo: download -> análise -> preparação
        
        Args:
            video_url: URL do vídeo YouTube
            
        Returns:
            VideoData processado ou None se falhou
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            self.logger.log_process_start("Processamento Completo", 
                                        url=video_url, 
                                        session_id=session_id)
            
            # 1. Download e validação
            self.logger.log_step("Download e validação", 1, 3)
            video_data = self.download_video(video_url)
            if not video_data:
                raise Exception("Falha no download/validação do vídeo")
            
            # 2. Análise do vídeo
            self.logger.log_step("Análise do vídeo", 2, 4)
            analysis_data = self.analyze_video(video_data)
            
            # 3. Criação dos shorts
            self.logger.log_step("Criação de shorts", 3, 4)
            shorts_created = self.create_shorts(video_data, analysis_data)
            
            # 4. Agendamento e preparação final
            self.logger.log_step("Agendamento e preparação final", 4, 4)
            
            # Agendar uploads dos shorts
            scheduled_ids = self.schedule_shorts_uploads(shorts_created)
            
            # Salvar dados da sessão
            session_data = {
                'session_id': session_id,
                'video_data': video_data.to_dict(),
                'analysis_data': analysis_data,
                'shorts_created': shorts_created,
                'scheduled_uploads': scheduled_ids,
                'upload_system_active': len(scheduled_ids) > 0,
                'processed_at': datetime.now().isoformat(),
                'next_steps': ['monitor_uploads', 'check_upload_status'] if scheduled_ids else ['retry_scheduling']
            }
            
            # Salvar em arquivo para próximas etapas
            session_file = f"temp/session_{session_id}.json"
            os.makedirs(os.path.dirname(session_file), exist_ok=True)
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            self.logger.log_process_end("Processamento Completo", 
                                      success=True,
                                      session_file=session_file,
                                      segments_found=analysis_data.get('segments_found', 0),
                                      shorts_created=len([s for s in shorts_created if s.get('created_successfully', False)]),
                                      uploads_scheduled=len(scheduled_ids))
            
            return video_data
            
        except Exception as e:
            self.logger.log_process_end("Processamento Completo", 
                                      success=False, 
                                      error=str(e))
            self.logger.log_error_details(e, "Processo completo")
            return None
        finally:
            # Limpar recursos
            self.processor.cleanup()
    
    def run_upload_monitor(self):
        """
        Executa monitor de upload com dashboard
        """
        try:
            # Inicializar sistema se necessário
            if not self.monitor:
                if not self.initialize_upload_system():
                    raise Exception("Falha ao inicializar sistema de upload")
            
            self.logger.info("Iniciando monitor de upload com dashboard")
            
            # Iniciar scheduler se não estiver rodando
            if not self.scheduler.is_running:
                self.scheduler.start_scheduler()
            
            # Iniciar monitor
            if not self.monitor.is_running:
                self.monitor.start_monitoring()
            
            # Loop do dashboard
            try:
                while True:
                    self.monitor.print_dashboard()
                    time.sleep(self.monitor.config['dashboard_refresh'])
            except KeyboardInterrupt:
                self.logger.info("Monitor interrompido pelo usuário")
                
        except Exception as e:
            self.logger.error(f"Erro no monitor: {str(e)}")
        finally:
            self.stop_all_services()
    
    def get_system_status(self) -> Dict:
        """
        Retorna status completo do sistema
        
        Returns:
            Dicionário com status de todos os componentes
        """
        try:
            status = {
                'system_initialized': True,
                'uploader_status': None,
                'scheduler_status': None,
                'monitor_status': None,
                'timestamp': datetime.now().isoformat()
            }
            
            if self.uploader:
                status['uploader_status'] = self.uploader.get_upload_stats()
            
            if self.scheduler:
                status['scheduler_status'] = self.scheduler.get_scheduler_status()
            
            if self.monitor:
                status['monitor_status'] = {
                    'is_running': self.monitor.is_running,
                    'dashboard_data': self.monitor.get_dashboard_data()
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {str(e)}")
            return {'error': str(e)}
    
    def stop_all_services(self):
        """
        Para todos os serviços em execução
        """
        try:
            self.logger.info("Parando todos os serviços...")
            
            if self.scheduler:
                self.scheduler.stop_scheduler()
            
            if self.monitor:
                self.monitor.stop_monitoring()
            
            if self.uploader:
                self.uploader.cleanup()
            
            self.logger.info("Todos os serviços parados")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar serviços: {str(e)}")
    
    def cleanup(self):
        """Limpeza de recursos"""
        try:
            # Parar serviços
            self.stop_all_services()
            
            # Limpar outros componentes
            if hasattr(self, 'processor'):
                self.processor.cleanup()
            
            if hasattr(self, 'downloader'):
                self.downloader.cleanup_downloads()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Erro na limpeza: {str(e)}")

def main():
    """Função principal com menu interativo"""
    automation = None
    
    try:
        print("🎬 YouTube Shorts Automation - Leonardo_Zarelli")
        print("=" * 50)
        
        # Inicializar sistema
        automation = YouTubeAutomation()
        
        while True:
            print("\n📋 MENU PRINCIPAL:")
            print("1. Processar vídeo específico (completo)")
            print("2. Monitor de upload com dashboard")
            print("3. Sistema avançado de upload de shorts")
            print("4. Inicializar sistema de upload")
            print("5. Verificar status do sistema")
            print("6. Validar sistema novamente")
            print("7. Sair")
            
            choice = input("\nEscolha uma opção (1-7): ").strip()
            
            if choice == '1':
                url = input("Digite a URL do vídeo YouTube: ").strip()
                if url:
                    print(f"\n🔄 Processando: {url}")
                    result = automation.process_video(url)
                    if result:
                        print(f"✅ Vídeo processado com sucesso: {result.title}")
                    else:
                        print("❌ Falha no processamento do vídeo")
                else:
                    print("❌ URL inválida")
            
            elif choice == '2':
                print("\n📊 Iniciando monitor de upload...")
                print("Pressione Ctrl+C para parar")
                automation.run_upload_monitor()
            
            elif choice == '3':
                print("\n🚀 Iniciando sistema avançado de upload...")
                import subprocess
                try:
                    subprocess.run([sys.executable, "upload_shorts_advanced.py"], check=True)
                except subprocess.CalledProcessError:
                    print("❌ Erro ao executar sistema avançado de upload")
                except FileNotFoundError:
                    print("❌ Arquivo upload_shorts_advanced.py não encontrado")
            
            elif choice == '4':
                print("\n🔧 Inicializando sistema de upload...")
                if automation.initialize_upload_system():
                    print("✅ Sistema de upload inicializado com sucesso")
                else:
                    print("❌ Falha ao inicializar sistema de upload")
            
            elif choice == '5':
                print("\n📋 Status do sistema:")
                status = automation.get_system_status()
                if 'error' not in status:
                    print(f"Sistema: {'✅ Ativo' if status['system_initialized'] else '❌ Inativo'}")
                    if status['uploader_status']:
                        auth = status['uploader_status']['service_authenticated']
                        print(f"Uploader: {'✅ Autenticado' if auth else '❌ Não autenticado'}")
                    if status['scheduler_status']:
                        running = status['scheduler_status']['is_running']
                        print(f"Scheduler: {'✅ Rodando' if running else '❌ Parado'}")
                        queue_size = status['scheduler_status']['queue_statistics']['total_items']
                        print(f"Fila de upload: {queue_size} itens")
                        
                        # Mostrar próximos uploads se houver
                        upcoming = status['scheduler_status'].get('upcoming_uploads', [])
                        if upcoming:
                            print(f"\n📅 Próximos uploads:")
                            for i, upload in enumerate(upcoming[:3], 1):
                                day_info = f"(Dia {upload['day_number']}, Slot {upload['time_slot']})" if upload.get('day_number') else ""
                                print(f"   {i}. {upload['formatted_time']} - {upload['title'][:30]}... {day_info}")
                    
                    if status['monitor_status']:
                        running = status['monitor_status']['is_running']
                        print(f"Monitor: {'✅ Rodando' if running else '❌ Parado'}")
                else:
                    print(f"❌ Erro: {status['error']}")
            
            elif choice == '6':
                validator = SystemValidator()
                results = validator.run_full_validation()
                validator.print_validation_report()
            
            elif choice == '7':
                print("\n👋 Encerrando sistema...")
                break
            
            else:
                print("❌ Opção inválida")
        
    except KeyboardInterrupt:
        print("\n\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro fatal: {str(e)}")
        if automation and automation.logger:
            automation.logger.log_error_details(e, "Main")
    finally:
        if automation:
            automation.cleanup()
        print("🧹 Limpeza concluída")

if __name__ == "__main__":
    main()