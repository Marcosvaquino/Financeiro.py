import sys, osimport sys, os

import shutilimport shutil

from datetime import datetimefrom datetime import datetime

root = r'D:\OneDrive\PROJETOFINANCEIRO.PY'

# Configurar caminhosys.path.insert(0, root)

root = r'D:\OneDrive\PROJETOFINANCEIRO.PY'

sys.path.insert(0, root)import openpyxl

from financeiro.veiculo_helper import VeiculoHelper

import openpyxlfrom financeiro.cliente_helper import ClienteHelper

from financeiro.veiculo_helper import VeiculoHelper

from financeiro.cliente_helper import ClienteHelperdef integrar_manifesto_direto(caminho_arquivo):

    """

def integrar_manifesto_direto(caminho_arquivo):    Integra manifesto diretamente no arquivo Excel original

    """    Adiciona 3 colunas: Status_Veiculo, Tipologia, Cliente_Real

    Integra manifesto diretamente no arquivo Excel original    

    Adiciona 3 colunas: Status_Veiculo, Tipologia, Cliente_Real    Args:

    """        caminho_arquivo (str): Caminho para o arquivo Excel

    try:        

        # Backup    Returns:

        backup_dir = os.path.join(os.path.dirname(caminho_arquivo), '..', '..', 'backups')        dict: {"success": bool, "message": str, "backup_path": str}

        os.makedirs(backup_dir, exist_ok=True)    """

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")    try:

        backup_path = os.path.join(backup_dir, f"backup_{timestamp}_{os.path.basename(caminho_arquivo)}")        # Criar backup antes de modificar

        shutil.copy2(caminho_arquivo, backup_path)        backup_dir = os.path.join(os.path.dirname(caminho_arquivo), '..', '..', 'backups')

                os.makedirs(backup_dir, exist_ok=True)

        print(f"💾 Backup: {os.path.basename(backup_path)}")        

        print(f'🚛 INTEGRANDO: {os.path.basename(caminho_arquivo)}')        nome_arquivo = os.path.basename(caminho_arquivo)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Carregar workbook        backup_filename = f"backup_{timestamp}_{nome_arquivo}"

        wb = openpyxl.load_workbook(caminho_arquivo, data_only=True)        backup_path = os.path.join(backup_dir, backup_filename)

        ws = wb.active        

                # Fazer backup

        print(f'📊 Carregado: {ws.max_row} linhas x {ws.max_column} colunas')        shutil.copy2(caminho_arquivo, backup_path)

                print(f"💾 Backup criado: {backup_filename}")

        # Adicionar colunas        

        nova_col_status = ws.max_column + 1        print(f'🚛 INTEGRANDO DIRETAMENTE: {nome_arquivo}')

        nova_col_tipologia = nova_col_status + 1    # Carregar workbook

        nova_col_cliente = nova_col_status + 2    wb = openpyxl.load_workbook(arquivo_original, data_only=True)

            ws = wb.active

        ws.cell(1, nova_col_status, 'Status_Veiculo')    

        ws.cell(1, nova_col_tipologia, 'Tipologia')     print(f'📊 Arquivo carregado: {ws.max_row} linhas x {ws.max_column} colunas')

        ws.cell(1, nova_col_cliente, 'Cliente_Real')    

            # Mostrar TODAS as colunas para identificar

        print(f'✅ Colunas adicionadas: {nova_col_status}, {nova_col_tipologia}, {nova_col_cliente}')    print('\n📋 TODAS as colunas do arquivo:')

            for col in range(1, ws.max_column + 1):

        # Encontrar colunas de dados        valor = ws.cell(1, col).value

        col_placa = col_cliente = None        print(f'  Col {col}: "{valor}"')

        for col in range(1, ws.max_column - 2):    

            valor = str(ws.cell(1, col).value or '').upper()    # Adicionar cabeçalhos das novas colunas

            if 'VEICULO' in valor or 'PLACA' in valor:    nova_col_status = ws.max_column + 1

                col_placa = col    nova_col_tipologia = nova_col_status + 1

                print(f'🚚 Coluna PLACA: Col {col}')    nova_col_cliente = nova_col_status + 2

            elif 'CLASSIFICACAO' in valor or 'CLIENTE' in valor:    

                col_cliente = col    ws.cell(1, nova_col_status, 'Status_Veiculo')

                print(f'👥 Coluna CLIENTE: Col {col}')    ws.cell(1, nova_col_tipologia, 'Tipologia')

            ws.cell(1, nova_col_cliente, 'Cliente_Real')

        # Coletar dados únicos    

        placas = set()    print(f'\n✅ Cabeçalhos adicionados nas colunas {nova_col_status}, {nova_col_tipologia}, {nova_col_cliente}')

        clientes = set()     

        for row in range(2, ws.max_row + 1):    # Identificar colunas manualmente baseado no que encontramos

            if col_placa:    col_placa = None

                placa = ws.cell(row, col_placa).value    col_cliente = None

                if placa: placas.add(str(placa).upper().strip())    

            if col_cliente:    # Buscar coluna de placa/veículo

                cliente = ws.cell(row, col_cliente).value    for col in range(1, ws.max_column - 2):

                if cliente: clientes.add(str(cliente).upper().strip())        valor = str(ws.cell(1, col).value or '').upper()

                if any(palavra in valor for palavra in ['PLACA', 'VEICULO', 'VEHICLE', 'TRUCK']):

        print(f'📊 Únicos: {len(placas)} placas, {len(clientes)} clientes')            col_placa = col

                    print(f'🚚 Coluna PLACA encontrada: Col {col} = "{ws.cell(1, col).value}"')

        # Buscar dados            break

        dados_veiculos = VeiculoHelper.buscar_multiplas_placas(list(placas)) if placas else {}    

        dados_clientes = ClienteHelper.buscar_multiplos_nomes_ajustados(list(clientes)) if clientes else {}    # Buscar coluna de cliente

            for col in range(1, ws.max_column - 2):

        veiculos_encontrados = sum(1 for v in dados_veiculos.values() if v.get('encontrado'))        valor = str(ws.cell(1, col).value or '').upper()

        clientes_encontrados = sum(1 for c in dados_clientes.values() if c.get('encontrado'))        if any(palavra in valor for palavra in ['CLIENTE', 'CLIENT', 'DESTINATARIO', 'REMETENTE']):

        print(f'✅ Encontrados: {veiculos_encontrados} veículos, {clientes_encontrados} clientes')            col_cliente = col

                    print(f'👥 Coluna CLIENTE encontrada: Col {col} = "{ws.cell(1, col).value}"')

        # Integrar            break

        print('🔄 Integrando dados...')    

        for row in range(2, ws.max_row + 1):    # Se não encontrou, usar algumas amostras de dados para tentar identificar

            if col_placa:    if not col_placa or not col_cliente:

                placa = ws.cell(row, col_placa).value        print('\n🔍 Tentando identificar por padrão dos dados...')

                if placa:        for row in range(2, min(6, ws.max_row + 1)):

                    placa_norm = str(placa).upper().strip()            linha_dados = []

                    veiculo = dados_veiculos.get(placa_norm, {})            for col in range(1, min(ws.max_column - 2, 15)):

                    ws.cell(row, nova_col_status, veiculo.get('status') or '0')                valor = ws.cell(row, col).value

                    ws.cell(row, nova_col_tipologia, veiculo.get('tipologia') or '0')                linha_dados.append(f'Col{col}:"{valor}"')

                else:            print(f'  Linha {row}: {" | ".join(linha_dados)}')

                    ws.cell(row, nova_col_status, '0')    

                    ws.cell(row, nova_col_tipologia, '0')    print(f'\n📍 RESULTADO - Placa: Col {col_placa}, Cliente: Col {col_cliente}')

                

            if col_cliente:    # Coletar amostra para testar

                cliente = ws.cell(row, col_cliente).value    placas_amostra = set()

                if cliente:    clientes_amostra = set()

                    cliente_norm = str(cliente).upper().strip()     

                    cliente_dados = dados_clientes.get(cliente_norm, {})    for row in range(2, min(20, ws.max_row + 1)):

                    ws.cell(row, nova_col_cliente, cliente_dados.get('nome_real') or '0')        if col_placa:

                else:            placa = ws.cell(row, col_placa).value

                    ws.cell(row, nova_col_cliente, '0')            if placa and str(placa).strip():

                            placas_amostra.add(str(placa).upper().strip())

            if row % 200 == 0:        

                print(f'  Processadas {row-1} linhas...')        if col_cliente:

                    cliente = ws.cell(row, col_cliente).value

        print('💾 Salvando arquivo...')            if cliente and str(cliente).strip():

        wb.save(caminho_arquivo)                clientes_amostra.add(str(cliente).upper().strip())

            

        resumo = f"✅ {ws.max_row-1} registros | 🚚 {veiculos_encontrados} veículos | 👥 {clientes_encontrados} clientes"    print(f'\n🔍 Amostra: {len(placas_amostra)} placas, {len(clientes_amostra)} clientes')

        print(f'🎉 CONCLUÍDO: {resumo}')    if placas_amostra:

                print(f'  Placas: {list(placas_amostra)[:3]}...')

        return {    if clientes_amostra:

            "success": True,        print(f'  Clientes: {list(clientes_amostra)[:3]}...')

            "message": resumo,    

            "backup_path": backup_path    # Buscar na base de dados

        }    dados_veiculos = {}

            dados_clientes = {}

    except Exception as e:    

        print(f'❌ ERRO: {e}')    if placas_amostra:

        import traceback        dados_veiculos = VeiculoHelper.buscar_multiplas_placas(list(placas_amostra))

        traceback.print_exc()        veiculos_encontrados = sum(1 for v in dados_veiculos.values() if v.get('encontrado', False))

        return {"success": False, "message": f"❌ Erro: {str(e)}", "backup_path": None}        print(f'\n🚚 Veículos encontrados: {veiculos_encontrados}/{len(placas_amostra)}')

    

# Execução direta    if clientes_amostra:

if __name__ == "__main__":        dados_clientes = ClienteHelper.buscar_multiplos_nomes_ajustados(list(clientes_amostra))

    arquivo_teste = os.path.join(root, 'financeiro', 'uploads', 'manifestos', 'Manifesto_Frete_09-25.xlsx')        clientes_encontrados = sum(1 for c in dados_clientes.values() if c.get('encontrado', False))

    if os.path.exists(arquivo_teste):        print(f'👥 Clientes encontrados: {clientes_encontrados}/{len(clientes_amostra)}')

        print("🧪 EXECUTANDO TESTE...")    

        resultado = integrar_manifesto_direto(arquivo_teste)    # Se temos dados, vamos integrar TODAS as linhas

        print(f"Resultado: {resultado['success']}")    print(f'\n🔄 Integrando TODAS as {ws.max_row - 1} linhas...')

    else:    

        print(f"❌ Arquivo não encontrado: {arquivo_teste}")    # Primeiro, coletar TODAS as placas e clientes únicos

        print("Para usar: integrar_manifesto_direto('/caminho/arquivo.xlsx')")    todas_placas = set()
    todos_clientes = set()
    
    for row in range(2, ws.max_row + 1):
        if col_placa:
            placa = ws.cell(row, col_placa).value
            if placa and str(placa).strip():
                todas_placas.add(str(placa).upper().strip())
        
        if col_cliente:
            cliente = ws.cell(row, col_cliente).value
            if cliente and str(cliente).strip():
                todos_clientes.add(str(cliente).upper().strip())
    
    print(f'📊 Total únicos: {len(todas_placas)} placas, {len(todos_clientes)} clientes')
    
    # Buscar TODOS os dados
    if todas_placas:
        print('🚚 Buscando TODOS os veículos...')
        dados_veiculos = VeiculoHelper.buscar_multiplas_placas(list(todas_placas))
    
    if todos_clientes:
        print('👥 Buscando TODOS os clientes...')
        dados_clientes = ClienteHelper.buscar_multiplos_nomes_ajustados(list(todos_clientes))
    
    # Integrar linha por linha
    linhas_processadas = 0
    for row in range(2, ws.max_row + 1):
        # Status e tipologia do veículo
        if col_placa:
            placa = ws.cell(row, col_placa).value
            if placa and str(placa).strip():
                placa_norm = str(placa).upper().strip()
                veiculo = dados_veiculos.get(placa_norm, {})
                ws.cell(row, nova_col_status, veiculo.get('status') or '0')
                ws.cell(row, nova_col_tipologia, veiculo.get('tipologia') or '0')
            else:
                ws.cell(row, nova_col_status, '0')
                ws.cell(row, nova_col_tipologia, '0')
        else:
            ws.cell(row, nova_col_status, '0')
            ws.cell(row, nova_col_tipologia, '0')
        
        # Cliente real
        if col_cliente:
            cliente = ws.cell(row, col_cliente).value
            if cliente and str(cliente).strip():
                cliente_norm = str(cliente).upper().strip()
                cliente_dados = dados_clientes.get(cliente_norm, {})
                ws.cell(row, nova_col_cliente, cliente_dados.get('nome_real') or '0')
            else:
                ws.cell(row, nova_col_cliente, '0')
        else:
            ws.cell(row, nova_col_cliente, '0')
        
        linhas_processadas += 1
        
        if linhas_processadas % 200 == 0:
            print(f'  Processadas {linhas_processadas} linhas...')
    
    # Salvar arquivo
    print('💾 Salvando arquivo...')
    wb.save(arquivo_original)
    
    print(f'\n🎉 INTEGRAÇÃO COMPLETA!')
    print(f'📁 Arquivo: {arquivo_original}')
    print(f'📊 {linhas_processadas} linhas integradas')
    print(f'➕ 3 colunas adicionadas: Status_Veiculo (Col {nova_col_status}), Tipologia (Col {nova_col_tipologia}), Cliente_Real (Col {nova_col_cliente})')
    print(f'🚚 {len(dados_veiculos)} placas processadas')
    print(f'👥 {len(dados_clientes)} clientes processados')
    
except Exception as e:
    print(f'❌ ERRO: {e}')
    import traceback
    traceback.print_exc()