#!/usr/bin/env python3
"""
Processador Simples de YouTube Shorts
Versão otimizada e funcional sem complexidades desnecessárias
"""

import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Optional

# Configurar logging simples
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleProcessor:
    """Processador simples e funcional"""
    
    def __init__(self, format_type="youtube_shorts"):
        """
        Inicializa o processador
        
        Args:
            format_type: "normal" ou "youtube_shorts"
        """
        self.config = self.load_config()
        self.format_type = format_type
        self.setup_directories()
        
    def load_config(self) -> Dict:
        """Carrega configuração"""
        try:
            with open("config/config.json", 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar config: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict:
        """Configuração padrão simples"""
        return {
            "shorts_config": {"duration": 60, "count_per_video": 7},
            "directories": {"downloads": "./downloads", "shorts": "./shorts"},
            "hashtags": ["#IA", "#tech", "#shorts"]
        }
    
    def setup_directories(self):
        """Cria diretórios necessários"""
        for dir_path in self.config["directories"].values():
            os.makedirs(dir_path, exist_ok=True)
    
    def download_video(self, url: str) -> Optional[str]:
        """Download simples usando yt-dlp"""
        try:
            from video_downloader import VideoDownloader
            
            downloader = VideoDownloader(self.config["directories"]["downloads"])
            result = downloader.download_video(url)
            
            if result and result.get("local_path"):
                logger.info(f"✅ Download concluído: {result['title']}")
                return result["local_path"]
            else:
                logger.error("❌ Falha no download")
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro no download: {e}")
            return None
    
    def analyze_video_simple(self, video_path: str) -> List[Dict]:
        """Análise simples para encontrar melhores momentos"""
        try:
            from audio_analyzer import AudioAnalyzer
            from moviepy import VideoFileClip
            
            # Informações básicas do vídeo
            video = VideoFileClip(video_path)
            duration = video.duration
            video.close()
            
            # Análise de áudio simples
            audio_analyzer = AudioAnalyzer()
            audio_result = audio_analyzer.analyze_audio_simple(video_path)
            
            if "error" in audio_result:
                logger.error(f"Erro na análise: {audio_result['error']}")
                return []
            
            energy_levels = audio_result.get("energy_levels", [])
            
            # Encontrar os melhores momentos baseado na energia
            segments = []
            short_duration = self.config["shorts_config"]["duration"]
            count = self.config["shorts_config"]["count_per_video"]
            
            # Dividir vídeo em segmentos possíveis
            max_start = duration - short_duration
            if max_start <= 0:
                logger.warning("Vídeo muito curto para criar shorts")
                return []
            
            # Encontrar pontos com maior energia
            best_points = []
            for i, energy in enumerate(energy_levels):
                start_time = i
                if start_time <= max_start:
                    best_points.append((start_time, energy))
            
            # Ordenar por energia e pegar os melhores
            best_points.sort(key=lambda x: x[1], reverse=True)
            
            # Criar segmentos evitando sobreposição
            used_ranges = []
            for i, (start_time, energy) in enumerate(best_points):
                if len(segments) >= count:
                    break
                
                end_time = start_time + short_duration
                
                # Verificar sobreposição
                overlap = False
                for used_start, used_end in used_ranges:
                    if not (end_time <= used_start or start_time >= used_end):
                        overlap = True
                        break
                
                if not overlap:
                    segments.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration": short_duration,
                        "energy_score": energy,
                        "segment_id": len(segments) + 1
                    })
                    used_ranges.append((start_time, end_time))
            
            logger.info(f"✅ Encontrados {len(segments)} segmentos para shorts")
            return segments
            
        except Exception as e:
            logger.error(f"❌ Erro na análise: {e}")
            return []
    
    def create_shorts(self, video_path: str, segments: List[Dict]) -> List[str]:
        """Cria shorts a partir dos segmentos no formato YouTube Shorts (1080x1920)"""
        try:
            from moviepy import VideoFileClip, ColorClip, CompositeVideoClip
            
            if not segments:
                logger.warning("Nenhum segmento para processar")
                return []
            
            video = VideoFileClip(video_path)
            created_files = []
            
            logger.info(f"📐 Vídeo original: {video.w}x{video.h} (ratio: {video.w/video.h:.3f})")
            
            for i, segment in enumerate(segments):
                try:
                    start = segment["start_time"]
                    end = segment["end_time"]
                    
                    # Extrair segmento  
                    clip = video.subclipped(start, end)
                    
                    # Aplicar formato baseado na escolha
                    if self.format_type == "youtube_shorts":
                        # Converter para formato YouTube Shorts (1080x1920, 9:16)
                        clip_formatted = self._convert_to_shorts_format(clip)
                        logger.info(f"✂️ Criando Short {i+1} em formato YouTube Shorts 1080x1920...")
                    elif self.format_type == "split_screen":
                        # Forçar layout split-screen
                        clip_formatted = self._create_split_screen_layout(clip)
                        logger.info(f"✂️ Criando Short {i+1} com layout de tela dividida...")
                    else:
                        # Manter formato original (normal)
                        clip_formatted = clip
                        logger.info(f"✂️ Criando Short {i+1} em formato original {clip.w}x{clip.h}...")
                    
                    # Nome do arquivo
                    base_name = os.path.splitext(os.path.basename(video_path))[0]
                    if self.format_type == "youtube_shorts":
                        suffix = "_shorts"
                    elif self.format_type == "split_screen":
                        suffix = "_teladividida"
                    else:
                        suffix = "_normal"
                    output_file = os.path.join(
                        self.config["directories"]["shorts"],
                        f"{base_name}_short_{i+1}{suffix}.mp4"
                    )
                    
                    # Garantir que o áudio está presente
                    if clip_formatted.audio is None:
                        logger.error(f"❌ Clip {i+1} sem áudio!")
                        clip.close()
                        if clip_formatted != clip:  # Só fechar se for objeto diferente
                            clip_formatted.close()
                        continue
                    
                    # Configurações otimizadas para shorts com áudio garantido
                    clip_formatted.write_videofile(
                        output_file,
                        codec='libx264',
                        audio_codec='aac',
                        temp_audiofile='temp-audio.m4a',
                        remove_temp=True,
                        audio_bitrate='128k',
                        fps=30
                    )
                    
                    clip.close()
                    if clip_formatted != clip:  # Só fechar se for objeto diferente
                        clip_formatted.close()
                    created_files.append(output_file)
                    
                    # Verificar se arquivo foi criado corretamente
                    if os.path.exists(output_file):
                        size_mb = os.path.getsize(output_file) / (1024*1024)
                        logger.info(f"✅ Short {i+1} criado: {os.path.basename(output_file)} ({size_mb:.1f}MB)")
                    else:
                        logger.error(f"❌ Arquivo não foi criado: {output_file}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao criar short {i+1}: {e}")
                    continue
            
            video.close()
            return created_files
            
        except Exception as e:
            logger.error(f"❌ Erro na criação de shorts: {e}")
            return []
    
    def _convert_to_shorts_format(self, clip):
        """
        Converte clip para formato YouTube Shorts (1080x1920, 9:16)
        
        Args:
            clip: VideoFileClip a ser convertido
            
        Returns:
            VideoFileClip no formato correto
        """
        from moviepy import ColorClip, CompositeVideoClip
        
        current_w, current_h = clip.size
        current_ratio = current_w / current_h
        target_ratio = 9/16  # 0.5625
        
        logger.info(f"📐 Convertendo {current_w}x{current_h} (ratio: {current_ratio:.3f}) para 1080x1920 (ratio: {target_ratio:.3f})")
        
        # Verificar se deve aplicar layout split-screen
        if self._should_use_split_screen(clip):
            return self._create_split_screen_layout(clip)
        
        if abs(current_ratio - target_ratio) <= 0.05:
            # Aspecto já é próximo do ideal, apenas redimensionar
            logger.info("🔄 Redimensionando para 1080x1920")
            return clip.resized((1080, 1920))
        
        elif current_ratio > 1:
            # Vídeo landscape - cortar para formato vertical
            logger.info("🔄 Cortando vídeo landscape para formato vertical")
            
            # Calcular novas dimensões mantendo altura e ajustando largura
            new_w = int(current_h * target_ratio)
            
            if new_w <= current_w:
                # Cortar largura (centralizado)
                x_center = current_w // 2
                x1 = x_center - new_w // 2
                x2 = x_center + new_w // 2
                cropped = clip.cropped(x1=x1, x2=x2)
            else:
                # Se a nova largura for maior, usar a largura atual e ajustar altura
                new_h = int(current_w / target_ratio)
                y_center = current_h // 2
                y1 = y_center - new_h // 2
                y2 = y_center + new_h // 2
                cropped = clip.cropped(y1=y1, y2=y2)
            
            return cropped.resized((1080, 1920))
        
        elif current_ratio < target_ratio:
            # Vídeo muito estreito - adicionar letterbox
            logger.info("🔄 Adicionando letterbox para formato vertical")
            
            # Redimensionar mantendo aspecto
            clip_resized = clip.resized(height=1920)
            
            if clip_resized.w < 1080:
                # Adicionar barras pretas nas laterais
                bg = ColorClip(size=(1080, 1920), color=(0,0,0), duration=clip.duration)
                x_offset = (1080 - clip_resized.w) // 2
                composite = CompositeVideoClip([bg, clip_resized.with_position((x_offset, 0))])
                return composite
            else:
                return clip_resized.resized((1080, 1920))
        
        else:
            # Caso padrão - redimensionar diretamente
            logger.info("🔄 Redimensionamento padrão para 1080x1920")
            return clip.resized((1080, 1920))
    
    def _should_use_split_screen(self, clip):
        """
        Determina se deve aplicar layout split-screen baseado nas características do vídeo
        
        Critérios:
        - Vídeo muito largo (indica possível screenshare + webcam)
        - Resolução alta (indica gravação de tela)
        - Aspecto muito diferente de 9:16
        """
        current_w, current_h = clip.size
        current_ratio = current_w / current_h
        
        # Se for muito largo e alta resolução, provavelmente tem webcam + tela
        is_very_wide = current_ratio > 1.5  # Mais largo que 3:2
        is_high_res = current_w >= 1280 or current_h >= 720  # HD ou maior
        
        return is_very_wide and is_high_res
    
    def _create_split_screen_layout(self, clip):
        """
        Cria layout split-screen otimizado para YouTube Shorts
        
        Layout melhorado:
        - Parte superior (45%): Webcam/pessoa com bordas arredondadas
        - Parte inferior (55%): Conteúdo/tela com melhor enquadramento
        - Separação visual elegante
        """
        from moviepy import ColorClip, CompositeVideoClip
        
        logger.info("🎬 Criando layout de tela dividida otimizado (webcam + conteúdo)")
        
        current_w, current_h = clip.size
        
        # Proporções otimizadas para melhor visualização
        webcam_height = int(1920 * 0.45)  # 45% superior = 864px
        content_height = int(1920 * 0.55)  # 55% inferior = 1056px
        
        # Detecção inteligente da área da webcam
        # Tentar diferentes posições comuns de webcam
        webcam_positions = [
            # Canto superior direito (mais comum)
            {'x_ratio': 0.70, 'y_ratio': 0.0, 'w_ratio': 0.30, 'h_ratio': 0.35},
            # Canto superior esquerdo
            {'x_ratio': 0.0, 'y_ratio': 0.0, 'w_ratio': 0.30, 'h_ratio': 0.35},
            # Centro superior
            {'x_ratio': 0.35, 'y_ratio': 0.0, 'w_ratio': 0.30, 'h_ratio': 0.35},
            # Lateral direita completa
            {'x_ratio': 0.75, 'y_ratio': 0.0, 'w_ratio': 0.25, 'h_ratio': 0.50}
        ]
        
        # Usar primeira posição (mais comum)
        pos = webcam_positions[0]
        webcam_x = int(current_w * pos['x_ratio'])
        webcam_y = int(current_h * pos['y_ratio'])
        webcam_w = int(current_w * pos['w_ratio'])
        webcam_h = int(current_h * pos['h_ratio'])
        
        # Extrair área da webcam com melhor enquadramento
        webcam_clip = clip.cropped(
            x1=webcam_x,
            y1=webcam_y,
            x2=min(webcam_x + webcam_w, current_w),
            y2=min(webcam_y + webcam_h, current_h)
        )
        
        # Redimensionar webcam mantendo proporção
        webcam_ratio = webcam_clip.w / webcam_clip.h
        target_webcam_w = min(1080, int(webcam_height * webcam_ratio))
        target_webcam_h = int(target_webcam_w / webcam_ratio)
        
        if target_webcam_h > webcam_height:
            target_webcam_h = webcam_height
            target_webcam_w = int(target_webcam_h * webcam_ratio)
        
        webcam_resized = webcam_clip.resized((target_webcam_w, target_webcam_h))
        
        # Área do conteúdo (área principal sem webcam)
        content_x = 0
        content_y = 0
        content_w = webcam_x if webcam_x > current_w * 0.5 else current_w
        content_h = current_h
        
        content_clip = clip.cropped(
            x1=content_x,
            y1=content_y,
            x2=content_w,
            y2=content_h
        )
        
        # Redimensionar conteúdo otimizando o espaço
        content_ratio = content_clip.w / content_clip.h
        
        # Calcular dimensões ideais para o conteúdo
        max_content_w = 1080
        max_content_h = content_height - 20  # Margem de 10px acima e abaixo
        
        if content_ratio > (max_content_w / max_content_h):
            # Vídeo mais largo - limitar pela largura
            target_content_w = max_content_w
            target_content_h = int(target_content_w / content_ratio)
        else:
            # Vídeo mais alto - limitar pela altura
            target_content_h = max_content_h
            target_content_w = int(target_content_h * content_ratio)
        
        content_resized = content_clip.resized((target_content_w, target_content_h))
        
        # Criar fundo com gradiente sutil
        background = ColorClip(size=(1080, 1920), color=(15, 15, 15), duration=clip.duration)
        
        # Posicionamento otimizado
        # Webcam centralizada na parte superior com margem
        webcam_x_pos = (1080 - target_webcam_w) // 2
        webcam_y_pos = (webcam_height - target_webcam_h) // 2
        webcam_positioned = webcam_resized.with_position((webcam_x_pos, webcam_y_pos))
        
        # Conteúdo centralizado na parte inferior
        content_x_pos = (1080 - target_content_w) // 2
        content_y_pos = webcam_height + (content_height - target_content_h) // 2
        content_positioned = content_resized.with_position((content_x_pos, content_y_pos))
        
        # Linha divisória mais elegante com gradiente
        divider_height = 2
        divider = ColorClip(size=(1080, divider_height), color=(80, 80, 80), duration=clip.duration)
        divider_positioned = divider.with_position((0, webcam_height - 1))
        
        # Bordas sutis para delimitar áreas (opcional)
        # Borda superior da webcam
        top_border = ColorClip(size=(1080, 1), color=(40, 40, 40), duration=clip.duration)
        top_border_positioned = top_border.with_position((0, 0))
        
        # Borda inferior do conteúdo
        bottom_border = ColorClip(size=(1080, 1), color=(40, 40, 40), duration=clip.duration)
        bottom_border_positioned = bottom_border.with_position((0, 1919))
        
        # Compor o vídeo final com camadas organizadas
        final_clip = CompositeVideoClip([
            background,              # Fundo
            content_positioned,      # Conteúdo principal (embaixo)
            webcam_positioned,       # Webcam (em cima)
            divider_positioned,      # Linha divisória
            top_border_positioned,   # Borda superior
            bottom_border_positioned # Borda inferior
        ])
        
        logger.info(f"✅ Layout split-screen otimizado: webcam {target_webcam_w}x{target_webcam_h}, conteúdo {target_content_w}x{target_content_h}")
        logger.info(f"📐 Proporções: webcam {webcam_height}px (45%), conteúdo {content_height}px (55%)")
        
        return final_clip
    
    def process_video_complete(self, url: str) -> Dict:
        """Processamento completo de um vídeo"""
        start_time = datetime.now()
        
        logger.info("🎬 INICIANDO PROCESSAMENTO COMPLETO")
        logger.info(f"URL: {url}")
        
        # 1. Download
        logger.info("\n📥 ETAPA 1: Download")
        video_path = self.download_video(url)
        if not video_path:
            return {"success": False, "error": "Falha no download"}
        
        # 2. Análise
        logger.info("\n🔍 ETAPA 2: Análise")
        segments = self.analyze_video_simple(video_path)
        if not segments:
            return {"success": False, "error": "Falha na análise"}
        
        # 3. Criação de shorts
        logger.info("\n✂️  ETAPA 3: Criação de Shorts")
        created_files = self.create_shorts(video_path, segments)
        
        # Resultado
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "success": len(created_files) > 0,
            "video_path": video_path,
            "segments_found": len(segments),
            "shorts_created": len(created_files),
            "created_files": created_files,
            "processing_time": f"{duration:.1f}s",
            "timestamp": end_time.isoformat()
        }
        
        # Log resultado
        logger.info("\n" + "="*50)
        logger.info("📊 RESULTADO FINAL:")
        logger.info(f"  ✅ Sucesso: {'Sim' if result['success'] else 'Não'}")
        logger.info(f"  📹 Shorts criados: {result['shorts_created']}")
        logger.info(f"  ⏱️  Tempo: {result['processing_time']}")
        logger.info("="*50)
        
        return result

def main():
    """Função principal"""
    print("🎬 YouTube Shorts - Processador Simples")
    print("="*50)
    
    processor = SimpleProcessor()
    
    # Menu simples
    while True:
        print("\n📋 OPÇÕES:")
        print("1. Processar vídeo do YouTube")
        print("2. Listar shorts criados")
        print("3. Sair")
        
        choice = input("\nEscolha (1-3): ").strip()
        
        if choice == "1":
            url = input("URL do YouTube: ").strip()
            if url:
                result = processor.process_video_complete(url)
                if result["success"]:
                    print(f"\n🎉 Sucesso! {result['shorts_created']} shorts criados")
                else:
                    print(f"\n❌ Erro: {result.get('error', 'Falha no processamento')}")
            else:
                print("❌ URL inválida")
                
        elif choice == "2":
            shorts_dir = processor.config["directories"]["shorts"]
            files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
            if files:
                print(f"\n📁 Shorts criados ({len(files)}):")
                for file in files:
                    print(f"  • {file}")
            else:
                print("\n📁 Nenhum short encontrado")
                
        elif choice == "3":
            print("\n👋 Encerrando...")
            break
            
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    main()