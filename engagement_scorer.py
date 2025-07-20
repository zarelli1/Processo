#!/usr/bin/env python3
"""
Engagement Scorer Module
Sistema para combinar análises e identificar os melhores segmentos para shorts
Canal: Your_Channel_Name
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import os
from datetime import datetime

@dataclass
class VideoSegment:
    """Estrutura para representar um segmento de vídeo com scores"""
    start_time: float
    end_time: float
    duration: float
    audio_score: float
    visual_score: float
    speech_score: float
    combined_score: float
    rank: int
    keywords: str = ""
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'audio_score': self.audio_score,
            'visual_score': self.visual_score,
            'speech_score': self.speech_score,
            'combined_score': self.combined_score,
            'rank': self.rank,
            'keywords': self.keywords
        }

class EngagementScorer:
    """Classe para combinar análises e identificar melhores segmentos"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações padrão
        self.config = config or {
            'weights': {
                'audio': 0.4,    # 40% peso para áudio
                'visual': 0.3,   # 30% peso para visual
                'speech': 0.3    # 30% peso para fala
            },
            'segment_duration': 60,      # Duração desejada dos shorts
            'min_separation': 30,        # Separação mínima entre segmentos
            'overlap_penalty': 0.5,      # Penalidade por sobreposição
            'distribution_bonus': 0.1,   # Bônus por distribuição ao longo do vídeo
            'normalization_method': 'minmax'  # Método de normalização
        }
        
        self.logger.info("EngagementScorer inicializado")
    
    def normalize_scores(self, scores: List[float], method: str = 'minmax') -> List[float]:
        """
        Normaliza scores para range 0-1
        
        Args:
            scores: Lista de scores
            method: Método de normalização ('minmax', 'zscore', 'robust')
            
        Returns:
            Lista de scores normalizados
        """
        if not scores or len(scores) == 0:
            return []
        
        scores_array = np.array(scores)
        
        try:
            if method == 'minmax':
                # Min-Max normalization
                min_val = np.min(scores_array)
                max_val = np.max(scores_array)
                
                if max_val == min_val:
                    return [0.5] * len(scores)  # Todos os valores iguais
                
                normalized = (scores_array - min_val) / (max_val - min_val)
                
            elif method == 'zscore':
                # Z-score normalization
                mean_val = np.mean(scores_array)
                std_val = np.std(scores_array)
                
                if std_val == 0:
                    return [0.5] * len(scores)
                
                normalized = (scores_array - mean_val) / std_val
                # Converter para 0-1 usando sigmoid
                normalized = 1 / (1 + np.exp(-normalized))
                
            elif method == 'robust':
                # Robust normalization (usando percentis)
                q25 = np.percentile(scores_array, 25)
                q75 = np.percentile(scores_array, 75)
                
                if q75 == q25:
                    return [0.5] * len(scores)
                
                normalized = (scores_array - q25) / (q75 - q25)
                normalized = np.clip(normalized, 0, 1)
                
            else:
                # Fallback para minmax
                normalized = self.normalize_scores(scores, 'minmax')
                return normalized
            
            # Garantir que está no range 0-1
            normalized = np.clip(normalized, 0, 1)
            
            return normalized.tolist()
            
        except Exception as e:
            self.logger.error(f"Erro na normalização: {str(e)}")
            return [0.5] * len(scores)  # Fallback
    
    def combine_scores(self, 
                      audio_scores: List[float], 
                      visual_scores: List[float], 
                      speech_scores: List[float]) -> List[float]:
        """
        Combina scores de diferentes análises
        
        Args:
            audio_scores: Scores de áudio
            visual_scores: Scores visuais
            speech_scores: Scores de fala
            
        Returns:
            Lista de scores combinados
        """
        try:
            # Sincronizar tamanhos das listas
            min_length = min(len(audio_scores), len(visual_scores), len(speech_scores))
            
            if min_length == 0:
                self.logger.warning("Uma ou mais listas de scores está vazia")
                return []
            
            # Truncar listas para o mesmo tamanho
            audio_sync = audio_scores[:min_length]
            visual_sync = visual_scores[:min_length]
            speech_sync = speech_scores[:min_length]
            
            # Normalizar cada tipo de score
            audio_norm = self.normalize_scores(audio_sync, self.config['normalization_method'])
            visual_norm = self.normalize_scores(visual_sync, self.config['normalization_method'])
            speech_norm = self.normalize_scores(speech_sync, self.config['normalization_method'])
            
            # Combinar com pesos configurados
            weights = self.config['weights']
            combined_scores = []
            
            for i in range(min_length):
                combined_score = (
                    audio_norm[i] * weights['audio'] +
                    visual_norm[i] * weights['visual'] +
                    speech_norm[i] * weights['speech']
                )
                combined_scores.append(combined_score)
            
            self.logger.info(f"Scores combinados: {len(combined_scores)} pontos")
            self.logger.info(f"Score médio: {np.mean(combined_scores):.3f}")
            self.logger.info(f"Score máximo: {np.max(combined_scores):.3f}")
            
            return combined_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao combinar scores: {str(e)}")
            return []
    
    def create_segments_from_timeline(self, 
                                    combined_scores: List[float], 
                                    interval_seconds: float = 1.0) -> List[VideoSegment]:
        """
        Cria segmentos candidatos baseados na timeline de scores
        
        Args:
            combined_scores: Scores combinados por segundo
            interval_seconds: Intervalo da timeline
            
        Returns:
            Lista de VideoSegments candidatos
        """
        try:
            segments = []
            segment_duration = self.config['segment_duration']
            segment_points = int(segment_duration / interval_seconds)
            
            # Criar segmentos deslizantes
            for start_idx in range(0, len(combined_scores) - segment_points + 1, segment_points // 2):
                end_idx = start_idx + segment_points
                
                if end_idx > len(combined_scores):
                    break
                
                # Calcular timestamps
                start_time = start_idx * interval_seconds
                end_time = end_idx * interval_seconds
                
                # Calcular score médio do segmento
                segment_scores = combined_scores[start_idx:end_idx]
                avg_score = np.mean(segment_scores)
                
                # Criar segmento
                segment = VideoSegment(
                    start_time=start_time,
                    end_time=end_time,
                    duration=end_time - start_time,
                    audio_score=0.0,  # Será calculado depois
                    visual_score=0.0,  # Será calculado depois
                    speech_score=0.0,  # Será calculado depois
                    combined_score=avg_score,
                    rank=0  # Será definido depois
                )
                
                segments.append(segment)
            
            self.logger.info(f"Criados {len(segments)} segmentos candidatos")
            return segments
            
        except Exception as e:
            self.logger.error(f"Erro ao criar segmentos: {str(e)}")
            return []
    
    def calculate_segment_scores(self,
                               segments: List[VideoSegment],
                               audio_scores: List[float],
                               visual_scores: List[float],
                               speech_scores: List[float],
                               interval_seconds: float = 1.0) -> List[VideoSegment]:
        """
        Calcula scores individuais para cada segmento
        
        Args:
            segments: Lista de segmentos
            audio_scores: Timeline de scores de áudio
            visual_scores: Timeline de scores visuais
            speech_scores: Timeline de scores de fala
            interval_seconds: Intervalo da timeline
            
        Returns:
            Lista de segmentos com scores calculados
        """
        try:
            updated_segments = []
            
            for segment in segments:
                # Calcular índices para o segmento
                start_idx = int(segment.start_time / interval_seconds)
                end_idx = int(segment.end_time / interval_seconds)
                
                # Extrair scores do segmento
                audio_seg = audio_scores[start_idx:end_idx] if start_idx < len(audio_scores) else []
                visual_seg = visual_scores[start_idx:end_idx] if start_idx < len(visual_scores) else []
                speech_seg = speech_scores[start_idx:end_idx] if start_idx < len(speech_scores) else []
                
                # Calcular médias
                segment.audio_score = np.mean(audio_seg) if audio_seg else 0.0
                segment.visual_score = np.mean(visual_seg) if visual_seg else 0.0
                segment.speech_score = np.mean(speech_seg) if speech_seg else 0.0
                
                updated_segments.append(segment)
            
            return updated_segments
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular scores dos segmentos: {str(e)}")
            return segments
    
    def apply_separation_penalty(self, segments: List[VideoSegment]) -> List[VideoSegment]:
        """
        Aplica penalidade para segmentos muito próximos
        
        Args:
            segments: Lista de segmentos ordenados por score
            
        Returns:
            Lista de segmentos com penalidades aplicadas
        """
        try:
            min_separation = self.config['min_separation']
            penalty = self.config['overlap_penalty']
            
            # Ordenar por score (maior primeiro)
            segments_sorted = sorted(segments, key=lambda x: x.combined_score, reverse=True)
            
            selected_segments = []
            
            for candidate in segments_sorted:
                too_close = False
                
                # Verificar se está muito próximo de segmentos já selecionados
                for selected in selected_segments:
                    # Calcular distância mínima entre segmentos
                    distance = min(
                        abs(candidate.start_time - selected.end_time),
                        abs(selected.start_time - candidate.end_time)
                    )
                    
                    if distance < min_separation:
                        too_close = True
                        break
                
                if not too_close:
                    selected_segments.append(candidate)
                else:
                    # Aplicar penalidade
                    candidate.combined_score *= penalty
            
            # Retornar todos os segmentos (alguns com penalidade)
            return segments_sorted
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar penalidade de separação: {str(e)}")
            return segments
    
    def apply_distribution_bonus(self, segments: List[VideoSegment], total_duration: float) -> List[VideoSegment]:
        """
        Aplica bônus para distribuição uniforme ao longo do vídeo
        
        Args:
            segments: Lista de segmentos
            total_duration: Duração total do vídeo
            
        Returns:
            Lista de segmentos com bônus aplicado
        """
        try:
            bonus = self.config['distribution_bonus']
            
            # Dividir vídeo em seções
            num_sections = 5
            section_duration = total_duration / num_sections
            
            for segment in segments:
                # Determinar em qual seção o segmento está
                section = int(segment.start_time / section_duration)
                section = min(section, num_sections - 1)
                
                # Contar quantos segmentos já temos nesta seção
                segments_in_section = len([s for s in segments 
                                         if int(s.start_time / section_duration) == section])
                
                # Aplicar bônus inversamente proporcional à densidade
                if segments_in_section > 0:
                    distribution_bonus = bonus / segments_in_section
                    segment.combined_score += distribution_bonus
            
            return segments
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar bônus de distribuição: {str(e)}")
            return segments
    
    def get_best_segments(self,
                         audio_scores: List[float],
                         visual_scores: List[float],
                         speech_scores: List[float],
                         duration: int = 60,
                         count: int = 7,
                         total_duration: float = None,
                         interval_seconds: float = 1.0) -> List[VideoSegment]:
        """
        Identifica os melhores segmentos para shorts
        
        Args:
            audio_scores: Timeline de scores de áudio
            visual_scores: Timeline de scores visuais
            speech_scores: Timeline de scores de fala
            duration: Duração desejada dos shorts
            count: Quantidade de shorts desejada
            total_duration: Duração total do vídeo
            interval_seconds: Intervalo da timeline
            
        Returns:
            Lista dos melhores segmentos ordenados por rank
        """
        try:
            self.logger.info(f"Iniciando seleção dos {count} melhores segmentos de {duration}s")
            
            # Atualizar configuração com parâmetros
            self.config['segment_duration'] = duration
            
            # Combinar scores
            combined_scores = self.combine_scores(audio_scores, visual_scores, speech_scores)
            
            if not combined_scores:
                self.logger.error("Não foi possível combinar scores")
                return []
            
            # Criar segmentos candidatos
            segments = self.create_segments_from_timeline(combined_scores, interval_seconds)
            
            # Calcular scores individuais
            segments = self.calculate_segment_scores(
                segments, audio_scores, visual_scores, speech_scores, interval_seconds
            )
            
            # Aplicar penalidade de separação
            segments = self.apply_separation_penalty(segments)
            
            # Aplicar bônus de distribuição
            if total_duration:
                segments = self.apply_distribution_bonus(segments, total_duration)
            
            # Ordenar por score final e selecionar os melhores
            segments.sort(key=lambda x: x.combined_score, reverse=True)
            best_segments = segments[:count]
            
            # Definir ranks
            for i, segment in enumerate(best_segments):
                segment.rank = i + 1
            
            # Ordenar por timestamp para apresentação
            best_segments.sort(key=lambda x: x.start_time)
            
            self.logger.info(f"Selecionados {len(best_segments)} melhores segmentos")
            
            # Log dos resultados
            for segment in best_segments:
                self.logger.info(f"Rank {segment.rank}: {segment.start_time:.1f}s-{segment.end_time:.1f}s "
                               f"(score: {segment.combined_score:.3f})")
            
            return best_segments
            
        except Exception as e:
            self.logger.error(f"Erro na seleção de segmentos: {str(e)}")
            return []
    
    def export_analysis_results(self, 
                               segments: List[VideoSegment], 
                               output_path: str = "temp/engagement_analysis.json"):
        """
        Exporta resultados da análise
        
        Args:
            segments: Lista de segmentos selecionados
            output_path: Caminho para salvar os resultados
        """
        try:
            # Preparar dados para exportação
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'config': self.config,
                'segments': [segment.to_dict() for segment in segments],
                'summary': {
                    'total_segments': len(segments),
                    'average_score': np.mean([s.combined_score for s in segments]),
                    'score_range': {
                        'min': min([s.combined_score for s in segments]) if segments else 0,
                        'max': max([s.combined_score for s in segments]) if segments else 0
                    },
                    'total_shorts_duration': sum([s.duration for s in segments]),
                    'coverage_percentage': (sum([s.duration for s in segments]) / 
                                          (max([s.end_time for s in segments]) if segments else 1)) * 100
                }
            }
            
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salvar arquivo JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Resultados da análise exportados: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar resultados: {str(e)}")
    
    def get_analysis_summary(self, segments: List[VideoSegment]) -> Dict:
        """
        Retorna resumo da análise de engagement
        
        Args:
            segments: Lista de segmentos analisados
            
        Returns:
            Dicionário com estatísticas da análise
        """
        try:
            if not segments:
                return {}
            
            audio_scores = [s.audio_score for s in segments]
            visual_scores = [s.visual_score for s in segments]
            speech_scores = [s.speech_score for s in segments]
            combined_scores = [s.combined_score for s in segments]
            
            summary = {
                'segments_count': len(segments),
                'total_duration': sum([s.duration for s in segments]),
                'score_statistics': {
                    'audio': {
                        'mean': float(np.mean(audio_scores)),
                        'max': float(np.max(audio_scores)),
                        'min': float(np.min(audio_scores)),
                        'std': float(np.std(audio_scores))
                    },
                    'visual': {
                        'mean': float(np.mean(visual_scores)),
                        'max': float(np.max(visual_scores)),
                        'min': float(np.min(visual_scores)),
                        'std': float(np.std(visual_scores))
                    },
                    'speech': {
                        'mean': float(np.mean(speech_scores)),
                        'max': float(np.max(speech_scores)),
                        'min': float(np.min(speech_scores)),
                        'std': float(np.std(speech_scores))
                    },
                    'combined': {
                        'mean': float(np.mean(combined_scores)),
                        'max': float(np.max(combined_scores)),
                        'min': float(np.min(combined_scores)),
                        'std': float(np.std(combined_scores))
                    }
                },
                'config_used': self.config,
                'best_segment': segments[0].to_dict() if segments else None,
                'time_distribution': {
                    'first_segment': segments[0].start_time if segments else 0,
                    'last_segment': segments[-1].start_time if segments else 0,
                    'average_separation': np.mean([segments[i+1].start_time - segments[i].end_time 
                                                 for i in range(len(segments)-1)]) if len(segments) > 1 else 0
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo: {str(e)}")
            return {}