#!/usr/bin/env python3
"""
Audio Analyzer Module
Sistema de análise de áudio para detectar picos de energia e momentos dinâmicos
Canal: Leonardo_Zarelli
"""

import os
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from pydub import AudioSegment
from pydub.utils import which
import matplotlib.pyplot as plt

class AudioAnalyzer:
    """Classe para análise de áudio e detecção de picos de energia"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.audio = None
        self.sample_rate = 44100
        self.chunk_duration = 1.0  # Análise por segundo
        
        # Verificar se FFmpeg está disponível
        if not which("ffmpeg"):
            self.logger.warning("FFmpeg não encontrado. Algumas funcionalidades podem não funcionar")
    
    def analyze_audio_simple(self, video_path: str) -> Dict:
        """Análise de áudio simplificada"""
        try:
            self.logger.info(f"Carregando áudio de: {video_path}")
            
            # Carregar áudio usando pydub
            audio = AudioSegment.from_file(video_path)
            
            # Converter para mono
            if audio.channels > 1:
                audio = audio.set_channels(1)
                
            duration = len(audio) / 1000.0  # Duração em segundos
            
            # Calcular energia em intervalos de 1s
            energy_levels = []
            chunk_ms = 1000  # 1 segundo
            
            for i in range(0, len(audio), chunk_ms):
                chunk = audio[i:i + chunk_ms]
                if len(chunk) > 0:
                    energy = float(chunk.rms)
                    energy_levels.append(energy)
                else:
                    energy_levels.append(0.0)
            
            self.logger.info(f"Áudio analisado: {duration:.1f}s, {len(energy_levels)} pontos")
            
            return {
                "duration": duration,
                "sample_rate": audio.frame_rate,
                "energy_levels": energy_levels,
                "channels": audio.channels
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise de áudio: {e}")
            return {"error": str(e)}
    
    def load_audio_from_video(self, video_path: str) -> bool:
        """
        Carrega áudio de um arquivo de vídeo
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            True se carregou com sucesso, False caso contrário
        """
        try:
            self.logger.info(f"Carregando áudio de: {video_path}")
            
            # Carregar áudio do vídeo usando pydub
            self.audio = AudioSegment.from_file(video_path)
            
            # Converter para mono se estéreo
            if self.audio.channels > 1:
                self.audio = self.audio.set_channels(1)
            
            # Normalizar sample rate
            if self.audio.frame_rate != self.sample_rate:
                self.audio = self.audio.set_frame_rate(self.sample_rate)
            
            duration = len(self.audio) / 1000.0  # Duração em segundos
            self.logger.info(f"Áudio carregado: {duration:.1f}s, {self.audio.frame_rate}Hz, {self.audio.channels} canal(is)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar áudio: {str(e)}")
            return False
    
    def calculate_energy_levels(self) -> List[float]:
        """
        Calcula níveis de energia sonora por segundo
        
        Returns:
            Lista de valores de energia por segundo
        """
        if not self.audio:
            self.logger.error("Nenhum áudio carregado")
            return []
        
        try:
            energy_levels = []
            chunk_ms = int(self.chunk_duration * 1000)  # Converter para milissegundos
            
            # Processar áudio em chunks de 1 segundo
            for i in range(0, len(self.audio), chunk_ms):
                chunk = self.audio[i:i + chunk_ms]
                
                if len(chunk) > 0:
                    # Calcular RMS (Root Mean Square) como medida de energia
                    rms = chunk.rms
                    energy_levels.append(float(rms))
                else:
                    energy_levels.append(0.0)
            
            self.logger.info(f"Calculados {len(energy_levels)} níveis de energia")
            return energy_levels
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular níveis de energia: {str(e)}")
            return []
    
    def detect_volume_variations(self) -> List[float]:
        """
        Detecta variações de volume para identificar momentos dinâmicos
        
        Returns:
            Lista de scores de variação por segundo
        """
        if not self.audio:
            return []
        
        try:
            variation_scores = []
            chunk_ms = int(self.chunk_duration * 1000)
            window_size = 3  # Janela de 3 segundos para calcular variação
            
            energy_levels = self.calculate_energy_levels()
            
            for i in range(len(energy_levels)):
                # Calcular variação em janela ao redor do ponto atual
                start_idx = max(0, i - window_size // 2)
                end_idx = min(len(energy_levels), i + window_size // 2 + 1)
                
                window_energies = energy_levels[start_idx:end_idx]
                
                if len(window_energies) > 1:
                    # Calcular desvio padrão como medida de variação
                    variation = np.std(window_energies)
                    variation_scores.append(float(variation))
                else:
                    variation_scores.append(0.0)
            
            self.logger.info(f"Calculadas {len(variation_scores)} variações de volume")
            return variation_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar variações: {str(e)}")
            return []
    
    def detect_silence_periods(self, silence_threshold: float = -40) -> List[Tuple[float, float]]:
        """
        Detecta períodos de silêncio prolongado
        
        Args:
            silence_threshold: Threshold em dB para considerar silêncio
            
        Returns:
            Lista de tuplas (início, fim) dos períodos de silêncio em segundos
        """
        if not self.audio:
            return []
        
        try:
            silence_periods = []
            chunk_ms = int(self.chunk_duration * 1000)
            min_silence_duration = 2.0  # Mínimo 2 segundos para considerar silêncio
            
            current_silence_start = None
            
            for i in range(0, len(self.audio), chunk_ms):
                chunk = self.audio[i:i + chunk_ms]
                timestamp = i / 1000.0
                
                if len(chunk) > 0:
                    # Calcular dB do chunk
                    db_level = chunk.dBFS
                    
                    if db_level < silence_threshold:
                        # Início de período silencioso
                        if current_silence_start is None:
                            current_silence_start = timestamp
                    else:
                        # Fim de período silencioso
                        if current_silence_start is not None:
                            silence_duration = timestamp - current_silence_start
                            
                            if silence_duration >= min_silence_duration:
                                silence_periods.append((current_silence_start, timestamp))
                            
                            current_silence_start = None
            
            # Verificar se há silêncio no final
            if current_silence_start is not None:
                final_timestamp = len(self.audio) / 1000.0
                silence_duration = final_timestamp - current_silence_start
                
                if silence_duration >= min_silence_duration:
                    silence_periods.append((current_silence_start, final_timestamp))
            
            self.logger.info(f"Detectados {len(silence_periods)} períodos de silêncio")
            return silence_periods
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar silêncios: {str(e)}")
            return []
    
    def calculate_audio_peaks(self, percentile: float = 90) -> List[Tuple[float, float]]:
        """
        Identifica picos de energia sonora
        
        Args:
            percentile: Percentil para considerar como pico
            
        Returns:
            Lista de tuplas (timestamp, energy_level) dos picos
        """
        energy_levels = self.calculate_energy_levels()
        
        if not energy_levels:
            return []
        
        try:
            # Calcular threshold baseado no percentil
            threshold = np.percentile(energy_levels, percentile)
            
            peaks = []
            for i, energy in enumerate(energy_levels):
                if energy >= threshold:
                    timestamp = i * self.chunk_duration
                    peaks.append((timestamp, energy))
            
            self.logger.info(f"Identificados {len(peaks)} picos de energia (>{percentile}° percentil)")
            return peaks
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular picos: {str(e)}")
            return []
    
    def get_audio_score_timeline(self) -> List[float]:
        """
        Gera timeline de scores de áudio combinando energia e variação
        
        Returns:
            Lista de scores normalizados (0-1) por segundo
        """
        try:
            energy_levels = self.calculate_energy_levels()
            variation_scores = self.detect_volume_variations()
            silence_periods = self.detect_silence_periods()
            
            if not energy_levels or not variation_scores:
                return []
            
            # Normalizar energy_levels (0-1)
            if max(energy_levels) > 0:
                energy_normalized = [e / max(energy_levels) for e in energy_levels]
            else:
                energy_normalized = [0.0] * len(energy_levels)
            
            # Normalizar variation_scores (0-1)
            if max(variation_scores) > 0:
                variation_normalized = [v / max(variation_scores) for v in variation_scores]
            else:
                variation_normalized = [0.0] * len(variation_scores)
            
            # Combinar scores (60% energia, 40% variação)
            combined_scores = []
            min_length = min(len(energy_normalized), len(variation_normalized))
            
            for i in range(min_length):
                timestamp = i * self.chunk_duration
                
                # Score base combinado
                score = (energy_normalized[i] * 0.6) + (variation_normalized[i] * 0.4)
                
                # Penalizar períodos de silêncio
                for silence_start, silence_end in silence_periods:
                    if silence_start <= timestamp <= silence_end:
                        score *= 0.1  # Reduzir score drasticamente em silêncios
                        break
                
                combined_scores.append(score)
            
            self.logger.info(f"Timeline de audio score gerada: {len(combined_scores)} pontos")
            return combined_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar timeline: {str(e)}")
            return []
    
    def export_audio_analysis(self, output_path: str = "temp/audio_analysis.png"):
        """
        Exporta gráfico da análise de áudio
        
        Args:
            output_path: Caminho para salvar o gráfico
        """
        try:
            energy_levels = self.calculate_energy_levels()
            variation_scores = self.detect_volume_variations()
            audio_scores = self.get_audio_score_timeline()
            
            if not energy_levels:
                return
            
            # Criar timestamps
            timestamps = [i * self.chunk_duration for i in range(len(energy_levels))]
            
            # Criar gráfico
            plt.figure(figsize=(15, 10))
            
            # Subplot 1: Níveis de energia
            plt.subplot(3, 1, 1)
            plt.plot(timestamps, energy_levels, 'b-', linewidth=1)
            plt.title('Níveis de Energia Sonora')
            plt.ylabel('RMS')
            plt.grid(True, alpha=0.3)
            
            # Subplot 2: Variações de volume
            plt.subplot(3, 1, 2)
            plt.plot(timestamps[:len(variation_scores)], variation_scores, 'g-', linewidth=1)
            plt.title('Variações de Volume')
            plt.ylabel('Desvio Padrão')
            plt.grid(True, alpha=0.3)
            
            # Subplot 3: Score final
            plt.subplot(3, 1, 3)
            plt.plot(timestamps[:len(audio_scores)], audio_scores, 'r-', linewidth=2)
            plt.title('Score de Áudio Combinado')
            plt.xlabel('Tempo (segundos)')
            plt.ylabel('Score (0-1)')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salvar gráfico
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Análise de áudio exportada: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar análise: {str(e)}")
    
    def get_analysis_summary(self) -> Dict:
        """
        Retorna resumo da análise de áudio
        
        Returns:
            Dicionário com estatísticas da análise
        """
        try:
            if not self.audio:
                return {}
            
            energy_levels = self.calculate_energy_levels()
            variation_scores = self.detect_volume_variations()
            silence_periods = self.detect_silence_periods()
            peaks = self.calculate_audio_peaks()
            audio_scores = self.get_audio_score_timeline()
            
            # Calcular estatísticas
            total_duration = len(self.audio) / 1000.0
            total_silence_duration = sum(end - start for start, end in silence_periods)
            silence_percentage = (total_silence_duration / total_duration) * 100
            
            summary = {
                'duration_seconds': total_duration,
                'sample_rate': self.audio.frame_rate,
                'channels': self.audio.channels,
                'energy_stats': {
                    'mean': float(np.mean(energy_levels)) if energy_levels else 0,
                    'max': float(np.max(energy_levels)) if energy_levels else 0,
                    'std': float(np.std(energy_levels)) if energy_levels else 0
                },
                'variation_stats': {
                    'mean': float(np.mean(variation_scores)) if variation_scores else 0,
                    'max': float(np.max(variation_scores)) if variation_scores else 0
                },
                'silence_analysis': {
                    'total_periods': len(silence_periods),
                    'total_duration': total_silence_duration,
                    'percentage': silence_percentage
                },
                'peaks_count': len(peaks),
                'average_audio_score': float(np.mean(audio_scores)) if audio_scores else 0,
                'max_audio_score': float(np.max(audio_scores)) if audio_scores else 0
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {}
    
    def cleanup(self):
        """Libera recursos de áudio"""
        self.audio = None
        self.logger.debug("Recursos de áudio liberados")