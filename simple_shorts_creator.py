#!/usr/bin/env python3
"""
Criador de Shorts Simplificado
Cria shorts do vídeo atual sem análise complexa
Formato automático: 1080x1920 (9:16) para YouTube Shorts
"""

import os
import sys
from moviepy import VideoFileClip, ColorClip, CompositeVideoClip
from audio_analyzer import AudioAnalyzer
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def convert_to_shorts_format(clip):
    """
    Converte clip para formato YouTube Shorts (1080x1920, 9:16)
    
    Args:
        clip: VideoFileClip a ser convertido
        
    Returns:
        VideoFileClip no formato correto
    """
    current_w, current_h = clip.size
    current_ratio = current_w / current_h
    target_ratio = 9/16  # 0.5625
    
    logger.info(f"📐 Convertendo {current_w}x{current_h} (ratio: {current_ratio:.3f}) para 1080x1920 (ratio: {target_ratio:.3f})")
    
    if abs(current_ratio - target_ratio) <= 0.05:
        # Aspecto já é próximo do ideal, apenas redimensionar
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
        return clip.resized((1080, 1920))

def create_shorts_from_video(video_path, num_shorts=7, short_duration=60):
    """
    Cria shorts a partir de um vídeo baixado
    
    Args:
        video_path: Caminho para o vídeo
        num_shorts: Número de shorts a criar
        short_duration: Duração de cada short em segundos
    """
    
    if not os.path.exists(video_path):
        logger.error(f"Vídeo não encontrado: {video_path}")
        return False
    
    logger.info(f"📹 Processando: {os.path.basename(video_path)}")
    
    try:
        # Carregar vídeo
        video = VideoFileClip(video_path)
        total_duration = video.duration
        
        logger.info(f"⏱️ Duração total: {total_duration:.1f}s")
        
        # Verificar se temos tempo suficiente
        if total_duration < short_duration:
            logger.warning("Vídeo muito curto para criar shorts")
            video.close()
            return False
        
        # Análise de áudio para encontrar melhores momentos
        audio_analyzer = AudioAnalyzer()
        audio_result = audio_analyzer.analyze_audio_simple(video_path)
        
        if not audio_result or 'energy_levels' not in audio_result:
            logger.warning("Análise de áudio falhou, usando divisão uniforme")
            energy_levels = [1.0] * int(total_duration)
        else:
            energy_levels = audio_result['energy_levels']
            logger.info(f"🎵 Análise de áudio: {len(energy_levels)} pontos")
        
        # Encontrar os melhores momentos baseado na energia
        best_segments = find_best_segments(energy_levels, total_duration, num_shorts, short_duration)
        
        logger.info(f"🎯 Criando {len(best_segments)} shorts...")
        
        # Criar diretório de saída
        os.makedirs("./shorts", exist_ok=True)
        
        # Criar shorts
        created_shorts = []
        base_name = os.path.splitext(os.path.basename(video_path))[0]
        
        for i, (start_time, end_time, score) in enumerate(best_segments, 1):
            short_name = f"{base_name}_short_{i}.mp4"
            short_path = os.path.join("./shorts", short_name)
            
            logger.info(f"✂️ Short {i}: {start_time:.1f}s-{end_time:.1f}s (score: {score:.3f})")
            
            try:
                # Extrair segmento
                short_clip = video.subclip(start_time, end_time)
                
                # Converter para formato YouTube Shorts (1080x1920, 9:16)
                short_clip_formatted = convert_to_shorts_format(short_clip)
                
                # Salvar short
                short_clip_formatted.write_videofile(
                    short_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile='temp-audio.m4a',
                    remove_temp=True,
                    verbose=False,
                    logger=None,
                    fps=min(30, video.fps)  # Máximo 30fps
                )
                
                short_clip.close()
                short_clip_formatted.close()
                
                # Verificar arquivo criado
                if os.path.exists(short_path):
                    file_size = os.path.getsize(short_path)
                    logger.info(f"✅ {short_name} - {file_size/1024/1024:.1f}MB")
                    created_shorts.append(short_path)
                else:
                    logger.error(f"❌ Falha ao criar {short_name}")
                    
            except Exception as e:
                logger.error(f"❌ Erro ao criar short {i}: {e}")
        
        video.close()
        
        logger.info(f"🎉 Criados {len(created_shorts)}/{len(best_segments)} shorts com sucesso!")
        
        return len(created_shorts) > 0
        
    except Exception as e:
        logger.error(f"❌ Erro no processamento: {e}")
        return False

def find_best_segments(energy_levels, total_duration, num_segments, segment_duration):
    """
    Encontra os melhores segmentos baseado na energia do áudio
    """
    
    # Converter energy_levels para valores por segundo
    if len(energy_levels) == 0:
        return [(i * segment_duration, (i + 1) * segment_duration, 1.0) 
                for i in range(min(num_segments, int(total_duration // segment_duration)))]
    
    # Calcular janela deslizante
    window_size = int(segment_duration)
    segments = []
    
    for start_idx in range(0, len(energy_levels) - window_size + 1, 5):  # Saltar de 5 em 5 segundos
        end_idx = start_idx + window_size
        
        if end_idx > len(energy_levels):
            break
            
        start_time = start_idx
        end_time = min(start_idx + segment_duration, total_duration)
        
        # Calcular score médio da janela
        window_energy = energy_levels[start_idx:end_idx]
        avg_score = sum(window_energy) / len(window_energy) if window_energy else 0
        
        segments.append((start_time, end_time, avg_score))
    
    # Ordenar por score e pegar os melhores
    segments.sort(key=lambda x: x[2], reverse=True)
    
    # Evitar sobreposição
    selected = []
    for segment in segments:
        start_time, end_time, score = segment
        
        # Verificar se não sobrepõe com segmentos já selecionados
        overlap = False
        for sel_start, sel_end, _ in selected:
            if not (end_time <= sel_start or start_time >= sel_end):
                overlap = True
                break
        
        if not overlap:
            selected.append(segment)
            
        if len(selected) >= num_segments:
            break
    
    # Ordenar por tempo
    selected.sort(key=lambda x: x[0])
    
    return selected

def main():
    """Processa o vídeo atual"""
    
    # Vídeo de teste atual
    test_video = "./downloads/Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster).mp4"
    
    if len(sys.argv) > 1:
        test_video = sys.argv[1]
    
    logger.info("🎬 CRIADOR DE SHORTS SIMPLIFICADO")
    logger.info("=" * 40)
    
    success = create_shorts_from_video(test_video)
    
    if success:
        logger.info("🎉 SHORTS CRIADOS COM SUCESSO!")
        
        # Listar shorts criados
        shorts_dir = "./shorts"
        if os.path.exists(shorts_dir):
            shorts = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
            logger.info(f"📁 Shorts disponíveis em {shorts_dir}:")
            for short in sorted(shorts):
                logger.info(f"  • {short}")
    else:
        logger.error("❌ FALHA NA CRIAÇÃO DOS SHORTS")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)