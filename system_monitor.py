#!/usr/bin/env python3
"""
System Monitor Module
Monitor de sistema com dashboard para automação YouTube Shorts
Canal: Your_Channel_Name
"""

import os
import time
import json
import logging
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import psutil
from dataclasses import dataclass

@dataclass
class SystemStatus:
    """Status do sistema em tempo real"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_free_gb: float
    active_threads: int
    upload_queue_size: int
    last_upload: str
    system_health: str
    errors_count: int

class SystemMonitor:
    """Monitor de sistema e dashboard para automação"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = config or {
            'monitor_interval': 30,  # segundos
            'history_file': 'temp/system_history.json',
            'max_history_entries': 288,  # 24h com interval de 5min
            'alert_cpu_threshold': 80,
            'alert_memory_threshold': 85,
            'alert_disk_threshold_gb': 2,
            'dashboard_refresh': 5
        }
        
        # Estado do monitor
        self.is_running = False
        self.monitor_thread = None
        self._stop_event = threading.Event()
        
        # Componentes monitorados
        self.scheduler = None
        self.uploader = None
        
        # Histórico de status
        self.status_history: List[SystemStatus] = []
        self.current_status = None
        
        # Contadores de erro
        self.error_counts = {
            'upload_errors': 0,
            'auth_errors': 0,
            'quota_errors': 0,
            'system_errors': 0
        }
        
        # Carregar histórico existente
        self.load_history()
        
        self.logger.info("SystemMonitor inicializado")
    
    def set_components(self, scheduler=None, uploader=None):
        """Define componentes a serem monitorados"""
        if scheduler:
            self.scheduler = scheduler
        if uploader:
            self.uploader = uploader
        self.logger.info("Componentes configurados para monitoramento")
    
    def load_history(self):
        """Carrega histórico de status"""
        try:
            if os.path.exists(self.config['history_file']):
                with open(self.config['history_file'], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Reconstruir objetos SystemStatus
                self.status_history = []
                for item in data.get('history', []):
                    status = SystemStatus(**item)
                    self.status_history.append(status)
                
                # Carregar contadores de erro
                self.error_counts.update(data.get('error_counts', {}))
                
                self.logger.info(f"Histórico carregado: {len(self.status_history)} entradas")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar histórico: {str(e)}")
            self.status_history = []
    
    def save_history(self):
        """Salva histórico de status"""
        try:
            # Limitar tamanho do histórico
            max_entries = self.config['max_history_entries']
            if len(self.status_history) > max_entries:
                self.status_history = self.status_history[-max_entries:]
            
            # Preparar dados para salvar
            data = {
                'last_updated': datetime.now().isoformat(),
                'history': [status.__dict__ for status in self.status_history],
                'error_counts': self.error_counts
            }
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(self.config['history_file']), exist_ok=True)
            
            # Salvar arquivo
            with open(self.config['history_file'], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar histórico: {str(e)}")
    
    def collect_system_metrics(self) -> Dict:
        """Coleta métricas do sistema"""
        try:
            # CPU e memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('.')
            disk_free_gb = disk.free / (1024**3)
            
            # Threads ativas
            active_threads = threading.active_count()
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_free_gb': disk_free_gb,
                'disk_total_gb': disk.total / (1024**3),
                'active_threads': active_threads,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas: {str(e)}")
            return {}
    
    def collect_application_metrics(self) -> Dict:
        """Coleta métricas da aplicação"""
        try:
            metrics = {
                'scheduler_running': False,
                'upload_queue_size': 0,
                'pending_uploads': 0,
                'completed_uploads': 0,
                'failed_uploads': 0,
                'last_upload': None,
                'uploader_authenticated': False,
                'quota_exceeded': False
            }
            
            # Métricas do scheduler
            if self.scheduler:
                status = self.scheduler.get_scheduler_status()
                metrics.update({
                    'scheduler_running': status['is_running'],
                    'upload_queue_size': status['queue_statistics']['total_items'],
                    'pending_uploads': status['queue_statistics']['pending'],
                    'completed_uploads': status['queue_statistics']['completed'],
                    'failed_uploads': status['queue_statistics']['failed'],
                    'next_upload': status.get('next_upload')
                })
            
            # Métricas do uploader
            if self.uploader:
                uploader_stats = self.uploader.get_upload_stats()
                metrics.update({
                    'uploader_authenticated': uploader_stats['service_authenticated'],
                    'quota_exceeded': uploader_stats['quota_exceeded']
                })
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas da aplicação: {str(e)}")
            return {}
    
    def assess_system_health(self, system_metrics: Dict, app_metrics: Dict) -> str:
        """Avalia saúde geral do sistema"""
        try:
            issues = []
            
            # Verificar CPU
            if system_metrics.get('cpu_percent', 0) > self.config['alert_cpu_threshold']:
                issues.append("CPU alta")
            
            # Verificar memória
            if system_metrics.get('memory_percent', 0) > self.config['alert_memory_threshold']:
                issues.append("Memória alta")
            
            # Verificar disco
            if system_metrics.get('disk_free_gb', 0) < self.config['alert_disk_threshold_gb']:
                issues.append("Pouco espaço em disco")
            
            # Verificar aplicação
            if not app_metrics.get('scheduler_running', False):
                issues.append("Scheduler parado")
            
            if app_metrics.get('quota_exceeded', False):
                issues.append("Quota excedida")
            
            if app_metrics.get('failed_uploads', 0) > 3:
                issues.append("Muitos uploads falharam")
            
            # Verificar erros
            total_errors = sum(self.error_counts.values())
            if total_errors > 10:
                issues.append("Muitos erros")
            
            # Determinar status
            if not issues:
                return "HEALTHY"
            elif len(issues) <= 2:
                return "WARNING"
            else:
                return "CRITICAL"
                
        except Exception as e:
            self.logger.error(f"Erro ao avaliar saúde: {str(e)}")
            return "UNKNOWN"
    
    def update_status(self):
        """Atualiza status atual do sistema"""
        try:
            # Coletar métricas
            system_metrics = self.collect_system_metrics()
            app_metrics = self.collect_application_metrics()
            
            # Avaliar saúde
            health = self.assess_system_health(system_metrics, app_metrics)
            
            # Criar novo status
            status = SystemStatus(
                timestamp=datetime.now().isoformat(),
                cpu_percent=system_metrics.get('cpu_percent', 0),
                memory_percent=system_metrics.get('memory_percent', 0),
                disk_free_gb=system_metrics.get('disk_free_gb', 0),
                active_threads=system_metrics.get('active_threads', 0),
                upload_queue_size=app_metrics.get('upload_queue_size', 0),
                last_upload=app_metrics.get('next_upload', ''),
                system_health=health,
                errors_count=sum(self.error_counts.values())
            )
            
            # Atualizar status atual
            self.current_status = status
            
            # Adicionar ao histórico
            self.status_history.append(status)
            
            # Salvar histórico periodicamente
            if len(self.status_history) % 10 == 0:
                self.save_history()
            
            # Log se houver problemas
            if health in ['WARNING', 'CRITICAL']:
                self.logger.warning(f"Sistema com problemas: {health}")
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar status: {str(e)}")
    
    def start_monitoring(self):
        """Inicia monitoramento em thread separada"""
        try:
            if self.is_running:
                self.logger.warning("Monitor já está rodando")
                return
            
            self.is_running = True
            self._stop_event.clear()
            
            # Iniciar thread de monitoramento
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.logger.info("Monitoramento iniciado")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar monitoramento: {str(e)}")
            self.is_running = False
    
    def _monitor_loop(self):
        """Loop principal do monitoramento"""
        self.logger.info("Loop de monitoramento iniciado")
        
        while not self._stop_event.is_set():
            try:
                self.update_status()
                time.sleep(self.config['monitor_interval'])
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {str(e)}")
                time.sleep(10)
        
        # Salvar histórico ao finalizar
        self.save_history()
        self.logger.info("Loop de monitoramento finalizado")
    
    def stop_monitoring(self):
        """Para o monitoramento"""
        try:
            if not self.is_running:
                return
            
            self.logger.info("Parando monitoramento...")
            
            self._stop_event.set()
            self.is_running = False
            
            # Aguardar thread finalizar
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5)
            
            # Salvar histórico final
            self.save_history()
            
            self.logger.info("Monitoramento parado")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar monitoramento: {str(e)}")
    
    def get_dashboard_data(self) -> Dict:
        """Retorna dados para dashboard"""
        try:
            if not self.current_status:
                return {'error': 'Sistema não monitorado'}
            
            # Status atual
            current = self.current_status.__dict__
            
            # Estatísticas recentes (última hora)
            recent_history = [
                s for s in self.status_history[-12:]  # Últimas 12 entradas
                if datetime.fromisoformat(s.timestamp) > datetime.now() - timedelta(hours=1)
            ]
            
            # Métricas de aplicação
            app_metrics = self.collect_application_metrics()
            
            # Tendências
            trends = self._calculate_trends(recent_history)
            
            return {
                'current_status': current,
                'application_metrics': app_metrics,
                'error_counts': self.error_counts,
                'trends': trends,
                'monitoring_info': {
                    'is_running': self.is_running,
                    'history_entries': len(self.status_history),
                    'monitor_interval': self.config['monitor_interval']
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar dashboard: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_trends(self, history: List[SystemStatus]) -> Dict:
        """Calcula tendências baseadas no histórico"""
        if len(history) < 2:
            return {}
        
        try:
            # CPU trend
            cpu_values = [s.cpu_percent for s in history]
            cpu_trend = "rising" if cpu_values[-1] > cpu_values[0] else "falling"
            
            # Memory trend
            mem_values = [s.memory_percent for s in history]
            mem_trend = "rising" if mem_values[-1] > mem_values[0] else "falling"
            
            # Upload queue trend
            queue_values = [s.upload_queue_size for s in history]
            queue_trend = "growing" if queue_values[-1] > queue_values[0] else "shrinking"
            
            return {
                'cpu_trend': cpu_trend,
                'memory_trend': mem_trend,
                'queue_trend': queue_trend,
                'avg_cpu': sum(cpu_values) / len(cpu_values),
                'avg_memory': sum(mem_values) / len(mem_values)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular tendências: {str(e)}")
            return {}
    
    def print_dashboard(self):
        """Imprime dashboard no terminal"""
        try:
            dashboard = self.get_dashboard_data()
            
            if 'error' in dashboard:
                print(f"❌ Erro no dashboard: {dashboard['error']}")
                return
            
            # Limpar tela
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Header
            print("="*60)
            print("🎬 YOUTUBE SHORTS AUTOMATION - DASHBOARD")
            print("Canal: Your_Channel_Name")
            print("="*60)
            
            # Status atual
            current = dashboard['current_status']
            health_emoji = {
                'HEALTHY': '🟢',
                'WARNING': '🟡',
                'CRITICAL': '🔴',
                'UNKNOWN': '⚪'
            }
            
            print(f"\n📊 STATUS DO SISTEMA: {health_emoji.get(current['system_health'], '⚪')} {current['system_health']}")
            print(f"🕐 Atualizado: {datetime.fromisoformat(current['timestamp']).strftime('%H:%M:%S')}")
            
            # Métricas do sistema
            print(f"\n💻 SISTEMA:")
            print(f"   CPU: {current['cpu_percent']:.1f}%")
            print(f"   Memória: {current['memory_percent']:.1f}%")
            print(f"   Disco livre: {current['disk_free_gb']:.1f} GB")
            print(f"   Threads ativas: {current['active_threads']}")
            
            # Métricas da aplicação
            app = dashboard['application_metrics']
            scheduler_status = "🟢 ATIVO" if app.get('scheduler_running') else "🔴 PARADO"
            uploader_status = "🟢 AUTENTICADO" if app.get('uploader_authenticated') else "🔴 NÃO AUTENTICADO"
            
            print(f"\n🤖 APLICAÇÃO:")
            print(f"   Scheduler: {scheduler_status}")
            print(f"   Uploader: {uploader_status}")
            print(f"   Fila de upload: {app.get('upload_queue_size', 0)} itens")
            print(f"   Pendentes: {app.get('pending_uploads', 0)}")
            print(f"   Completados: {app.get('completed_uploads', 0)}")
            print(f"   Falharam: {app.get('failed_uploads', 0)}")
            
            if app.get('quota_exceeded'):
                print(f"   ⚠️  QUOTA EXCEDIDA")
            
            # Próximo upload
            if app.get('next_upload'):
                next_dt = datetime.fromisoformat(app['next_upload'])
                print(f"   📅 Próximo upload: {next_dt.strftime('%d/%m %H:%M')}")
            
            # Erros
            errors = dashboard['error_counts']
            total_errors = sum(errors.values())
            if total_errors > 0:
                print(f"\n❌ ERROS (Total: {total_errors}):")
                for error_type, count in errors.items():
                    if count > 0:
                        print(f"   {error_type}: {count}")
            
            # Rodapé
            print(f"\n{'='*60}")
            print("🔄 Dashboard atualiza a cada 30 segundos")
            print("Pressione Ctrl+C para sair")
            
        except Exception as e:
            print(f"Erro ao exibir dashboard: {str(e)}")
    
    def increment_error(self, error_type: str):
        """Incrementa contador de erro"""
        if error_type in self.error_counts:
            self.error_counts[error_type] += 1
        else:
            self.error_counts['system_errors'] += 1
    
    def reset_error_counts(self):
        """Reseta contadores de erro"""
        self.error_counts = {key: 0 for key in self.error_counts.keys()}
        self.logger.info("Contadores de erro resetados")
    
    def cleanup(self):
        """Limpa recursos do monitor"""
        self.stop_monitoring()
        self.logger.debug("Recursos do monitor limpos")