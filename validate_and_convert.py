#!/usr/bin/env python3
"""
🎬 MENU INTERATIVO - VALIDADOR YOUTUBE SHORTS
Interface amigável para validar e converter vídeos
"""

import os
import sys
from youtube_shorts_validator import YouTubeShortsValidator

def main():
    """Menu interativo principal"""
    
    print("🎬 VALIDADOR E CONVERSOR YOUTUBE SHORTS")
    print("=" * 60)
    print("📱 Formato obrigatório: 1080x1920 pixels (9:16)")
    print("⏱️ Duração máxima: 3 minutos")
    print("🎯 Orientação: Vertical (retrato)")
    print("=" * 60)
    
    validator = YouTubeShortsValidator()
    
    while True:
        print("\n🔧 OPÇÕES DISPONÍVEIS:")
        print("   1 📋 Validar um vídeo específico")
        print("   2 🔄 Converter um vídeo para YouTube Shorts")
        print("   3 📁 Validar todos os vídeos de uma pasta")
        print("   4 🔄 Converter todos os vídeos de uma pasta")
        print("   5 📊 Validar shorts existentes (pasta ./shorts/)")
        print("   6 ❌ Sair")
        
        choice = input("\n👉 Escolha uma opção (1-6): ").strip()
        
        if choice == "1":
            validate_single_video(validator)
        elif choice == "2":
            convert_single_video(validator)
        elif choice == "3":
            validate_directory(validator)
        elif choice == "4":
            convert_directory(validator)
        elif choice == "5":
            validate_shorts_folder(validator)
        elif choice == "6":
            print("\n👋 Encerrando validador...")
            break
        else:
            print("❌ Opção inválida. Escolha 1, 2, 3, 4, 5 ou 6")

def validate_single_video(validator):
    """Validar um vídeo específico"""
    print("\n📋 VALIDAÇÃO DE VÍDEO ÚNICO")
    print("-" * 40)
    
    video_path = input("📁 Digite o caminho do vídeo: ").strip()
    
    if not video_path:
        print("❌ Caminho vazio")
        return
    
    if not os.path.exists(video_path):
        print(f"❌ Arquivo não encontrado: {video_path}")
        return
    
    print(f"\n🔍 Validando: {os.path.basename(video_path)}")
    result = validator.validate_video(video_path)
    
    print_validation_result(result)

def convert_single_video(validator):
    """Converter um vídeo específico"""
    print("\n🔄 CONVERSÃO DE VÍDEO ÚNICO")
    print("-" * 40)
    
    video_path = input("📁 Digite o caminho do vídeo: ").strip()
    
    if not video_path:
        print("❌ Caminho vazio")
        return
    
    if not os.path.exists(video_path):
        print(f"❌ Arquivo não encontrado: {video_path}")
        return
    
    # Primeiro validar
    print(f"\n🔍 Validando: {os.path.basename(video_path)}")
    result = validator.validate_video(video_path)
    
    if result.get('valid', False):
        print("✅ Vídeo já está no formato correto!")
        return
    
    print_validation_result(result, show_conversion_option=False)
    
    # Perguntar se quer converter
    convert = input("\n🔄 Converter para YouTube Shorts? [s/N]: ").lower()
    if convert not in ['s', 'sim', 'y', 'yes']:
        print("❌ Conversão cancelada")
        return
    
    # Converter
    print(f"\n🔄 Convertendo vídeo...")
    converted_path = validator.convert_to_youtube_shorts(video_path)
    
    if converted_path:
        print(f"\n🎉 CONVERSÃO CONCLUÍDA!")
        print(f"📁 Arquivo convertido: {converted_path}")
        
        # Validar resultado
        final_result = validator.validate_video(converted_path)
        if final_result.get('valid', False):
            print("✅ Vídeo convertido está perfeito para YouTube Shorts!")
        else:
            print("⚠️ Conversão pode ter problemas")
    else:
        print("\n❌ FALHA NA CONVERSÃO")

def validate_directory(validator):
    """Validar todos os vídeos de uma pasta"""
    print("\n📁 VALIDAÇÃO DE PASTA")
    print("-" * 40)
    
    directory = input("📂 Digite o caminho da pasta: ").strip()
    
    if not directory:
        print("❌ Caminho vazio")
        return
    
    if not os.path.exists(directory):
        print(f"❌ Pasta não encontrada: {directory}")
        return
    
    print(f"\n🔍 Validando vídeos em: {directory}")
    results = validator.batch_validate(directory)
    
    if not results:
        print("❌ Nenhum vídeo encontrado na pasta")
        return
    
    print_batch_results(results)

def convert_directory(validator):
    """Converter todos os vídeos de uma pasta"""
    print("\n🔄 CONVERSÃO DE PASTA")
    print("-" * 40)
    
    directory = input("📂 Digite o caminho da pasta: ").strip()
    
    if not directory:
        print("❌ Caminho vazio")
        return
    
    if not os.path.exists(directory):
        print(f"❌ Pasta não encontrada: {directory}")
        return
    
    # Primeiro mostrar o que será convertido
    results = validator.batch_validate(directory)
    
    if not results:
        print("❌ Nenhum vídeo encontrado na pasta")
        return
    
    invalid_videos = [r for r in results if not r.get('valid', False)]
    
    if not invalid_videos:
        print("✅ Todos os vídeos já estão no formato correto!")
        return
    
    print(f"\n📊 Encontrados {len(invalid_videos)} vídeos que precisam de conversão:")
    for result in invalid_videos:
        filename = os.path.basename(result['file_path'])
        print(f"   🔄 {filename}")
    
    # Confirmar conversão
    convert = input(f"\n🔄 Converter {len(invalid_videos)} vídeos? [s/N]: ").lower()
    if convert not in ['s', 'sim', 'y', 'yes']:
        print("❌ Conversão cancelada")
        return
    
    # Converter
    print(f"\n🔄 Convertendo vídeos...")
    converted_files = validator.batch_convert(directory)
    
    print(f"\n🎉 CONVERSÃO EM LOTE CONCLUÍDA!")
    print(f"📊 {len(converted_files)} vídeos convertidos")
    
    if converted_files:
        print("\n✅ Arquivos convertidos:")
        for file_path in converted_files:
            print(f"   • {os.path.basename(file_path)}")

def validate_shorts_folder(validator):
    """Validar pasta shorts específica"""
    shorts_dir = "./shorts"
    
    print(f"\n📊 VALIDAÇÃO DA PASTA SHORTS")
    print("-" * 40)
    
    if not os.path.exists(shorts_dir):
        print(f"❌ Pasta {shorts_dir} não encontrada")
        print("💡 Execute primeiro: python3 production_script.py URL_VIDEO")
        return
    
    results = validator.batch_validate(shorts_dir)
    
    if not results:
        print("❌ Nenhum vídeo encontrado na pasta shorts")
        return
    
    print_batch_results(results)
    
    # Oferecer conversão dos que estão incorretos
    invalid_videos = [r for r in results if not r.get('valid', False)]
    
    if invalid_videos:
        print(f"\n⚠️ {len(invalid_videos)} vídeos não estão no formato correto")
        convert = input("🔄 Converter todos para formato YouTube Shorts? [s/N]: ").lower()
        
        if convert in ['s', 'sim', 'y', 'yes']:
            converted_files = validator.batch_convert(shorts_dir)
            print(f"\n🎉 {len(converted_files)} vídeos convertidos!")

def print_validation_result(result, show_conversion_option=True):
    """Imprime resultado de validação de forma amigável"""
    
    if 'error' in result:
        print(f"❌ ERRO: {result['error']}")
        return
    
    print("-" * 50)
    
    if result.get('valid', False):
        print("✅ VÍDEO PERFEITO PARA YOUTUBE SHORTS!")
    else:
        print("❌ VÍDEO NÃO ESTÁ NO FORMATO CORRETO")
    
    if 'current_specs' in result:
        specs = result['current_specs']
        target = result['target_specs']
        
        print(f"\n📊 ESPECIFICAÇÕES:")
        print(f"   📐 Resolução: {specs['resolution']} {'✅' if specs['width'] == 1080 and specs['height'] == 1920 else '❌'}")
        print(f"   📏 Proporção: {specs['aspect_ratio']:.3f} {'✅' if abs(specs['aspect_ratio'] - 0.5625) <= 0.01 else '❌'} (alvo: 0.563)")
        print(f"   📱 Orientação: {'Vertical ✅' if specs['is_vertical'] else 'Horizontal ❌'}")
        print(f"   ⏱️ Duração: {specs['duration']:.1f}s {'✅' if specs['duration'] <= 180 else '❌'} (máx: 180s)")
        print(f"   🎬 FPS: {specs['fps']:.1f}")
        print(f"   🔊 Áudio: {'Sim ✅' if specs['has_audio'] else 'Não ⚠️'}")
        print(f"   💾 Tamanho: {specs['file_size_mb']:.1f} MB")
    
    if 'issues' in result and result['issues']:
        print(f"\n🚨 PROBLEMAS ENCONTRADOS:")
        for issue in result['issues']:
            print(f"   • {issue}")
    
    if 'recommendations' in result and result['recommendations']:
        print(f"\n💡 RECOMENDAÇÕES:")
        for rec in result['recommendations']:
            print(f"   • {rec}")
    
    if show_conversion_option and result.get('needs_conversion', False):
        print(f"\n🔄 Este vídeo precisa ser convertido para YouTube Shorts")

def print_batch_results(results):
    """Imprime resultados de validação em lote"""
    
    valid_count = sum(1 for r in results if r.get('valid', False))
    total_count = len(results)
    
    print(f"\n📊 RESULTADO DA VALIDAÇÃO:")
    print(f"   ✅ Vídeos corretos: {valid_count}")
    print(f"   ❌ Vídeos incorretos: {total_count - valid_count}")
    print(f"   📊 Total analisado: {total_count}")
    
    print(f"\n📋 DETALHES POR ARQUIVO:")
    
    for result in results:
        filename = os.path.basename(result['file_path'])
        
        if result.get('valid', False):
            print(f"   ✅ {filename} - Perfeito para YouTube Shorts")
        elif 'error' in result:
            print(f"   ❌ {filename} - ERRO: {result['error']}")
        else:
            specs = result.get('current_specs', {})
            resolution = specs.get('resolution', 'N/A')
            duration = specs.get('duration', 0)
            print(f"   ❌ {filename} - {resolution}, {duration:.1f}s")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Encerrando...")
        sys.exit(0)