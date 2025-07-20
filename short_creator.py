#!/usr/bin/env python3
"""
Short Creator Module
Sistema de criação automática de shorts com formatação profissional
Canal: Leonardo_Zarelli
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from moviepy import (
    VideoFileClip, TextClip, CompositeVideoClip, 
    concatenate_videoclips, vfx, afx
)
# check_dependencies não existe no MoviePy 2.x+
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

class ShortCreator:
    """Classe para criação automática de shorts formatados"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações padrão
        self.config = config or {
            'output_resolution': (1080, 1920),  # 9:16 vertical
            'target_duration_range': (30, 60),  # 30-60 segundos
            'video_codec': 'libx264',
            'audio_codec': 'aac',
            'video_bitrate': '2M',
            'audio_bitrate': '128k',
            'fps': None,  # Manter FPS original
            'intro_duration': 3.0,  # Duração da intro em segundos
            'outro_duration': 3.0,   # Duração das hashtags
            'text_font_size': 60,
            'text_color': 'white',
            'text_stroke_color': 'black',
            'text_stroke_width': 3,
            'fade_duration': 0.5
        }
        
        # Verificar dependências
        self._check_moviepy_dependencies()
        
        self.logger.info("ShortCreator inicializado")
    
    def _check_moviepy_dependencies(self):
        """Verifica se as dependências do MoviePy estão disponíveis"""
        try:
            check_dependencies()
            self.logger.info("Dependências do MoviePy verificadas")
        except Exception as e:
            self.logger.warning(f"Algumas dependências podem estar faltando: {str(e)}")
    
    def extract_segment(self, video_path: str, start_time: float, end_time: float) -> VideoFileClip:
        """
        Extrai segmento específico do vídeo
        
        Args:
            video_path: Caminho do vídeo original
            start_time: Tempo de início em segundos
            end_time: Tempo de fim em segundos
            
        Returns:
            VideoFileClip do segmento extraído
        """
        try:
            self.logger.debug(f"Extraindo segmento: {start_time:.1f}s - {end_time:.1f}s")
            
            # Carregar vídeo
            video = VideoFileClip(video_path)
            
            # Validar tempos
            max_duration = video.duration
            start_time = max(0, min(start_time, max_duration - 1))
            end_time = max(start_time + 1, min(end_time, max_duration))
            
            # Extrair segmento
            segment = video.subclip(start_time, end_time)
            
            self.logger.debug(f"Segmento extraído: {segment.duration:.1f}s")
            return segment
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair segmento: {str(e)}")
            raise
    
    def crop_to_vertical(self, video_clip: VideoFileClip) -> VideoFileClip:
        """
        Converte vídeo para formato vertical 9:16 com crop inteligente
        
        Args:
            video_clip: Clip de vídeo original
            
        Returns:
            VideoFileClip no formato 9:16
        """
        try:
            # Obter dimensões originais
            original_width, original_height = video_clip.size
            target_width, target_height = self.config['output_resolution']
            
            self.logger.debug(f"Conversão: {original_width}x{original_height} -> {target_width}x{target_height}")
            
            # Calcular aspect ratios
            original_ratio = original_width / original_height
            target_ratio = target_width / target_height
            
            if original_ratio > target_ratio:
                # Vídeo muito largo - crop horizontal
                new_width = int(original_height * target_ratio)
                x_offset = (original_width - new_width) // 2
                
                # Crop mantendo o centro
                cropped = video_clip.crop(x1=x_offset, x2=x_offset + new_width)
                
            else:
                # Vídeo muito alto - crop vertical
                new_height = int(original_width / target_ratio)
                y_offset = (original_height - new_height) // 3  # Foco no terço superior
                
                # Crop mantendo foco no terço superior
                cropped = video_clip.crop(y1=y_offset, y2=y_offset + new_height)
            
            # Redimensionar para resolução final
            resized = cropped.resize(self.config['output_resolution'])
            
            self.logger.debug("Conversão para formato vertical concluída")
            return resized
            
        except Exception as e:
            self.logger.error(f"Erro na conversão vertical: {str(e)}")
            raise
    
    def create_intro_text(self, part_number: int, total_parts: int = 7) -> TextClip:
        """
        Cria texto de introdução "Parte X/7"
        
        Args:
            part_number: Número da parte (1-7)
            total_parts: Total de partes
            
        Returns:
            TextClip com texto de introdução
        """
        try:
            intro_text = f"Parte {part_number}/{total_parts}"
            
            # Criar texto com formatação
            text_clip = TextClip(
                intro_text,
                fontsize=self.config['text_font_size'],
                color=self.config['text_color'],
                font='Arial-Bold',
                stroke_color=self.config['text_stroke_color'],
                stroke_width=self.config['text_stroke_width']
            ).set_duration(self.config['intro_duration'])
            
            # Posicionar no topo
            text_clip = text_clip.set_position(('center', 50))
            
            # Adicionar fade in/out
            text_clip = text_clip.fadein(self.config['fade_duration']).fadeout(self.config['fade_duration'])
            
            self.logger.debug(f"Texto de intro criado: {intro_text}")
            return text_clip
            
        except Exception as e:
            self.logger.error(f"Erro ao criar intro: {str(e)}")
            raise
    
    def create_hashtag_text(self, hashtags: List[str]) -> TextClip:
        """
        Cria texto de hashtags para o rodapé
        
        Args:
            hashtags: Lista de hashtags
            
        Returns:
            TextClip com hashtags
        """
        try:
            # Limitar hashtags e formatar
            max_hashtags = 5
            hashtag_text = " ".join(hashtags[:max_hashtags])
            
            # Criar texto
            text_clip = TextClip(
                hashtag_text,
                fontsize=self.config['text_font_size'] - 10,  # Menor que intro
                color=self.config['text_color'],
                font='Arial',
                stroke_color=self.config['text_stroke_color'],
                stroke_width=self.config['text_stroke_width'] - 1
            ).set_duration(self.config['outro_duration'])
            
            # Posicionar no rodapé
            text_clip = text_clip.set_position(('center', 'bottom')).set_margin(bottom=50)
            
            # Adicionar fade in/out
            text_clip = text_clip.fadein(self.config['fade_duration']).fadeout(self.config['fade_duration'])
            
            self.logger.debug(f"Texto de hashtags criado: {hashtag_text}")
            return text_clip
            
        except Exception as e:
            self.logger.error(f"Erro ao criar hashtags: {str(e)}")
            raise
    
    def add_professional_formatting(self, 
                                  video_clip: VideoFileClip,
                                  part_number: int,
                                  hashtags: List[str]) -> VideoFileClip:
        """
        Adiciona formatação profissional ao short
        
        Args:
            video_clip: Clip de vídeo base
            part_number: Número da parte
            hashtags: Lista de hashtags
            
        Returns:
            VideoFileClip com formatação aplicada
        """
        try:
            self.logger.debug("Aplicando formatação profissional")
            
            # Criar elementos de texto
            intro_text = self.create_intro_text(part_number)
            hashtag_text = self.create_hashtag_text(hashtags)
            
            # Posicionar texto de intro no início
            intro_text = intro_text.set_start(0)
            
            # Posicionar hashtags no final
            hashtag_text = hashtag_text.set_start(video_clip.duration - self.config['outro_duration'])
            
            # Compor vídeo final
            final_video = CompositeVideoClip([
                video_clip,
                intro_text,
                hashtag_text
            ])
            
            self.logger.debug("Formatação profissional aplicada")
            return final_video
            
        except Exception as e:
            self.logger.error(f"Erro na formatação: {str(e)}")
            raise
    
    def optimize_quality(self, video_clip: VideoFileClip) -> VideoFileClip:
        """
        Otimiza qualidade do vídeo para shorts
        
        Args:
            video_clip: Clip de vídeo original
            
        Returns:
            VideoFileClip otimizado
        """
        try:
            self.logger.debug("Otimizando qualidade do vídeo")
            
            # Aplicar filtros de melhoria se necessário
            optimized = video_clip
            
            # Ajustar FPS se configurado
            if self.config['fps'] and self.config['fps'] != video_clip.fps:
                optimized = optimized.set_fps(self.config['fps'])
            
            # Aplicar suavização se necessário
            # optimized = optimized.fx(vfx.blur, 0.5)  # Blur muito leve se necessário
            
            self.logger.debug("Otimização de qualidade concluída")
            return optimized
            
        except Exception as e:
            self.logger.error(f"Erro na otimização: {str(e)}")
            return video_clip  # Retornar original em caso de erro
    
    def create_short(self,
                    video_path: str,
                    segment: Dict,
                    part_number: int,
                    title: str,
                    hashtags: List[str],
                    output_dir: str = "shorts") -> Dict:
        """
        Cria um short completo com formatação profissional
        
        Args:
            video_path: Caminho do vídeo original
            segment: Dicionário com start_time, end_time, etc.
            part_number: Número da parte (1-7)
            title: Título base do vídeo
            hashtags: Lista de hashtags
            output_dir: Diretório de saída
            
        Returns:
            Dicionário com informações do short criado
        """
        try:
            self.logger.info(f"Criando short {part_number}/7: {segment['start_time']:.1f}s-{segment['end_time']:.1f}s")
            
            # Criar diretório de saída
            os.makedirs(output_dir, exist_ok=True)
            
            # 1. Extrair segmento
            video_segment = self.extract_segment(
                video_path, 
                segment['start_time'], 
                segment['end_time']
            )
            
            # 2. Converter para formato vertical
            vertical_video = self.crop_to_vertical(video_segment)
            
            # 3. Adicionar formatação profissional
            formatted_video = self.add_professional_formatting(
                vertical_video, 
                part_number, 
                hashtags
            )
            
            # 4. Otimizar qualidade
            optimized_video = self.optimize_quality(formatted_video)
            
            # 5. Gerar nome do arquivo
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_Parte_{part_number:02d}.mp4"
            output_path = os.path.join(output_dir, filename)
            
            # 6. Renderizar vídeo final
            self.logger.info(f"Renderizando: {filename}")
            
            optimized_video.write_videofile(
                output_path,
                codec=self.config['video_codec'],
                audio_codec=self.config['audio_codec'],
                bitrate=self.config['video_bitrate'],
                audio_bitrate=self.config['audio_bitrate'],
                temp_audiofile='temp/audio_temp.m4a',
                remove_temp=True,
                verbose=False,
                logger=None  # Suprimir logs verbosos
            )
            
            # 7. Limpar recursos
            optimized_video.close()
            formatted_video.close()
            vertical_video.close()
            video_segment.close()
            
            # 8. Validar arquivo criado
            if not os.path.exists(output_path):
                raise Exception(f"Arquivo não foi criado: {output_path}")
            
            file_size = os.path.getsize(output_path)
            if file_size < 1024:  # Menor que 1KB indica problema
                raise Exception(f"Arquivo muito pequeno: {file_size} bytes")
            
            # 9. Preparar informações do short
            short_info = {
                'part_number': part_number,
                'filename': filename,
                'output_path': output_path,
                'file_size': file_size,
                'duration': segment['end_time'] - segment['start_time'],
                'start_time': segment['start_time'],
                'end_time': segment['end_time'],
                'title': f"{title} - Parte {part_number}/7 #Shorts",
                'hashtags': hashtags,
                'resolution': self.config['output_resolution'],
                'created_successfully': True
            }
            
            self.logger.info(f"Short {part_number} criado: {filename} ({file_size/1024/1024:.1f}MB)")
            return short_info
            
        except Exception as e:
            self.logger.error(f"Erro ao criar short {part_number}: {str(e)}")
            
            # Retornar info de falha
            return {
                'part_number': part_number,
                'filename': f"ERROR_Parte_{part_number:02d}.mp4",
                'output_path': None,
                'file_size': 0,
                'duration': 0,
                'error': str(e),
                'created_successfully': False
            }
    
    def generate_thumbnail(self, video_path: str, timestamp: float, output_path: str) -> bool:
        """
        Gera thumbnail do vídeo em timestamp específico
        
        Args:
            video_path: Caminho do vídeo
            timestamp: Momento para capturar (segundos)
            output_path: Caminho para salvar thumbnail
            
        Returns:
            True se gerou com sucesso
        """
        try:
            # Usar OpenCV para capturar frame
            cap = cv2.VideoCapture(video_path)
            
            # Ir para o timestamp
            cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            
            # Capturar frame
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Converter BGR para RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Criar imagem PIL
                image = Image.fromarray(frame_rgb)
                
                # Redimensionar para thumbnail (mantendo aspect ratio)
                image.thumbnail((320, 180), Image.Resampling.LANCZOS)
                
                # Salvar
                image.save(output_path, 'JPEG', quality=85)
                
                self.logger.debug(f"Thumbnail gerada: {output_path}")
                return True
            else:
                self.logger.warning(f"Não foi possível capturar frame em {timestamp}s")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao gerar thumbnail: {str(e)}")
            return False
    
    def validate_short_quality(self, short_info: Dict) -> Dict:
        """
        Valida qualidade do short criado
        
        Args:
            short_info: Informações do short
            
        Returns:
            Dicionário com resultado da validação
        """
        try:
            if not short_info.get('created_successfully', False):
                return {
                    'is_valid': False,
                    'issues': ['Short não foi criado com sucesso'],
                    'warnings': []
                }
            
            output_path = short_info['output_path']
            issues = []
            warnings = []
            
            # Verificar se arquivo existe
            if not os.path.exists(output_path):
                issues.append('Arquivo não encontrado')
                return {'is_valid': False, 'issues': issues, 'warnings': warnings}
            
            # Verificar tamanho do arquivo
            file_size_mb = short_info['file_size'] / (1024 * 1024)
            if file_size_mb < 0.5:
                issues.append(f'Arquivo muito pequeno: {file_size_mb:.1f}MB')
            elif file_size_mb > 100:
                warnings.append(f'Arquivo grande: {file_size_mb:.1f}MB')
            
            # Verificar duração
            duration = short_info['duration']
            min_duration, max_duration = self.config['target_duration_range']
            
            if duration < min_duration:
                issues.append(f'Duração muito curta: {duration:.1f}s (mín: {min_duration}s)')
            elif duration > max_duration:
                warnings.append(f'Duração longa: {duration:.1f}s (máx: {max_duration}s)')
            
            # Tentar abrir vídeo para validação técnica
            try:
                test_clip = VideoFileClip(output_path)
                
                # Verificar se tem áudio
                if test_clip.audio is None:
                    warnings.append('Vídeo sem áudio')
                
                # Verificar resolução
                if test_clip.size != tuple(self.config['output_resolution']):
                    issues.append(f'Resolução incorreta: {test_clip.size}')
                
                test_clip.close()
                
            except Exception as e:
                issues.append(f'Erro ao validar arquivo: {str(e)}')
            
            # Resultado da validação
            is_valid = len(issues) == 0
            
            validation_result = {
                'is_valid': is_valid,
                'issues': issues,
                'warnings': warnings,
                'file_size_mb': file_size_mb,
                'duration': duration
            }
            
            if is_valid:
                self.logger.debug(f"Short validado: {short_info['filename']}")
            else:
                self.logger.warning(f"Short com problemas: {', '.join(issues)}")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Erro na validação: {str(e)}")
            return {
                'is_valid': False,
                'issues': [f'Erro na validação: {str(e)}'],
                'warnings': []
            }