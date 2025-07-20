#!/usr/bin/env python3
"""
🎬 VALIDADOR E CONVERSOR YOUTUBE SHORTS
Garante que todos os vídeos estejam no formato exato do YouTube Shorts

FORMATO OBRIGATÓRIO:
- Resolução: 1080x1920 pixels
- Proporção: 9:16 (vertical)
- Orientação: Retrato (altura maior que largura)
- Duração máxima: 3 minutos (recomendado 15-60 segundos)
"""

import os
import sys
from typing import Dict, Optional, List, Tuple
try:
    from moviepy.editor import VideoFileClip, ColorClip, CompositeVideoClip
except ImportError:
    try:
        from moviepy import VideoFileClip, ColorClip, CompositeVideoClip
    except ImportError:
        print("❌ MoviePy não está instalado. Execute: pip install moviepy")
        sys.exit(1)
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class YouTubeShortsValidator:
    """Validador e conversor para formato YouTube Shorts"""
    
    # ESPECIFICAÇÕES OFICIAIS DO YOUTUBE SHORTS
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    TARGET_RATIO = 9/16  # 0.5625
    MAX_DURATION = 180  # 3 minutos em segundos
    RECOMMENDED_MIN_DURATION = 15
    RECOMMENDED_MAX_DURATION = 60
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def validate_video(self, video_path: str) -> Dict:
        """
        Valida se o vídeo está no formato YouTube Shorts
        
        Args:
            video_path: Caminho para o vídeo
            
        Returns:
            Dict com resultado da validação
        """
        if not os.path.exists(video_path):
            return {
                'valid': False,
                'error': 'Arquivo não encontrado',
                'file_path': video_path
            }
        
        try:
            video = VideoFileClip(video_path)
            
            # Extrair informações do vídeo
            width, height = video.size
            duration = video.duration
            fps = video.fps
            has_audio = video.audio is not None
            aspect_ratio = width / height
            is_vertical = height > width
            
            # Verificações específicas do YouTube Shorts
            validation_result = {
                'valid': True,
                'file_path': video_path,
                'current_specs': {
                    'resolution': f"{width}x{height}",
                    'width': width,
                    'height': height,
                    'aspect_ratio': aspect_ratio,
                    'duration': duration,
                    'fps': fps,
                    'has_audio': has_audio,
                    'is_vertical': is_vertical,
                    'file_size_mb': os.path.getsize(video_path) / (1024*1024)
                },
                'target_specs': {
                    'resolution': f"{self.TARGET_WIDTH}x{self.TARGET_HEIGHT}",
                    'aspect_ratio': self.TARGET_RATIO,
                    'max_duration': self.MAX_DURATION
                },
                'checks': {},
                'issues': [],
                'recommendations': [],
                'needs_conversion': False,
                'conversion_type': None
            }
            
            # 1. Verificar resolução exata
            resolution_perfect = (width == self.TARGET_WIDTH and height == self.TARGET_HEIGHT)
            validation_result['checks']['resolution_perfect'] = resolution_perfect
            
            if not resolution_perfect:
                validation_result['valid'] = False
                validation_result['needs_conversion'] = True
                validation_result['issues'].append(f"Resolução incorreta: {width}x{height} (deve ser {self.TARGET_WIDTH}x{self.TARGET_HEIGHT})")
            
            # 2. Verificar proporção 9:16
            ratio_tolerance = 0.01  # 1% de tolerância
            ratio_correct = abs(aspect_ratio - self.TARGET_RATIO) <= ratio_tolerance
            validation_result['checks']['aspect_ratio_correct'] = ratio_correct
            
            if not ratio_correct:
                validation_result['valid'] = False
                validation_result['needs_conversion'] = True
                validation_result['issues'].append(f"Proporção incorreta: {aspect_ratio:.3f} (deve ser {self.TARGET_RATIO:.3f})")
            
            # 3. Verificar orientação vertical
            validation_result['checks']['is_vertical'] = is_vertical
            
            if not is_vertical:
                validation_result['valid'] = False
                validation_result['needs_conversion'] = True
                validation_result['issues'].append("Vídeo deve estar em orientação vertical (retrato)")
            
            # 4. Verificar duração
            duration_valid = duration <= self.MAX_DURATION
            validation_result['checks']['duration_valid'] = duration_valid
            
            if not duration_valid:
                validation_result['valid'] = False
                validation_result['issues'].append(f"Duração muito longa: {duration:.1f}s (máximo {self.MAX_DURATION}s)")
            
            # 5. Recomendações de duração
            if duration < self.RECOMMENDED_MIN_DURATION:
                validation_result['recommendations'].append(f"Duração muito curta: {duration:.1f}s (recomendado: {self.RECOMMENDED_MIN_DURATION}-{self.RECOMMENDED_MAX_DURATION}s)")
            elif duration > self.RECOMMENDED_MAX_DURATION:
                validation_result['recommendations'].append(f"Duração longa: {duration:.1f}s (recomendado: {self.RECOMMENDED_MIN_DURATION}-{self.RECOMMENDED_MAX_DURATION}s)")
            
            # 6. Verificar áudio
            if not has_audio:
                validation_result['recommendations'].append("Vídeo sem áudio - shorts com áudio têm melhor performance")
            
            # 7. Verificar FPS
            if fps < 24:
                validation_result['recommendations'].append(f"FPS baixo: {fps:.1f} (recomendado: 24-30)")
            elif fps > 30:
                validation_result['recommendations'].append(f"FPS alto: {fps:.1f} (recomendado: 24-30)")
            
            # Determinar tipo de conversão necessária
            if validation_result['needs_conversion']:
                validation_result['conversion_type'] = self._determine_conversion_type(width, height, aspect_ratio)
            
            video.close()
            return validation_result
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Erro ao analisar vídeo: {str(e)}",
                'file_path': video_path
            }
    
    def _determine_conversion_type(self, width: int, height: int, aspect_ratio: float) -> str:
        """Determina o tipo de conversão necessária"""
        
        if aspect_ratio > 1:  # Landscape
            return "crop_landscape_to_vertical"
        elif aspect_ratio < self.TARGET_RATIO:  # Muito estreito
            return "add_letterbox"
        elif height > width:  # Já vertical, mas resolução errada
            return "resize_vertical"
        else:
            return "force_convert"
    
    def convert_to_youtube_shorts(self, video_path: str, output_path: str = None) -> Optional[str]:
        """
        Converte vídeo para formato YouTube Shorts exato
        
        Args:
            video_path: Caminho do vídeo original
            output_path: Caminho de saída (opcional)
            
        Returns:
            Caminho do arquivo convertido ou None se falhou
        """
        if not os.path.exists(video_path):
            self.logger.error(f"Arquivo não encontrado: {video_path}")
            return None
        
        # Validar primeiro
        validation = self.validate_video(video_path)
        
        if validation.get('valid', False):
            self.logger.info(f"✅ Vídeo já está no formato correto: {video_path}")
            return video_path
        
        if 'error' in validation:
            self.logger.error(f"❌ Erro na validação: {validation['error']}")
            return None
        
        try:
            # Definir caminho de saída
            if not output_path:
                base_name = os.path.splitext(os.path.basename(video_path))[0]
                output_dir = os.path.join(os.path.dirname(video_path), "shorts_converted")
                os.makedirs(output_dir, exist_ok=True)
                output_path = os.path.join(output_dir, f"{base_name}_youtube_shorts.mp4")
            
            self.logger.info(f"🔄 Convertendo para YouTube Shorts: {os.path.basename(output_path)}")
            
            # Carregar vídeo
            video = VideoFileClip(video_path)
            
            # Aplicar conversão baseada no tipo
            conversion_type = validation['conversion_type']
            self.logger.info(f"📐 Tipo de conversão: {conversion_type}")
            
            if conversion_type == "crop_landscape_to_vertical":
                converted_clip = self._crop_landscape_to_vertical(video)
            elif conversion_type == "add_letterbox":
                converted_clip = self._add_letterbox(video)
            elif conversion_type == "resize_vertical":
                converted_clip = self._resize_to_target(video)
            else:
                converted_clip = self._force_convert(video)
            
            # Limitar duração se necessário
            if converted_clip.duration > self.MAX_DURATION:
                self.logger.warning(f"⚠️ Cortando vídeo para {self.MAX_DURATION}s")
                converted_clip = converted_clip.subclipped(0, self.MAX_DURATION)
            
            # Salvar com especificações otimizadas para YouTube Shorts
            self.logger.info("💾 Salvando vídeo convertido...")
            converted_clip.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=min(30, video.fps),  # Máximo 30fps
                audio_bitrate='128k',
                preset='medium',  # Equilíbrio entre qualidade e velocidade
                verbose=False,
                logger=None
            )
            
            # Verificar se conversão foi bem-sucedida
            if os.path.exists(output_path):
                validation_result = self.validate_video(output_path)
                if validation_result.get('valid', False):
                    self.logger.info(f"✅ Conversão bem-sucedida: {output_path}")
                    size_mb = os.path.getsize(output_path) / (1024*1024)
                    self.logger.info(f"📊 Tamanho final: {size_mb:.1f} MB")
                else:
                    self.logger.error("❌ Conversão falhou - vídeo não está no formato correto")
                    return None
            else:
                self.logger.error("❌ Arquivo convertido não foi criado")
                return None
            
            # Limpar recursos
            video.close()
            converted_clip.close()
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ Erro na conversão: {str(e)}")
            return None
    
    def _crop_landscape_to_vertical(self, video: VideoFileClip) -> VideoFileClip:
        """Corta vídeo landscape para formato vertical 9:16"""
        current_w, current_h = video.size
        
        # Calcular nova largura mantendo altura
        new_w = int(current_h * self.TARGET_RATIO)
        
        if new_w <= current_w:
            # Cortar largura (centralizado)
            x_center = current_w // 2
            x1 = x_center - new_w // 2
            x2 = x_center + new_w // 2
            cropped = video.cropped(x1=x1, x2=x2)
        else:
            # Se precisar de mais largura, ajustar altura
            new_h = int(current_w / self.TARGET_RATIO)
            y_center = current_h // 2
            y1 = y_center - new_h // 2
            y2 = y_center + new_h // 2
            cropped = video.cropped(y1=y1, y2=y2)
        
        return cropped.resized((self.TARGET_WIDTH, self.TARGET_HEIGHT))
    
    def _add_letterbox(self, video: VideoFileClip) -> VideoFileClip:
        """Adiciona letterbox para vídeos muito estreitos"""
        # Redimensionar mantendo aspecto
        video_resized = video.resized(height=self.TARGET_HEIGHT)
        
        if video_resized.w < self.TARGET_WIDTH:
            # Adicionar barras pretas nas laterais
            bg = ColorClip(size=(self.TARGET_WIDTH, self.TARGET_HEIGHT), color=(0,0,0), duration=video.duration)
            x_offset = (self.TARGET_WIDTH - video_resized.w) // 2
            composite = CompositeVideoClip([bg, video_resized.with_position((x_offset, 0))])
            return composite
        else:
            return video_resized.resized((self.TARGET_WIDTH, self.TARGET_HEIGHT))
    
    def _resize_to_target(self, video: VideoFileClip) -> VideoFileClip:
        """Redimensiona diretamente para o tamanho alvo"""
        return video.resized((self.TARGET_WIDTH, self.TARGET_HEIGHT))
    
    def _force_convert(self, video: VideoFileClip) -> VideoFileClip:
        """Conversão forçada com letterbox se necessário"""
        current_w, current_h = video.size
        current_ratio = current_w / current_h
        
        if current_ratio > self.TARGET_RATIO:
            # Muito largo - cortar
            return self._crop_landscape_to_vertical(video)
        else:
            # Muito estreito - letterbox
            return self._add_letterbox(video)
    
    def batch_validate(self, directory: str) -> List[Dict]:
        """Valida todos os vídeos em um diretório"""
        if not os.path.exists(directory):
            self.logger.error(f"Diretório não encontrado: {directory}")
            return []
        
        video_files = [f for f in os.listdir(directory) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))]
        
        if not video_files:
            self.logger.warning(f"Nenhum vídeo encontrado em: {directory}")
            return []
        
        results = []
        
        for video_file in video_files:
            video_path = os.path.join(directory, video_file)
            validation = self.validate_video(video_path)
            results.append(validation)
        
        return results
    
    def batch_convert(self, directory: str, output_dir: str = None) -> List[str]:
        """Converte todos os vídeos de um diretório"""
        if not output_dir:
            output_dir = os.path.join(directory, "youtube_shorts_converted")
        
        os.makedirs(output_dir, exist_ok=True)
        
        video_files = [f for f in os.listdir(directory) if f.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm'))]
        converted_files = []
        
        for video_file in video_files:
            video_path = os.path.join(directory, video_file)
            base_name = os.path.splitext(video_file)[0]
            output_path = os.path.join(output_dir, f"{base_name}_youtube_shorts.mp4")
            
            converted_path = self.convert_to_youtube_shorts(video_path, output_path)
            if converted_path:
                converted_files.append(converted_path)
        
        return converted_files

def main():
    """Interface de linha de comando"""
    print("🎬 VALIDADOR E CONVERSOR YOUTUBE SHORTS")
    print("=" * 60)
    print("📱 Formato obrigatório: 1080x1920 pixels (9:16)")
    print("⏱️ Duração máxima: 3 minutos")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n📋 USO:")
        print("   python3 youtube_shorts_validator.py <comando> [argumentos]")
        print("\n🔧 COMANDOS:")
        print("   validate <arquivo>      - Validar um vídeo")
        print("   convert <arquivo>       - Converter um vídeo")
        print("   batch-validate <pasta>  - Validar todos os vídeos de uma pasta")
        print("   batch-convert <pasta>   - Converter todos os vídeos de uma pasta")
        print("\n📝 EXEMPLOS:")
        print("   python3 youtube_shorts_validator.py validate video.mp4")
        print("   python3 youtube_shorts_validator.py convert video.mp4")
        print("   python3 youtube_shorts_validator.py batch-convert ./shorts/")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    validator = YouTubeShortsValidator()
    
    if command == "validate":
        if len(sys.argv) < 3:
            print("❌ Especifique o arquivo para validar")
            sys.exit(1)
        
        video_path = sys.argv[2]
        result = validator.validate_video(video_path)
        
        print(f"\n🔍 VALIDAÇÃO: {os.path.basename(video_path)}")
        print("-" * 50)
        
        if result.get('valid', False):
            print("✅ VÍDEO PERFEITO PARA YOUTUBE SHORTS!")
        else:
            print("❌ VÍDEO NÃO ESTÁ NO FORMATO CORRETO")
            
            if 'issues' in result:
                print("\n🚨 PROBLEMAS ENCONTRADOS:")
                for issue in result['issues']:
                    print(f"   • {issue}")
            
            if 'recommendations' in result:
                print("\n💡 RECOMENDAÇÕES:")
                for rec in result['recommendations']:
                    print(f"   • {rec}")
        
        if 'current_specs' in result:
            specs = result['current_specs']
            print(f"\n📊 ESPECIFICAÇÕES ATUAIS:")
            print(f"   📐 Resolução: {specs['resolution']}")
            print(f"   📏 Proporção: {specs['aspect_ratio']:.3f}")
            print(f"   ⏱️ Duração: {specs['duration']:.1f}s")
            print(f"   🎬 FPS: {specs['fps']:.1f}")
            print(f"   🔊 Áudio: {'Sim' if specs['has_audio'] else 'Não'}")
    
    elif command == "convert":
        if len(sys.argv) < 3:
            print("❌ Especifique o arquivo para converter")
            sys.exit(1)
        
        video_path = sys.argv[2]
        converted_path = validator.convert_to_youtube_shorts(video_path)
        
        if converted_path:
            print(f"\n🎉 CONVERSÃO CONCLUÍDA!")
            print(f"📁 Arquivo convertido: {converted_path}")
        else:
            print("\n❌ FALHA NA CONVERSÃO")
            sys.exit(1)
    
    elif command == "batch-validate":
        if len(sys.argv) < 3:
            print("❌ Especifique a pasta para validar")
            sys.exit(1)
        
        directory = sys.argv[2]
        results = validator.batch_validate(directory)
        
        print(f"\n📋 VALIDAÇÃO EM LOTE: {directory}")
        print("-" * 50)
        
        valid_count = sum(1 for r in results if r.get('valid', False))
        total_count = len(results)
        
        print(f"📊 Resultados: {valid_count}/{total_count} vídeos válidos")
        
        for result in results:
            filename = os.path.basename(result['file_path'])
            status = "✅" if result.get('valid', False) else "❌"
            print(f"   {status} {filename}")
    
    elif command == "batch-convert":
        if len(sys.argv) < 3:
            print("❌ Especifique a pasta para converter")
            sys.exit(1)
        
        directory = sys.argv[2]
        converted_files = validator.batch_convert(directory)
        
        print(f"\n🔄 CONVERSÃO EM LOTE CONCLUÍDA")
        print(f"📊 {len(converted_files)} vídeos convertidos")
        
        for file_path in converted_files:
            print(f"   ✅ {os.path.basename(file_path)}")
    
    else:
        print(f"❌ Comando inválido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()