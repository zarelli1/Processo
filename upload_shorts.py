#!/usr/bin/env python3
"""
🚀 UPLOAD INTELIGENTE DE SHORTS
Sistema com opção de escolher quantos vídeos postar
"""

import os
import sys
import time
from youtube_uploader import YouTubeUploader
from video_processor import VideoProcessor

def main():
    """Função principal com menu interativo"""
    
    print("🚀 UPLOAD INTELIGENTE DE SHORTS - Your Name")
    print("=" * 60)
    
    # Verificar pasta de shorts
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        print("❌ Pasta 'shorts' não encontrada")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        sys.exit(1)
    
    # Listar arquivos disponíveis
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    shorts_files.sort()
    
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        sys.exit(1)
    
    print(f"📁 SHORTS DISPONÍVEIS ({len(shorts_files)}):")
    for i, file in enumerate(shorts_files, 1):
        size = os.path.getsize(os.path.join(shorts_dir, file)) / (1024*1024)
        print(f"   {i:2d}. {file} ({size:.1f} MB)")
    
    # Menu de opções
    print(f"\n🎯 OPÇÕES DE UPLOAD:")
    print(f"   1 📊 Fazer upload de TODOS os {len(shorts_files)} shorts")
    print(f"   2 🔢 Escolher QUANTIDADE específica")
    print(f"   3 📋 SELECIONAR shorts individualmente")
    print(f"   0 ⬅️ Voltar (encerrar)")
    
    while True:
        choice = input(f"\n👉 Escolha uma opção (1-3) ou 0 para sair: ").strip()
        
        videos_to_upload = []
        
        if choice == "1":
            videos_to_upload = shorts_files
            print(f"✅ Selecionados TODOS os {len(videos_to_upload)} shorts")
            break
            
        elif choice == "2":
            while True:
                try:
                    max_videos = len(shorts_files)
                    print(f"\n📝 Quantos shorts fazer upload?")
                    print(f"   💡 Máximo disponível: {max_videos}")
                    print(f"   0️⃣ Digite '0' para voltar ao menu anterior")
                    
                    num_input = input(f"👉 Digite um número (1-{max_videos}) ou 0 para voltar: ").strip()
                    
                    if num_input == "0":
                        break  # Volta ao menu principal
                        
                    num_videos = int(num_input)
                    
                    if 1 <= num_videos <= max_videos:
                        videos_to_upload = shorts_files[:num_videos]
                        print(f"✅ Selecionados os primeiros {num_videos} shorts")
                        
                        # Confirmar seleção
                        print(f"\n📋 CONFIRMAÇÃO:")
                        print(f"   S - Confirmar seleção")
                        print(f"   N - Refazer seleção")
                        print(f"   0 - Voltar ao menu principal")
                        
                        confirm = input("👉 Confirma, refaz ou volta? [S/n/0]: ").strip().lower()
                        
                        if confirm == "0":
                            break  # Volta ao menu principal
                        elif confirm in ['', 's', 'sim', 'y', 'yes']:
                            break  # Confirma e sai do loop interno
                        else:
                            continue  # Refaz a seleção
                    else:
                        print(f"❌ Número deve estar entre 1 e {max_videos}")
                        
                except ValueError:
                    print("❌ Digite apenas números")
                    
            if num_input == "0":  # Se escolheu voltar
                continue  # Volta ao menu principal
            elif videos_to_upload:  # Se selecionou vídeos
                break  # Sai do loop principal
                
        elif choice == "3":
            while True:
                print(f"\n📋 SELEÇÃO INDIVIDUAL:")
                print(f"   • Digite números separados por vírgula: 1,3,5")
                print(f"   • Use hífen para range: 1-4")
                print(f"   • Combine ambos: 1,3,5-7")
                print(f"   • Digite '0' para voltar ao menu anterior")
                
                selection = input("👉 Sua seleção ou 0 para voltar: ").strip()
                
                if selection == "0":
                    break  # Volta ao menu principal
                
                try:
                    selected_indices = parse_selection(selection, len(shorts_files))
                    videos_to_upload = [shorts_files[i-1] for i in selected_indices]
                    
                    print(f"✅ Selecionados {len(videos_to_upload)} shorts:")
                    for video in videos_to_upload:
                        print(f"   • {video}")
                    
                    # Confirmar seleção
                    print(f"\n📋 CONFIRMAÇÃO:")
                    print(f"   S - Confirmar seleção")
                    print(f"   N - Refazer seleção")
                    print(f"   0 - Voltar ao menu principal")
                    
                    confirm = input("👉 Confirma, refaz ou volta? [S/n/0]: ").strip().lower()
                    
                    if confirm == "0":
                        break  # Volta ao menu principal
                    elif confirm in ['', 's', 'sim', 'y', 'yes']:
                        break  # Confirma e sai do loop interno
                    else:
                        continue  # Refaz a seleção
                    
                except Exception as e:
                    print(f"❌ Seleção inválida: {e}")
                    print("\n🔄 Tente novamente ou digite '0' para voltar")
                    retry = input("👉 Pressione Enter para tentar novamente ou 0 para voltar: ").strip()
                    if retry == "0":
                        break
                    continue
                    
            if selection == "0":  # Se escolheu voltar
                continue  # Volta ao menu principal
            elif videos_to_upload:  # Se selecionou vídeos
                break  # Sai do loop principal
                
        elif choice == "0":
            print("⬅️ Encerrando sistema de upload...")
            sys.exit(0)
        else:
            print("❌ Opção inválida. Escolha 1, 2, 3 ou 0")
    
    if not videos_to_upload:
        print("❌ Nenhum vídeo selecionado")
        sys.exit(1)
    
    # Resumo e confirmação
    print(f"\n🎯 RESUMO DO UPLOAD:")
    print(f"   📊 Shorts selecionados: {len(videos_to_upload)}")
    print(f"   ⏱️  Tempo estimado: {len(videos_to_upload) * 0.5:.1f} minutos")
    print(f"   📺 Canal: @your_channel")
    
    print(f"\n📋 CONFIRMAÇÃO FINAL:")
    print(f"   S - Confirmar e iniciar upload")
    print(f"   N - Cancelar upload")
    print(f"   0 - Voltar ao menu de seleção")
    
    confirm = input(f"\n✅ Confirma, cancela ou volta? [s/N/0]: ").lower()
    
    if confirm == "0":
        main()  # Reinicia o menu principal
        return
    elif confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Upload cancelado")
        sys.exit(0)
    
    # Realizar upload
    success = upload_selected_shorts(videos_to_upload)
    
    if success:
        print(f"\n🎉 UPLOAD CONCLUÍDO COM SUCESSO!")
        print(f"📺 Acesse: https://youtube.com/@your_channel")
    else:
        print(f"\n❌ Problemas durante o upload")
        sys.exit(1)

def parse_selection(selection, max_num):
    """Parseia seleção de vídeos"""
    indices = set()
    parts = [part.strip() for part in selection.split(',')]
    
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            if 1 <= start <= max_num and 1 <= end <= max_num and start <= end:
                indices.update(range(start, end + 1))
            else:
                raise ValueError(f"Range inválido: {part}")
        else:
            num = int(part)
            if 1 <= num <= max_num:
                indices.add(num)
            else:
                raise ValueError(f"Número fora do range: {num}")
    
    return sorted(list(indices))

def upload_selected_shorts(videos_to_upload):
    """Faz upload dos shorts selecionados"""
    
    print(f"\n🔧 INICIANDO UPLOAD...")
    print("=" * 50)
    
    # Inicializar uploader
    uploader = YouTubeUploader()
    
    if not uploader.authenticate():
        print("❌ Falha na autenticação do YouTube")
        return False
    
    print("✅ Autenticação YouTube OK!")
    
    uploaded_count = 0
    failed_count = 0
    shorts_dir = 'shorts'
    
    for i, filename in enumerate(videos_to_upload, 1):
        file_path = os.path.join(shorts_dir, filename)
        
        print(f"\n⬆️  [{i}/{len(videos_to_upload)}] {filename}")
        print("-" * 40)
        
        # Validar formato
        print("🔍 Validando formato...")
        processor = VideoProcessor()
        video_info = processor.load_video(file_path)
        
        if not video_info:
            print("❌ Erro ao carregar vídeo - pulando...")
            failed_count += 1
            processor.cleanup()
            continue
        
        shorts_format = video_info['validation']['shorts_format']
        
        if shorts_format['is_shorts_format']:
            print("✅ Formato perfeito para YouTube Shorts!")
        else:
            print(f"⚠️  Formato será aceito: {video_info['width']}x{video_info['height']}")
        
        processor.cleanup()
        
        # Gerar metadados
        title = generate_title(filename)
        description = generate_description(filename)
        tags = generate_tags(filename)
        
        print(f"📝 Título: {title}")
        
        try:
            # Upload
            result = uploader.upload_video(
                file_path=file_path,
                title=title,
                description=description,
                tags=tags,
                category='22',
                privacy='public'
            )
            
            if result and result.get('success'):
                video_id = result.get('video_id')
                uploaded_count += 1
                print(f"✅ Upload concluído!")
                print(f"🔗 https://youtu.be/{video_id}")
                
                # 🗑️ Apagar arquivo após upload bem-sucedido
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        print(f"🗑️ Arquivo removido: {filename}")
                except Exception as e:
                    print(f"⚠️ Erro ao remover arquivo: {e}")
                
                # Aguardar entre uploads
                if i < len(videos_to_upload):
                    print("⏳ Aguardando 30s...")
                    time.sleep(30)
            else:
                failed_count += 1
                print("❌ Upload falhou")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Erro: {e}")
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESULTADO FINAL:")
    print(f"   ✅ Sucessos: {uploaded_count}")
    print(f"   ❌ Falhas: {failed_count}")
    print(f"   📊 Total: {len(videos_to_upload)}")
    
    return uploaded_count > 0

def get_video_info(filename):
    """Extrai informações do vídeo original para gerar conteúdo relevante"""
    base_name = filename.replace('.mp4', '')
    
    # Remover sufixos de formato
    clean_name = base_name
    for suffix in ['_teladividida', '_shorts', '_normal']:
        clean_name = clean_name.replace(suffix, '')
    
    # Remover _short_X
    if '_short_' in clean_name:
        clean_name = clean_name.split('_short_')[0]
    
    # Buscar informações do vídeo original no diretório downloads
    downloads_dir = './downloads'
    if os.path.exists(downloads_dir):
        for file in os.listdir(downloads_dir):
            if clean_name.lower() in file.lower() and file.endswith('.info.json'):
                try:
                    import json
                    with open(os.path.join(downloads_dir, file), 'r', encoding='utf-8') as f:
                        info = json.load(f)
                        return {
                            'title': info.get('title', ''),
                            'description': info.get('description', ''),
                            'tags': info.get('tags', []),
                            'channel': info.get('uploader', ''),
                            'duration': info.get('duration', 0)
                        }
                except:
                    pass
    
    return {'title': clean_name, 'description': '', 'tags': [], 'channel': '', 'duration': 0}

def generate_title(filename):
    """Gera título baseado no conteúdo do vídeo"""
    import re
    
    base_name = filename.replace('.mp4', '')
    video_info = get_video_info(filename)
    original_title = video_info['title']
    
    # Extrair número do short
    short_num = "1"
    if '_short_' in base_name:
        parts = base_name.split('_short_')
        if len(parts) == 2:
            number_match = re.search(r'^(\d+)', parts[1])
            if number_match:
                short_num = number_match.group(1)
    
    # Gerar título baseado no conteúdo original
    if original_title:
        # Limpar título original
        clean_title = original_title[:50]
        
        # Detectar temas principais
        title_lower = original_title.lower()
        
        if any(word in title_lower for word in ['ia', 'inteligencia artificial', 'ai', 'machine learning']):
            return f"🤖 {clean_title} - Parte {short_num}"
        elif any(word in title_lower for word in ['automacao', 'automation', 'workflow']):
            return f"⚡ {clean_title} - Parte {short_num}"
        elif any(word in title_lower for word in ['programacao', 'coding', 'desenvolvimento', 'python', 'javascript']):
            return f"💻 {clean_title} - Parte {short_num}"
        elif any(word in title_lower for word in ['negocio', 'business', 'empreendedorismo', 'startup']):
            return f"🚀 {clean_title} - Parte {short_num}"
        elif any(word in title_lower for word in ['tutorial', 'como fazer', 'passo a passo', 'dica']):
            return f"📚 {clean_title} - Parte {short_num}"
        else:
            return f"🎯 {clean_title} - Parte {short_num}"
    
    return f"🎬 Conteúdo Exclusivo - Parte {short_num}"

def generate_description(filename):
    """Gera descrição baseada no conteúdo do vídeo"""
    video_info = get_video_info(filename)
    original_title = video_info['title']
    original_desc = video_info['description'][:200] if video_info['description'] else ""
    
    # Detectar tema principal para descrição personalizada
    if original_title:
        title_lower = original_title.lower()
        
        if any(word in title_lower for word in ['ia', 'inteligencia artificial', 'ai', 'machine learning']):
            return f"""🤖 {original_title}

{original_desc}

💡 Conteúdo sobre Inteligência Artificial:
• Conceitos fundamentais
• Aplicações práticas
• Ferramentas e tecnologias
• Casos de uso reais

🚀 Acompanhe para mais conteúdo sobre IA!

---
📱 CONECTE-SE:
🔗 LinkedIn: Your Name
📧 your.email@example.com

#IA #InteligenciaArtificial #AI #MachineLearning #Tecnologia #Inovacao #TechBrasil #DigitalTransformation"""

        elif any(word in title_lower for word in ['automacao', 'automation', 'workflow']):
            return f"""⚡ {original_title}

{original_desc}

💡 Sobre Automação:
• Otimização de processos
• Ferramentas de automação
• Integração de sistemas
• Produtividade máxima

🚀 Transforme seu workflow!

---
📱 CONECTE-SE:
🔗 LinkedIn: Your Name
📧 your.email@example.com

#Automacao #Automation #Produtividade #Workflow #Tecnologia #Eficiencia #TechTips #Inovacao"""

        elif any(word in title_lower for word in ['programacao', 'coding', 'desenvolvimento', 'python', 'javascript']):
            return f"""💻 {original_title}

{original_desc}

💡 Conteúdo de Programação:
• Técnicas de desenvolvimento
• Boas práticas
• Linguagens de programação
• Projetos práticos

🚀 Evolua suas skills de dev!

---
📱 CONECTE-SE:
🔗 LinkedIn: Your Name
📧 your.email@example.com

#Programacao #Coding #Desenvolvimento #Python #JavaScript #WebDev #SoftwareDevelopment #TechBrasil"""

        elif any(word in title_lower for word in ['negocio', 'business', 'empreendedorismo', 'startup']):
            return f"""🚀 {original_title}

{original_desc}

💡 Conteúdo Empresarial:
• Estratégias de negócio
• Empreendedorismo digital
• Gestão e liderança
• Crescimento sustentável

🚀 Acelere seu negócio!

---
📱 CONECTE-SE:
🔗 LinkedIn: Your Name
📧 your.email@example.com

#Empreendedorismo #Business #Startup #Negocios #Gestao #Lideranca #Estrategia #Crescimento"""

        else:
            return f"""🎯 {original_title}

{original_desc}

💡 Conteúdo de qualidade sobre:
• Tecnologia e inovação
• Desenvolvimento profissional
• Tendências do mercado
• Dicas práticas

🚀 Acompanhe para mais!

---
📱 CONECTE-SE:
🔗 LinkedIn: Your Name
📧 your.email@example.com

#Tecnologia #Inovacao #Profissional #Desenvolvimento #TechTips #Educacao #Conteudo #TechBrasil"""
    
    # Fallback genérico
    return """🎬 Conteúdo exclusivo e de qualidade!

💡 Acompanhe para:
• Dicas e insights valiosos
• Conteúdo educativo
• Tendências e novidades
• Conhecimento prático

🚀 Ative as notificações!

---
📱 CONECTE-SE:
🔗 LinkedIn: Your Name  
📧 your.email@example.com

#Conteudo #Educacao #Dicas #Conhecimento #Aprendizado #TechBrasil"""

def generate_tags(filename):
    """Gera tags baseadas no conteúdo do vídeo"""
    video_info = get_video_info(filename)
    original_title = video_info['title']
    original_tags = video_info['tags']
    
    # Tags base sempre presentes
    base_tags = ['Your Name', 'TechBrasil', 'Conteúdo']
    
    # Tags específicas baseadas no conteúdo
    if original_title:
        title_lower = original_title.lower()
        
        if any(word in title_lower for word in ['ia', 'inteligencia artificial', 'ai', 'machine learning']):
            return base_tags + [
                'IA', 'Inteligência Artificial', 'AI', 'MachineLearning',
                'Tecnologia', 'Inovação', 'DigitalTransformation', 'Automação',
                'TechTips', 'Futuro', 'ChatGPT', 'OpenAI'
            ]
        elif any(word in title_lower for word in ['automacao', 'automation', 'workflow']):
            return base_tags + [
                'Automação', 'Automation', 'Produtividade', 'Workflow',
                'Eficiência', 'Processos', 'Otimização', 'Tecnologia',
                'TechTips', 'Sistemas', 'Integração'
            ]
        elif any(word in title_lower for word in ['programacao', 'coding', 'desenvolvimento', 'python', 'javascript']):
            return base_tags + [
                'Programação', 'Coding', 'Desenvolvimento', 'Python',
                'JavaScript', 'WebDev', 'SoftwareDevelopment', 'Programming',
                'Tech', 'Developer', 'Code', 'Tutorial'
            ]
        elif any(word in title_lower for word in ['negocio', 'business', 'empreendedorismo', 'startup']):
            return base_tags + [
                'Empreendedorismo', 'Business', 'Startup', 'Negócios',
                'Gestão', 'Liderança', 'Estratégia', 'Crescimento',
                'Sucesso', 'Inovação', 'Mercado'
            ]
    
    # Tags do vídeo original se disponíveis
    if original_tags:
        relevant_tags = [tag for tag in original_tags[:8] if len(tag) > 2]
        return base_tags + relevant_tags
    
    # Tags genéricas
    return base_tags + [
        'Tecnologia', 'Educação', 'Dicas', 'Conhecimento',
        'Aprendizado', 'Inovação', 'TechTips', 'Conteúdo',
        'Tutorial', 'Desenvolvimento'
    ]

if __name__ == "__main__":
    main()