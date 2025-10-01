#!/usr/bin/env python3
"""
Script para testar debugging do frontend do painel de frete.
Executa o servidor e mostra instruções para testar.
"""

import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("🔧 TESTE DE DEBUG DO FRONTEND - PAINEL DE FRETE")
    print("=" * 50)
    
    # Mudar para o diretório do projeto
    os.chdir(r"d:\OneDrive\PROJETOFINANCEIRO.PY")
    
    print("📂 Diretório atual:", os.getcwd())
    print("🚀 Iniciando servidor Flask...")
    
    try:
        # Executar o servidor
        processo = subprocess.Popen([
            sys.executable, "run_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar um pouco para o servidor iniciar
        time.sleep(3)
        
        print("\n📋 INSTRUÇÕES PARA TESTE:")
        print("-" * 30)
        print("1. Abra o navegador e vá para: http://127.0.0.1:5000/frete/painel/")
        print("2. Abra o Console do Desenvolvedor (F12)")
        print("3. Vá para a aba 'Console'")
        print("4. Teste os filtros:")
        print("   - Selecione um CLIENTE (ex: Friboi)")
        print("   - Observe os logs no console")
        print("   - Verifique se o gráfico atualiza")
        print("5. Procure por estas mensagens no console:")
        print("   - 🔄 Cliente alterado: [nome]")
        print("   - 🌐 Fazendo requisição para API...")
        print("   - 📊 Dados recebidos da API:")
        print("   - 📈 Atualizando gráfico principal...")
        print("   - 🏁 Gráfico principal atualizado com sucesso!")
        print("   - ✅ Status dos filtros restaurado com sucesso!")
        
        print("\n🎯 EXPECTATIVAS:")
        print("- O gráfico deve mudar os valores ao selecionar filtros")
        print("- Os totais mensais devem atualizar")
        print("- O status deve mostrar o filtro aplicado")
        
        print("\n⚠️  SE NÃO FUNCIONAR:")
        print("- Anote em qual etapa o console para de mostrar logs")
        print("- Verifique se há erros em vermelho no console")
        print("- Teste com diferentes filtros")
        
        print(f"\n🖥️  Abrindo navegador...")
        webbrowser.open("http://127.0.0.1:5000/frete/painel/")
        
        print("\n⏸️  Pressione CTRL+C para parar o servidor")
        
        # Aguardar até o usuário parar o processo
        processo.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        processo.terminate()
        print("✅ Servidor parado.")
    except Exception as e:
        print(f"❌ Erro ao executar: {e}")

if __name__ == "__main__":
    main()