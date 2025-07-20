#!/usr/bin/env python3
"""
System Validator Module
Validação de dependências, configurações e credenciais do sistema
Canal: Leonardo_Zarelli
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class SystemValidator:
    """Classe para validar configurações e dependências do sistema"""
    
    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = config_path
        self.config = {}
        self.logger = logging.getLogger(__name__)
        self.validation_results = {
            'passed': [],
            'warnings': [],
            'errors': [],
            'system_info': {}
        }
    
    def load_config(self) -> bool:
        """Carrega arquivo de configuração"""
        try:
            if not os.path.exists(self.config_path):
                self.validation_results['errors'].append(f"Arquivo de configuração não encontrado: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            self.validation_results['passed'].append("Configuração carregada com sucesso")
            self.logger.info("Configuração carregada")
            return True
            
        except json.JSONDecodeError as e:
            self.validation_results['errors'].append(f"Erro no JSON da configuração: {str(e)}")
            return False
        except Exception as e:
            self.validation_results['errors'].append(f"Erro ao carregar configuração: {str(e)}")
            return False
    
    def validate_python_version(self) -> bool:
        """Valida versão do Python"""
        try:
            version = sys.version_info
            self.validation_results['system_info']['python_version'] = f"{version.major}.{version.minor}.{version.micro}"
            
            if version < (3, 8):
                self.validation_results['errors'].append(f"Python {version.major}.{version.minor} não suportado. Requerido: 3.8+")
                return False
            elif version < (3, 9):
                self.validation_results['warnings'].append(f"Python {version.major}.{version.minor} funciona, mas recomendado: 3.9+")
            
            self.validation_results['passed'].append(f"Python {version.major}.{version.minor}.{version.micro} OK")
            return True
            
        except Exception as e:
            self.validation_results['errors'].append(f"Erro ao verificar versão Python: {str(e)}")
            return False
    
    def validate_dependencies(self) -> bool:
        """Valida dependências Python instaladas"""
        required_packages = [
            ('moviepy', 'MoviePy'),
            ('cv2', 'OpenCV'),
            ('yt_dlp', 'yt-dlp'),
            ('googleapiclient', 'Google API Client'),
            ('speech_recognition', 'SpeechRecognition'),
            ('pydub', 'PyDub'),
            ('numpy', 'NumPy'),
            ('schedule', 'Schedule'),
            ('requests', 'Requests')
        ]
        
        missing_packages = []
        installed_packages = []
        
        for package_name, display_name in required_packages:
            try:
                __import__(package_name)
                installed_packages.append(display_name)
                self.logger.debug(f"Dependência OK: {display_name}")
            except ImportError:
                missing_packages.append(display_name)
                self.logger.warning(f"Dependência faltando: {display_name}")
        
        if missing_packages:
            self.validation_results['errors'].append(f"Dependências faltando: {', '.join(missing_packages)}")
            return False
        
        self.validation_results['passed'].append(f"Todas as dependências instaladas: {', '.join(installed_packages)}")
        return True
    
    def validate_ffmpeg(self) -> bool:
        """Verifica se FFmpeg está instalado"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Extrair versão do FFmpeg
                version_line = result.stdout.split('\n')[0]
                version = version_line.split(' ')[2] if len(version_line.split(' ')) > 2 else "desconhecida"
                
                self.validation_results['system_info']['ffmpeg_version'] = version
                self.validation_results['passed'].append(f"FFmpeg instalado: {version}")
                return True
            else:
                self.validation_results['errors'].append("FFmpeg não responde corretamente")
                return False
                
        except subprocess.TimeoutExpired:
            self.validation_results['errors'].append("FFmpeg não responde (timeout)")
            return False
        except FileNotFoundError:
            self.validation_results['errors'].append("FFmpeg não encontrado. Instale: https://ffmpeg.org/download.html")
            return False
        except Exception as e:
            self.validation_results['errors'].append(f"Erro ao verificar FFmpeg: {str(e)}")
            return False
    
    def validate_directories(self) -> bool:
        """Valida e cria diretórios necessários"""
        if not self.config:
            return False
        
        directories = self.config.get('directories', {})
        created_dirs = []
        permission_errors = []
        
        for dir_name, dir_path in directories.items():
            try:
                # Criar diretório se não existir
                os.makedirs(dir_path, exist_ok=True)
                
                # Testar permissões de escrita
                test_file = os.path.join(dir_path, '.test_permission')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                
                created_dirs.append(f"{dir_name}: {dir_path}")
                self.logger.debug(f"Diretório OK: {dir_path}")
                
            except PermissionError:
                permission_errors.append(f"{dir_name}: {dir_path}")
                self.logger.error(f"Sem permissão: {dir_path}")
            except Exception as e:
                permission_errors.append(f"{dir_name}: {dir_path} ({str(e)})")
                self.logger.error(f"Erro no diretório {dir_path}: {str(e)}")
        
        if permission_errors:
            self.validation_results['errors'].append(f"Problemas de permissão: {'; '.join(permission_errors)}")
            return False
        
        if created_dirs:
            self.validation_results['passed'].append(f"Diretórios OK: {'; '.join(created_dirs)}")
        
        return True
    
    def validate_disk_space(self, min_gb: float = 5.0) -> bool:
        """Verifica espaço em disco disponível"""
        try:
            import psutil
            
            # Verificar espaço no diretório atual
            disk_usage = psutil.disk_usage('.')
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            
            self.validation_results['system_info']['disk_free_gb'] = f"{free_gb:.1f}"
            self.validation_results['system_info']['disk_total_gb'] = f"{total_gb:.1f}"
            
            if free_gb < min_gb:
                self.validation_results['errors'].append(f"Pouco espaço em disco: {free_gb:.1f}GB (mínimo: {min_gb}GB)")
                return False
            elif free_gb < min_gb * 2:
                self.validation_results['warnings'].append(f"Espaço em disco baixo: {free_gb:.1f}GB")
            
            self.validation_results['passed'].append(f"Espaço em disco OK: {free_gb:.1f}GB livres")
            return True
            
        except Exception as e:
            self.validation_results['warnings'].append(f"Não foi possível verificar espaço em disco: {str(e)}")
            return True  # Não bloquear por isso
    
    def validate_oauth_credentials(self) -> bool:
        """Valida credenciais OAuth"""
        try:
            client_secrets_path = "config/client_secrets.json"
            
            if not os.path.exists(client_secrets_path):
                self.validation_results['errors'].append("Arquivo client_secrets.json não encontrado")
                return False
            
            with open(client_secrets_path, 'r') as f:
                credentials = json.load(f)
            
            # Validar estrutura básica (suporta 'web' e 'installed')
            if 'web' in credentials:
                config_section = credentials['web']
            elif 'installed' in credentials:
                config_section = credentials['installed']
            else:
                self.validation_results['errors'].append("Estrutura inválida em client_secrets.json (esperado 'web' ou 'installed')")
                return False
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            
            missing_fields = [field for field in required_fields if field not in config_section]
            if missing_fields:
                self.validation_results['errors'].append(f"Campos faltando em client_secrets.json: {', '.join(missing_fields)}")
                return False
            
            # Validar se não são valores placeholder
            if 'YOUR_CLIENT_ID' in config_section.get('client_id', ''):
                self.validation_results['errors'].append("client_id ainda é placeholder")
                return False
            
            if 'YOUR_CLIENT_SECRET' in config_section.get('client_secret', ''):
                self.validation_results['errors'].append("client_secret ainda é placeholder")
                return False
            
            self.validation_results['passed'].append("Credenciais OAuth configuradas")
            return True
            
        except Exception as e:
            self.validation_results['errors'].append(f"Erro ao validar credenciais OAuth: {str(e)}")
            return False
    
    def validate_youtube_config(self) -> bool:
        """Valida configurações específicas do YouTube"""
        if not self.config:
            return False
        
        # Validar configurações de shorts
        shorts_config = self.config.get('shorts_config', {})
        if not shorts_config:
            self.validation_results['errors'].append("Configuração de shorts não encontrada")
            return False
        
        # Validar resolução
        resolution = shorts_config.get('resolution', '')
        if not resolution or 'x' not in resolution:
            self.validation_results['errors'].append("Resolução de shorts inválida")
            return False
        
        try:
            width, height = map(int, resolution.split('x'))
            if width < 720 or height < 1280:
                self.validation_results['warnings'].append(f"Resolução baixa para shorts: {resolution}")
        except ValueError:
            self.validation_results['errors'].append(f"Formato de resolução inválido: {resolution}")
            return False
        
        # Validar hashtags
        hashtags = self.config.get('hashtags', [])
        if not hashtags:
            self.validation_results['warnings'].append("Nenhuma hashtag configurada")
        elif len(hashtags) > 30:
            self.validation_results['warnings'].append(f"Muitas hashtags: {len(hashtags)} (máximo recomendado: 30)")
        
        # Validar horário de upload
        upload_time = self.config.get('upload_schedule', {}).get('time', '')
        if not upload_time or ':' not in upload_time:
            self.validation_results['errors'].append("Horário de upload inválido")
            return False
        
        self.validation_results['passed'].append("Configurações do YouTube OK")
        return True
    
    def validate_network_connection(self) -> bool:
        """Testa conectividade de rede"""
        try:
            import requests
            
            # Testar conexão com YouTube
            response = requests.get('https://www.youtube.com', timeout=10)
            if response.status_code == 200:
                self.validation_results['passed'].append("Conexão com YouTube OK")
            else:
                self.validation_results['warnings'].append(f"YouTube respondeu com status {response.status_code}")
            
            # Testar conexão com Google API
            response = requests.get('https://www.googleapis.com', timeout=10)
            if response.status_code == 200:
                self.validation_results['passed'].append("Conexão com Google API OK")
            else:
                self.validation_results['warnings'].append(f"Google API respondeu com status {response.status_code}")
            
            return True
            
        except requests.exceptions.Timeout:
            self.validation_results['errors'].append("Timeout na conexão de rede")
            return False
        except requests.exceptions.ConnectionError:
            self.validation_results['errors'].append("Erro de conexão de rede")
            return False
        except Exception as e:
            self.validation_results['warnings'].append(f"Erro ao testar rede: {str(e)}")
            return True  # Não bloquear por isso
    
    def collect_system_info(self):
        """Coleta informações do sistema"""
        try:
            import platform
            import psutil
            
            self.validation_results['system_info'].update({
                'os': f"{platform.system()} {platform.release()}",
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'cpu_count': psutil.cpu_count(),
                'memory_gb': f"{psutil.virtual_memory().total / (1024**3):.1f}",
                'working_directory': os.getcwd(),
                'timestamp': os.path.basename(__file__)
            })
            
        except Exception as e:
            self.logger.warning(f"Erro ao coletar informações do sistema: {str(e)}")
    
    def run_full_validation(self) -> Dict:
        """Executa validação completa do sistema"""
        self.logger.info("Iniciando validação completa do sistema")
        
        # Coletar informações do sistema
        self.collect_system_info()
        
        # Lista de validações
        validations = [
            ("Configuração", self.load_config),
            ("Versão Python", self.validate_python_version),
            ("Dependências", self.validate_dependencies),
            ("FFmpeg", self.validate_ffmpeg),
            ("Diretórios", self.validate_directories),
            ("Espaço em disco", self.validate_disk_space),
            ("Credenciais OAuth", self.validate_oauth_credentials),
            ("Configurações YouTube", self.validate_youtube_config),
            ("Conexão de rede", self.validate_network_connection)
        ]
        
        # Executar validações
        for name, validation_func in validations:
            try:
                self.logger.info(f"Validando: {name}")
                result = validation_func()
                if result:
                    self.logger.info(f"✓ {name}: OK")
                else:
                    self.logger.error(f"✗ {name}: FALHOU")
            except Exception as e:
                self.validation_results['errors'].append(f"Erro na validação {name}: {str(e)}")
                self.logger.error(f"✗ {name}: ERRO - {str(e)}")
        
        # Resumo final
        total_errors = len(self.validation_results['errors'])
        total_warnings = len(self.validation_results['warnings'])
        total_passed = len(self.validation_results['passed'])
        
        self.validation_results['summary'] = {
            'total_validations': len(validations),
            'passed': total_passed,
            'warnings': total_warnings,
            'errors': total_errors,
            'success': total_errors == 0
        }
        
        self.logger.info("Validação completa finalizada")
        self.logger.info(f"Resultados: {total_passed} OK, {total_warnings} avisos, {total_errors} erros")
        
        return self.validation_results
    
    def print_validation_report(self):
        """Imprime relatório de validação"""
        print("\n" + "="*60)
        print("RELATÓRIO DE VALIDAÇÃO DO SISTEMA")
        print("="*60)
        
        if self.validation_results['passed']:
            print(f"\n✅ SUCESSOS ({len(self.validation_results['passed'])}):")
            for item in self.validation_results['passed']:
                print(f"   • {item}")
        
        if self.validation_results['warnings']:
            print(f"\n⚠️  AVISOS ({len(self.validation_results['warnings'])}):")
            for item in self.validation_results['warnings']:
                print(f"   • {item}")
        
        if self.validation_results['errors']:
            print(f"\n❌ ERROS ({len(self.validation_results['errors'])}):")
            for item in self.validation_results['errors']:
                print(f"   • {item}")
        
        if self.validation_results['system_info']:
            print(f"\n🖥️  INFORMAÇÕES DO SISTEMA:")
            for key, value in self.validation_results['system_info'].items():
                print(f"   • {key}: {value}")
        
        print("\n" + "="*60)
        
        summary = self.validation_results.get('summary', {})
        if summary.get('success', False):
            print("🎉 SISTEMA VALIDADO COM SUCESSO!")
        else:
            print("❌ SISTEMA POSSUI PROBLEMAS QUE PRECISAM SER CORRIGIDOS")
        
        print("="*60)