#!/usr/bin/env python3
"""
Upload automático dos shorts existentes
"""

import os
import time
from youtube_uploader import YouTubeUploader
from video_processor import VideoProcessor

def parse_selection(selection, max_num):
    """
    Parseia seleção de vídeos (ex: 1,3,5 ou 1-4 ou 2,5-7)
    
    Args:
        selection: String com seleção (ex: "1,3,5" ou "1-4")
        max_num: Número máximo permitido
        
    Returns:
        Lista de índices selecionados
    """
    indices = set()
    
    # Dividir por vírgulas
    parts = [part.strip() for part in selection.split(',')]
    
    for part in parts:
        if '-' in part:
            # Range (ex: 1-4)
            try:
                start, end = map(int, part.split('-'))
                if 1 <= start <= max_num and 1 <= end <= max_num and start <= end:
                    indices.update(range(start, end + 1))
                else:
                    raise ValueError(f"Range inválido: {part}")
            except ValueError:
                raise ValueError(f"Range mal formatado: {part}")
        else:
            # Número individual
            try:
                num = int(part)
                if 1 <= num <= max_num:
                    indices.add(num)
                else:
                    raise ValueError(f"Número fora do range: {num}")
            except ValueError:
                raise ValueError(f"Número inválido: {part}")
    
    return sorted(list(indices))

def upload_all_shorts():
    """Upload de shorts com opção de escolher quantidade"""
    
    print("🚀 UPLOAD AUTOMÁTICO DOS SHORTS")
    print("=" * 50)
    
    # Verificar pasta de shorts
    shorts_dir = 'shorts'
    if not os.path.exists(shorts_dir):
        print("❌ Pasta 'shorts' não encontrada")
        return False
    
    # Listar arquivos
    shorts_files = [f for f in os.listdir(shorts_dir) if f.endswith('.mp4')]
    shorts_files.sort()  # Ordenar alfabeticamente
    
    if not shorts_files:
        print("❌ Nenhum short encontrado")
        return False
    
    print(f"📁 Encontrados {len(shorts_files)} shorts disponíveis:")
    for i, file in enumerate(shorts_files, 1):
        size = os.path.getsize(os.path.join(shorts_dir, file)) / (1024*1024)
        print(f"   {i}. {file} ({size:.1f} MB)")
    
    # Perguntar quantos vídeos fazer upload
    print(f"\n📊 OPÇÕES DE UPLOAD:")
    print(f"   1. Todos os {len(shorts_files)} shorts")
    print(f"   2. Escolher quantidade específica")
    print(f"   3. Selecionar shorts individualmente")
    
    choice = input(f"\n🔢 Escolha uma opção (1-3): ").strip()
    
    videos_to_upload = []
    
    if choice == "1":
        # Todos os vídeos
        videos_to_upload = shorts_files
        print(f"✅ Selecionados TODOS os {len(videos_to_upload)} shorts para upload")
        
    elif choice == "2":
        # Quantidade específica
        try:
            max_videos = len(shorts_files)
            num_videos = int(input(f"📝 Quantos shorts fazer upload? (1-{max_videos}): "))
            
            if 1 <= num_videos <= max_videos:
                videos_to_upload = shorts_files[:num_videos]
                print(f"✅ Selecionados os primeiros {num_videos} shorts para upload")
            else:
                print(f"❌ Número inválido. Deve ser entre 1 e {max_videos}")
                return False
                
        except ValueError:
            print("❌ Entrada inválida. Digite um número.")
            return False
            
    elif choice == "3":
        # Seleção individual
        print(f"\n📋 Digite os números dos shorts que deseja fazer upload:")
        print(f"   Exemplo: 1,3,5 ou 1-4 ou 2,5-7")
        selection = input("🔢 Sua seleção: ").strip()
        
        try:
            selected_indices = parse_selection(selection, len(shorts_files))
            videos_to_upload = [shorts_files[i-1] for i in selected_indices]
            print(f"✅ Selecionados {len(videos_to_upload)} shorts para upload:")
            for video in videos_to_upload:
                print(f"   • {video}")
        except Exception as e:
            print(f"❌ Seleção inválida: {e}")
            return False
    else:
        print("❌ Opção inválida")
        return False
    
    if not videos_to_upload:
        print("❌ Nenhum vídeo selecionado")
        return False
    
    # Confirmação final
    print(f"\n🎯 RESUMO DO UPLOAD:")
    print(f"   📊 Total de shorts: {len(videos_to_upload)}")
    print(f"   ⏱️  Tempo estimado: {len(videos_to_upload) * 0.5:.1f} minutos")
    
    confirm = input(f"\n✅ Confirma o upload de {len(videos_to_upload)} shorts? [s/N]: ").lower()
    if confirm not in ['s', 'sim', 'y', 'yes']:
        print("❌ Upload cancelado pelo usuário")
        return False
    
    # Inicializar uploader
    print("\n🔧 Inicializando YouTube Uploader...")
    uploader = YouTubeUploader()
    
    if not uploader.authenticate():
        print("❌ Falha na autenticação")
        return False
    
    print("✅ Autenticação OK!")
    
    # Upload de cada arquivo selecionado
    uploaded_count = 0
    failed_count = 0
    
    for i, filename in enumerate(videos_to_upload, 1):
        file_path = os.path.join(shorts_dir, filename)
        
        print(f"\n⬆️  [{i}/{len(videos_to_upload)}] Uploading: {filename}")
        print("-" * 40)
        
        # Validar formato do vídeo
        print("🔍 Validando formato do vídeo...")
        processor = VideoProcessor()
        video_info = processor.load_video(file_path)
        
        if not video_info:
            print("❌ Erro ao carregar vídeo - pulando...")
            failed_count += 1
            processor.cleanup()
            continue
        
        # Verificar se está no formato correto para Shorts
        shorts_format = video_info['validation']['shorts_format']
        
        if not shorts_format['is_shorts_format'] and shorts_format['needs_conversion']:
            print(f"⚠️  Formato não é ideal para Shorts: {video_info['width']}x{video_info['height']}")
            print(f"📐 Aspecto atual: {shorts_format['current_aspect_ratio']:.3f} (ideal: {shorts_format['target_aspect_ratio']:.3f})")
            
            # Oferecer conversão
            response = input("🔄 Converter para formato Shorts (1080x1920, 9:16)? [s/N]: ").lower()
            if response in ['s', 'sim', 'y', 'yes']:
                print("🔄 Convertendo vídeo...")
                converted_path = processor.convert_to_shorts_format()
                
                if converted_path:
                    file_path = converted_path
                    print(f"✅ Vídeo convertido: {converted_path}")
                else:
                    print("❌ Falha na conversão - usando vídeo original")
            else:
                print("⚠️  Usando vídeo no formato original")
        else:
            if shorts_format['is_shorts_format']:
                print("✅ Formato perfeito para YouTube Shorts!")
            else:
                print("ℹ️  Formato será aceito pelo YouTube")
        
        # Limpar recursos do processor
        processor.cleanup()
        
        # Gerar metadados inteligentes
        title = generate_title(filename)
        description = generate_description(filename)
        tags = generate_tags(filename)
        
        metadata = {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '22',  # People & Blogs
            'privacyStatus': 'public'  # PÚBLICO
        }
        
        print(f"📝 Título: {title}")
        print(f"🏷️  Tags: {', '.join(tags[:3])}...")
        
        try:
            # Fazer upload com parâmetros corretos
            result = uploader.upload_video(
                file_path=file_path,
                title=metadata['title'],
                description=metadata['description'],
                tags=metadata['tags'],
                category=metadata['categoryId'],
                privacy=metadata['privacyStatus']
            )
            
            if result and result.get('success'):
                video_id = result.get('video_id')
                uploaded_count += 1
                print(f"✅ Upload concluído!")
                print(f"🔗 YouTube: https://youtu.be/{video_id}")
                
                # Aguardar entre uploads (rate limiting)
                if i < len(videos_to_upload):
                    print("⏳ Aguardando 30s antes do próximo upload...")
                    time.sleep(30)
            else:
                failed_count += 1
                print("❌ Upload falhou")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Erro no upload: {e}")
    
    # Resumo final
    print("\n" + "="*50)
    print("📊 RESUMO DO UPLOAD:")
    print(f"   ✅ Sucessos: {uploaded_count}")
    print(f"   ❌ Falhas: {failed_count}")
    print(f"   📊 Total: {len(videos_to_upload)}")
    
    if uploaded_count > 0:
        print(f"\n🎉 {uploaded_count} shorts publicados no canal Leonardo_Zarelli!")
        print("🔗 Acesse: https://youtube.com/@leonardo_zarelli")
    
    return uploaded_count > 0

def generate_title(filename):
    """Gerar título inteligente baseado no arquivo"""
    
    # Remover extensão e limpar nome
    base_name = filename.replace('.mp4', '')
    
    # Se contém "short_X", extrair número
    if 'short_' in base_name:
        parts = base_name.split('_short_')
        if len(parts) == 2:
            video_name = parts[0]
            short_num = parts[1]
            
            # Criar título mais atrativo
            if 'Ecossistema' in video_name:
                titles = [
                    f"🚀 Como Estruturar Seu Ecossistema de IA - Parte {short_num}",
                    f"💡 Automação com IA: Meu Sistema Completo #{short_num}",
                    f"🎯 Ecossistema dos Sonhos com IA e Automação #{short_num}",
                    f"⚡ Transformando Negócios com IA - Episódio {short_num}",
                    f"🔥 Meu Setup de IA que Mudou Tudo - Parte {short_num}"
                ]
                return titles[int(short_num) % len(titles)]
    
    # Título padrão
    return f"🚀 {base_name[:45]}... #IA #Automação"

def generate_description(filename):
    """Gerar descrição otimizada"""
    
    return """🎯 Transformando negócios com Inteligência Artificial e Automação!

📈 Neste vídeo compartilho estratégias práticas de como estruturar um ecossistema completo de IA para maximizar produtividade e resultados.

💡 O que você vai aprender:
• Ferramentas de IA essenciais
• Automação de processos
• Integração de sistemas
• Otimização de workflow

🚀 Quer dominar IA e Automação? 
👉 Ative o sininho e acompanhe a série completa!

---
📱 CONECTE-SE COMIGO:
🔗 LinkedIn: Leonardo Zarelli
📧 Contato: lzrgeracaoz2000@gmail.com

#IA #InteligenciaArtificial #Automacao #Tecnologia #Produtividade #Empreendedorismo #DigitalTransformation #AI #MachineLearning #TechTips #Inovacao #Startup #TechBrasil"""

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

def generate_tags(filename):
    """Gera tags baseadas no conteúdo do vídeo"""
    video_info = get_video_info(filename)
    original_title = video_info['title']
    original_tags = video_info['tags']
    
    # Tags base sempre presentes
    base_tags = ['Leonardo Zarelli', 'TechBrasil', 'Conteúdo']
    
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
    success = upload_all_shorts()
    
    if success:
        print("\n🎉 UPLOAD AUTOMÁTICO CONCLUÍDO!")
        print("📺 Seus shorts estão sendo processados pelo YouTube")
        print("⏰ Em alguns minutos estarão disponíveis publicamente")
        
        print("\n🔄 PARA PROCESSAR NOVOS VÍDEOS:")
        print("python3 production_script.py https://youtu.be/VIDEO_ID 5")
    else:
        print("❌ Problemas no upload automático")