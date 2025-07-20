#!/usr/bin/env python3
"""
Video Processor Module
Sistema de processamento e validação de vídeos usando MoviePy
Canal: Your_Channel_Name
"""

import os
import logging
import shutil
from typing import Dict, Optional, Tuple
from datetime import datetime

# Imports defensivos com tratamento de erro
try:
    from moviepy import VideoFileClip
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    logging.error(f"MoviePy não disponível: {e}")
    MOVIEPY_AVAILABLE = False
    VideoFileClip = None

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError as e:
    logging.error(f"OpenCV não disponível: {e}")
    OPENCV_AVAILABLE = False
    cv2 = None

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError as e:
    logging.error(f"NumPy não disponível: {e}")
    NUMPY_AVAILABLE = False
    np = None

class VideoProcessor:
    """Classe para processamento e validação de vídeos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_video = None
        self.video_info = {}
        
        # Verificar dependências críticas
        if not MOVIEPY_AVAILABLE:
            raise ImportError("MoviePy é obrigatório para processamento de vídeo")
        if not OPENCV_AVAILABLE:
            self.logger.warning("OpenCV não disponível - algumas funcionalidades limitadas")
        if not NUMPY_AVAILABLE:
            self.logger.warning("NumPy não disponível - processamento matemático limitado")
        
    def load_video(self, video_path: str) -> Optional[Dict]:
        """
        Carrega vídeo e extrai informações técnicas
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            Dict com informações técnicas ou None se falhou
        """
        if not os.path.exists(video_path):
            self.logger.error(f"Arquivo não encontrado: {video_path}")
            return None
            
        try:
            self.logger.info(f"Carregando vídeo: {video_path}")
            
            # Carregar com MoviePy
            self.current_video = VideoFileClip(video_path)
            
            # Extrair informações básicas
            video_info = {
                'path': video_path,
                'filename': os.path.basename(video_path),
                'duration': self.current_video.duration,
                'fps': self.current_video.fps,
                'size': self.current_video.size,  # (width, height)
                'width': self.current_video.w,
                'height': self.current_video.h,
                'aspect_ratio': self.current_video.w / self.current_video.h,
                'has_audio': self.current_video.audio is not None,
                'audio_fps': self.current_video.audio.fps if self.current_video.audio else None,
                'file_size': os.path.getsize(video_path),
                'format': os.path.splitext(video_path)[1].lower(),
                'loaded_at': datetime.now().isoformat()
            }
            
            # Validar informações com OpenCV para mais detalhes
            cv_info = self._get_opencv_info(video_path)
            if cv_info:
                video_info.update(cv_info)
            
            # Validar requisitos mínimos
            validation_result = self._validate_video_requirements(video_info)
            video_info['validation'] = validation_result
            
            self.video_info = video_info
            
            self.logger.info(f"Vídeo carregado: {video_info['duration']:.1f}s, "
                           f"{video_info['width']}x{video_info['height']}, "
                           f"{video_info['fps']:.1f}fps")
            
            return video_info
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar vídeo {video_path}: {str(e)}")
            return None
    
    def _get_opencv_info(self, video_path: str) -> Optional[Dict]:
        """Extrai informações adicionais usando OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                self.logger.warning("OpenCV não conseguiu abrir o vídeo")
                return None
            
            # Informações do OpenCV
            cv_info = {
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'cv_fps': cap.get(cv2.CAP_PROP_FPS),
                'cv_width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'cv_height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fourcc': int(cap.get(cv2.CAP_PROP_FOURCC)),
                'codec': self._fourcc_to_string(int(cap.get(cv2.CAP_PROP_FOURCC)))
            }
            
            cap.release()
            return cv_info
            
        except Exception as e:
            self.logger.warning(f"Erro ao extrair info OpenCV: {str(e)}")
            return None
    
    def _fourcc_to_string(self, fourcc: int) -> str:
        """Converte código FOURCC para string legível"""
        try:
            return "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
        except:
            return "Unknown"
    
    def _validate_video_requirements(self, video_info: Dict) -> Dict:
        """Valida se o vídeo atende aos requisitos mínimos"""
        validation = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': [],
            'shorts_format': self._validate_shorts_format(video_info)
        }
        
        # Validar duração mínima (5 minutos)
        if video_info['duration'] < 300:
            validation['warnings'].append(f"Vídeo curto ({video_info['duration']:.1f}s). Recomendado: ≥5 minutos")
            validation['recommendations'].append("Considere vídeos mais longos para mais opções de shorts")
        
        # Validar resolução mínima (relaxando para testes)
        if video_info['width'] < 480 or video_info['height'] < 360:
            validation['errors'].append(f"Resolução muito baixa: {video_info['width']}x{video_info['height']}")
            validation['is_valid'] = False
        elif video_info['width'] < 720 or video_info['height'] < 480:
            validation['warnings'].append(f"Resolução baixa: {video_info['width']}x{video_info['height']}")
            validation['recommendations'].append("Recomenda-se resolução mínima de 720x480 para melhor qualidade")
        
        # Validar FPS
        if video_info['fps'] < 15:
            validation['warnings'].append(f"FPS baixo: {video_info['fps']}")
            validation['recommendations'].append("Vídeos com FPS ≥24 produzem melhores shorts")
        
        # Validar áudio
        if not video_info['has_audio']:
            validation['warnings'].append("Vídeo sem áudio detectado")
            validation['recommendations'].append("Vídeos com áudio são mais adequados para shorts")
        
        # Validar tamanho do arquivo
        file_size_mb = video_info['file_size'] / (1024 * 1024)
        if file_size_mb > 2000:  # 2GB
            validation['warnings'].append(f"Arquivo grande: {file_size_mb:.1f}MB")
            validation['recommendations'].append("Arquivos menores processam mais rapidamente")
        
        # Validar formato
        supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        if video_info['format'] not in supported_formats:
            validation['warnings'].append(f"Formato {video_info['format']} pode causar problemas")
            validation['recommendations'].append("Formatos recomendados: MP4, AVI, MOV")
        
        # Log dos resultados
        if validation['errors']:
            self.logger.error(f"Vídeo inválido: {'; '.join(validation['errors'])}")
        if validation['warnings']:
            self.logger.warning(f"Avisos: {'; '.join(validation['warnings'])}")
        if validation['recommendations']:
            self.logger.info(f"Recomendações: {'; '.join(validation['recommendations'])}")
        
        return validation
    
    def _validate_shorts_format(self, video_info: Dict) -> Dict:
        """Valida se o vídeo está no formato correto para YouTube Shorts"""
        shorts_validation = {
            'is_shorts_format': False,
            'target_resolution': '1080x1920',
            'target_aspect_ratio': 9/16,
            'current_aspect_ratio': video_info['aspect_ratio'],
            'needs_conversion': False,
            'conversion_type': None,
            'recommendations': []
        }
        
        width, height = video_info['width'], video_info['height']
        aspect_ratio = video_info['aspect_ratio']
        
        # Verificar se é formato vertical (9:16 ou próximo)
        target_ratio = 9/16  # 0.5625
        ratio_tolerance = 0.05  # 5% de tolerância
        
        if abs(aspect_ratio - target_ratio) <= ratio_tolerance:
            # Aspecto correto, verificar resolução
            if width == 1080 and height == 1920:
                shorts_validation['is_shorts_format'] = True
                shorts_validation['recommendations'].append("✅ Formato perfeito para YouTube Shorts!")
            elif width >= 720 and height >= 1280:
                shorts_validation['needs_conversion'] = True
                shorts_validation['conversion_type'] = 'resize'
                shorts_validation['recommendations'].append(f"Resolução {width}x{height} precisa ser ajustada para 1080x1920")
            else:
                shorts_validation['needs_conversion'] = True
                shorts_validation['conversion_type'] = 'upscale'
                shorts_validation['recommendations'].append(f"Resolução baixa {width}x{height} - upscale necessário")
        else:
            # Aspecto incorreto
            if aspect_ratio > 1:  # Landscape
                shorts_validation['needs_conversion'] = True
                shorts_validation['conversion_type'] = 'crop_rotate'
                shorts_validation['recommendations'].append("Vídeo em landscape - precisa ser cortado/rotacionado para 9:16")
            elif aspect_ratio < target_ratio:  # Muito estreito
                shorts_validation['needs_conversion'] = True
                shorts_validation['conversion_type'] = 'letterbox'
                shorts_validation['recommendations'].append("Vídeo muito estreito - adicionar letterbox para 9:16")
            else:  # Próximo mas não exato
                shorts_validation['needs_conversion'] = True
                shorts_validation['conversion_type'] = 'minor_adjust'
                shorts_validation['recommendations'].append("Pequeno ajuste de aspecto necessário")
        
        return shorts_validation
    
    def convert_to_shorts_format(self, output_path: str = None) -> Optional[str]:
        """
        Converte o vídeo atual para o formato YouTube Shorts (1080x1920, 9:16)
        
        Args:
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do arquivo convertido ou None se falhou
        """
        if not self.current_video:
            self.logger.error("Nenhum vídeo carregado para conversão")
            return None
        
        try:
            # Definir caminho de saída
            if not output_path:
                base_name = os.path.splitext(self.video_info['filename'])[0]
                output_path = f"shorts/{base_name}_shorts_format.mp4"
            
            # Criar diretório se necessário
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            self.logger.info(f"Convertendo para formato Shorts: {output_path}")
            
            # Obter informações de formato
            shorts_info = self.video_info['validation']['shorts_format']
            conversion_type = shorts_info['conversion_type']
            
            # Aplicar conversão baseada no tipo necessário
            if conversion_type == 'resize':
                converted_clip = self._resize_to_shorts(self.current_video)
            elif conversion_type == 'crop_rotate':
                converted_clip = self._crop_to_shorts(self.current_video)
            elif conversion_type == 'letterbox':
                converted_clip = self._letterbox_to_shorts(self.current_video)
            elif conversion_type == 'upscale':
                converted_clip = self._upscale_to_shorts(self.current_video)
            else:
                # Conversão padrão - redimensionar
                converted_clip = self._resize_to_shorts(self.current_video)
            
            # Salvar o vídeo convertido
            self.logger.info("Salvando vídeo convertido...")
            converted_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=min(30, self.video_info['fps'])  # Máximo 30fps para Shorts
            )
            
            # Limpar clip temporário
            converted_clip.close()
            
            self.logger.info(f"✅ Conversão concluída: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Erro na conversão para formato Shorts: {str(e)}")
            return None
    
    def _resize_to_shorts(self, clip):
        """Redimensiona o vídeo para 1080x1920 mantendo aspecto"""
        return clip.resized((1080, 1920))
    
    def _crop_to_shorts(self, clip):
        """Corta vídeo landscape para formato vertical 9:16"""
        # Calcular dimensões de corte para 9:16
        current_w, current_h = clip.size
        target_ratio = 9/16
        
        if current_w / current_h > 1/target_ratio:
            # Muito largo - cortar largura
            new_w = int(current_h * target_ratio)
            x_center = current_w // 2
            x1 = x_center - new_w // 2
            x2 = x_center + new_w // 2
            cropped = clip.cropped(x1=x1, x2=x2)
        else:
            # Muito alto - cortar altura
            new_h = int(current_w / target_ratio)
            y_center = current_h // 2
            y1 = y_center - new_h // 2
            y2 = y_center + new_h // 2
            cropped = clip.cropped(y1=y1, y2=y2)
        
        return cropped.resized(newsize=(1080, 1920))
    
    def _letterbox_to_shorts(self, clip):
        """Adiciona letterbox para ajustar vídeo muito estreito"""
        # Redimensionar mantendo aspecto e adicionar letterbox preto
        clip_resized = clip.resized(height=1920)
        if clip_resized.w < 1080:
            # Adicionar barras pretas nas laterais
            from moviepy import ColorClip, CompositeVideoClip
            bg = ColorClip(size=(1080, 1920), color=(0,0,0), duration=clip.duration)
            x_offset = (1080 - clip_resized.w) // 2
            composite = CompositeVideoClip([bg, clip_resized.with_position((x_offset, 0))])
            return composite
        else:
            return clip_resized.resized(newsize=(1080, 1920))
    
    def _upscale_to_shorts(self, clip):
        """Faz upscale de vídeo de baixa resolução"""
        return clip.resized((1080, 1920))
    
    def get_video_preview(self, timestamp: float = None) -> Optional[str]:
        """
        Gera preview (screenshot) do vídeo em timestamp específico
        
        Args:
            timestamp: Tempo em segundos (None = meio do vídeo)
            
        Returns:
            Caminho para o arquivo de preview ou None
        """
        if not self.current_video:
            self.logger.error("Nenhum vídeo carregado")
            return None
            
        try:
            if timestamp is None:
                timestamp = self.current_video.duration / 2
            
            # Garantir que timestamp está dentro dos limites
            timestamp = max(0, min(timestamp, self.current_video.duration - 1))
            
            # Gerar preview
            frame = self.current_video.get_frame(timestamp)
            
            # Salvar preview
            preview_path = f"temp/preview_{os.path.splitext(self.video_info['filename'])[0]}.jpg"
            os.makedirs(os.path.dirname(preview_path), exist_ok=True)
            
            # Converter array numpy para imagem e salvar
            import PIL.Image
            img = PIL.Image.fromarray(frame.astype('uint8'))
            img.save(preview_path, 'JPEG', quality=85)
            
            self.logger.info(f"Preview gerado: {preview_path}")
            return preview_path
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar preview: {str(e)}")
            return None
    
    def analyze_video_segments(self, segment_duration: int = 60) -> list:
        """
        Divide o vídeo em segmentos para análise
        
        Args:
            segment_duration: Duração de cada segmento em segundos
            
        Returns:
            Lista de segmentos com informações
        """
        if not self.current_video:
            self.logger.error("Nenhum vídeo carregado")
            return []
        
        try:
            segments = []
            total_duration = self.current_video.duration
            
            for start_time in range(0, int(total_duration), segment_duration):
                end_time = min(start_time + segment_duration, total_duration)
                
                segment = {
                    'index': len(segments),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'middle_time': start_time + (end_time - start_time) / 2
                }
                
                segments.append(segment)
            
            self.logger.info(f"Vídeo dividido em {len(segments)} segmentos de {segment_duration}s")
            return segments
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar segmentos: {str(e)}")
            return []
    
    def get_video_stats(self) -> Optional[Dict]:
        """Retorna estatísticas detalhadas do vídeo"""
        if not self.current_video or not self.video_info:
            return None
            
        try:
            stats = {
                'basic_info': {
                    'filename': self.video_info['filename'],
                    'duration_formatted': f"{int(self.video_info['duration'] // 60)}:{int(self.video_info['duration'] % 60):02d}",
                    'resolution': f"{self.video_info['width']}x{self.video_info['height']}",
                    'fps': f"{self.video_info['fps']:.1f}",
                    'file_size_mb': f"{self.video_info['file_size'] / (1024*1024):.1f}",
                    'aspect_ratio': f"{self.video_info['aspect_ratio']:.2f}",
                    'has_audio': self.video_info['has_audio']
                },
                'technical_info': {
                    'format': self.video_info['format'],
                    'codec': self.video_info.get('codec', 'Unknown'),
                    'frame_count': self.video_info.get('frame_count', 0),
                    'audio_fps': self.video_info.get('audio_fps')
                },
                'validation': self.video_info['validation'],
                'processing_info': {
                    'loaded_at': self.video_info['loaded_at'],
                    'memory_usage': self._estimate_memory_usage()
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar estatísticas: {str(e)}")
            return None
    
    def _estimate_memory_usage(self) -> str:
        """Estima uso de memória do vídeo carregado"""
        if not self.video_info:
            return "0 MB"
            
        try:
            # Estimativa baseada em resolução, FPS e duração
            pixels_per_frame = self.video_info['width'] * self.video_info['height']
            total_frames = self.video_info['fps'] * self.video_info['duration']
            bytes_estimate = pixels_per_frame * total_frames * 3  # RGB
            mb_estimate = bytes_estimate / (1024 * 1024)
            
            return f"{mb_estimate:.1f} MB"
            
        except:
            return "Unknown"
    
    def cleanup(self):
        """Libera memória e recursos"""
        try:
            if self.current_video:
                self.current_video.close()
                self.current_video = None
                
            self.video_info = {}
            
            # Força garbage collection
            import gc
            gc.collect()
            
            self.logger.info("Recursos de vídeo liberados")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza de recursos: {str(e)}")
    
    def __del__(self):
        """Destrutor - garante limpeza de recursos"""
        self.cleanup()