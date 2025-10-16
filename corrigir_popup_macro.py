"""
Script para corrigir popups do Macro Setores
"""

import re

caminho = r'z:\FRZ LOGISTICA\Diretoria\Sistema.PY\Projeto.PY\Financeiro.py\financeiro\templates\logistica\mapa_calor.html'

# Ler arquivo
with open(caminho, 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Padrão antigo
antigo = """                    // Popup ao clicar no polígono
                    geoJsonLayer.bindPopup(`
                        <div style="text-align: center; min-width: 200px;">
                            <div style="background: ${corPadrao}; color: white; padding: 8px; margin: -10px -10px 10px -10px; border-radius: 3px 3px 0 0;">
                                <h6 style="margin: 0; font-weight: bold;">
                                    <i class="fas fa-map-marker-alt"></i> ${item.cidade}
                                </h6>
                            </div>
                            <div style="padding: 5px;">
                                <p style="margin: 5px 0; font-size: 13px;">
                                    <strong>📊 Ocorrências:</strong> ${item.valor.toLocaleString('pt-BR')}
                                </p>
                                <hr style="margin: 8px 0; border-color: #ddd;">
                                <p style="margin: 5px 0; font-size: 12px; color: #666;">"""

# Novo
novo = """                    // Popup dinâmico baseado na métrica
                    const valorPrincipalMacro = tipoMetrica === 'peso' 
                        ? `<strong>⚖️ Peso:</strong> ${(item.peso || 0).toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ton`
                        : `<strong>📊 Ocorrências:</strong> ${item.valor.toLocaleString('pt-BR')}`;
                    
                    const valorSecundarioMacro = tipoMetrica === 'peso'
                        ? `<p style="margin: 5px 0; font-size: 12px; color: #666;">
                            📊 Ocorrências: ${item.valor.toLocaleString('pt-BR')}
                        </p>`
                        : (item.peso ? `<p style="margin: 5px 0; font-size: 12px; color: #666;">
                            ⚖️ Peso: ${item.peso.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})} ton
                        </p>` : '');
                    
                    // Popup ao clicar no polígono
                    geoJsonLayer.bindPopup(`
                        <div style="text-align: center; min-width: 200px;">
                            <div style="background: ${cor}; color: white; padding: 8px; margin: -10px -10px 10px -10px; border-radius: 3px 3px 0 0;">
                                <h6 style="margin: 0; font-weight: bold;">
                                    <i class="fas fa-map-marker-alt"></i> ${item.cidade}
                                    ${item.isMaiorPeso ? ' 🏆' : ''}
                                </h6>
                            </div>
                            <div style="padding: 5px;">
                                <p style="margin: 5px 0; font-size: 13px;">
                                    ${valorPrincipalMacro}
                                </p>
                                ${valorSecundarioMacro}
                                <hr style="margin: 8px 0; border-color: #ddd;">
                                <p style="margin: 5px 0; font-size: 12px; color: #666;">"""

# Substituir
conteudo = conteudo.replace(antigo, novo)

# Salvar
with open(caminho, 'w', encoding='utf-8') as f:
    f.write(conteudo)

print("✅ Popup do Macro corrigido!")
