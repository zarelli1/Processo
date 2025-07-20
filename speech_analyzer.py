#!/usr/bin/env python3
"""
Speech Analyzer Module
Sistema de análise de fala para detectar palavras-chave e momentos relevantes
Canal: Leonardo_Zarelli
"""

import os
import logging
import re
from typing import Dict, List, Tuple, Optional
import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class SpeechAnalyzer:
    """Classe para análise de fala e detecção de palavras-chave"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.audio_path = None
        self.segments = []
        self.transcription_cache = {}
        
        # Palavras-chave importantes para identificar momentos relevantes
        self.keywords = {
            'impact': [
                'incrível', 'inacreditável', 'impressionante', 'fantástico',
                'extraordinário', 'surpreendente', 'espetacular'
            ],
            'attention': [
                'importante', 'atenção', 'cuidado', 'veja', 'olha',
                'escuta', 'observe', 'repare', 'note'
            ],
            'revelation': [
                'resultado', 'descoberta', 'revelação', 'segredo',
                'mistério', 'verdade', 'resposta'
            ],
            'instruction': [
                'dica', 'método', 'técnica', 'estratégia', 'forma',
                'maneira', 'jeito', 'modo', 'como fazer'
            ],
            'emotion': [
                'amor', 'ódio', 'medo', 'alegria', 'tristeza',
                'raiva', 'surpresa', 'êxtase', 'paixão'
            ],
            'action': [
                'vamos', 'faça', 'execute', 'realize', 'comece',
                'inicie', 'termine', 'finalize', 'clique'
            ],
            'technology': [
                'inteligência artificial', 'ia', 'tecnologia', 'inovação',
                'futuro', 'revolução', 'automação', 'digital'
            ],
            'money': [
                'dinheiro', 'lucro', 'ganhar', 'economia', 'investimento',
                'renda', 'negócio', 'empreendimento', 'sucesso'
            ]
        }
        
        # Configurações de análise
        self.segment_duration = 30  # Segundos por segmento
        self.overlap_duration = 5   # Sobreposição entre segmentos
        
    def load_audio_from_video(self, video_path: str) -> bool:
        """
        Extrai e carrega áudio de um vídeo
        
        Args:
            video_path: Caminho para o arquivo de vídeo
            
        Returns:
            True se carregou com sucesso
        """
        try:
            self.logger.info(f"Extraindo áudio de: {video_path}")
            
            # Extrair áudio usando pydub
            audio = AudioSegment.from_file(video_path)
            
            # Converter para formato adequado para speech recognition
            audio = audio.set_frame_rate(16000).set_channels(1)
            
            # Salvar áudio temporário
            temp_audio_path = "temp/extracted_audio.wav"
            os.makedirs(os.path.dirname(temp_audio_path), exist_ok=True)
            audio.export(temp_audio_path, format="wav")
            
            self.audio_path = temp_audio_path
            
            # Dividir áudio em segmentos
            self._create_audio_segments(audio)
            
            self.logger.info(f"Áudio extraído e segmentado: {len(self.segments)} segmentos")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar áudio: {str(e)}")
            return False
    
    def _create_audio_segments(self, audio: AudioSegment):
        """
        Divide áudio em segmentos para processamento
        
        Args:
            audio: AudioSegment do pydub
        """
        try:
            self.segments = []
            duration_ms = len(audio)
            segment_ms = self.segment_duration * 1000
            overlap_ms = self.overlap_duration * 1000
            
            start_ms = 0
            segment_index = 0
            
            while start_ms < duration_ms:
                end_ms = min(start_ms + segment_ms, duration_ms)
                
                # Extrair segmento
                segment = audio[start_ms:end_ms]
                
                # Salvar segmento temporário
                segment_path = f"temp/segment_{segment_index:03d}.wav"
                segment.export(segment_path, format="wav")
                
                # Adicionar à lista
                self.segments.append({
                    'index': segment_index,
                    'start_time': start_ms / 1000.0,
                    'end_time': end_ms / 1000.0,
                    'duration': (end_ms - start_ms) / 1000.0,
                    'path': segment_path
                })
                
                # Próximo segmento com sobreposição
                start_ms += segment_ms - overlap_ms
                segment_index += 1
            
            self.logger.info(f"Criados {len(self.segments)} segmentos de áudio")
            
        except Exception as e:
            self.logger.error(f"Erro ao criar segmentos: {str(e)}")
    
    def transcribe_segment(self, segment: Dict) -> Optional[str]:
        """
        Transcreve um segmento de áudio
        
        Args:
            segment: Dicionário com informações do segmento
            
        Returns:
            Texto transcrito ou None se falhou
        """
        try:
            # Verificar cache
            cache_key = f"{segment['index']}_{segment['duration']}"
            if cache_key in self.transcription_cache:
                return self.transcription_cache[cache_key]
            
            # Carregar áudio do segmento
            with sr.AudioFile(segment['path']) as source:
                audio_data = self.recognizer.record(source)
            
            # Tentar transcrição com Google (gratuito)
            try:
                text = self.recognizer.recognize_google(audio_data, language='pt-BR')
                self.transcription_cache[cache_key] = text
                
                self.logger.debug(f"Segmento {segment['index']} transcrito: {text[:50]}...")
                return text
                
            except sr.UnknownValueError:
                self.logger.debug(f"Segmento {segment['index']}: fala não detectada")
                return ""
            except sr.RequestError as e:
                self.logger.warning(f"Erro na API de transcrição: {e}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao transcrever segmento {segment['index']}: {str(e)}")
            return None
    
    def transcribe_all_segments(self, max_workers: int = 3) -> Dict[int, str]:
        """
        Transcreve todos os segmentos em paralelo
        
        Args:
            max_workers: Número máximo de workers para processamento paralelo
            
        Returns:
            Dicionário {segment_index: transcription}
        """
        try:
            transcriptions = {}
            
            self.logger.info(f"Iniciando transcrição de {len(self.segments)} segmentos")
            
            # Processar em paralelo
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter tarefas
                future_to_segment = {
                    executor.submit(self.transcribe_segment, segment): segment
                    for segment in self.segments
                }
                
                # Coletar resultados
                completed = 0
                for future in as_completed(future_to_segment):
                    segment = future_to_segment[future]
                    
                    try:
                        transcription = future.result()
                        if transcription is not None:
                            transcriptions[segment['index']] = transcription
                        
                        completed += 1
                        
                        if completed % 5 == 0:  # Log a cada 5 segmentos
                            self.logger.info(f"Transcrição: {completed}/{len(self.segments)} segmentos processados")
                            
                    except Exception as e:
                        self.logger.error(f"Erro no segmento {segment['index']}: {str(e)}")
            
            self.logger.info(f"Transcrição concluída: {len(transcriptions)} segmentos com texto")
            return transcriptions
            
        except Exception as e:
            self.logger.error(f"Erro na transcrição paralela: {str(e)}")
            return {}
    
    def analyze_keywords_in_text(self, text: str) -> Dict[str, List[str]]:
        """
        Analisa palavras-chave em um texto
        
        Args:
            text: Texto para análise
            
        Returns:
            Dicionário {categoria: [palavras_encontradas]}
        """
        if not text:
            return {}
        
        text_lower = text.lower()
        found_keywords = {}
        
        for category, keywords in self.keywords.items():
            found_in_category = []
            
            for keyword in keywords:
                # Buscar palavra-chave (word boundary para evitar matches parciais)
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text_lower):
                    found_in_category.append(keyword)
            
            if found_in_category:
                found_keywords[category] = found_in_category
        
        return found_keywords
    
    def calculate_keyword_density(self, transcriptions: Dict[int, str]) -> List[float]:
        """
        Calcula densidade de palavras-chave por segmento
        
        Args:
            transcriptions: Dicionário {segment_index: transcription}
            
        Returns:
            Lista de scores de densidade por segmento
        """
        try:
            density_scores = []
            
            for segment in self.segments:
                segment_idx = segment['index']
                text = transcriptions.get(segment_idx, "")
                
                if not text:
                    density_scores.append(0.0)
                    continue
                
                # Analisar palavras-chave
                found_keywords = self.analyze_keywords_in_text(text)
                
                # Calcular score baseado em categorias e quantidade
                total_score = 0.0
                word_count = len(text.split())
                
                if word_count == 0:
                    density_scores.append(0.0)
                    continue
                
                # Pesos por categoria
                category_weights = {
                    'impact': 3.0,
                    'attention': 2.5,
                    'revelation': 3.0,
                    'instruction': 2.0,
                    'emotion': 1.5,
                    'action': 2.0,
                    'technology': 2.5,
                    'money': 2.0
                }
                
                for category, keywords_found in found_keywords.items():
                    weight = category_weights.get(category, 1.0)
                    keyword_score = len(keywords_found) * weight
                    total_score += keyword_score
                
                # Normalizar por contagem de palavras
                density_score = min(total_score / word_count, 1.0)
                density_scores.append(density_score)
            
            self.logger.info(f"Calculada densidade de palavras-chave: {len(density_scores)} scores")
            return density_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao calcular densidade: {str(e)}")
            return []
    
    def get_speech_score_timeline(self, interval_seconds: float = 1.0) -> List[float]:
        """
        Gera timeline de scores de fala
        
        Args:
            interval_seconds: Intervalo para timeline
            
        Returns:
            Lista de scores por segundo
        """
        try:
            if not self.segments:
                return []
            
            # Transcrever todos os segmentos
            transcriptions = self.transcribe_all_segments()
            
            # Calcular densidade por segmento
            segment_densities = self.calculate_keyword_density(transcriptions)
            
            # Converter para timeline por segundo
            total_duration = max(segment['end_time'] for segment in self.segments)
            timeline_length = int(total_duration / interval_seconds) + 1
            timeline_scores = [0.0] * timeline_length
            
            # Mapear scores de segmentos para timeline
            for i, segment in enumerate(self.segments):
                if i < len(segment_densities):
                    score = segment_densities[i]
                    
                    # Distribuir score ao longo do segmento
                    start_idx = int(segment['start_time'] / interval_seconds)
                    end_idx = int(segment['end_time'] / interval_seconds)
                    
                    for timeline_idx in range(start_idx, min(end_idx + 1, len(timeline_scores))):
                        timeline_scores[timeline_idx] = max(timeline_scores[timeline_idx], score)
            
            self.logger.info(f"Timeline de speech score gerada: {len(timeline_scores)} pontos")
            return timeline_scores
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar timeline: {str(e)}")
            return []
    
    def get_most_relevant_moments(self, top_n: int = 7) -> List[Tuple[float, float, float, str]]:
        """
        Identifica os momentos mais relevantes baseados na análise de fala
        
        Args:
            top_n: Número de momentos para retornar
            
        Returns:
            Lista de tuplas (start_time, end_time, score, keywords_summary)
        """
        try:
            transcriptions = self.transcribe_all_segments()
            segment_densities = self.calculate_keyword_density(transcriptions)
            
            # Criar lista de momentos com scores
            moments = []
            
            for i, segment in enumerate(self.segments):
                if i < len(segment_densities):
                    score = segment_densities[i]
                    text = transcriptions.get(segment['index'], "")
                    
                    # Resumo das palavras-chave encontradas
                    found_keywords = self.analyze_keywords_in_text(text)
                    keywords_summary = ""
                    
                    for category, keywords in found_keywords.items():
                        if keywords:
                            keywords_summary += f"{category}: {', '.join(keywords[:3])}; "
                    
                    moments.append((
                        segment['start_time'],
                        segment['end_time'],
                        score,
                        keywords_summary.strip()
                    ))
            
            # Ordenar por score (maior primeiro)
            moments.sort(key=lambda x: x[2], reverse=True)
            
            # Retornar top N
            top_moments = moments[:top_n]
            
            self.logger.info(f"Identificados {len(top_moments)} momentos mais relevantes")
            return top_moments
            
        except Exception as e:
            self.logger.error(f"Erro ao identificar momentos relevantes: {str(e)}")
            return []
    
    def get_analysis_summary(self) -> Dict:
        """
        Retorna resumo da análise de fala
        
        Returns:
            Dicionário com estatísticas da análise
        """
        try:
            if not self.segments:
                return {}
            
            transcriptions = self.transcribe_all_segments()
            density_scores = self.calculate_keyword_density(transcriptions)
            
            # Estatísticas gerais
            total_segments = len(self.segments)
            transcribed_segments = len([t for t in transcriptions.values() if t])
            
            # Análise de palavras-chave
            all_keywords = {}
            total_words = 0
            
            for text in transcriptions.values():
                if text:
                    total_words += len(text.split())
                    found = self.analyze_keywords_in_text(text)
                    
                    for category, keywords in found.items():
                        if category not in all_keywords:
                            all_keywords[category] = set()
                        all_keywords[category].update(keywords)
            
            # Converter sets para listas para serialização
            keyword_summary = {cat: list(keywords) for cat, keywords in all_keywords.items()}
            
            summary = {
                'segments': {
                    'total': total_segments,
                    'transcribed': transcribed_segments,
                    'success_rate': transcribed_segments / total_segments if total_segments > 0 else 0
                },
                'transcription': {
                    'total_words': total_words,
                    'average_words_per_segment': total_words / transcribed_segments if transcribed_segments > 0 else 0
                },
                'keyword_analysis': {
                    'categories_found': len(all_keywords),
                    'total_unique_keywords': sum(len(keywords) for keywords in all_keywords.values()),
                    'keywords_by_category': keyword_summary
                },
                'density_scores': {
                    'mean': float(np.mean(density_scores)) if density_scores else 0,
                    'max': float(np.max(density_scores)) if density_scores else 0,
                    'segments_with_keywords': len([s for s in density_scores if s > 0])
                }
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar resumo de fala: {str(e)}")
            return {}
    
    def cleanup(self):
        """Limpa arquivos temporários e cache"""
        try:
            # Limpar segmentos temporários
            for segment in self.segments:
                if os.path.exists(segment['path']):
                    os.remove(segment['path'])
            
            # Limpar áudio extraído
            if self.audio_path and os.path.exists(self.audio_path):
                os.remove(self.audio_path)
            
            # Limpar cache
            self.transcription_cache.clear()
            self.segments.clear()
            
            self.logger.debug("Recursos de speech analysis liberados")
            
        except Exception as e:
            self.logger.error(f"Erro na limpeza: {str(e)}")