#!/usr/bin/env python3
"""
Upload Scheduler Module
Sistema de agendamento automático para uploads de shorts
Canal: Leonardo_Zarelli
"""

import os
import json
import logging
import schedule
import time
import threading
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

class UploadStatus(Enum):
    """Estados possíveis de um upload"""
    PENDING = "pending"
    SCHEDULED = "scheduled"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class UploadItem:
    """Item da fila de upload"""
    id: str
    file_path: str
    title: str
    description: str
    tags: List[str]
    scheduled_time: str  # ISO format
    status: UploadStatus
    metadata: Dict
    attempts: int = 0
    max_attempts: int = 3
    created_at: str = ""
    last_attempt_at: str = ""
    completed_at: str = ""
    error_message: str = ""
    video_id: str = ""
    video_url: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()

class UploadQueue:
    """Gerenciador de fila de uploads com persistência"""
    
    def __init__(self, queue_file: str = "temp/upload_queue.json"):
        self.queue_file = queue_file
        self.queue: List[UploadItem] = []
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        
        # Carregar fila existente
        self.load_queue()
        
        self.logger.info("UploadQueue inicializada")
    
    def load_queue(self):
        """Carrega fila do arquivo JSON"""
        try:
            if os.path.exists(self.queue_file):
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.queue = []
                for item_data in data.get('items', []):
                    # Converter status de string para enum
                    item_data['status'] = UploadStatus(item_data['status'])
                    item = UploadItem(**item_data)
                    self.queue.append(item)
                
                self.logger.info(f"Fila carregada: {len(self.queue)} itens")
            else:
                self.queue = []
                self.logger.info("Nova fila criada")
                
        except Exception as e:
            self.logger.error(f"Erro ao carregar fila: {str(e)}")
            self.queue = []
    
    def save_queue(self):
        """Salva fila no arquivo JSON"""
        try:
            with self._lock:
                # Converter para formato serializável
                queue_data = {
                    'saved_at': datetime.now().isoformat(),
                    'items': [
                        {**asdict(item), 'status': item.status.value}
                        for item in self.queue
                    ]
                }
                
                # Criar diretório se não existir
                os.makedirs(os.path.dirname(self.queue_file), exist_ok=True)
                
                # Salvar arquivo
                with open(self.queue_file, 'w', encoding='utf-8') as f:
                    json.dump(queue_data, f, indent=2, ensure_ascii=False)
                
                self.logger.debug("Fila salva")
                
        except Exception as e:
            self.logger.error(f"Erro ao salvar fila: {str(e)}")
    
    def add_item(self, 
                file_path: str,
                title: str,
                description: str,
                tags: List[str],
                scheduled_time: datetime,
                metadata: Dict = None) -> str:
        """
        Adiciona item à fila
        
        Args:
            file_path: Caminho do arquivo
            title: Título do vídeo
            description: Descrição
            tags: Lista de tags
            scheduled_time: Horário agendado
            metadata: Metadados adicionais
            
        Returns:
            ID do item adicionado
        """
        try:
            # Gerar ID único
            item_id = f"upload_{int(time.time())}_{len(self.queue)}"
            
            # Criar item
            item = UploadItem(
                id=item_id,
                file_path=file_path,
                title=title,
                description=description,
                tags=tags or [],
                scheduled_time=scheduled_time.isoformat(),
                status=UploadStatus.PENDING,
                metadata=metadata or {}
            )
            
            with self._lock:
                self.queue.append(item)
                self.save_queue()
            
            self.logger.info(f"Item adicionado à fila: {title} (agendado para {scheduled_time})")
            return item_id
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar item: {str(e)}")
            return ""
    
    def get_pending_items(self, limit_time: datetime = None) -> List[UploadItem]:
        """
        Retorna itens pendentes até determinado horário
        
        Args:
            limit_time: Horário limite (default: agora)
            
        Returns:
            Lista de itens pendentes
        """
        if limit_time is None:
            limit_time = datetime.now()
        
        pending_items = []
        
        with self._lock:
            for item in self.queue:
                if item.status in [UploadStatus.PENDING, UploadStatus.SCHEDULED]:
                    scheduled_dt = datetime.fromisoformat(item.scheduled_time)
                    if scheduled_dt <= limit_time:
                        pending_items.append(item)
        
        return pending_items
    
    def update_item_status(self, 
                          item_id: str, 
                          status: UploadStatus,
                          error_message: str = "",
                          video_id: str = "",
                          video_url: str = ""):
        """
        Atualiza status de um item
        
        Args:
            item_id: ID do item
            status: Novo status
            error_message: Mensagem de erro (se aplicável)
            video_id: ID do vídeo no YouTube
            video_url: URL do vídeo
        """
        try:
            with self._lock:
                for item in self.queue:
                    if item.id == item_id:
                        item.status = status
                        item.last_attempt_at = datetime.now().isoformat()
                        
                        if status == UploadStatus.UPLOADING:
                            item.attempts += 1
                        elif status == UploadStatus.COMPLETED:
                            item.completed_at = datetime.now().isoformat()
                            item.video_id = video_id
                            item.video_url = video_url
                        elif status == UploadStatus.FAILED:
                            item.error_message = error_message
                        
                        self.save_queue()
                        
                        self.logger.info(f"Item {item_id} atualizado: {status.value}")
                        return
                
                self.logger.warning(f"Item não encontrado: {item_id}")
                
        except Exception as e:
            self.logger.error(f"Erro ao atualizar item: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas da fila"""
        stats = {
            'total_items': len(self.queue),
            'pending': 0,
            'scheduled': 0,
            'uploading': 0,
            'completed': 0,
            'failed': 0,
            'retrying': 0
        }
        
        with self._lock:
            for item in self.queue:
                stats[item.status.value] += 1
        
        return stats
    
    def cleanup_completed(self, older_than_days: int = 7):
        """Remove itens completados mais antigos que X dias"""
        try:
            cutoff_time = datetime.now() - timedelta(days=older_than_days)
            
            with self._lock:
                original_count = len(self.queue)
                
                self.queue = [
                    item for item in self.queue
                    if not (
                        item.status == UploadStatus.COMPLETED and
                        item.completed_at and
                        datetime.fromisoformat(item.completed_at) < cutoff_time
                    )
                ]
                
                removed_count = original_count - len(self.queue)
                
                if removed_count > 0:
                    self.save_queue()
                    self.logger.info(f"Removidos {removed_count} itens completados antigos")
                    
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {str(e)}")

class UploadScheduler:
    """Sistema de agendamento de uploads"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = config or {
            'upload_time': '09:00',
            'timezone': 'America/Sao_Paulo',
            'daily_uploads': True,
            'max_concurrent_uploads': 1,
            'check_interval': 60,  # segundos
            'retry_failed_uploads': True,
            'retry_delay_hours': 4
        }
        
        # Componentes
        self.queue = UploadQueue()
        self.uploader = None  # Será definido posteriormente
        
        # Estado do scheduler
        self.is_running = False
        self.scheduler_thread = None
        self._stop_event = threading.Event()
        
        self.logger.info("UploadScheduler inicializado")
    
    def set_uploader(self, uploader):
        """Define o uploader a ser usado"""
        self.uploader = uploader
        self.logger.info("Uploader configurado")
    
    def schedule_shorts(self, 
                       shorts_info: List[Dict], 
                       start_date: datetime = None,
                       upload_time: str = None,
                       days_duration: int = 7,
                       videos_per_day: int = 3,
                       daily_times: List[str] = None) -> List[str]:
        """
        Agenda lista de shorts para upload com múltiplos horários diários
        
        Args:
            shorts_info: Lista de informações dos shorts
            start_date: Data de início (default: amanhã)
            upload_time: Horário de upload (backward compatibility)
            days_duration: Duração em dias do agendamento
            videos_per_day: Quantidade de vídeos por dia
            daily_times: Lista de horários diários ['08:00', '12:00', '18:30']
            
        Returns:
            Lista de IDs dos itens agendados
        """
        try:
            if start_date is None:
                start_date = datetime.now() + timedelta(days=1)
            
            # Configuração dos horários diários
            if daily_times is None:
                if upload_time:
                    # Backward compatibility - usar horário único
                    daily_times = [upload_time]
                    videos_per_day = 1
                else:
                    # Novos horários padrão
                    daily_times = ['08:00', '12:00', '18:30']
            
            # Validar que temos horários suficientes
            if len(daily_times) < videos_per_day:
                self.logger.warning(f"Apenas {len(daily_times)} horários para {videos_per_day} vídeos/dia")
                videos_per_day = len(daily_times)
            
            scheduled_ids = []
            successful_shorts = [s for s in shorts_info if s.get('created_successfully', False)]
            
            total_slots = days_duration * videos_per_day
            videos_to_schedule = min(len(successful_shorts), total_slots)
            
            self.logger.info(f"Agendando {videos_to_schedule} shorts:")
            self.logger.info(f"  • Período: {days_duration} dias")
            self.logger.info(f"  • Vídeos/dia: {videos_per_day}")
            self.logger.info(f"  • Horários: {', '.join(daily_times[:videos_per_day])}")
            self.logger.info(f"  • Início: {start_date.date()}")
            
            video_index = 0
            
            for day in range(days_duration):
                if video_index >= len(successful_shorts):
                    break
                    
                current_date = start_date + timedelta(days=day)
                
                for time_slot in range(videos_per_day):
                    if video_index >= len(successful_shorts):
                        break
                        
                    # Obter horário para este slot
                    time_str = daily_times[time_slot % len(daily_times)]
                    hour, minute = map(int, time_str.split(':'))
                    
                    # Calcular datetime do agendamento
                    upload_datetime = current_date.replace(
                        hour=hour,
                        minute=minute,
                        second=0,
                        microsecond=0
                    )
                    
                    # Obter informações do short
                    short_info = successful_shorts[video_index]
                    metadata = short_info.get('metadata', {})
                    
                    # Adicionar à fila
                    item_id = self.queue.add_item(
                        file_path=short_info['output_path'],
                        title=metadata.get('title', short_info.get('title', f'Short {video_index+1}')),
                        description=metadata.get('description', ''),
                        tags=metadata.get('tags', []),
                        scheduled_time=upload_datetime,
                        metadata={
                            **metadata,
                            'day_number': day + 1,
                            'time_slot': time_slot + 1,
                            'scheduled_time_str': time_str
                        }
                    )
                    
                    if item_id:
                        scheduled_ids.append(item_id)
                        self.logger.info(f"📅 Dia {day+1}, Slot {time_slot+1}: {upload_datetime.strftime('%d/%m/%Y %H:%M')}")
                    
                    video_index += 1
            
            self.logger.info(f"Agendamento concluído: {len(scheduled_ids)} shorts na fila")
            
            if video_index < len(successful_shorts):
                remaining = len(successful_shorts) - video_index
                self.logger.warning(f"⚠️ {remaining} shorts não foram agendados (excederam o período configurado)")
            
            return scheduled_ids
            
        except Exception as e:
            self.logger.error(f"Erro no agendamento: {str(e)}")
            return []
    
    def process_pending_uploads(self):
        """Processa uploads pendentes"""
        try:
            pending_items = self.queue.get_pending_items()
            
            if not pending_items:
                return
            
            self.logger.info(f"Processando {len(pending_items)} uploads pendentes")
            
            for item in pending_items:
                if self._stop_event.is_set():
                    break
                
                # Verificar se arquivo ainda existe
                if not os.path.exists(item.file_path):
                    self.queue.update_item_status(
                        item.id, 
                        UploadStatus.FAILED, 
                        error_message="Arquivo não encontrado"
                    )
                    continue
                
                # Verificar se já excedeu tentativas
                if item.attempts >= item.max_attempts:
                    self.queue.update_item_status(
                        item.id, 
                        UploadStatus.FAILED, 
                        error_message="Máximo de tentativas excedido"
                    )
                    continue
                
                # Fazer upload
                self._upload_item(item)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar uploads: {str(e)}")
    
    def _upload_item(self, item: UploadItem):
        """Faz upload de um item específico"""
        try:
            if not self.uploader:
                raise Exception("Uploader não configurado")
            
            self.logger.info(f"Iniciando upload: {item.title}")
            
            # Atualizar status para uploading
            self.queue.update_item_status(item.id, UploadStatus.UPLOADING)
            
            # Fazer upload
            result = self.uploader.upload_video(
                file_path=item.file_path,
                title=item.title,
                description=item.description,
                tags=item.tags,
                category=item.metadata.get('category'),
                privacy=item.metadata.get('privacy_status')
            )
            
            # Atualizar status baseado no resultado
            if result['success']:
                self.queue.update_item_status(
                    item.id,
                    UploadStatus.COMPLETED,
                    video_id=result.get('video_id', ''),
                    video_url=result.get('video_url', '')
                )
                self.logger.info(f"✅ Upload concluído: {result.get('video_url')}")
                
                # 🗑️ Apagar arquivo após upload bem-sucedido
                try:
                    if os.path.exists(item.file_path):
                        os.remove(item.file_path)
                        self.logger.info(f"🗑️ Arquivo removido após upload: {os.path.basename(item.file_path)}")
                except Exception as e:
                    self.logger.warning(f"⚠️ Erro ao remover arquivo {item.file_path}: {str(e)}")
            else:
                error_msg = result.get('error', 'Erro desconhecido')
                
                # Decidir se deve tentar novamente
                if item.attempts < item.max_attempts and "quota" not in error_msg.lower():
                    self.queue.update_item_status(
                        item.id,
                        UploadStatus.RETRYING,
                        error_message=error_msg
                    )
                    self.logger.warning(f"⚠️ Upload falhou, tentando novamente: {error_msg}")
                else:
                    self.queue.update_item_status(
                        item.id,
                        UploadStatus.FAILED,
                        error_message=error_msg
                    )
                    self.logger.error(f"❌ Upload falhou definitivamente: {error_msg}")
                    
        except Exception as e:
            error_msg = str(e)
            self.queue.update_item_status(
                item.id,
                UploadStatus.FAILED,
                error_message=error_msg
            )
            self.logger.error(f"Erro no upload: {error_msg}")
    
    def start_scheduler(self):
        """Inicia o scheduler em thread separada"""
        try:
            if self.is_running:
                self.logger.warning("Scheduler já está rodando")
                return
            
            self.is_running = True
            self._stop_event.clear()
            
            # Configurar schedule
            schedule.every(self.config['check_interval']).seconds.do(self.process_pending_uploads)
            
            # Configurar limpeza diária
            schedule.every().day.at("02:00").do(self.queue.cleanup_completed)
            
            # Iniciar thread
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.logger.info("Scheduler iniciado")
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar scheduler: {str(e)}")
            self.is_running = False
    
    def _run_scheduler(self):
        """Loop principal do scheduler"""
        self.logger.info("Loop do scheduler iniciado")
        
        while not self._stop_event.is_set():
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Erro no loop do scheduler: {str(e)}")
                time.sleep(10)
        
        self.logger.info("Loop do scheduler finalizado")
    
    def stop_scheduler(self):
        """Para o scheduler"""
        try:
            if not self.is_running:
                return
            
            self.logger.info("Parando scheduler...")
            
            self._stop_event.set()
            self.is_running = False
            
            # Aguardar thread finalizar
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            # Limpar schedule
            schedule.clear()
            
            self.logger.info("Scheduler parado")
            
        except Exception as e:
            self.logger.error(f"Erro ao parar scheduler: {str(e)}")
    
    def get_scheduler_status(self) -> Dict:
        """Retorna status do scheduler"""
        queue_stats = self.queue.get_statistics()
        
        next_upload = None
        upcoming_uploads = []
        pending_items = self.queue.get_pending_items()
        
        if pending_items:
            # Próximo upload
            next_item = min(pending_items, key=lambda x: x.scheduled_time)
            next_upload = next_item.scheduled_time
            
            # Próximos 5 uploads
            sorted_items = sorted(pending_items, key=lambda x: x.scheduled_time)[:5]
            for item in sorted_items:
                upload_dt = datetime.fromisoformat(item.scheduled_time)
                upcoming_uploads.append({
                    'title': item.title,
                    'scheduled_time': item.scheduled_time,
                    'formatted_time': upload_dt.strftime('%d/%m/%Y %H:%M'),
                    'day_number': item.metadata.get('day_number'),
                    'time_slot': item.metadata.get('time_slot')
                })
        
        return {
            'is_running': self.is_running,
            'uploader_configured': self.uploader is not None,
            'queue_statistics': queue_stats,
            'next_upload': next_upload,
            'upcoming_uploads': upcoming_uploads,
            'check_interval': self.config['check_interval'],
            'upload_time': self.config.get('upload_time', 'Multiple times')
        }
    
    def cleanup(self):
        """Limpa recursos do scheduler"""
        self.stop_scheduler()
        if hasattr(self, 'queue'):
            self.queue.save_queue()
        self.logger.debug("Recursos do scheduler limpos")