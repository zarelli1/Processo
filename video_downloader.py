#!/usr/bin/env python3
"""
Video Downloader Module
Sistema de download de vídeos do YouTube usando yt-dlp
Canal: Your_Channel_Name
"""

import os
import re
import logging
import yt_dlp
from typing import Dict, Optional, Callable
from datetime import datetime
from urllib.parse import urlparse, parse_qs

class VideoDownloader:
    """Classe para download de vídeos do YouTube"""
    
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        self.logger = logging.getLogger(__name__)
        self.ensure_download_dir()
        
    def ensure_download_dir(self):
        """Garante que o diretório de download existe"""
        os.makedirs(self.download_dir, exist_ok=True)
        self.logger.info(f"Diretório de download configurado: {self.download_dir}")
    
    def validate_youtube_url(self, url: str) -> bool:
        """Valida se a URL é do YouTube"""
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/v/[\w-]+'
        ]
        
        for pattern in youtube_patterns:
            if re.match(pattern, url):
                self.logger.info(f"URL válida do YouTube: {url}")
                return True
        
        self.logger.error(f"URL inválida do YouTube: {url}")
        return False
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extrai o ID do vídeo da URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                self.logger.info(f"Video ID extraído: {video_id}")
                return video_id
        
        self.logger.error(f"Não foi possível extrair video ID de: {url}")
        return None
    
    def progress_hook(self, d: Dict):
        """Callback para monitorar progresso do download"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.logger.info(f"Download: {percent:.1f}% - {d['filename']}")
            elif '_percent_str' in d:
                self.logger.info(f"Download: {d['_percent_str']} - {d['filename']}")
                
        elif d['status'] == 'finished':
            self.logger.info(f"Download concluído: {d['filename']}")
            
        elif d['status'] == 'error':
            self.logger.error(f"Erro no download: {d.get('error', 'Erro desconhecido')}")
    
    def get_video_info(self, url: str) -> Optional[Dict]:
        """Extrai informações do vídeo sem fazer download"""
        if not self.validate_youtube_url(url):
            return None
            
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                video_info = {
                    'id': info.get('id'),
                    'title': info.get('title', 'Título não disponível'),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'format_id': info.get('format_id', ''),
                    'ext': info.get('ext', 'mp4'),
                    'filesize': info.get('filesize', 0),
                    'fps': info.get('fps', 30),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0)
                }
                
                self.logger.info(f"Informações extraídas: {video_info['title']} ({video_info['duration']}s)")
                return video_info
                
        except Exception as e:
            self.logger.error(f"Erro ao extrair informações do vídeo: {str(e)}")
            return None
    
    def download_video(self, url: str, progress_callback: Optional[Callable] = None) -> Optional[Dict]:
        """
        Faz download do vídeo e retorna informações completas
        
        Args:
            url: URL do vídeo YouTube
            progress_callback: Função callback para progresso (opcional)
            
        Returns:
            Dict com informações do vídeo baixado ou None se falhou
        """
        if not self.validate_youtube_url(url):
            return None
        
        # Configurações do yt-dlp
        ydl_opts = {
            'format': 'best[height<=1080]',  # Máximo 1080p
            'outtmpl': os.path.join(self.download_dir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_callback or self.progress_hook],
            'extract_flat': False,
            'writeinfojson': True,  # Salva metadados em JSON
            'writethumbnail': True,  # Baixa thumbnail
        }
        
        try:
            self.logger.info(f"Iniciando download: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extrai informações primeiro
                info = ydl.extract_info(url, download=False)
                
                # Validações antes do download
                duration = info.get('duration', 0)
                if duration < 300:  # Menos de 5 minutos
                    self.logger.warning(f"Vídeo muito curto ({duration}s), pode não ser adequado para shorts")
                
                # Faz o download
                ydl.download([url])
                
                # Monta informações de retorno
                # Usar o filename real que foi baixado
                actual_filename = ydl.prepare_filename(info)
                
                video_data = {
                    'id': info.get('id'),
                    'title': info.get('title', 'Título não disponível'),
                    'description': info.get('description', ''),
                    'duration': duration,
                    'view_count': info.get('view_count', 0),
                    'uploader': info.get('uploader', ''),
                    'upload_date': info.get('upload_date', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'webpage_url': info.get('webpage_url', url),
                    'fps': info.get('fps', 30),
                    'width': info.get('width', 0),
                    'height': info.get('height', 0),
                    'filesize': info.get('filesize', 0),
                    'ext': info.get('ext', 'mp4'),
                    'filename': actual_filename,
                    'local_path': actual_filename,  # Usar o filename real
                    'download_date': datetime.now().isoformat(),
                    'success': True
                }
                
                self.logger.info(f"Download concluído com sucesso: {video_data['title']}")
                return video_data
                
        except yt_dlp.DownloadError as e:
            if "Private video" in str(e):
                self.logger.error(f"Vídeo privado ou não disponível: {url}")
            elif "Copyright" in str(e):
                self.logger.error(f"Vídeo com restrições de copyright: {url}")
            elif "Video unavailable" in str(e):
                self.logger.error(f"Vídeo não disponível: {url}")
            else:
                self.logger.error(f"Erro no download: {str(e)}")
            return None
            
        except Exception as e:
            self.logger.error(f"Erro inesperado durante download: {str(e)}")
            return None
    
    def find_downloaded_video(self, title: str, video_id: str = None) -> Optional[str]:
        """
        Procura arquivo de vídeo baixado no diretório, mesmo com caracteres especiais
        
        Args:
            title: Título do vídeo
            video_id: ID do vídeo (opcional)
            
        Returns:
            Caminho do arquivo encontrado ou None
        """
        if not os.path.exists(self.download_dir):
            return None
        
        # Procurar arquivos MP4 no diretório
        for filename in os.listdir(self.download_dir):
            if filename.endswith('.mp4'):
                file_path = os.path.join(self.download_dir, filename)
                
                # Verificar se o título está contido no nome do arquivo
                # Remover caracteres especiais para comparação
                clean_title = re.sub(r'[^\w\s-]', '', title.lower())
                clean_filename = re.sub(r'[^\w\s-]', '', filename.lower())
                
                if clean_title in clean_filename or (video_id and video_id in filename):
                    self.logger.info(f"Arquivo encontrado: {filename}")
                    return file_path
        
        self.logger.warning(f"Arquivo não encontrado para título: {title}")
        return None

    def cleanup_downloads(self, max_age_days: int = 7):
        """Remove downloads antigos para economizar espaço"""
        if not os.path.exists(self.download_dir):
            return
            
        current_time = datetime.now()
        removed_count = 0
        
        for filename in os.listdir(self.download_dir):
            file_path = os.path.join(self.download_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                age_days = (current_time - file_time).days
                
                if age_days > max_age_days:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                        self.logger.info(f"Removido arquivo antigo: {filename}")
                    except Exception as e:
                        self.logger.error(f"Erro ao remover {filename}: {str(e)}")
        
        if removed_count > 0:
            self.logger.info(f"Limpeza concluída: {removed_count} arquivos removidos")
        else:
            self.logger.info("Nenhum arquivo antigo para remover")