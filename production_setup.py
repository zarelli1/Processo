#!/usr/bin/env python3
"""
Production Setup Script
Script para configurar o sistema em modo de produção
Canal: Your_Channel_Name
"""

import os
import sys
import logging
from main import YouTubeAutomation
from system_validator import SystemValidator

def setup_production():
    """Configura sistema para produção"""
    print("🚀 CONFIGURAÇÃO DE PRODUÇÃO - LEONARDO_ZARELLI")
    print("=" * 60)
    
    try:
        # 1. Validação completa do sistema
        print("\n1️⃣ Validando sistema...")
        validator = SystemValidator()
        results = validator.run_full_validation()
        
        if not results['summary']['success']:
            print("❌ Sistema não validado. Corrija os erros antes de continuar.")
            validator.print_validation_report()
            return False
        
        print("✅ Sistema validado")
        
        # 2. Inicializar automação
        print("\n2️⃣ Inicializando sistema...")
        automation = YouTubeAutomation()
        print("✅ Sistema inicializado")
        
        # 3. Configurar autenticação OAuth
        print("\n3️⃣ Configurando autenticação YouTube...")
        print("🔐 Este passo requer interação do usuário")
        
        if automation.initialize_upload_system():
            print("✅ Autenticação OAuth configurada com sucesso!")
            print("📋 Credenciais salvas em: config/youtube_credentials.pickle")
        else:
            print("❌ Falha na autenticação OAuth")
            return False
        
        # 4. Verificar status final
        print("\n4️⃣ Verificando status final...")
        status = automation.get_system_status()
        
        if status.get('uploader_status', {}).get('service_authenticated', False):
            print("✅ Sistema autenticado e pronto para produção!")
        else:
            print("❌ Sistema não autenticado")
            return False
        
        # 5. Criação de script de produção
        print("\n5️⃣ Criando scripts de produção...")
        create_production_scripts()
        
        print("\n🎉 CONFIGURAÇÃO DE PRODUÇÃO CONCLUÍDA!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python3 production_run.py para processar vídeos")
        print("2. Execute: python3 production_monitor.py para monitorar uploads")
        print("3. Configure cron job para execução automática (opcional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na configuração: {e}")
        return False
    finally:
        if 'automation' in locals():
            automation.cleanup()

def create_production_scripts():
    """Cria scripts de produção"""
    
    # Script principal de produção
    production_run_script = '''#!/usr/bin/env python3
"""
Production Run Script
Executa processamento em modo de produção
"""

import sys
from main import YouTubeAutomation

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 production_run.py <URL_YOUTUBE>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    try:
        automation = YouTubeAutomation()
        print(f"🚀 Processando em produção: {url}")
        
        result = automation.process_video(url)
        
        if result:
            print(f"✅ Sucesso: {result.title}")
        else:
            print("❌ Falha no processamento")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
    finally:
        if 'automation' in locals():
            automation.cleanup()

if __name__ == "__main__":
    main()
'''
    
    # Script de monitoramento
    production_monitor_script = '''#!/usr/bin/env python3
"""
Production Monitor Script
Monitor de uploads em produção
"""

from main import YouTubeAutomation

def main():
    try:
        automation = YouTubeAutomation()
        print("📊 Iniciando monitor de produção...")
        print("Pressione Ctrl+C para parar")
        
        automation.run_upload_monitor()
        
    except KeyboardInterrupt:
        print("\\n🛑 Monitor interrompido")
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        if 'automation' in locals():
            automation.cleanup()

if __name__ == "__main__":
    main()
'''
    
    # Salvar scripts
    with open('production_run.py', 'w') as f:
        f.write(production_run_script)
    
    with open('production_monitor.py', 'w') as f:
        f.write(production_monitor_script)
    
    # Tornar executáveis
    os.chmod('production_run.py', 0o755)
    os.chmod('production_monitor.py', 0o755)
    
    print("✅ Scripts de produção criados:")
    print("   - production_run.py (processa vídeos)")
    print("   - production_monitor.py (monitora uploads)")

if __name__ == "__main__":
    success = setup_production()
    sys.exit(0 if success else 1)