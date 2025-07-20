#!/usr/bin/env python3
"""
Analisador de Conteúdo Inteligente
Analisa vídeos para gerar títulos, descrições e hashtags únicos
"""

import os
import re
import json
import random
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ContentAnalyzer:
    """Analisa conteúdo de vídeos para gerar metadados únicos"""
    
    def __init__(self):
        self.keywords_database = self._load_keywords_database()
        self.title_templates = self._load_title_templates()
        self.description_templates = self._load_description_templates()
        self.hashtag_categories = self._load_hashtag_categories()
        
    def _load_keywords_database(self) -> Dict:
        """Base de dados de palavras-chave por categoria"""
        return {
            "programacao": [
                "python", "javascript", "java", "react", "node", "css", "html", 
                "api", "backend", "frontend", "database", "sql", "nosql", "git",
                "docker", "kubernetes", "aws", "cloud", "devops", "algoritmo",
                "codigo", "desenvolvimento", "software", "aplicativo", "sistema"
            ],
            "tutorial": [
                "tutorial", "como fazer", "passo a passo", "aprenda", "curso",
                "aula", "explicacao", "demonstracao", "exemplo", "pratica",
                "basico", "avancado", "iniciante", "completo", "rapido"
            ],
            "tecnologia": [
                "tecnologia", "tech", "inovacao", "digital", "futuro", "ai",
                "inteligencia artificial", "machine learning", "data science",
                "blockchain", "iot", "5g", "mobile", "web", "cybersecurity"
            ],
            "negócios": [
                "business", "empresa", "startup", "empreendedorismo", "marketing",
                "vendas", "gestao", "lideranca", "produtividade", "estrategia",
                "financas", "investimento", "economia", "mercado", "cliente"
            ],
            "design": [
                "design", "ui", "ux", "interface", "experiencia", "usuario",
                "prototipo", "figma", "adobe", "criativo", "visual", "grafico",
                "branding", "identidade", "layout", "tipografia", "cores"
            ]
        }
    
    def _load_title_templates(self) -> List[Dict]:
        """Templates de títulos melhorados e mais coerentes"""
        return [
            {
                "pattern": "{action} {topic} em {time} | {emotion}",
                "actions": ["Aprenda", "Domine", "Descubra", "Entenda", "Veja como", "Comece", "Pratique"],
                "emotions": ["🔥 VIRAL", "💡 GENIUS", "⚡ RÁPIDO", "🎯 CERTEIRO", "✨ INCRÍVEL", "🚀 ÉPICO", "💎 PREMIUM"],
                "times": ["60 segundos", "2 minutos", "5 minutos", "menos de 3min", "poucos minutos", "rapidamente", "agora mesmo"]
            },
            {
                "pattern": "{question} {topic}? | {benefit}",
                "questions": ["Como dominar", "Por que usar", "Quando aplicar", "Onde encontrar", "Como começar com"],
                "benefits": ["A resposta vai te chocar", "Mudará sua perspectiva", "Ninguém te conta isso", "Segredo dos experts", "Método comprovado", "Estratégia profissional"]
            },
            {
                "pattern": "{number} {thing} de {topic} que {result}",
                "numbers": ["3", "5", "7", "10"],
                "things": ["estratégias", "técnicas avançadas", "truques profissionais", "métodos secretos", "dicas fundamentais", "conceitos essenciais"],
                "results": ["todo profissional deveria saber", "vão acelerar seu aprendizado", "transformarão seus resultados", "são game changers", "farão a diferença"]
            },
            {
                "pattern": "{topic}: {insight} | {call_to_action}",
                "insights": ["O que ninguém te ensina", "A verdade por trás", "Metodologia completa", "Guia definitivo", "Estratégia avançada", "Técnica profissional"],
                "call_to_actions": ["SALVE AGORA!", "COMPARTILHE!", "APLIQUE HOJE!", "TESTE VOCÊ MESMO!", "IMPLEMENTE JÁ!"]
            },
            {
                "pattern": "{intensity} {topic} | {promise}",
                "intensity": ["Masterclass de", "Curso intensivo de", "Workshop prático de", "Guia completo de", "Fundamentos de"],
                "promise": ["Resultados garantidos", "Método testado", "Passo a passo", "Do zero ao pro", "Fácil e rápido", "Sem enrolação"]
            },
            {
                "pattern": "{topic} {level} | {hook}",
                "level": ["para iniciantes", "nível avançado", "profissional", "do básico ao avançado", "intermediário"],
                "hook": ["Você vai se surpreender", "Mais simples do que parece", "A forma correta", "Como os experts fazem", "Método revolucionário"]
            }
        ]
    
    def _load_description_templates(self) -> List[str]:
        """Templates de descrições variadas com link obrigatório"""
        return [
            """🎯 {hook}

{main_content}

💡 O que você achou? Comenta aí sua opinião!

🚀 AUTOMATIZE SEU NEGÓCIO:
👉 https://automatize.lovable.app

🔗 SIGA PARA MAIS CONTEÚDO:
✅ Dicas exclusivas
✅ Tutoriais práticos  
✅ Automação e tecnologia

{hashtags}

#Shorts {category_tags}""",

            """⚡ {hook}

{main_content}

🤔 Já conhecia essa estratégia? Deixa nos comentários!

🎯 ACELERE SEUS RESULTADOS:
🔗 https://automatize.lovable.app

📚 QUER APRENDER MAIS?
👉 Segue aqui para conteúdo diário
👉 Salva o post para não perder
👉 Compartilha com quem precisa

{hashtags}

#Shorts {category_tags}""",

            """🔥 {hook}

{main_content}

💭 Qual sua experiência com isso? Conta pra gente!

💼 TRANSFORME SEU NEGÓCIO:
✨ https://automatize.lovable.app

🎯 SE CURTIU:
⭐ Deixa o like
💬 Comenta sua dúvida
📤 Compartilha com os amigos

{hashtags}

#Shorts {category_tags}""",

            """✨ {hook}

{main_content}

🚀 Gostou? Tem muito mais vindo por aí!

🎪 SOLUÇÕES COMPLETAS:
🌟 https://automatize.lovable.app

📱 SEGUE PRA NÃO PERDER:
🔔 Conteúdo exclusivo
💡 Dicas valiosas
🎓 Automação e crescimento

{hashtags}

#Shorts {category_tags}""",

            """🚀 {hook}

{main_content}

🔥 Aplique isso no seu projeto!

⚡ POTENCIALIZE SEUS RESULTADOS:
🎯 https://automatize.lovable.app

🎬 CONTEÚDO DE QUALIDADE:
📈 Estratégias testadas
🛠️ Ferramentas práticas
💎 Insights valiosos

{hashtags}

#Shorts {category_tags}""",

            """💎 {hook}

{main_content}

🎯 Implementou? Conta o resultado!

🚀 ACELERE SEU CRESCIMENTO:
💼 https://automatize.lovable.app

🔔 NOTIFICAÇÕES ATIVADAS?
✅ Novos vídeos toda semana
✅ Dicas exclusivas
✅ Conteúdo premium

{hashtags}

#Shorts {category_tags}"""
        ]
    
    def _load_hashtag_categories(self) -> Dict:
        """Categorias de hashtags por tipo de conteúdo"""
        return {
            "programacao": [
                "#Python", "#JavaScript", "#Programacao", "#Codigo", "#Developer",
                "#Programming", "#WebDev", "#TechTips", "#SoftwareDev", "#API"
            ],
            "tutorial": [
                "#Tutorial", "#AprendaComigo", "#ComoFazer", "#PassoAPasso", "#Dicas",
                "#Aprenda", "#Curso", "#Aula", "#Educacao", "#Conhecimento"
            ],
            "tecnologia": [
                "#Tech", "#Tecnologia", "#Inovacao", "#Digital", "#Futuro",
                "#AI", "#MachineLearning", "#TechNews", "#Innovation", "#Technology"
            ],
            "negócios": [
                "#Business", "#Empreendedorismo", "#Marketing", "#Vendas", "#Gestao",
                "#Lideranca", "#Produtividade", "#Startup", "#Empresa", "#Sucesso"
            ],
            "design": [
                "#Design", "#UI", "#UX", "#Interface", "#Creative", "#Visual",
                "#Designer", "#Prototipo", "#Criatividade", "#Arte"
            ],
            "geral": [
                "#Viral", "#Trending", "#MustWatch", "#Incrivel", "#Impressionante",
                "#Curiosidade", "#Interessante", "#Surpreendente", "#Legal", "#Top"
            ]
        }
    
    def analyze_video_content(self, video_title: str, video_description: str = "", 
                            video_tags: List[str] = None) -> Dict:
        """
        Analisa conteúdo do vídeo para determinar categoria e temas
        
        Args:
            video_title: Título do vídeo original
            video_description: Descrição do vídeo original
            video_tags: Tags do vídeo original
            
        Returns:
            Dict com análise do conteúdo
        """
        logger.info(f"Analisando conteúdo: {video_title}")
        
        content_text = f"{video_title} {video_description or ''}".lower()
        video_tags = video_tags or []
        
        # Detectar categorias
        category_scores = {}
        for category, keywords in self.keywords_database.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in content_text:
                    score += content_text.count(keyword.lower())
            category_scores[category] = score
        
        # Categoria principal
        main_category = max(category_scores, key=category_scores.get)
        confidence = category_scores[main_category] / max(sum(category_scores.values()), 1)
        
        # Extrair tópicos principais
        topics = self._extract_topics(content_text, main_category)
        
        # Detectar tipo de conteúdo
        content_type = self._detect_content_type(content_text)
        
        return {
            "main_category": main_category,
            "confidence": confidence,
            "category_scores": category_scores,
            "topics": topics,
            "content_type": content_type,
            "original_title": video_title,
            "original_tags": video_tags
        }
    
    def _extract_topics(self, content_text: str, category: str) -> List[str]:
        """Extrai tópicos principais do conteúdo"""
        topics = []
        
        # Buscar palavras-chave da categoria
        if category in self.keywords_database:
            for keyword in self.keywords_database[category]:
                if keyword.lower() in content_text:
                    topics.append(keyword)
        
        # Extrair palavras importantes (> 3 caracteres, não stopwords)
        stopwords = {
            "para", "como", "que", "uma", "com", "por", "sobre", "este", "esta",
            "seu", "sua", "mais", "muito", "quando", "onde", "porque", "assim",
            "the", "and", "or", "in", "on", "at", "to", "for", "of", "with"
        }
        
        words = re.findall(r'\b\w{4,}\b', content_text)
        for word in words:
            if word not in stopwords and len(topics) < 10:
                topics.append(word)
        
        return list(set(topics))[:5]  # Top 5 tópicos únicos
    
    def _detect_content_type(self, content_text: str) -> str:
        """Detecta o tipo de conteúdo"""
        
        if any(word in content_text for word in ["tutorial", "como", "passo", "aprenda"]):
            return "tutorial"
        elif any(word in content_text for word in ["review", "análise", "opinião", "teste"]):
            return "review"
        elif any(word in content_text for word in ["dica", "truque", "segredo", "hack"]):
            return "dica"
        elif any(word in content_text for word in ["noticia", "news", "atualização", "lançamento"]):
            return "news"
        else:
            return "geral"
    
    def generate_unique_title(self, content_analysis: Dict, part_number: int = 1) -> str:
        """Gera título único e coerente baseado na análise de conteúdo"""
        
        # Garantir que cada parte tenha um template diferente
        template_index = (part_number - 1) % len(self.title_templates)
        template_data = self.title_templates[template_index]
        pattern = template_data["pattern"]
        
        # Melhorar tópico baseado na categoria
        main_topic = content_analysis["topics"][0] if content_analysis["topics"] else "tecnologia"
        
        # Refinar tópico baseado na categoria
        topic_refinements = {
            "programacao": ["Python", "JavaScript", "desenvolvimento", "código", "programação"],
            "tutorial": ["este método", "esta técnica", "este conceito", "esta estratégia"],
            "tecnologia": ["tecnologia", "inovação", "ferramentas", "soluções"],
            "negócios": ["negócios", "estratégias", "produtividade", "resultados"],
            "design": ["design", "criatividade", "interfaces", "experiência"]
        }
        
        category = content_analysis["main_category"]
        if category in topic_refinements:
            refined_topics = topic_refinements[category]
            # Usar parte do número para garantir consistência
            topic_index = (part_number - 1) % len(refined_topics)
            main_topic = refined_topics[topic_index]
        
        # Preparar variáveis com mais contexto
        variables = {
            "topic": main_topic,
            "part": f"Parte {part_number}",
            "number": random.choice(template_data.get("numbers", ["5"])),
        }
        
        # Adicionar variáveis específicas do template de forma determinística
        for key, values in template_data.items():
            if key != "pattern" and isinstance(values, list):
                # Usar part_number para garantir variedade mas consistência
                value_index = (part_number - 1 + hash(key)) % len(values)
                variables[key] = values[value_index]
        
        try:
            title = pattern.format(**variables)
        except KeyError as e:
            # Fallback melhorado
            fallback_actions = ["Aprenda", "Descubra", "Domine", "Entenda", "Veja"]
            action = fallback_actions[(part_number - 1) % len(fallback_actions)]
            title = f"{action} {main_topic} | Parte {part_number} 🔥"
        
        # Adicionar emoji baseado na categoria de forma consistente
        category_emojis = {
            "programacao": "💻",
            "tutorial": "📚", 
            "tecnologia": "🚀",
            "negócios": "💼",
            "design": "🎨"
        }
        
        emoji = category_emojis.get(content_analysis["main_category"], "⚡")
        
        # Garantir que emoji não se repita
        if emoji not in title:
            title = f"{title} {emoji}"
        
        # Adicionar variação numérica se necessário
        if part_number > 1 and "Parte" not in title:
            title = f"{title} #{part_number}"
        
        return title[:100]  # Limite do YouTube
    
    def generate_unique_description(self, content_analysis: Dict, 
                                  original_video_url: str = "") -> str:
        """Gera descrição única baseada na análise"""
        
        # Selecionar template aleatório
        template = random.choice(self.description_templates)
        
        # Obter tópico principal
        main_topic = content_analysis['topics'][0] if content_analysis['topics'] else content_analysis['main_category']
        
        # Gerar ganchos mais específicos e coerentes
        hooks = [
            f"Você sabia que {main_topic} pode transformar completamente seus resultados?",
            f"A estratégia de {main_topic} que está mudando o jogo para milhares de pessoas!",
            f"Finalmente! O método de {main_topic} que os experts não querem que você saiba!",
            f"Atenção! Esta técnica de {main_topic} vai revolucionar seu conhecimento!",
            f"Descobri o segredo por trás de {main_topic} e você precisa ver isso!",
            f"Por que {main_topic} é fundamental para seu sucesso profissional?"
        ]
        
        # Gerar conteúdo principal mais elaborado
        main_contents = [
            f"Neste vídeo, compartilho insights práticos sobre {content_analysis['main_category']} que podem acelerar seus resultados imediatamente.",
            f"Uma abordagem estratégica e testada para dominar {content_analysis['main_category']} de forma eficiente e profissional.",
            f"As técnicas mais avançadas de {content_analysis['main_category']} explicadas de maneira simples e aplicável no seu dia a dia.",
            f"Metodologia comprovada em {content_analysis['main_category']} que já ajudou milhares de pessoas a alcançarem seus objetivos.",
            f"Conteúdo exclusivo e aprofundado sobre {content_analysis['main_category']} baseado em experiências reais e casos de sucesso.",
            f"Estratégias profissionais de {content_analysis['main_category']} que você pode implementar hoje mesmo para ver resultados."
        ]
        
        # Gerar hashtags específicas
        hashtags = self._generate_content_hashtags(content_analysis)
        category_tags = " ".join(self.hashtag_categories.get(content_analysis["main_category"], [])[:5])
        
        # Preencher template
        description = template.format(
            hook=random.choice(hooks),
            main_content=random.choice(main_contents),
            hashtags=" ".join(hashtags[:10]),
            category_tags=category_tags
        )
        
        # Adicionar link do vídeo original se fornecido
        if original_video_url:
            description += f"\n\n🎬 Vídeo completo: {original_video_url}"
        
        return description[:5000]  # Limite do YouTube
    
    def _generate_content_hashtags(self, content_analysis: Dict) -> List[str]:
        """Gera hashtags específicas baseadas no conteúdo"""
        hashtags = []
        
        # Hashtags da categoria principal
        main_category_tags = self.hashtag_categories.get(content_analysis["main_category"], [])
        hashtags.extend(random.sample(main_category_tags, min(3, len(main_category_tags))))
        
        # Hashtags baseadas nos tópicos
        for topic in content_analysis["topics"][:3]:
            hashtags.append(f"#{topic.title()}")
        
        # Hashtags gerais
        general_tags = self.hashtag_categories["geral"]
        hashtags.extend(random.sample(general_tags, 2))
        
        # Hashtags baseadas no tipo de conteúdo
        content_type_tags = {
            "tutorial": ["#Tutorial", "#Aprenda", "#ComoFazer"],
            "review": ["#Review", "#Analise", "#Teste"],
            "dica": ["#Dica", "#Truque", "#Hack"],
            "news": ["#News", "#Novidade", "#Atualização"]
        }
        
        if content_analysis["content_type"] in content_type_tags:
            hashtags.extend(content_type_tags[content_analysis["content_type"]][:2])
        
        # Remover duplicatas e limitar
        unique_hashtags = list(dict.fromkeys(hashtags))
        return unique_hashtags[:15]
    
    def generate_video_metadata(self, video_title: str, video_description: str = "",
                              part_number: int = 1, original_url: str = "") -> Dict:
        """
        Gera metadados completos para um vídeo
        
        Returns:
            Dict com title, description, tags
        """
        logger.info(f"Gerando metadados para parte {part_number}")
        
        # Analisar conteúdo
        content_analysis = self.analyze_video_content(video_title, video_description)
        
        # Gerar título único
        unique_title = self.generate_unique_title(content_analysis, part_number)
        
        # Gerar descrição única
        unique_description = self.generate_unique_description(content_analysis, original_url)
        
        # Gerar tags
        tags = self._generate_content_hashtags(content_analysis)
        
        return {
            "title": unique_title,
            "description": unique_description,
            "tags": [tag.replace("#", "") for tag in tags],  # Remove # para tags
            "category": content_analysis["main_category"],
            "content_type": content_analysis["content_type"]
        }