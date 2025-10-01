#!/usr/bin/env python3
"""
Teste das correções: dias não cortados e estilo limpo
"""

import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("🔧 TESTE DAS CORREÇÕES")
    print("=" * 30)
    print("✅ Removidas bolinhas grandes")
    print("✅ Removidas bordas brancas")
    print("✅ Removidos rótulos nas linhas")
    print("✅ Ajustado eixo X (dias não cortados)")
    print("✅ Dados continuam acumulados")
    print("-" * 30)
    
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
        
        print("\n🎯 VERIFICAR:")
        print("- Os números dos dias (1,2,3...) não estão cortados")
        print("- Linhas limpas (sem bolinhas grandes)")
        print("- Sem bordas brancas nos pontos")
        print("- Sem rótulos de valores nas linhas")
        print("- Dados continuam acumulados (crescentes)")
        
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