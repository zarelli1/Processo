#!/usr/bin/env python3
"""
Visual Analyzer Module
Sistema de análise visual para detectar mudanças de cena e movimento
Canal: Your_Channel_Name
"""

import cv2
import numpy as np
import logging
import os
from typing import Dict, List, Tuple, Optional
import matplotlib
matplotlib.use('Agg')  # Backend não-interativo
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import threading

class VisualAnalyzer:
    """Classe para análise visual de vídeos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.video_path = None
        self.frame_count = 0
        self.fps = 30.0
        self.duration = 0.0
        self.resolution = (0, 0)
        
        # Cache para frames processados
        self._frame_cache = {}
        self._lock = threading.Lock()
    
    def load_video(self, video_path: str) -> bool:
        """
        Carrega vídeo para análise
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            True se carregou com sucesso
        """
        try:
            if not os.path.exists(video_path):
                self.logger.error(f"Arquivo não encontrado: {video_path}")
                return False
            
            # Abrir vídeo com OpenCV
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                self.logger.error(f"Não foi possível abrir o vídeo: {video_path}")
                return False
            
            # Extrair informações do vídeo
            self.frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            self.duration = self.frame_count / self.fps
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.resolution = (width, height)
            
            cap.release()
            
            self.video_path = video_path
            
            self.logger.info(f"Vídeo carregado: {self.duration:.1f}s, {self.frame_count} frames, "
                           f"{self.fps:.1f}fps, {width}x{height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar vídeo: {str(e)}")
            return False
    
    def extract_frames_at_intervals(self, interval_seconds: float = 1.0) -> List[Tuple[float, np.ndarray]]:
        """
        Extrai frames em intervalos específicos
        
        Args:
            interval_seconds: Intervalo entre frames em segundos
            
        Returns:
            Lista de tuplas (timestamp, frame)
        """
        if not self.video_path:
            return []
        
        try:
            cap = cv2.VideoCapture(self.video_path)
            frames = []
            
            frame_interval = int(self.fps * interval_seconds)
            
            for frame_num in range(0, self.frame_count, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()
                
                if ret:
                    timestamp = frame_num / self.fps
                    frames.append((timestamp, frame))
            
            cap.release()
            
            self.logger.info(f"Extraídos {len(frames)} frames em intervalos de {interval_seconds}s")
            return frames
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair frames: {str(e)}")
            return []
    
    def calculate_frame_differences(self, interval_seconds: float = 1.0) -> List[float]:
        """
        Calcula diferenças entre frames consecutivos
        
        Args:
            interval_seconds: Intervalo para análise
            
        Returns:
            Lista de scores de diferença por timestamp
        """
        try:
            frames = self.extract_frames_at_intervals(interval_seconds)
            
            if len(frames) < 2:
                return []
            
            differences = []
            prev_frame = None
            
            for timestamp, frame in frames:
                if prev_frame is not None:
                    # Converter para escala de cinza
                    gray_current = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    
                    # Calcular diferença absoluta
                    diff = cv2.absdiff(gray_current, gray_prev)
                    
                    # Calcular score como média da diferença
                    diff_score = np.mean(diff) / 255.0  # Normalizar 0-1
                    differences.append(diff_score)
                else:
                    differences.append(0.0)  # Primeiro frame
                
                prev_frame = frame
            
            self.logger.info(f"Calculadas {len(differences)} diferenças entre frames")
            return differences
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular diferenças: {str(e)}")
            return []
    
    def detect_scene_changes(self, threshold: float = 0.3, interval_seconds: float = 1.0) -> List[Tuple[float, float]]:
        """
        Detecta mudanças significativas de cena
        
        Args:
            threshold: Threshold para considerar mudança de cena
            interval_seconds: Intervalo para análise
            
        Returns:
            Lista de tuplas (timestamp, score) das mudanças
        """
        try:
            differences = self.calculate_frame_differences(interval_seconds)
            scene_changes = []
            
            for i, diff_score in enumerate(differences):
                if diff_score >= threshold:
                    timestamp = i * interval_seconds
                    scene_changes.append((timestamp, diff_score))
            
            self.logger.info(f"Detectadas {len(scene_changes)} mudanças de cena")
            return scene_changes
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar mudanças de cena: {str(e)}")
            return []
    
    def analyze_movement_intensity(self, interval_seconds: float = 1.0) -> List[float]:
        """
        Analisa intensidade de movimento usando optical flow
        
        Args:
            interval_seconds: Intervalo para análise
            
        Returns:
            Lista de scores de movimento por timestamp
        """
        try:
            frames = self.extract_frames_at_intervals(interval_seconds)
            
            if len(frames) < 2:
                return []
            
            movement_scores = []
            prev_gray = None
            
            for timestamp, frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_gray is not None:
                    # Calcular optical flow usando Lucas-Kanade
                    # Primeiro, detectar pontos interessantes
                    corners = cv2.goodFeaturesToTrack(prev_gray, 
                                                    maxCorners=100,
                                                    qualityLevel=0.3,
                                                    minDistance=7,
                                                    blockSize=7)
                    
                    if corners is not None and len(corners) > 0:
                        # Calcular optical flow
                        flow_points, status, error = cv2.calcOpticalFlowPyrLK(
                            prev_gray, gray, corners, None)
                        
                        # Calcular magnitude média do movimento
                        good_points = flow_points[status == 1]
                        good_corners = corners[status == 1]
                        
                        if len(good_points) > 0:
                            # Calcular distâncias de movimento
                            distances = np.sqrt(np.sum((good_points - good_corners) ** 2, axis=1))
                            movement_score = np.mean(distances) / 100.0  # Normalizar
                            movement_scores.append(min(movement_score, 1.0))
                        else:
                            movement_scores.append(0.0)
                    else:
                        movement_scores.append(0.0)
                else:
                    movement_scores.append(0.0)  # Primeiro frame
                
                prev_gray = gray
            
            self.logger.info(f"Analisada intensidade de movimento: {len(movement_scores)} pontos")
            return movement_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao analisar movimento: {str(e)}")
            return []
    
    def detect_transitions_and_cuts(self, interval_seconds: float = 1.0) -> List[Tuple[float, str, float]]:
        """
        Detecta transições e cortes no vídeo
        
        Args:
            interval_seconds: Intervalo para análise
            
        Returns:
            Lista de tuplas (timestamp, tipo, score)
        """
        try:
            differences = self.calculate_frame_differences(interval_seconds)
            transitions = []
            
            # Calcular thresholds baseados na distribuição
            if differences:
                mean_diff = np.mean(differences)
                std_diff = np.std(differences)
                
                hard_cut_threshold = mean_diff + (2 * std_diff)  # Cortes abruptos
                transition_threshold = mean_diff + std_diff      # Transições suaves
                
                for i, diff_score in enumerate(differences):
                    timestamp = i * interval_seconds
                    
                    if diff_score >= hard_cut_threshold:
                        transitions.append((timestamp, "hard_cut", diff_score))
                    elif diff_score >= transition_threshold:
                        transitions.append((timestamp, "transition", diff_score))
            
            self.logger.info(f"Detectadas {len(transitions)} transições/cortes")
            return transitions
            
        except Exception as e:
            self.logger.error(f"Erro ao detectar transições: {str(e)}")
            return []
    
    def calculate_visual_activity_score(self, interval_seconds: float = 1.0) -> List[float]:
        """
        Calcula score de atividade visual combinando diferentes métricas
        
        Args:
            interval_seconds: Intervalo para análise
            
        Returns:
            Lista de scores de atividade visual (0-1)
        """
        try:
            # Obter métricas individuais
            frame_diffs = self.calculate_frame_differences(interval_seconds)
            movement_scores = self.analyze_movement_intensity(interval_seconds)
            
            # Sincronizar listas (usar o tamanho menor)
            min_length = min(len(frame_diffs), len(movement_scores))
            
            visual_scores = []
            
            for i in range(min_length):
                # Combinar métricas (50% diferença de frames, 50% movimento)
                combined_score = (frame_diffs[i] * 0.5) + (movement_scores[i] * 0.5)
                
                # Garantir que está no range 0-1
                visual_scores.append(min(max(combined_score, 0.0), 1.0))
            
            self.logger.info(f"Calculados {len(visual_scores)} scores de atividade visual")
            return visual_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular atividade visual: {str(e)}")
            return []
    
    def get_visual_score_timeline(self, interval_seconds: float = 1.0) -> List[float]:
        """
        Gera timeline completa de scores visuais
        
        Args:
            interval_seconds: Intervalo para análise
            
        Returns:
            Lista de scores normalizados por segundo
        """
        try:
            activity_scores = self.calculate_visual_activity_score(interval_seconds)
            
            if not activity_scores:
                return []
            
            # Aplicar suavização para reduzir ruído
            smoothed_scores = self._apply_smoothing(activity_scores, window_size=3)
            
            # Normalizar scores finais
            if max(smoothed_scores) > 0:
                normalized_scores = [score / max(smoothed_scores) for score in smoothed_scores]
            else:
                normalized_scores = smoothed_scores
            
            return normalized_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar timeline visual: {str(e)}")
            return []
    
    def _apply_smoothing(self, scores: List[float], window_size: int = 3) -> List[float]:
        """
        Aplica suavização em uma lista de scores
        
        Args:
            scores: Lista de scores
            window_size: Tamanho da janela para suavização
            
        Returns:
            Lista de scores suavizados
        """
        if len(scores) < window_size:
            return scores
        
        smoothed = []
        half_window = window_size // 2
        
        for i in range(len(scores)):
            start_idx = max(0, i - half_window)
            end_idx = min(len(scores), i + half_window + 1)
            
            window_scores = scores[start_idx:end_idx]
            smoothed.append(np.mean(window_scores))
        
        return smoothed
    
    def export_visual_analysis(self, output_path: str = "temp/visual_analysis.png", interval_seconds: float = 1.0):
        """
        Exporta gráfico da análise visual
        
        Args:
            output_path: Caminho para salvar o gráfico
            interval_seconds: Intervalo usado na análise
        """
        try:
            frame_diffs = self.calculate_frame_differences(interval_seconds)
            movement_scores = self.analyze_movement_intensity(interval_seconds)
            visual_scores = self.get_visual_score_timeline(interval_seconds)
            
            if not frame_diffs:
                return
            
            # Criar timestamps
            timestamps = [i * interval_seconds for i in range(len(frame_diffs))]
            
            # Criar gráfico
            plt.figure(figsize=(15, 12))
            
            # Subplot 1: Diferenças entre frames
            plt.subplot(4, 1, 1)
            plt.plot(timestamps, frame_diffs, 'b-', linewidth=1)
            plt.title('Diferenças entre Frames Consecutivos')
            plt.ylabel('Diferença')
            plt.grid(True, alpha=0.3)
            
            # Subplot 2: Intensidade de movimento
            plt.subplot(4, 1, 2)
            timestamps_mov = [i * interval_seconds for i in range(len(movement_scores))]
            plt.plot(timestamps_mov, movement_scores, 'g-', linewidth=1)
            plt.title('Intensidade de Movimento (Optical Flow)')
            plt.ylabel('Movimento')
            plt.grid(True, alpha=0.3)
            
            # Subplot 3: Score visual combinado
            plt.subplot(4, 1, 3)
            timestamps_vis = [i * interval_seconds for i in range(len(visual_scores))]
            plt.plot(timestamps_vis, visual_scores, 'r-', linewidth=2)
            plt.title('Score Visual Combinado')
            plt.ylabel('Score (0-1)')
            plt.grid(True, alpha=0.3)
            
            # Subplot 4: Detectar transições
            plt.subplot(4, 1, 4)
            transitions = self.detect_transitions_and_cuts(interval_seconds)
            
            # Plot base
            plt.plot(timestamps, frame_diffs, 'lightblue', alpha=0.5, linewidth=1)
            
            # Marcar transições
            for timestamp, trans_type, score in transitions:
                color = 'red' if trans_type == 'hard_cut' else 'orange'
                plt.scatter(timestamp, score, color=color, s=50, alpha=0.8)
            
            plt.title('Detecção de Transições e Cortes')
            plt.xlabel('Tempo (segundos)')
            plt.ylabel('Intensidade')
            plt.legend(['Diferenças', 'Cortes Abruptos', 'Transições'], loc='upper right')
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salvar gráfico
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
            self.logger.info(f"Análise visual exportada: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar análise visual: {str(e)}")
    
    def get_analysis_summary(self) -> Dict:
        """
        Retorna resumo da análise visual
        
        Returns:
            Dicionário com estatísticas da análise
        """
        try:
            if not self.video_path:
                return {}
            
            frame_diffs = self.calculate_frame_differences()
            movement_scores = self.analyze_movement_intensity()
            visual_scores = self.get_visual_score_timeline()
            transitions = self.detect_transitions_and_cuts()
            scene_changes = self.detect_scene_changes()
            
            summary = {
                'video_info': {
                    'duration_seconds': self.duration,
                    'frame_count': self.frame_count,
                    'fps': self.fps,
                    'resolution': self.resolution
                },
                'frame_analysis': {
                    'mean_difference': float(np.mean(frame_diffs)) if frame_diffs else 0,
                    'max_difference': float(np.max(frame_diffs)) if frame_diffs else 0,
                    'std_difference': float(np.std(frame_diffs)) if frame_diffs else 0
                },
                'movement_analysis': {
                    'mean_movement': float(np.mean(movement_scores)) if movement_scores else 0,
                    'max_movement': float(np.max(movement_scores)) if movement_scores else 0
                },
                'visual_activity': {
                    'mean_score': float(np.mean(visual_scores)) if visual_scores else 0,
                    'max_score': float(np.max(visual_scores)) if visual_scores else 0
                },
                'transitions': {
                    'total_count': len(transitions),
                    'hard_cuts': len([t for t in transitions if t[1] == 'hard_cut']),
                    'soft_transitions': len([t for t in transitions if t[1] == 'transition'])
                },
                'scene_changes': len(scene_changes)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo visual: {str(e)}")
            return {}
    
    def cleanup(self):
        """Libera recursos e cache"""
        with self._lock:
            self._frame_cache.clear()
        
        self.video_path = None
        self.logger.debug("Recursos visuais liberados")