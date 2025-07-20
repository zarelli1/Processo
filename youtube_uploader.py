#!/usr/bin/env python3
"""
YouTube Uploader Module
Sistema de upload automático para YouTube com OAuth 2.0
Canal: Leonardo_Zarelli
"""

import os
import json
import logging
import time
import pickle
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import threading

class YouTubeUploader:
    """Classe para upload automático de vídeos no YouTube"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = config or {
            'client_secrets_file': 'config/client_secrets.json',
            'credentials_file': 'config/youtube_credentials.pickle',
            'scopes': ['https://www.googleapis.com/auth/youtube'],
            'api_service_name': 'youtube',
            'api_version': 'v3',
            'default_category': '22',  # People & Blogs
            'default_privacy': 'public',
            'max_retries': 3,
            'retry_delay': 5,
            'chunk_size': 1024 * 1024,  # 1MB chunks
            'rate_limit_delay': 1  # 1 segundo entre uploads
        }
        
        # Estado do uploader
        self.service = None
        self.credentials = None
        self.quota_exceeded = False
        self.last_upload_time = 0
        
        # Lock para thread safety
        self._upload_lock = threading.Lock()
        
        self.logger.info("YouTubeUploader inicializado")
    
    def authenticate(self) -> bool:
        """
        Autentica com a API do YouTube usando OAuth 2.0
        
        Returns:
            True se autenticação bem-sucedida
        """
        try:
            self.logger.info("Iniciando autenticação OAuth 2.0")
            
            # Verificar se já temos credenciais salvas
            if os.path.exists(self.config['credentials_file']):
                self.logger.info("Carregando credenciais salvas")
                with open(self.config['credentials_file'], 'rb') as token:
                    self.credentials = pickle.load(token)
            
            # Se credenciais inválidas ou expiradas, renovar
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.logger.info("Renovando credenciais expiradas")
                    self.credentials.refresh(Request())
                else:
                    self.logger.info("Solicitando nova autenticação")
                    
                    # Verificar se arquivo de secrets existe
                    if not os.path.exists(self.config['client_secrets_file']):
                        raise FileNotFoundError(f"Arquivo de secrets não encontrado: {self.config['client_secrets_file']}")
                    
                    # Criar flow OAuth
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config['client_secrets_file'],
                        self.config['scopes']
                    )
                    
                    # Executar flow local
                    self.credentials = flow.run_local_server(
                        port=8080,
                        open_browser=True,
                        authorization_prompt_message='Por favor, autorize o acesso ao YouTube no navegador...'
                    )
                
                # Salvar credenciais
                with open(self.config['credentials_file'], 'wb') as token:
                    pickle.dump(self.credentials, token)
                
                self.logger.info("Credenciais salvas")
            
            # Criar serviço da API
            self.service = build(
                self.config['api_service_name'],
                self.config['api_version'],
                credentials=self.credentials
            )
            
            # Testar conexão
            self._test_connection()
            
            self.logger.info("Autenticação concluída com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na autenticação: {str(e)}")
            return False
    
    def _test_connection(self):
        """Testa conexão com a API do YouTube"""
        try:
            # Fazer uma chamada simples para testar
            response = self.service.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            channel_title = response['items'][0]['snippet']['title']
            self.logger.info(f"Conectado ao canal: {channel_title}")
            
        except Exception as e:
            self.logger.warning(f"Erro ao testar conexão: {str(e)}")
    
    def _respect_rate_limit(self):
        """Respeita limite de taxa de uploads"""
        with self._upload_lock:
            current_time = time.time()
            time_since_last = current_time - self.last_upload_time
            
            if time_since_last < self.config['rate_limit_delay']:
                sleep_time = self.config['rate_limit_delay'] - time_since_last
                self.logger.debug(f"Rate limiting: aguardando {sleep_time:.1f}s")
                time.sleep(sleep_time)
            
            self.last_upload_time = time.time()
    
    def _upload_with_retry(self, 
                          media_file: MediaFileUpload,
                          video_data: Dict) -> Optional[str]:
        """
        Faz upload com retry em caso de falha
        
        Args:
            media_file: Arquivo de mídia para upload
            video_data: Dados do vídeo (título, descrição, etc.)
            
        Returns:
            ID do vídeo no YouTube ou None se falhou
        """
        for attempt in range(self.config['max_retries']):
            try:
                self.logger.info(f"Tentativa {attempt + 1}/{self.config['max_retries']} de upload")
                
                # Preparar dados do vídeo
                video_body = {
                    'snippet': {
                        'title': video_data['title'],
                        'description': video_data['description'],
                        'tags': video_data.get('tags', []),
                        'categoryId': video_data.get('category', self.config['default_category'])
                    },
                    'status': {
                        'privacyStatus': video_data.get('privacy', self.config['default_privacy']),
                        'selfDeclaredMadeForKids': False
                    }
                }
                
                # Adicionar agendamento se especificado
                if 'publish_at' in video_data and video_data['publish_at']:
                    # Para agendamento, vídeo deve ser privado até a data de publicação
                    video_body['status']['privacyStatus'] = 'private'
                    video_body['status']['publishAt'] = video_data['publish_at']
                    self.logger.info(f"Agendando publicação para: {video_data['publish_at']}")
                
                # Preparar request de inserção
                insert_request = self.service.videos().insert(
                    part='snippet,status',
                    body=video_body,
                    media_body=media_file
                )
                
                # Executar upload com resumable upload
                response = None
                error = None
                
                try:
                    status, response = insert_request.next_chunk()
                    while response is None:
                        status, response = insert_request.next_chunk()
                        if status:
                            progress = int(status.progress() * 100)
                            self.logger.info(f"Upload: {progress}% concluído")
                
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        # Erros temporários do servidor
                        error = f"Erro temporário do servidor: {e.resp.status}"
                    elif e.resp.status == 403:
                        # Quota excedida
                        self.quota_exceeded = True
                        error = "Quota da API excedida"
                        break
                    else:
                        error = f"Erro HTTP: {e}"
                
                if response:
                    video_id = response['id']
                    self.logger.info(f"Upload concluído! Video ID: {video_id}")
                    return video_id
                
                if error:
                    self.logger.warning(f"Erro na tentativa {attempt + 1}: {error}")
                    if attempt < self.config['max_retries'] - 1:
                        delay = self.config['retry_delay'] * (2 ** attempt)  # Backoff exponencial
                        self.logger.info(f"Aguardando {delay}s antes da próxima tentativa")
                        time.sleep(delay)
                
            except Exception as e:
                self.logger.error(f"Erro inesperado na tentativa {attempt + 1}: {str(e)}")
                if attempt < self.config['max_retries'] - 1:
                    time.sleep(self.config['retry_delay'])
        
        self.logger.error("Todas as tentativas de upload falharam")
        return None
    
    def upload_video(self,
                    file_path: str,
                    title: str,
                    description: str,
                    tags: List[str] = None,
                    category: str = None,
                    privacy: str = None,
                    publish_at: str = None) -> Dict:
        """
        Faz upload de um vídeo para o YouTube
        
        Args:
            file_path: Caminho do arquivo de vídeo
            title: Título do vídeo
            description: Descrição do vídeo
            tags: Lista de tags
            category: ID da categoria
            privacy: Status de privacidade
            publish_at: Data/hora de publicação (ISO 8601) para agendamento
            
        Returns:
            Dicionário com resultado do upload
        """
        try:
            self.logger.info(f"Iniciando upload: {os.path.basename(file_path)}")
            
            # Verificar autenticação
            if not self.service:
                if not self.authenticate():
                    raise Exception("Falha na autenticação")
            
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            # Verificar quota
            if self.quota_exceeded:
                raise Exception("Quota da API excedida. Tente novamente amanhã.")
            
            # Respeitar rate limit
            self._respect_rate_limit()
            
            # Preparar dados do vídeo
            video_data = {
                'title': title[:100],  # Limite de 100 caracteres
                'description': description[:5000],  # Limite de 5000 caracteres
                'tags': tags or [],
                'category': category or self.config['default_category'],
                'privacy': privacy or self.config['default_privacy'],
                'publish_at': publish_at  # Agendamento nativo do YouTube
            }
            
            # Preparar arquivo de mídia
            media_file = MediaFileUpload(
                file_path,
                chunksize=self.config['chunk_size'],
                resumable=True,
                mimetype='video/*'
            )
            
            # Fazer upload
            start_time = time.time()
            video_id = self._upload_with_retry(media_file, video_data)
            upload_time = time.time() - start_time
            
            if video_id:
                # Upload bem-sucedido
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                result = {
                    'success': True,
                    'video_id': video_id,
                    'video_url': video_url,
                    'title': title,
                    'file_path': file_path,
                    'file_size_mb': file_size_mb,
                    'upload_time_seconds': upload_time,
                    'uploaded_at': datetime.now().isoformat()
                }
                
                self.logger.info(f"✅ Upload bem-sucedido: {video_url}")
                return result
            else:
                # Upload falhou
                result = {
                    'success': False,
                    'error': 'Upload falhou após todas as tentativas',
                    'title': title,
                    'file_path': file_path,
                    'attempted_at': datetime.now().isoformat()
                }
                
                self.logger.error(f"❌ Upload falhou: {title}")
                return result
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Erro no upload: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'title': title,
                'file_path': file_path,
                'attempted_at': datetime.now().isoformat()
            }
    
    def upload_video_scheduled(self, file_path: str, title: str, description: str = "",
                              tags: List[str] = None, category: str = None,
                              publish_at: str = None) -> Dict:
        """
        Faz upload de vídeo com agendamento direto no YouTube
        
        Args:
            file_path: Caminho para o arquivo de vídeo
            title: Título do vídeo
            description: Descrição do vídeo
            tags: Lista de tags
            category: ID da categoria
            publish_at: Data/hora de publicação no formato ISO 8601 (ex: "2025-07-08T18:00:00Z")
            
        Returns:
            Dicionário com resultado do upload
        """
        try:
            self.logger.info(f"Iniciando upload agendado: {os.path.basename(file_path)}")
            self.logger.info(f"Publicação agendada para: {publish_at}")
            
            # Verificar autenticação
            if not self.service:
                if not self.authenticate():
                    raise Exception("Falha na autenticação")
            
            # Verificar se arquivo existe
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
            
            # Verificar quota
            if self.quota_exceeded:
                raise Exception("Quota da API excedida. Tente novamente amanhã.")
            
            # Respeitar rate limit
            self._respect_rate_limit()
            
            # Preparar dados do vídeo
            video_data = {
                'title': title[:100],  # Limite de 100 caracteres
                'description': description[:5000],  # Limite de 5000 caracteres
                'tags': tags or [],
                'category': category or self.config['default_category'],
                'privacy': 'private',  # Sempre privado para agendamento
                'publish_at': publish_at  # Data de publicação
            }
            
            # Preparar arquivo de mídia
            media_file = MediaFileUpload(
                file_path,
                chunksize=self.config['chunk_size'],
                resumable=True,
                mimetype='video/*'
            )
            
            # Fazer upload
            start_time = time.time()
            video_id = self._upload_with_retry(media_file, video_data)
            upload_time = time.time() - start_time
            
            if video_id:
                # Upload bem-sucedido
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                
                result = {
                    'success': True,
                    'video_id': video_id,
                    'video_url': video_url,
                    'title': title,
                    'file_path': file_path,
                    'file_size_mb': file_size_mb,
                    'upload_time_seconds': upload_time,
                    'uploaded_at': datetime.now().isoformat(),
                    'scheduled_for': publish_at,
                    'status': 'scheduled'
                }
                
                self.logger.info(f"✅ Upload agendado com sucesso: {video_url}")
                self.logger.info(f"📅 Será publicado em: {publish_at}")
                return result
            else:
                # Upload falhou
                result = {
                    'success': False,
                    'error': 'Upload falhou após todas as tentativas',
                    'title': title,
                    'file_path': file_path,
                    'attempted_at': datetime.now().isoformat()
                }
                
                self.logger.error(f"❌ Upload agendado falhou: {title}")
                return result
                
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Erro no upload agendado: {error_msg}")
            
            return {
                'success': False,
                'error': error_msg,
                'title': title,
                'file_path': file_path,
                'attempted_at': datetime.now().isoformat()
            }
    
    def upload_shorts_batch(self, shorts_info: List[Dict]) -> List[Dict]:
        """
        Faz upload de múltiplos shorts
        
        Args:
            shorts_info: Lista com informações dos shorts
            
        Returns:
            Lista com resultados dos uploads
        """
        try:
            self.logger.info(f"Iniciando upload de {len(shorts_info)} shorts")
            
            upload_results = []
            successful_uploads = 0
            
            for i, short_info in enumerate(shorts_info, 1):
                if not short_info.get('created_successfully', False):
                    self.logger.warning(f"Pulando short {i} (não foi criado com sucesso)")
                    continue
                
                self.logger.info(f"Uploading short {i}/{len(shorts_info)}")
                
                # Extrair metadados se disponível
                metadata = short_info.get('metadata', {})
                
                result = self.upload_video(
                    file_path=short_info['output_path'],
                    title=metadata.get('title', short_info.get('title', f'Short {i}')),
                    description=metadata.get('description', ''),
                    tags=metadata.get('tags', []),
                    category=metadata.get('category'),
                    privacy=metadata.get('privacy_status')
                )
                
                upload_results.append(result)
                
                if result['success']:
                    successful_uploads += 1
                    self.logger.info(f"✅ Short {i} uploaded: {result['video_url']}")
                else:
                    self.logger.error(f"❌ Short {i} failed: {result.get('error')}")
                
                # Verificar se quota foi excedida
                if self.quota_exceeded:
                    self.logger.warning("Quota excedida, interrompendo uploads")
                    break
            
            # Resumo do lote
            success_rate = (successful_uploads / len(upload_results)) * 100 if upload_results else 0
            self.logger.info(f"Upload de lote concluído: {successful_uploads}/{len(upload_results)} "
                           f"({success_rate:.1f}% sucesso)")
            
            return upload_results
            
        except Exception as e:
            self.logger.error(f"Erro no upload de lote: {str(e)}")
            return []
    
    def get_quota_status(self) -> Dict:
        """
        Verifica status da quota da API
        
        Returns:
            Dicionário com informações da quota
        """
        try:
            # Fazer uma chamada simples para testar quota
            response = self.service.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            return {
                'quota_available': True,
                'quota_exceeded': False,
                'channel_count': len(response.get('items', [])),
                'checked_at': datetime.now().isoformat()
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                return {
                    'quota_available': False,
                    'quota_exceeded': True,
                    'error': 'Quota excedida',
                    'checked_at': datetime.now().isoformat()
                }
            else:
                return {
                    'quota_available': False,
                    'quota_exceeded': False,
                    'error': f'Erro na API: {e}',
                    'checked_at': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'quota_available': False,
                'quota_exceeded': False,
                'error': str(e),
                'checked_at': datetime.now().isoformat()
            }
    
    def get_upload_stats(self) -> Dict:
        """
        Retorna estatísticas de upload
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'service_authenticated': self.service is not None,
            'quota_exceeded': self.quota_exceeded,
            'last_upload_time': self.last_upload_time,
            'credentials_file_exists': os.path.exists(self.config['credentials_file']),
            'client_secrets_exists': os.path.exists(self.config['client_secrets_file']),
            'rate_limit_delay': self.config['rate_limit_delay'],
            'max_retries': self.config['max_retries']
        }
    
    def reset_quota_status(self):
        """Reseta status de quota (para novo dia)"""
        self.quota_exceeded = False
        self.logger.info("Status de quota resetado")
    
    def cleanup(self):
        """Limpa recursos"""
        if self.service:
            self.service = None
        self.credentials = None
        self.logger.debug("Recursos do uploader limpos")