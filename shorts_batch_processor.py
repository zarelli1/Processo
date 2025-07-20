#!/usr/bin/env python3
"""
Shorts Batch Processor Module
Sistema de processamento em lote para criação de múltiplos shorts
Canal: Your_Channel_Name
"""

import os
import json
import logging
import time
import threading
from typing import Dict, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import shutil

# Importar módulos locais
from short_creator import ShortCreator
from metadata_generator import MetadataGenerator

class ShortsQualityController:
    """Controlador de qualidade para shorts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_batch_requirements(self, video_path: str, segments: List[Dict]) -> Dict:
        """
        Valida requisitos antes do processamento em lote
        
        Args:
            video_path: Caminho do vídeo original
            segments: Lista de segmentos para processar
            
        Returns:
            Dicionário com resultado da validação
        """
        try:
            issues = []
            warnings = []
            
            # Verificar arquivo de vídeo
            if not os.path.exists(video_path):
                issues.append(f"Vídeo não encontrado: {video_path}")
            else:
                # Verificar tamanho do arquivo
                file_size_gb = os.path.getsize(video_path) / (1024**3)
                if file_size_gb > 10:
                    warnings.append(f"Arquivo muito grande: {file_size_gb:.1f}GB")
                elif file_size_gb < 0.01:
                    issues.append(f"Arquivo muito pequeno: {file_size_gb*1024:.1f}MB")
            
            # Verificar segmentos
            if not segments:
                issues.append("Nenhum segmento para processar")
            elif len(segments) > 10:
                warnings.append(f"Muitos segmentos: {len(segments)} (recomendado: ≤7)")
            
            # Verificar cada segmento
            for i, segment in enumerate(segments):
                if 'start_time' not in segment or 'end_time' not in segment:
                    issues.append(f"Segmento {i+1} sem timestamps")
                    continue
                
                duration = segment['end_time'] - segment['start_time']
                if duration < 10:
                    warnings.append(f"Segmento {i+1} muito curto: {duration:.1f}s")
                elif duration > 120:
                    warnings.append(f"Segmento {i+1} muito longo: {duration:.1f}s")
            
            # Verificar espaço em disco
            try:
                import psutil
                disk_free_gb = psutil.disk_usage('.').free / (1024**3)
                estimated_output_size = len(segments) * 0.5  # Estimativa: 500MB por short
                
                if disk_free_gb < estimated_output_size * 2:  # Margem de segurança
                    issues.append(f"Pouco espaço em disco: {disk_free_gb:.1f}GB livre, "
                                f"necessário: ~{estimated_output_size*2:.1f}GB")
            except:
                warnings.append("Não foi possível verificar espaço em disco")
            
            return {
                'is_valid': len(issues) == 0,
                'issues': issues,
                'warnings': warnings,
                'segments_count': len(segments),
                'estimated_time_minutes': len(segments) * 2  # 2 min por short
            }
            
        except Exception as e:
            self.logger.error(f"Erro na validação: {str(e)}")
            return {
                'is_valid': False,
                'issues': [f"Erro na validação: {str(e)}"],
                'warnings': []
            }
    
    def check_output_integrity(self, shorts_info: List[Dict]) -> Dict:
        """
        Verifica integridade dos shorts criados
        
        Args:
            shorts_info: Lista de informações dos shorts
            
        Returns:
            Relatório de integridade
        """
        try:
            successful = []
            failed = []
            warnings = []
            
            for short_info in shorts_info:
                if short_info.get('created_successfully', False):
                    # Verificar se arquivo existe e tem tamanho adequado
                    output_path = short_info.get('output_path')
                    if output_path and os.path.exists(output_path):
                        file_size = os.path.getsize(output_path)
                        if file_size > 1024 * 1024:  # Maior que 1MB
                            successful.append(short_info)
                        else:
                            warnings.append(f"Arquivo muito pequeno: {short_info['filename']}")
                            failed.append(short_info)
                    else:
                        failed.append(short_info)
                else:
                    failed.append(short_info)
            
            return {
                'total_shorts': len(shorts_info),
                'successful': len(successful),
                'failed': len(failed),
                'warnings_count': len(warnings),
                'success_rate': len(successful) / len(shorts_info) * 100 if shorts_info else 0,
                'successful_shorts': successful,
                'failed_shorts': failed,
                'warnings': warnings
            }
            
        except Exception as e:
            self.logger.error(f"Erro na verificação de integridade: {str(e)}")
            return {'error': str(e)}

class ShortsBatchProcessor:
    """Processador em lote para criação de shorts"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações
        self.config = config or {
            'output_dir': 'shorts',
            'backup_original': True,
            'backup_dir': 'backup',
            'max_parallel_jobs': 2,
            'recovery_enabled': True,
            'progress_callback': None,
            'create_thumbnails': True,
            'save_metadata_files': True
        }
        
        # Inicializar componentes
        self.short_creator = ShortCreator()
        self.metadata_generator = MetadataGenerator()
        self.quality_controller = ShortsQualityController()
        
        # Estado do processamento
        self._processing_state = {
            'is_running': False,
            'current_step': '',
            'progress': 0,
            'total_steps': 0,
            'start_time': None,
            'errors': []
        }
        
        # Lock para thread safety
        self._state_lock = threading.Lock()
        
        self.logger.info("ShortsBatchProcessor inicializado")
    
    def _update_progress(self, step: str, current: int, total: int, details: str = ""):
        """Atualiza estado do progresso"""
        with self._state_lock:
            self._processing_state.update({
                'current_step': step,
                'progress': current,
                'total_steps': total,
                'details': details
            })
        
        # Callback de progresso
        if self.config.get('progress_callback'):
            try:
                progress_pct = (current / total * 100) if total > 0 else 0
                self.config['progress_callback'](step, progress_pct, details)
            except Exception as e:
                self.logger.warning(f"Erro no callback de progresso: {str(e)}")
    
    def get_processing_state(self) -> Dict:
        """Retorna estado atual do processamento"""
        with self._state_lock:
            state = self._processing_state.copy()
            
            # Calcular tempo decorrido
            if state['start_time']:
                elapsed = time.time() - state['start_time']
                state['elapsed_time'] = elapsed
                
                # Estimativa de tempo restante
                if state['progress'] > 0:
                    eta = (elapsed / state['progress']) * (state['total_steps'] - state['progress'])
                    state['eta_seconds'] = eta
            
            return state
    
    def backup_original_video(self, video_path: str) -> Optional[str]:
        """
        Cria backup do vídeo original
        
        Args:
            video_path: Caminho do vídeo original
            
        Returns:
            Caminho do backup ou None se falhou
        """
        try:
            if not self.config['backup_original']:
                return None
            
            backup_dir = self.config['backup_dir']
            os.makedirs(backup_dir, exist_ok=True)
            
            filename = os.path.basename(video_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{timestamp}_{filename}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            self.logger.info(f"Criando backup: {backup_path}")
            shutil.copy2(video_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {str(e)}")
            return None
    
    def process_single_short(self, 
                           video_path: str,
                           segment: Dict,
                           part_number: int,
                           title: str,
                           hashtags: List[str],
                           metadata: Dict) -> Dict:
        """
        Processa um único short
        
        Args:
            video_path: Caminho do vídeo original
            segment: Dados do segmento
            part_number: Número da parte
            title: Título base
            hashtags: Lista de hashtags
            metadata: Metadados pré-gerados
            
        Returns:
            Resultado do processamento
        """
        try:
            self.logger.info(f"Processando short {part_number}")
            
            # Criar diretório de saída
            output_dir = self.config['output_dir']
            os.makedirs(output_dir, exist_ok=True)
            
            # Criar short
            short_info = self.short_creator.create_short(
                video_path=video_path,
                segment=segment,
                part_number=part_number,
                title=title,
                hashtags=hashtags,
                output_dir=output_dir
            )
            
            # Validar qualidade
            if short_info.get('created_successfully', False):
                validation = self.short_creator.validate_short_quality(short_info)
                short_info['validation'] = validation
                
                # Criar thumbnail se configurado
                if self.config['create_thumbnails'] and validation['is_valid']:
                    thumbnail_path = short_info['output_path'].replace('.mp4', '_thumb.jpg')
                    middle_time = (segment['start_time'] + segment['end_time']) / 2
                    
                    if self.short_creator.generate_thumbnail(video_path, middle_time, thumbnail_path):
                        short_info['thumbnail_path'] = thumbnail_path
                
                # Salvar metadados se configurado
                if self.config['save_metadata_files']:
                    metadata_path = short_info['output_path'].replace('.mp4', '_metadata.json')
                    self.metadata_generator.save_metadata_file(metadata, metadata_path)
                    short_info['metadata_path'] = metadata_path
            
            # Adicionar metadados ao resultado
            short_info['metadata'] = metadata
            
            return short_info
            
        except Exception as e:
            self.logger.error(f"Erro ao processar short {part_number}: {str(e)}")
            return {
                'part_number': part_number,
                'created_successfully': False,
                'error': str(e),
                'metadata': metadata
            }
    
    def process_batch_parallel(self,
                             video_path: str,
                             segments: List[Dict],
                             title: str,
                             hashtags: List[str]) -> List[Dict]:
        """
        Processa shorts em paralelo
        
        Args:
            video_path: Caminho do vídeo original
            segments: Lista de segmentos
            title: Título base
            hashtags: Lista de hashtags
            
        Returns:
            Lista de resultados dos shorts
        """
        try:
            # Gerar metadados para todos os shorts
            self._update_progress("Gerando metadados", 0, len(segments))
            
            batch_metadata = self.metadata_generator.generate_batch_metadata(
                title, segments, hashtags
            )
            
            # Processar shorts em paralelo
            shorts_results = []
            max_workers = min(self.config['max_parallel_jobs'], len(segments))
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submeter tarefas
                future_to_part = {}
                
                for i, (segment, metadata) in enumerate(zip(segments, batch_metadata), 1):
                    future = executor.submit(
                        self.process_single_short,
                        video_path, segment, i, title, hashtags, metadata
                    )
                    future_to_part[future] = i
                
                # Coletar resultados
                completed = 0
                for future in as_completed(future_to_part):
                    part_number = future_to_part[future]
                    
                    try:
                        result = future.result()
                        shorts_results.append(result)
                        
                        completed += 1
                        self._update_progress(
                            "Criando shorts", 
                            completed, 
                            len(segments),
                            f"Short {part_number} concluído"
                        )
                        
                        if result.get('created_successfully', False):
                            self.logger.info(f"✓ Short {part_number} criado com sucesso")
                        else:
                            self.logger.error(f"✗ Falha no short {part_number}: {result.get('error', 'Erro desconhecido')}")
                    
                    except Exception as e:
                        self.logger.error(f"Erro no processamento paralelo (parte {part_number}): {str(e)}")
                        shorts_results.append({
                            'part_number': part_number,
                            'created_successfully': False,
                            'error': str(e)
                        })
            
            # Ordenar resultados por número da parte
            shorts_results.sort(key=lambda x: x.get('part_number', 0))
            
            return shorts_results
            
        except Exception as e:
            self.logger.error(f"Erro no processamento paralelo: {str(e)}")
            raise
    
    def process_batch_sequential(self,
                               video_path: str,
                               segments: List[Dict],
                               title: str,
                               hashtags: List[str]) -> List[Dict]:
        """
        Processa shorts sequencialmente (mais estável)
        
        Args:
            video_path: Caminho do vídeo original
            segments: Lista de segmentos  
            title: Título base
            hashtags: Lista de hashtags
            
        Returns:
            Lista de resultados dos shorts
        """
        try:
            # Gerar metadados
            self._update_progress("Gerando metadados", 0, len(segments))
            
            batch_metadata = self.metadata_generator.generate_batch_metadata(
                title, segments, hashtags
            )
            
            # Processar sequencialmente
            shorts_results = []
            
            for i, (segment, metadata) in enumerate(zip(segments, batch_metadata), 1):
                self._update_progress(
                    "Criando shorts", 
                    i-1, 
                    len(segments),
                    f"Processando short {i}"
                )
                
                result = self.process_single_short(
                    video_path, segment, i, title, hashtags, metadata
                )
                
                shorts_results.append(result)
                
                if result.get('created_successfully', False):
                    self.logger.info(f"✓ Short {i} criado com sucesso")
                else:
                    self.logger.error(f"✗ Falha no short {i}: {result.get('error', 'Erro desconhecido')}")
            
            return shorts_results
            
        except Exception as e:
            self.logger.error(f"Erro no processamento sequencial: {str(e)}")
            raise
    
    def create_shorts_batch(self,
                          video_path: str,
                          segments: List[Dict],
                          title: str,
                          hashtags: List[str] = None,
                          parallel: bool = True) -> Dict:
        """
        Cria lote completo de shorts
        
        Args:
            video_path: Caminho do vídeo original
            segments: Lista de segmentos
            title: Título base
            hashtags: Lista de hashtags
            parallel: Se deve processar em paralelo
            
        Returns:
            Relatório completo do processamento
        """
        try:
            with self._state_lock:
                self._processing_state.update({
                    'is_running': True,
                    'start_time': time.time(),
                    'errors': []
                })
            
            self.logger.info(f"Iniciando criação de {len(segments)} shorts")
            
            # Usar hashtags padrão se não fornecidas
            if hashtags is None:
                hashtags = self.metadata_generator.config['default_hashtags']
            
            # Validar requisitos
            self._update_progress("Validando requisitos", 0, 1)
            validation = self.quality_controller.validate_batch_requirements(video_path, segments)
            
            if not validation['is_valid']:
                raise Exception(f"Validação falhou: {'; '.join(validation['issues'])}")
            
            if validation['warnings']:
                for warning in validation['warnings']:
                    self.logger.warning(warning)
            
            # Criar backup se configurado
            backup_path = None
            if self.config['backup_original']:
                self._update_progress("Criando backup", 0, 1)
                backup_path = self.backup_original_video(video_path)
            
            # Processar shorts
            if parallel and len(segments) > 1:
                shorts_results = self.process_batch_parallel(video_path, segments, title, hashtags)
            else:
                shorts_results = self.process_batch_sequential(video_path, segments, title, hashtags)
            
            # Verificar integridade
            self._update_progress("Verificando integridade", 0, 1)
            integrity_report = self.quality_controller.check_output_integrity(shorts_results)
            
            # Preparar relatório final
            processing_state = self.get_processing_state()
            
            final_report = {
                'processing_info': {
                    'video_path': video_path,
                    'title': title,
                    'segments_processed': len(segments),
                    'processing_time': processing_state.get('elapsed_time', 0),
                    'parallel_processing': parallel,
                    'backup_created': backup_path is not None,
                    'backup_path': backup_path
                },
                'results': {
                    'shorts_created': shorts_results,
                    'integrity_report': integrity_report,
                    'validation': validation
                },
                'summary': {
                    'total_shorts': len(segments),
                    'successful_shorts': integrity_report.get('successful', 0),
                    'failed_shorts': integrity_report.get('failed', 0),
                    'success_rate': integrity_report.get('success_rate', 0),
                    'total_output_size_mb': sum([
                        s.get('file_size', 0) / (1024*1024) 
                        for s in shorts_results 
                        if s.get('created_successfully', False)
                    ])
                },
                'completed_at': datetime.now().isoformat()
            }
            
            # Log resumo
            success_count = integrity_report.get('successful', 0)
            total_count = len(segments)
            self.logger.info(f"Processamento concluído: {success_count}/{total_count} shorts criados com sucesso")
            
            return final_report
            
        except Exception as e:
            self.logger.error(f"Erro no processamento em lote: {str(e)}")
            raise
        finally:
            with self._state_lock:
                self._processing_state['is_running'] = False
    
    def cleanup_temp_files(self):
        """Limpa arquivos temporários"""
        try:
            temp_patterns = ['temp/audio_temp.m4a', 'temp/*.tmp']
            
            for pattern in temp_patterns:
                import glob
                for temp_file in glob.glob(pattern):
                    try:
                        os.remove(temp_file)
                        self.logger.debug(f"Arquivo temporário removido: {temp_file}")
                    except:
                        pass
                        
        except Exception as e:
            self.logger.warning(f"Erro na limpeza: {str(e)}")
    
    def get_batch_summary_report(self, report: Dict) -> str:
        """
        Gera relatório textual resumido
        
        Args:
            report: Relatório do processamento
            
        Returns:
            String com resumo formatado
        """
        try:
            summary = report['summary']
            processing_info = report['processing_info']
            
            report_text = f"""
📊 RELATÓRIO DE CRIAÇÃO DE SHORTS
================================

🎥 Vídeo: {os.path.basename(processing_info['video_path'])}
📝 Título: {processing_info['title']}

📈 RESULTADOS:
• Total de shorts: {summary['total_shorts']}
• Criados com sucesso: {summary['successful_shorts']}
• Falharam: {summary['failed_shorts']}
• Taxa de sucesso: {summary['success_rate']:.1f}%
• Tamanho total: {summary['total_output_size_mb']:.1f} MB

⏱️ TEMPO:
• Processamento: {processing_info['processing_time']:.1f} segundos
• Modo: {'Paralelo' if processing_info['parallel_processing'] else 'Sequencial'}

💾 BACKUP:
• Criado: {'Sim' if processing_info['backup_created'] else 'Não'}

✅ STATUS: {'SUCESSO' if summary['success_rate'] > 80 else 'PARCIAL' if summary['success_rate'] > 50 else 'FALHA'}
"""
            return report_text
            
        except Exception as e:
            return f"Erro ao gerar relatório: {str(e)}"