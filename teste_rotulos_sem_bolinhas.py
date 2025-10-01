#!/usr/bin/env python3
"""
Teste: Rótulos de dados SIM, bolinhas brancas NÃO
"""

import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("🎯 TESTE: RÓTULOS SIM, BOLINHAS NÃO")
    print("=" * 35)
    print("✅ Rótulos de dados nas linhas (como Excel)")
    print("✅ Linhas limpas (sem bolinhas grandes)")
    print("✅ Dados acumulados mantidos")
    print("✅ Números dos dias todos visíveis")
    print("-" * 35)
    
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
        
        print("\n🔍 DEVE MOSTRAR:")
        print("✅ Rótulos com valores (R$ 190k, R$ 313k, etc.)")
        print("✅ Rótulos a cada 5 dias + último dia")  
        print("✅ Linhas simples (sem bolinhas grandes)")
        print("✅ Dados crescendo (acumulados)")
        print("✅ Números 1,2,3...31 todos visíveis")
        
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