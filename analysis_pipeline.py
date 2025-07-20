#!/usr/bin/env python3
"""
Analysis Pipeline Module
Pipeline de análise com threading e cache para processamento paralelo
Canal: Leonardo_Zarelli
"""

import os
import json
import hashlib
import logging
import threading
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import time

# Importar analisadores
from audio_analyzer import AudioAnalyzer
from visual_analyzer import VisualAnalyzer
from speech_analyzer import SpeechAnalyzer
from engagement_scorer import EngagementScorer, VideoSegment

class AnalysisPipeline:
    """Pipeline de análise com processamento paralelo e cache"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = config or {
            'cache_enabled': True,
            'cache_dir': 'temp/cache',
            'max_workers': 3,
            'progress_callback': None,
            'export_graphs': True,
            'analysis_interval': 1.0  # Análise por segundo
        }
        
        # Inicializar analisadores
        self.audio_analyzer = AudioAnalyzer()
        self.visual_analyzer = VisualAnalyzer()
        self.speech_analyzer = SpeechAnalyzer()
        self.engagement_scorer = EngagementScorer()
        
        # Cache
        self.cache_enabled = self.config['cache_enabled']
        self.cache_dir = self.config['cache_dir']
        
        # Threading
        self._analysis_lock = threading.Lock()
        self._progress_lock = threading.Lock()
        self._current_progress = {}
        
        # Criar diretório de cache
        if self.cache_enabled:
            os.makedirs(self.cache_dir, exist_ok=True)
        
        self.logger.info("Pipeline de análise inicializado")
    
    def _generate_cache_key(self, video_path: str, analysis_type: str) -> str:
        """
        Gera chave única para cache baseada no arquivo e tipo de análise
        
        Args:
            video_path: Caminho do vídeo
            analysis_type: Tipo de análise (audio, visual, speech)
            
        Returns:
            Chave única para cache
        """
        try:
            # Usar hash do arquivo + tipo + timestamp de modificação
            file_stat = os.stat(video_path)
            content = f"{video_path}_{analysis_type}_{file_stat.st_mtime}_{file_stat.st_size}"
            
            hash_obj = hashlib.md5(content.encode())
            return hash_obj.hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Erro ao gerar chave de cache: {str(e)}")
            return f"{analysis_type}_{int(time.time())}"
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """
        Salva dados no cache
        
        Args:
            cache_key: Chave do cache
            data: Dados para salvar
        """
        if not self.cache_enabled:
            return
        
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': data
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Dados salvos no cache: {cache_key}")
            
        except Exception as e:
            self.logger.warning(f"Erro ao salvar cache {cache_key}: {str(e)}")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """
        Carrega dados do cache
        
        Args:
            cache_key: Chave do cache
            
        Returns:
            Dados do cache ou None se não encontrado
        """
        if not self.cache_enabled:
            return None
        
        try:
            cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            self.logger.debug(f"Dados carregados do cache: {cache_key}")
            return cache_data.get('data')
            
        except Exception as e:
            self.logger.warning(f"Erro ao carregar cache {cache_key}: {str(e)}")
            return None
    
    def _update_progress(self, analysis_type: str, progress: float, status: str = ""):
        """
        Atualiza progresso da análise
        
        Args:
            analysis_type: Tipo de análise
            progress: Progresso (0-100)
            status: Status adicional
        """
        with self._progress_lock:
            self._current_progress[analysis_type] = {
                'progress': progress,
                'status': status,
                'timestamp': datetime.now().isoformat()
            }
        
        # Callback de progresso se configurado
        if self.config.get('progress_callback'):
            try:
                self.config['progress_callback'](analysis_type, progress, status)
            except Exception as e:
                self.logger.warning(f"Erro no callback de progresso: {str(e)}")
    
    def get_current_progress(self) -> Dict:
        """
        Retorna progresso atual de todas as análises
        
        Returns:
            Dicionário com progresso de cada análise
        """
        with self._progress_lock:
            return self._current_progress.copy()
    
    def analyze_audio(self, video_path: str) -> Tuple[List[float], Dict]:
        """
        Executa análise de áudio
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Tupla (timeline_scores, analysis_summary)
        """
        analysis_type = "audio"
        
        try:
            self._update_progress(analysis_type, 0, "Iniciando análise de áudio")
            
            # Verificar cache
            cache_key = self._generate_cache_key(video_path, analysis_type)
            cached_data = self._load_from_cache(cache_key)
            
            if cached_data:
                self.logger.info("Análise de áudio carregada do cache")
                self._update_progress(analysis_type, 100, "Carregado do cache")
                return cached_data['timeline'], cached_data['summary']
            
            # Carregar áudio
            self._update_progress(analysis_type, 10, "Carregando áudio")
            if not self.audio_analyzer.load_audio_from_video(video_path):
                raise Exception("Falha ao carregar áudio")
            
            # Análise de energia
            self._update_progress(analysis_type, 30, "Analisando energia sonora")
            energy_levels = self.audio_analyzer.calculate_energy_levels()
            
            # Análise de variações
            self._update_progress(analysis_type, 50, "Analisando variações de volume")
            variation_scores = self.audio_analyzer.detect_volume_variations()
            
            # Detectar silêncios
            self._update_progress(analysis_type, 70, "Detectando períodos de silêncio")
            silence_periods = self.audio_analyzer.detect_silence_periods()
            
            # Gerar timeline final
            self._update_progress(analysis_type, 90, "Gerando timeline de scores")
            timeline_scores = self.audio_analyzer.get_audio_score_timeline()
            
            # Gerar resumo
            summary = self.audio_analyzer.get_analysis_summary()
            
            # Exportar gráfico se configurado
            if self.config.get('export_graphs', True):
                self.audio_analyzer.export_audio_analysis("temp/audio_analysis.png")
            
            # Salvar no cache
            cache_data = {
                'timeline': timeline_scores,
                'summary': summary
            }
            self._save_to_cache(cache_key, cache_data)
            
            self._update_progress(analysis_type, 100, "Análise de áudio concluída")
            self.logger.info("Análise de áudio concluída")
            
            return timeline_scores, summary
            
        except Exception as e:
            self._update_progress(analysis_type, -1, f"Erro: {str(e)}")
            self.logger.error(f"Erro na análise de áudio: {str(e)}")
            raise
        finally:
            self.audio_analyzer.cleanup()
    
    def analyze_visual(self, video_path: str) -> Tuple[List[float], Dict]:
        """
        Executa análise visual
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Tupla (timeline_scores, analysis_summary)
        """
        analysis_type = "visual"
        
        try:
            self._update_progress(analysis_type, 0, "Iniciando análise visual")
            
            # Verificar cache
            cache_key = self._generate_cache_key(video_path, analysis_type)
            cached_data = self._load_from_cache(cache_key)
            
            if cached_data:
                self.logger.info("Análise visual carregada do cache")
                self._update_progress(analysis_type, 100, "Carregado do cache")
                return cached_data['timeline'], cached_data['summary']
            
            # Carregar vídeo
            self._update_progress(analysis_type, 10, "Carregando vídeo")
            if not self.visual_analyzer.load_video(video_path):
                raise Exception("Falha ao carregar vídeo")
            
            # Análise de diferenças entre frames
            self._update_progress(analysis_type, 30, "Analisando diferenças entre frames")
            frame_diffs = self.visual_analyzer.calculate_frame_differences(self.config['analysis_interval'])
            
            # Análise de movimento
            self._update_progress(analysis_type, 60, "Analisando intensidade de movimento")
            movement_scores = self.visual_analyzer.analyze_movement_intensity(self.config['analysis_interval'])
            
            # Gerar timeline final
            self._update_progress(analysis_type, 90, "Gerando timeline visual")
            timeline_scores = self.visual_analyzer.get_visual_score_timeline(self.config['analysis_interval'])
            
            # Gerar resumo
            summary = self.visual_analyzer.get_analysis_summary()
            
            # Exportar gráfico se configurado
            if self.config.get('export_graphs', True):
                self.visual_analyzer.export_visual_analysis("temp/visual_analysis.png", self.config['analysis_interval'])
            
            # Salvar no cache
            cache_data = {
                'timeline': timeline_scores,
                'summary': summary
            }
            self._save_to_cache(cache_key, cache_data)
            
            self._update_progress(analysis_type, 100, "Análise visual concluída")
            self.logger.info("Análise visual concluída")
            
            return timeline_scores, summary
            
        except Exception as e:
            self._update_progress(analysis_type, -1, f"Erro: {str(e)}")
            self.logger.error(f"Erro na análise visual: {str(e)}")
            raise
        finally:
            self.visual_analyzer.cleanup()
    
    def analyze_speech(self, video_path: str) -> Tuple[List[float], Dict]:
        """
        Executa análise de fala
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Tupla (timeline_scores, analysis_summary)
        """
        analysis_type = "speech"
        
        try:
            self._update_progress(analysis_type, 0, "Iniciando análise de fala")
            
            # Verificar cache
            cache_key = self._generate_cache_key(video_path, analysis_type)
            cached_data = self._load_from_cache(cache_key)
            
            if cached_data:
                self.logger.info("Análise de fala carregada do cache")
                self._update_progress(analysis_type, 100, "Carregado do cache")
                return cached_data['timeline'], cached_data['summary']
            
            # Carregar áudio
            self._update_progress(analysis_type, 10, "Extraindo áudio para análise")
            if not self.speech_analyzer.load_audio_from_video(video_path):
                raise Exception("Falha ao extrair áudio")
            
            # Transcrição (processo mais longo)
            self._update_progress(analysis_type, 20, "Transcrevendo segmentos de áudio")
            
            # Gerar timeline de scores
            self._update_progress(analysis_type, 80, "Analisando palavras-chave")
            timeline_scores = self.speech_analyzer.get_speech_score_timeline(self.config['analysis_interval'])
            
            # Gerar resumo
            summary = self.speech_analyzer.get_analysis_summary()
            
            # Salvar no cache
            cache_data = {
                'timeline': timeline_scores,
                'summary': summary
            }
            self._save_to_cache(cache_key, cache_data)
            
            self._update_progress(analysis_type, 100, "Análise de fala concluída")
            self.logger.info("Análise de fala concluída")
            
            return timeline_scores, summary
            
        except Exception as e:
            self._update_progress(analysis_type, -1, f"Erro: {str(e)}")
            self.logger.error(f"Erro na análise de fala: {str(e)}")
            raise
        finally:
            self.speech_analyzer.cleanup()
    
    def run_parallel_analysis(self, video_path: str) -> Dict:
        """
        Executa todas as análises em paralelo
        
        Args:
            video_path: Caminho do vídeo
            
        Returns:
            Dicionário com todos os resultados
        """
        try:
            self.logger.info("Iniciando análise paralela")
            start_time = time.time()
            
            # Executar análises em paralelo
            with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
                # Submeter tarefas
                future_audio = executor.submit(self.analyze_audio, video_path)
                future_visual = executor.submit(self.analyze_visual, video_path)
                future_speech = executor.submit(self.analyze_speech, video_path)
                
                # Coletar resultados
                results = {}
                
                # Áudio
                try:
                    audio_timeline, audio_summary = future_audio.result()
                    results['audio'] = {
                        'timeline': audio_timeline,
                        'summary': audio_summary
                    }
                    self.logger.info("✓ Análise de áudio concluída")
                except Exception as e:
                    self.logger.error(f"✗ Falha na análise de áudio: {str(e)}")
                    results['audio'] = {'timeline': [], 'summary': {}}
                
                # Visual
                try:
                    visual_timeline, visual_summary = future_visual.result()
                    results['visual'] = {
                        'timeline': visual_timeline,
                        'summary': visual_summary
                    }
                    self.logger.info("✓ Análise visual concluída")
                except Exception as e:
                    self.logger.error(f"✗ Falha na análise visual: {str(e)}")
                    results['visual'] = {'timeline': [], 'summary': {}}
                
                # Fala
                try:
                    speech_timeline, speech_summary = future_speech.result()
                    results['speech'] = {
                        'timeline': speech_timeline,
                        'summary': speech_summary
                    }
                    self.logger.info("✓ Análise de fala concluída")
                except Exception as e:
                    self.logger.error(f"✗ Falha na análise de fala: {str(e)}")
                    results['speech'] = {'timeline': [], 'summary': {}}
            
            # Calcular tempo total
            total_time = time.time() - start_time
            
            # Adicionar metadados (sem objetos não serializáveis)
            safe_config = {k: v for k, v in self.config.items() if not callable(v)}
            results['metadata'] = {
                'video_path': video_path,
                'analysis_time': total_time,
                'timestamp': datetime.now().isoformat(),
                'config': safe_config
            }
            
            self.logger.info(f"Análise paralela concluída em {total_time:.1f}s")
            return results
            
        except Exception as e:
            self.logger.error(f"Erro na análise paralela: {str(e)}")
            raise
    
    def find_best_segments(self, analysis_results: Dict, 
                          shorts_duration: int = 60, 
                          shorts_count: int = 7) -> List[VideoSegment]:
        """
        Identifica os melhores segmentos baseado nas análises
        
        Args:
            analysis_results: Resultados das análises
            shorts_duration: Duração desejada dos shorts
            shorts_count: Quantidade de shorts
            
        Returns:
            Lista dos melhores segmentos
        """
        try:
            self.logger.info(f"Identificando {shorts_count} melhores segmentos de {shorts_duration}s")
            
            # Extrair timelines
            audio_timeline = analysis_results.get('audio', {}).get('timeline', [])
            visual_timeline = analysis_results.get('visual', {}).get('timeline', [])
            speech_timeline = analysis_results.get('speech', {}).get('timeline', [])
            
            if not any([audio_timeline, visual_timeline, speech_timeline]):
                self.logger.error("Nenhuma timeline disponível para análise")
                return []
            
            # Calcular duração total (estimativa)
            max_timeline_length = max(len(audio_timeline), len(visual_timeline), len(speech_timeline))
            total_duration = max_timeline_length * self.config['analysis_interval']
            
            # Usar EngagementScorer para encontrar melhores segmentos
            best_segments = self.engagement_scorer.get_best_segments(
                audio_scores=audio_timeline,
                visual_scores=visual_timeline,
                speech_scores=speech_timeline,
                duration=shorts_duration,
                count=shorts_count,
                total_duration=total_duration,
                interval_seconds=self.config['analysis_interval']
            )
            
            # Exportar resultados
            self.engagement_scorer.export_analysis_results(best_segments, "temp/engagement_analysis.json")
            
            self.logger.info(f"Identificados {len(best_segments)} segmentos candidatos")
            return best_segments
            
        except Exception as e:
            self.logger.error(f"Erro ao encontrar melhores segmentos: {str(e)}")
            return []
    
    def analyze_video_complete(self, video_path: str, 
                             shorts_duration: int = 60, 
                             shorts_count: int = 7) -> Dict:
        """
        Pipeline completo de análise
        
        Args:
            video_path: Caminho do vídeo
            shorts_duration: Duração dos shorts
            shorts_count: Quantidade de shorts
            
        Returns:
            Dicionário com análises completas e segmentos selecionados
        """
        try:
            self.logger.info(f"Iniciando análise completa: {video_path}")
            
            # Executar análises paralelas
            analysis_results = self.run_parallel_analysis(video_path)
            
            # Encontrar melhores segmentos
            best_segments = self.find_best_segments(
                analysis_results, shorts_duration, shorts_count
            )
            
            # Preparar resultado final
            complete_results = {
                'video_path': video_path,
                'analysis_results': analysis_results,
                'best_segments': [segment.to_dict() for segment in best_segments],
                'summary': {
                    'total_analysis_time': analysis_results.get('metadata', {}).get('analysis_time', 0),
                    'segments_found': len(best_segments),
                    'shorts_duration': shorts_duration,
                    'shorts_count': shorts_count
                }
            }
            
            # Salvar resultado completo
            output_file = "temp/complete_analysis.json"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(complete_results, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Análise completa salva: {output_file}")
            return complete_results
            
        except Exception as e:
            self.logger.error(f"Erro na análise completa: {str(e)}")
            raise
    
    def cleanup(self):
        """Limpa recursos e cache temporário"""
        try:
            # Limpar analisadores
            self.audio_analyzer.cleanup()
            self.visual_analyzer.cleanup()
            self.speech_analyzer.cleanup()
            
            # Limpar progresso
            with self._progress_lock:
                self._current_progress.clear()
            
            self.logger.debug("Pipeline limpo")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza do pipeline: {str(e)}")
    
    def clear_cache(self):
        """Limpa cache de análises"""
        try:
            if not self.cache_enabled or not os.path.exists(self.cache_dir):
                return
            
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
            
            for cache_file in cache_files:
                os.remove(os.path.join(self.cache_dir, cache_file))
            
            self.logger.info(f"Cache limpo: {len(cache_files)} arquivos removidos")
            
        except Exception as e:
            self.logger.error(f"Erro ao limpar cache: {str(e)}")