#!/usr/bin/env python3
"""
Teste: Rótulos APENAS na linha verde (Frete Correto)
"""

import subprocess
import webbrowser
import time
import sys
import os

def main():
    print("💚 TESTE: RÓTULOS APENAS NO FRETE CORRETO")
    print("=" * 40)
    print("✅ Rótulos APENAS na linha verde (Frete Correto)")
    print("❌ SEM rótulos na linha laranja (Despesas Gerais)")
    print("✅ Dados acumulados mantidos")
    print("✅ Números dos dias todos visíveis")
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
        
        print("\n👀 DEVE MOSTRAR:")
        print("💚 Rótulos verdes APENAS na linha do Frete Correto")
        print("🚫 NENHUM rótulo na linha laranja (Despesas Gerais)")
        print("📊 Valores tipo 'R$ 190k', 'R$ 470k', etc.")
        print("📅 A cada 5 dias + último dia (1, 5, 10, 15, 20, 25, 30, 31)")
        
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