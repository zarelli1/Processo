#!/usr/bin/env python3
"""
Advanced Logging Configuration
Sistema de logging avançado com rotação e múltiplos níveis
Canal: Your_Channel_Name
"""

import os
import logging
import logging.handlers
from datetime import datetime
from typing import Optional

class AdvancedLogger:
    """Configuração avançada de logging com rotação por data"""
    
    def __init__(self, config: dict = None):
        self.config = config or self._get_default_config()
        self.logger = None
        self.setup_logging()
    
    def _get_default_config(self) -> dict:
        """Configuração padrão de logging"""
        return {
            'level': 'INFO',
            'file': 'logs/automation.log',
            'max_size': '10MB',
            'backup_count': 5,
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'rotation': 'time',  # 'time' ou 'size'
            'when': 'midnight',  # Para rotação por tempo
            'interval': 1,
            'console_output': True
        }
    
    def setup_logging(self):
        """Configura o sistema de logging avançado"""
        try:
            # Criar diretório de logs se não existir
            log_dir = os.path.dirname(self.config['file'])
            os.makedirs(log_dir, exist_ok=True)
            
            # Configurar logger principal
            self.logger = logging.getLogger('YouTubeAutomation')
            self.logger.setLevel(getattr(logging, self.config['level'].upper()))
            
            # Remover handlers existentes para evitar duplicação
            self.logger.handlers.clear()
            
            # Formatter
            formatter = logging.Formatter(
                self.config['format'],
                datefmt=self.config['datefmt']
            )
            
            # Handler para arquivo com rotação
            if self.config['rotation'] == 'time':
                file_handler = logging.handlers.TimedRotatingFileHandler(
                    self.config['file'],
                    when=self.config['when'],
                    interval=self.config['interval'],
                    backupCount=self.config['backup_count'],
                    encoding='utf-8'
                )
            else:
                # Rotação por tamanho
                max_bytes = self._parse_size(self.config['max_size'])
                file_handler = logging.handlers.RotatingFileHandler(
                    self.config['file'],
                    maxBytes=max_bytes,
                    backupCount=self.config['backup_count'],
                    encoding='utf-8'
                )
            
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            # Handler para console (se habilitado)
            if self.config['console_output']:
                console_handler = logging.StreamHandler()
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%H:%M:%S'
                )
                console_handler.setFormatter(console_formatter)
                self.logger.addHandler(console_handler)
            
            # Log inicial
            self.logger.info("="*60)
            self.logger.info("YouTube Shorts Automation - Your_Channel_Name")
            self.logger.info("Sistema de logging iniciado")
            self.logger.info(f"Nível: {self.config['level']}")
            self.logger.info(f"Arquivo: {self.config['file']}")
            self.logger.info(f"Rotação: {self.config['rotation']}")
            self.logger.info("="*60)
            
        except Exception as e:
            print(f"Erro ao configurar logging: {str(e)}")
            raise
    
    def _parse_size(self, size_str: str) -> int:
        """Converte string de tamanho para bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """Retorna logger configurado"""
        if name:
            return logging.getLogger(f'YouTubeAutomation.{name}')
        return self.logger
    
    def log_process_start(self, process_name: str, **kwargs):
        """Log padronizado para início de processo"""
        self.logger.info("="*50)
        self.logger.info(f"INICIANDO: {process_name}")
        for key, value in kwargs.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("="*50)
    
    def log_process_end(self, process_name: str, success: bool = True, **kwargs):
        """Log padronizado para fim de processo"""
        status = "SUCESSO" if success else "ERRO"
        self.logger.info("-"*50)
        self.logger.info(f"FINALIZANDO: {process_name} - {status}")
        for key, value in kwargs.items():
            self.logger.info(f"  {key}: {value}")
        self.logger.info("-"*50)
    
    def log_step(self, step_name: str, step_number: int = None, total_steps: int = None):
        """Log padronizado para etapas de processo"""
        if step_number and total_steps:
            self.logger.info(f"ETAPA {step_number}/{total_steps}: {step_name}")
        else:
            self.logger.info(f"ETAPA: {step_name}")
    
    def log_progress(self, current: int, total: int, item_name: str = "item"):
        """Log de progresso"""
        percentage = (current / total) * 100
        self.logger.info(f"Progresso: {current}/{total} {item_name}s ({percentage:.1f}%)")
    
    def log_error_details(self, error: Exception, context: str = ""):
        """Log detalhado de erros"""
        self.logger.error("*"*60)
        self.logger.error(f"ERRO DETALHADO: {context}")
        self.logger.error(f"Tipo: {type(error).__name__}")
        self.logger.error(f"Mensagem: {str(error)}")
        
        # Stack trace se disponível
        import traceback
        self.logger.error("Stack trace:")
        for line in traceback.format_exc().split('\n'):
            if line.strip():
                self.logger.error(f"  {line}")
        self.logger.error("*"*60)
    
    def log_video_info(self, video_info: dict):
        """Log especializado para informações de vídeo"""
        self.logger.info("INFORMAÇÕES DO VÍDEO:")
        self.logger.info(f"  Título: {video_info.get('title', 'N/A')}")
        self.logger.info(f"  Duração: {video_info.get('duration', 0):.1f}s")
        self.logger.info(f"  Resolução: {video_info.get('width', 0)}x{video_info.get('height', 0)}")
        self.logger.info(f"  FPS: {video_info.get('fps', 0):.1f}")
        self.logger.info(f"  Tamanho: {video_info.get('filesize', 0) / (1024*1024):.1f}MB")
        self.logger.info(f"  Formato: {video_info.get('ext', 'N/A')}")
    
    def log_shorts_creation(self, shorts_info: list):
        """Log especializado para criação de shorts"""
        self.logger.info("SHORTS CRIADOS:")
        for i, short in enumerate(shorts_info, 1):
            self.logger.info(f"  Short {i}:")
            self.logger.info(f"    Arquivo: {short.get('filename', 'N/A')}")
            self.logger.info(f"    Duração: {short.get('duration', 0):.1f}s")
            self.logger.info(f"    Início: {short.get('start_time', 0):.1f}s")
            self.logger.info(f"    Fim: {short.get('end_time', 0):.1f}s")
    
    def log_upload_result(self, upload_result: dict):
        """Log especializado para resultado de upload"""
        status = "SUCESSO" if upload_result.get('success', False) else "ERRO"
        self.logger.info("RESULTADO DO UPLOAD:")
        self.logger.info(f"  Status: {status}")
        self.logger.info(f"  Vídeo ID: {upload_result.get('video_id', 'N/A')}")
        self.logger.info(f"  URL: {upload_result.get('url', 'N/A')}")
        self.logger.info(f"  Título: {upload_result.get('title', 'N/A')}")
        
        if not upload_result.get('success', False):
            self.logger.error(f"  Erro: {upload_result.get('error', 'Erro desconhecido')}")
    
    def log_system_info(self):
        """Log informações do sistema"""
        import platform
        import psutil
        
        self.logger.info("INFORMAÇÕES DO SISTEMA:")
        self.logger.info(f"  OS: {platform.system()} {platform.release()}")
        self.logger.info(f"  Python: {platform.python_version()}")
        self.logger.info(f"  CPU: {psutil.cpu_count()} cores")
        self.logger.info(f"  RAM: {psutil.virtual_memory().total / (1024**3):.1f}GB")
        self.logger.info(f"  Disco livre: {psutil.disk_usage('.').free / (1024**3):.1f}GB")
    
    def create_session_log(self, session_id: str = None):
        """Cria log de sessão específica"""
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_file = f"logs/session_{session_id}.log"
        
        # Handler específico para sessão
        session_handler = logging.FileHandler(session_file, encoding='utf-8')
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        session_handler.setFormatter(formatter)
        
        session_logger = logging.getLogger(f'Session_{session_id}')
        session_logger.addHandler(session_handler)
        session_logger.setLevel(self.logger.level)
        
        session_logger.info(f"Sessão iniciada: {session_id}")
        
        return session_logger, session_file
    
    def cleanup_old_logs(self, max_age_days: int = 30):
        """Remove logs antigos"""
        log_dir = os.path.dirname(self.config['file'])
        if not os.path.exists(log_dir):
            return
        
        current_time = datetime.now()
        removed_count = 0
        
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                file_path = os.path.join(log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                age_days = (current_time - file_time).days
                
                if age_days > max_age_days:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        self.logger.info(f"Log antigo removido: {filename}")
                    except Exception as e:
                        self.logger.error(f"Erro ao remover log {filename}: {str(e)}")
        
        if removed_count > 0:
            self.logger.info(f"Limpeza de logs concluída: {removed_count} arquivos removidos")

# Instância global para facilitar uso
_global_logger = None

def setup_global_logger(config: dict = None) -> AdvancedLogger:
    """Configura logger global"""
    global _global_logger
    _global_logger = AdvancedLogger(config)
    return _global_logger

def get_logger(name: str = None) -> logging.Logger:
    """Retorna logger configurado"""
    if _global_logger is None:
        setup_global_logger()
    return _global_logger.get_logger(name)