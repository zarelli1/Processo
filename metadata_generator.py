#!/usr/bin/env python3
"""
Metadata Generator Module
Sistema de geração automática de metadados para shorts
Canal: Your_Channel_Name
"""

import os
import logging
import re
from typing import Dict, List, Optional
from datetime import datetime
import json

class MetadataGenerator:
    """Classe para geração automática de metadados dos shorts"""
    
    def __init__(self, config: Dict = None):
        self.logger = logging.getLogger(__name__)
        
        # Configurações padrão
        self.config = config or {
            'channel_name': 'Your_Channel_Name',
            'default_hashtags': [
                '#IA', '#thedreamjob', '#crypto', '#automacao', 
                '#claudecode', '#shorts', '#tech'
            ],
            'description_template': """🎯 {title}

📊 Este é um clipe dos melhores momentos do vídeo original!

🔥 Inscreva-se para mais conteúdo sobre:
• Inteligência Artificial
• Automação
• Criptomoedas
• Tecnologia
• Empreendedorismo

{hashtags}

---
💡 Gerado automaticamente com IA
🤖 Canal: @Your_Channel_Name""",
            'title_max_length': 100,
            'description_max_length': 5000,
            'tags_max_count': 15
        }
        
        # Palavras-chave para tags automáticas
        self.keyword_tags = {
            'tecnologia': ['tech', 'tecnologia', 'inovacao', 'futuro'],
            'ia': ['inteligenciaartificial', 'ai', 'machinelearning', 'automacao'],
            'crypto': ['bitcoin', 'ethereum', 'blockchain', 'criptomoedas'],
            'negocio': ['empreendedorismo', 'startup', 'business', 'sucesso'],
            'educacao': ['aprendizado', 'tutorial', 'dicas', 'conhecimento'],
            'inspiracao': ['motivacao', 'inspiracao', 'mindset', 'crescimento']
        }
        
        self.logger.info("MetadataGenerator inicializado")
    
    def clean_text(self, text: str) -> str:
        """
        Limpa texto removendo caracteres especiais
        
        Args:
            text: Texto para limpar
            
        Returns:
            Texto limpo
        """
        # Remover caracteres especiais exceto básicos
        cleaned = re.sub(r'[^\w\s\-_.,!?()]', '', text)
        
        # Remover espaços extras
        cleaned = ' '.join(cleaned.split())
        
        return cleaned.strip()
    
    def generate_title(self, 
                      original_title: str, 
                      part_number: int, 
                      total_parts: int = 7,
                      keywords: str = "") -> str:
        """
        Gera título automático para o short
        
        Args:
            original_title: Título do vídeo original
            part_number: Número da parte
            total_parts: Total de partes
            keywords: Palavras-chave encontradas no segmento
            
        Returns:
            Título otimizado para o short
        """
        try:
            # Limpar título original
            clean_title = self.clean_text(original_title)
            
            # Truncar se muito longo
            max_base_length = self.config['title_max_length'] - 20  # Reservar espaço para " - Parte X/7 #Shorts"
            if len(clean_title) > max_base_length:
                clean_title = clean_title[:max_base_length].rsplit(' ', 1)[0] + "..."
            
            # Adicionar informação da parte
            part_info = f" - Parte {part_number}/{total_parts}"
            
            # Adicionar hashtag de shorts
            shorts_tag = " #Shorts"
            
            # Construir título final
            final_title = clean_title + part_info + shorts_tag
            
            # Validar comprimento final
            if len(final_title) > self.config['title_max_length']:
                # Reduzir título base ainda mais
                max_base_length = self.config['title_max_length'] - len(part_info) - len(shorts_tag) - 3
                clean_title = clean_title[:max_base_length] + "..."
                final_title = clean_title + part_info + shorts_tag
            
            self.logger.debug(f"Título gerado: {final_title}")
            return final_title
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar título: {str(e)}")
            return f"Short {part_number}/{total_parts} #Shorts"
    
    def extract_keywords_from_segment(self, segment_data: Dict) -> List[str]:
        """
        Extrai palavras-chave relevantes do segmento
        
        Args:
            segment_data: Dados do segmento com informações de análise
            
        Returns:
            Lista de palavras-chave encontradas
        """
        try:
            keywords_found = []
            
            # Extrair palavras-chave se disponível
            keywords_field = segment_data.get('keywords', '')
            
            if keywords_field:
                # Processar string de keywords
                for category, keywords in self.keyword_tags.items():
                    for keyword in keywords:
                        if keyword.lower() in keywords_field.lower():
                            keywords_found.append(keyword)
            
            # Adicionar tags baseadas no score
            score = segment_data.get('combined_score', 0)
            if score > 0.8:
                keywords_found.extend(['viral', 'trending', 'destaque'])
            elif score > 0.6:
                keywords_found.extend(['interessante', 'relevante'])
            
            # Remover duplicatas mantendo ordem
            unique_keywords = []
            for keyword in keywords_found:
                if keyword not in unique_keywords:
                    unique_keywords.append(keyword)
            
            return unique_keywords[:10]  # Limitar a 10 keywords
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair keywords: {str(e)}")
            return []
    
    def generate_description(self, 
                           title: str, 
                           segment_data: Dict,
                           custom_hashtags: List[str] = None) -> str:
        """
        Gera descrição automática para o short
        
        Args:
            title: Título do short
            segment_data: Dados do segmento
            custom_hashtags: Hashtags customizadas (opcional)
            
        Returns:
            Descrição formatada
        """
        try:
            # Usar hashtags customizadas ou padrão
            hashtags = custom_hashtags or self.config['default_hashtags']
            
            # Adicionar hashtags baseadas nas keywords do segmento
            segment_keywords = self.extract_keywords_from_segment(segment_data)
            for keyword in segment_keywords:
                hashtag = f"#{keyword}"
                if hashtag not in hashtags:
                    hashtags.append(hashtag)
            
            # Limitar número de hashtags
            hashtags = hashtags[:20]  # Máximo 20 hashtags
            
            # Formatar hashtags para a descrição
            hashtags_text = ' '.join(hashtags)
            
            # Gerar descrição usando template
            description = self.config['description_template'].format(
                title=title.replace(' #Shorts', ''),
                hashtags=hashtags_text
            )
            
            # Validar comprimento
            if len(description) > self.config['description_max_length']:
                # Reduzir hashtags se necessário
                while len(description) > self.config['description_max_length'] and len(hashtags) > 5:
                    hashtags.pop()
                    hashtags_text = ' '.join(hashtags)
                    description = self.config['description_template'].format(
                        title=title.replace(' #Shorts', ''),
                        hashtags=hashtags_text
                    )
            
            self.logger.debug(f"Descrição gerada: {len(description)} caracteres")
            return description
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar descrição: {str(e)}")
            return f"Short do canal {self.config['channel_name']} #Shorts"
    
    def generate_tags(self, 
                     title: str, 
                     segment_data: Dict) -> List[str]:
        """
        Gera tags relevantes para o algoritmo do YouTube
        
        Args:
            title: Título do short
            segment_data: Dados do segmento
            
        Returns:
            Lista de tags otimizadas
        """
        try:
            tags = []
            
            # Tags básicas do canal
            basic_tags = [
                'your channel name',
                'shorts',
                'inteligencia artificial',
                'tecnologia',
                'automacao'
            ]
            tags.extend(basic_tags)
            
            # Tags baseadas nas keywords do segmento
            segment_keywords = self.extract_keywords_from_segment(segment_data)
            tags.extend(segment_keywords)
            
            # Tags baseadas no título
            title_words = self.clean_text(title.lower()).split()
            relevant_words = [word for word in title_words 
                            if len(word) > 3 and word not in ['parte', 'shorts']]
            tags.extend(relevant_words[:5])
            
            # Tags baseadas na categoria do conteúdo
            for category, keywords in self.keyword_tags.items():
                for keyword in keywords:
                    if any(keyword in text.lower() for text in [title, segment_data.get('keywords', '')]):
                        tags.append(category)
                        break
            
            # Remover duplicatas e limpar
            unique_tags = []
            for tag in tags:
                clean_tag = self.clean_text(tag.lower())
                if clean_tag and clean_tag not in unique_tags and len(clean_tag) > 2:
                    unique_tags.append(clean_tag)
            
            # Limitar número de tags
            final_tags = unique_tags[:self.config['tags_max_count']]
            
            self.logger.debug(f"Tags geradas: {len(final_tags)} tags")
            return final_tags
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar tags: {str(e)}")
            return ['shorts', 'your channel name', 'tecnologia']
    
    def generate_complete_metadata(self,
                                  original_title: str,
                                  segment_data: Dict,
                                  part_number: int,
                                  total_parts: int = 7,
                                  custom_hashtags: List[str] = None) -> Dict:
        """
        Gera metadados completos para o short
        
        Args:
            original_title: Título do vídeo original
            segment_data: Dados do segmento
            part_number: Número da parte
            total_parts: Total de partes
            custom_hashtags: Hashtags customizadas
            
        Returns:
            Dicionário com metadados completos
        """
        try:
            self.logger.info(f"Gerando metadados para parte {part_number}/{total_parts}")
            
            # Gerar título
            title = self.generate_title(
                original_title, 
                part_number, 
                total_parts,
                segment_data.get('keywords', '')
            )
            
            # Gerar descrição
            description = self.generate_description(
                title, 
                segment_data, 
                custom_hashtags
            )
            
            # Gerar tags
            tags = self.generate_tags(title, segment_data)
            
            # Metadados completos
            metadata = {
                'title': title,
                'description': description,
                'tags': tags,
                'category': 'Science & Technology',  # Categoria padrão
                'privacy_status': 'public',
                'part_info': {
                    'part_number': part_number,
                    'total_parts': total_parts,
                    'segment_start': segment_data.get('start_time', 0),
                    'segment_end': segment_data.get('end_time', 0),
                    'segment_score': segment_data.get('combined_score', 0)
                },
                'generated_at': datetime.now().isoformat(),
                'channel': self.config['channel_name']
            }
            
            # Adicionar informações de qualidade
            metadata['quality_info'] = {
                'title_length': len(title),
                'description_length': len(description),
                'tags_count': len(tags),
                'has_keywords': len(self.extract_keywords_from_segment(segment_data)) > 0
            }
            
            self.logger.info(f"Metadados gerados: {title}")
            return metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar metadados completos: {str(e)}")
            
            # Metadados de fallback
            return {
                'title': f"Short {part_number}/{total_parts} #Shorts",
                'description': f"Short do canal {self.config['channel_name']}",
                'tags': ['shorts', 'your channel name'],
                'category': 'Science & Technology',
                'privacy_status': 'public',
                'error': str(e)
            }
    
    def save_metadata_file(self, metadata: Dict, output_path: str) -> bool:
        """
        Salva metadados em arquivo JSON
        
        Args:
            metadata: Metadados para salvar
            output_path: Caminho do arquivo
            
        Returns:
            True se salvou com sucesso
        """
        try:
            # Criar diretório se não existir
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Salvar arquivo JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.logger.debug(f"Metadados salvos: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar metadados: {str(e)}")
            return False
    
    def generate_batch_metadata(self,
                               original_title: str,
                               segments_data: List[Dict],
                               custom_hashtags: List[str] = None) -> List[Dict]:
        """
        Gera metadados para um lote de shorts
        
        Args:
            original_title: Título do vídeo original
            segments_data: Lista de dados dos segmentos
            custom_hashtags: Hashtags customizadas
            
        Returns:
            Lista de metadados para cada short
        """
        try:
            self.logger.info(f"Gerando metadados para {len(segments_data)} shorts")
            
            batch_metadata = []
            total_parts = len(segments_data)
            
            for i, segment_data in enumerate(segments_data, 1):
                metadata = self.generate_complete_metadata(
                    original_title,
                    segment_data,
                    i,
                    total_parts,
                    custom_hashtags
                )
                batch_metadata.append(metadata)
            
            self.logger.info(f"Metadados de lote gerados: {len(batch_metadata)} itens")
            return batch_metadata
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar metadados de lote: {str(e)}")
            return []
    
    def optimize_for_algorithm(self, metadata: Dict) -> Dict:
        """
        Otimiza metadados para o algoritmo do YouTube
        
        Args:
            metadata: Metadados originais
            
        Returns:
            Metadados otimizados
        """
        try:
            optimized = metadata.copy()
            
            # Otimizar título para engajamento
            title = optimized['title']
            
            # Adicionar emojis se não tiver
            if not any(ord(char) > 127 for char in title):  # Sem emojis
                engagement_emojis = ['🔥', '💡', '🚀', '⚡', '🎯']
                if optimized['part_info']['segment_score'] > 0.8:
                    title = f"{engagement_emojis[0]} {title}"
                elif optimized['part_info']['segment_score'] > 0.6:
                    title = f"{engagement_emojis[1]} {title}"
                
                optimized['title'] = title
            
            # Otimizar tags para alcance
            tags = optimized['tags']
            
            # Adicionar tags de trending se score alto
            if optimized['part_info']['segment_score'] > 0.7:
                trending_tags = ['viral', 'trending', 'populares']
                for tag in trending_tags:
                    if tag not in tags and len(tags) < self.config['tags_max_count']:
                        tags.append(tag)
            
            optimized['tags'] = tags
            
            # Adicionar informação de otimização
            optimized['optimization'] = {
                'optimized_at': datetime.now().isoformat(),
                'changes_made': ['emoji_added', 'trending_tags_added'],
                'algorithm_score': optimized['part_info']['segment_score']
            }
            
            return optimized
            
        except Exception as e:
            self.logger.error(f"Erro na otimização: {str(e)}")
            return metadata