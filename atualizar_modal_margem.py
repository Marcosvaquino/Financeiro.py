import re

# Ler o arquivo HTML
with open('financeiro/templates/painel_frete.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Procurar o modal de margem e substituir
pattern = r'(<!-- Modal de Análise de Margem Líquida REFORMULADO -->.*?<div class="modal-body">)(.*?)(</div>\s*</div>\s*</div>\s*<!-- Modal de Análise de Rentabilidade -->)'

new_modal_body = '''
                <!-- Cards executivos no topo -->
                <div class="executive-stats-grid compact">
                    <div class="exec-stat-card profit">
                        <div class="stat-header">
                            <span class="stat-icon">💎</span>
                            <h4>Total Margem</h4>
                        </div>
                        <div class="stat-value" id="exec-margem-total">R$ 0</div>
                        <div class="stat-detail">Receita - Despesas</div>
                        <div class="stat-growth positive">Lucro</div>
                    </div>
                    
                    <div class="exec-stat-card efficiency">
                        <div class="stat-header">
                            <span class="stat-icon">🏆</span>
                            <h4>Top Cliente</h4>
                        </div>
                        <div class="stat-value" id="exec-melhor-margem-cliente" style="font-size: 18px;">-</div>
                        <div class="stat-detail" id="exec-melhor-margem-valor">R$ 0</div>
                        <div class="stat-growth positive" id="exec-melhor-margem-percent">0%</div>
                    </div>
                    
                    <div class="exec-stat-card benchmark">
                        <div class="stat-header">
                            <span class="stat-icon">⚡</span>
                            <h4>% Médio</h4>
                        </div>
                        <div class="stat-value" id="exec-percentual-margem">0%</div>
                        <div class="stat-detail">Rentabilidade</div>
                        <div class="stat-growth neutral" id="exec-status-margem">Excelente</div>
                    </div>
                    
                    <div class="exec-stat-card savings">
                        <div class="stat-header">
                            <span class="stat-icon">💰</span>
                            <h4>Ticket Médio</h4>
                        </div>
                        <div class="stat-value" id="exec-ticket-medio-margem">R$ 0</div>
                        <div class="stat-detail" id="exec-margem-media-desc">Por Operação</div>
                        <div class="stat-growth positive">Média</div>
                    </div>
                </div>

                <!-- Top 5 - Clientes Mais Rentáveis -->
                <div class="executive-analysis">
                    <div class="analysis-section">
                        <h3>🎯 Top 5 - Clientes Mais Rentáveis</h3>
                        <div class="top-items-container">
                            <div class="top-items-grid">
                                <div class="top-item-card">
                                    <div class="rank">1º</div>
                                    <div class="item-info">
                                        <h4 id="top-margem-cliente-1">-</h4>
                                        <span id="top-margem-valor-1">R$ 0</span>
                                    </div>
                                    <div class="item-metric">
                                        <span id="top-margem-percent-1">0%</span>
                                        <small>margem</small>
                                    </div>
                                </div>
                                <div class="top-item-card">
                                    <div class="rank">2º</div>
                                    <div class="item-info">
                                        <h4 id="top-margem-cliente-2">-</h4>
                                        <span id="top-margem-valor-2">R$ 0</span>
                                    </div>
                                    <div class="item-metric">
                                        <span id="top-margem-percent-2">0%</span>
                                        <small>margem</small>
                                    </div>
                                </div>
                                <div class="top-item-card">
                                    <div class="rank">3º</div>
                                    <div class="item-info">
                                        <h4 id="top-margem-cliente-3">-</h4>
                                        <span id="top-margem-valor-3">R$ 0</span>
                                    </div>
                                    <div class="item-metric">
                                        <span id="top-margem-percent-3">0%</span>
                                        <small>margem</small>
                                    </div>
                                </div>
                                <div class="top-item-card">
                                    <div class="rank">4º</div>
                                    <div class="item-info">
                                        <h4 id="top-margem-cliente-4">-</h4>
                                        <span id="top-margem-valor-4">R$ 0</span>
                                    </div>
                                    <div class="item-metric">
                                        <span id="top-margem-percent-4">0%</span>
                                        <small>margem</small>
                                    </div>
                                </div>
                                <div class="top-item-card">
                                    <div class="rank">5º</div>
                                    <div class="item-info">
                                        <h4 id="top-margem-cliente-5">-</h4>
                                        <span id="top-margem-valor-5">R$ 0</span>
                                    </div>
                                    <div class="item-metric">
                                        <span id="top-margem-percent-5">0%</span>
                                        <small>margem</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Filtros DEPOIS dos Top 5 -->
                <div class="modal-filters">
                    <div class="filter-group">
                        <label>🏢 Filtrar por Cliente:</label>
                        <select id="filtro-cliente-margem" onchange="filtrarTabelaMargem()">
                            <option value="">Todos os Clientes</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>🚚 Filtrar por Veículo:</label>
                        <select id="filtro-veiculo-margem" onchange="filtrarTabelaMargem()">
                            <option value="">Todos os Veículos</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <label>📅 Filtrar por Mês:</label>
                        <select id="filtro-mes-margem" onchange="filtrarTabelaMargem()">
                            <option value="">Todos os Meses</option>
                        </select>
                    </div>
                    <div class="filter-group">
                        <button class="btn-clear-filters" onclick="limparFiltrosMargem()">🗑️ Limpar Filtros</button>
                    </div>
                </div>

                <!-- Tabela completa COM TODAS as operações -->
                <div class="modal-table-container">
                    <table class="modal-table">
                        <thead>
                            <tr>
                                <th>CLIENTE</th>
                                <th>VEÍCULO</th>
                                <th>RECEITA</th>
                                <th>DESPESAS</th>
                                <th>MARGEM LÍQUIDA</th>
                                <th>% MARGEM</th>
                            </tr>
                        </thead>
                        <tbody id="tabela-margem-completa">
                            <tr><td colspan="6">Carregando dados...</td></tr>
                        </tbody>
                    </table>
                </div>
            '''

# Fazer a substituição
new_content = re.sub(pattern, r'\1' + new_modal_body + r'\3', content, flags=re.DOTALL)

# Salvar o arquivo
with open('financeiro/templates/painel_frete.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Modal de Margem Líquida atualizado com sucesso!")
print("🎨 Agora está no mesmo padrão dos outros modais bonitos")
print("💎 Inclui: 4 cards executivos + Top 5 clientes + filtros + tabela completa")