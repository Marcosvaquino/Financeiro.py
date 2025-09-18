import sys
sys.path.append('financeiro')

from database import init_db, get_connection
from main import build_dashboard_data_with_filters
import json

# Testa a função para agosto de 2025
print("=== TESTE DA FUNÇÃO DASHBOARD ===")

try:
    data = build_dashboard_data_with_filters(8, 2025)
    print("\nEstrutura retornada:")
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
except Exception as e:
    print(f"Erro: {e}")
    import traceback
    traceback.print_exc()