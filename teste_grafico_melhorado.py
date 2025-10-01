#!/usr/bin/env python3
"""
Script rápido para testar as melhorias do gráfico
"""

import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("🎨 TESTE DAS MELHORIAS DO GRÁFICO")
    print("=" * 40)
    print("✅ Dados acumulados implementados")
    print("✅ Números dos dias (sem 'Dia')")
    print("✅ Rótulos de dados nas linhas")
    print("✅ Melhor visualização do eixo X")
    print("-" * 40)
    
    # Mudar para o diretório do projeto
    os.chdir(r"d:\OneDrive\PROJETOFINANCEIRO.PY")
    
    print("🚀 Iniciando servidor...")
    
    try:
        # Executar o servidor
        processo = subprocess.Popen([
            sys.executable, "run_app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Aguardar um pouco para o servidor iniciar
        time.sleep(3)
        
        print(f"🖥️  Abrindo http://127.0.0.1:5000/frete/painel/")
        webbrowser.open("http://127.0.0.1:5000/frete/painel/")
        
        print("\n🔍 VERIFICAR:")
        print("- Gráfico mostra valores acumulados (crescentes)")
        print("- Eixo X mostra apenas números (1, 2, 3...)")
        print("- Rótulos com valores aparecem nas linhas")
        print("- Datas não estão cortadas")
        
        print("\n⏸️  Pressione CTRL+C para parar")
        
        # Aguardar até o usuário parar o processo
        processo.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        processo.terminate()
        print("✅ Servidor parado.")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()