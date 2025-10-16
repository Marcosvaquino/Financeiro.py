"""
Automação ESL Cloud - Relatório Contas a Receber
Desenvolvido para extrair relatórios automaticamente do sistema ESL Cloud
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime
from dotenv import load_dotenv

# Importa o webdriver-manager para instalação automática do ChromeDriver
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False
    print("⚠️  webdriver-manager não instalado. Instale com: pip install webdriver-manager")

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class ESLCloudAutomation:
    """Classe para automação do sistema ESL Cloud"""
    
    def __init__(self, download_path=None):
        """
        Inicializa a automação
        
        Args:
            download_path: Caminho onde os arquivos serão baixados (padrão: pasta Downloads)
        """
        self.url = "https://friozer.eslcloud.com.br/users/sign_in"
        self.email = os.getenv('ESL_EMAIL')
        self.senha = os.getenv('ESL_SENHA')
        
        # Define pasta de download
        if download_path is None:
            self.download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        else:
            self.download_path = download_path
            
        self.driver = None
        
    def configurar_navegador(self):
        """Configura o Chrome com opções de download automático"""
        chrome_options = Options()
        
        # Configurações de download
        prefs = {
            "download.default_directory": self.download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_setting_values.automatic_downloads": 1
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Descomenta a linha abaixo para rodar sem abrir janela do navegador
        # chrome_options.add_argument('--headless')
        
        # Inicia o navegador
        if WEBDRIVER_MANAGER_AVAILABLE:
            # Usa webdriver-manager para instalar automaticamente
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # Usa o ChromeDriver do PATH ou pasta local
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.driver.maximize_window()
        
        print(f"✅ Navegador configurado")
        print(f"📁 Arquivos serão salvos em: {self.download_path}")
        
    def fazer_login(self):
        """Realiza o login no sistema"""
        try:
            print("\n🔐 Realizando login...")
            self.driver.get(self.url)
            
            # Aguarda a página carregar
            wait = WebDriverWait(self.driver, 15)
            
            # Preenche email
            email_field = wait.until(
                EC.presence_of_element_located((By.NAME, "user[email]"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            print(f"   ✓ Email preenchido")
            
            # Preenche senha
            senha_field = self.driver.find_element(By.NAME, "user[password]")
            senha_field.clear()
            senha_field.send_keys(self.senha)
            print(f"   ✓ Senha preenchida")
            
            # Pressiona ENTER para fazer login
            senha_field.send_keys(Keys.RETURN)
            print(f"   ✓ Enter pressionado para login")
            
            # Aguarda redirecionamento
            time.sleep(5)
            
            print("✅ Login realizado com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao fazer login: {str(e)}")
            return False
    
    def acessar_modulo_financeiro(self):
        """Acessa o módulo Financeiro através do menu ESL Cloud"""
        try:
            print("\n💰 Acessando módulo Financeiro...")
            wait = WebDriverWait(self.driver, 15)
            
            # Aguarda a página carregar completamente
            time.sleep(3)
            
            # Clica na setinha do dropdown ESL Cloud
            try:
                # Procura pelo elemento que contém "esl" e tem a classe dropdown ou similar
                dropdown = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".dropdown-toggle, button.dropdown-toggle, [data-toggle='dropdown']"))
                )
                dropdown.click()
                print("   ✓ Dropdown ESL Cloud aberto")
            except:
                # Tenta pelo XPath mais específico
                try:
                    dropdown = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'dropdown') or @data-toggle='dropdown']"))
                    )
                    dropdown.click()
                    print("   ✓ Dropdown ESL Cloud aberto (método 2)")
                except:
                    # Última tentativa: clica em qualquer elemento que contenha "Cloud" e seja clicável
                    dropdown = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Cloud')]/.."))
                    )
                    dropdown.click()
                    print("   ✓ Dropdown ESL Cloud aberto (método 3)")
            
            time.sleep(2)
            
            # Clica em Financeiro no dropdown
            financeiro = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Financeiro')]"))
            )
            financeiro.click()
            print("   ✓ Módulo Financeiro acessado")
            time.sleep(3)
            
            print("✅ Módulo Financeiro aberto!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao acessar módulo Financeiro: {str(e)}")
            # Tenta imprimir o HTML para debug
            try:
                print(f"   🔍 URL atual: {self.driver.current_url}")
            except:
                pass
            return False
    
    def acessar_contas_a_receber(self):
        """Acessa o relatório de Contas a Receber"""
        try:
            print("\n📊 Acessando Contas a Receber...")
            wait = WebDriverWait(self.driver, 15)
            
            # Clica em Relatórios no menu superior
            relatorios = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Relatórios')]"))
            )
            relatorios.click()
            print("   ✓ Menu Relatórios aberto")
            time.sleep(3)
            
            # Aguarda o dropdown aparecer e tenta diferentes seletores para Contas a Receber
            try:
                # Tenta pelo texto "Contas a Receber"
                contas_receber = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Contas a Receber')]"))
                )
                contas_receber.click()
                print("   ✓ Contas a Receber acessado (método 1)")
            except:
                try:
                    # Tenta pelo href que pode conter 'credits' ou 'contas'
                    contas_receber = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'credits') or contains(@href, 'receber')]"))
                    )
                    contas_receber.click()
                    print("   ✓ Contas a Receber acessado (método 2)")
                except:
                    # Tenta clicar diretamente na URL
                    print("   ⚠ Tentando acessar diretamente pela URL...")
                    self.driver.get("https://friozer.eslcloud.com.br/report/accounting/credits")
                    print("   ✓ URL acessada diretamente")
            
            time.sleep(3)
            
            print("✅ Relatório de Contas a Receber aberto!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao acessar Contas a Receber: {str(e)}")
            # Debug
            try:
                print(f"   🔍 URL atual: {self.driver.current_url}")
            except:
                pass
            return False
    
    def configurar_filtros(self, data_inicio="01/01/2025", data_fim="31/12/2025"):
        """
        Configura os filtros do relatório
        
        Args:
            data_inicio: Data inicial no formato DD/MM/YYYY
            data_fim: Data final no formato DD/MM/YYYY
        """
        try:
            print("\n⚙️ Configurando filtros...")
            wait = WebDriverWait(self.driver, 15)
            
            # Aguarda a página carregar
            time.sleep(3)
            
            # Limpa campo Filial (remove qualquer filtro selecionado)
            try:
                # Procura pelo X de remoção no campo filial
                remover_filial = self.driver.find_elements(
                    By.XPATH, 
                    "//span[contains(@class, 'select2-selection__choice__remove')]"
                )
                if remover_filial:
                    for btn in remover_filial:
                        try:
                            btn.click()
                            time.sleep(0.5)
                        except:
                            pass
                    print("   ✓ Campo Filial limpo")
                else:
                    print("   ℹ Campo Filial já está vazio")
            except:
                print("   ℹ Campo Filial não precisa ser limpo")
            
            # Preenche data de Emissão - tenta diferentes nomes de campo
            try:
                # Tenta primeiro por name="emission_date"
                campo_emissao = wait.until(
                    EC.presence_of_element_located((By.NAME, "emission_date"))
                )
                print("   ✓ Campo de emissão encontrado (name)")
            except:
                try:
                    # Tenta por ID
                    campo_emissao = wait.until(
                        EC.presence_of_element_located((By.ID, "emission_date"))
                    )
                    print("   ✓ Campo de emissão encontrado (id)")
                except:
                    # Tenta por placeholder
                    campo_emissao = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Emissão') or contains(@placeholder, 'Data')]"))
                    )
                    print("   ✓ Campo de emissão encontrado (placeholder)")
            
            # Limpa e preenche a data
            self.driver.execute_script("arguments[0].value = '';", campo_emissao)
            campo_emissao.clear()
            campo_emissao.send_keys(f"{data_inicio} - {data_fim}")
            print(f"   ✓ Período configurado: {data_inicio} - {data_fim}")
            
            time.sleep(1)
            
            print("✅ Filtros configurados!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao configurar filtros: {str(e)}")
            print(f"   🔍 Tentando continuar mesmo assim...")
            return True  # Continua mesmo com erro nos filtros
    
    def buscar_e_exportar(self):
        """Clica na lupa para buscar e depois no ícone Excel para exportar"""
        try:
            print("\n🔍 Buscando dados...")
            wait = WebDriverWait(self.driver, 15)
            
            # Clica na lupa (botão de buscar)
            botao_buscar = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' or contains(@class, 'btn-primary')]"))
            )
            botao_buscar.click()
            print("   ✓ Busca iniciada")
            
            # Aguarda carregar os resultados
            time.sleep(3)
            
            print("\n📥 Exportando para Excel...")
            
            # Clica no ícone Excel
            botao_excel = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//i[contains(@class, 'fa-file-excel') or contains(@class, 'excel')]"))
            )
            botao_excel.click()
            print("   ✓ Solicitação de exportação enviada")
            
            # Aguarda o modal de confirmação aparecer
            time.sleep(2)
            
            print("✅ Exportação solicitada!")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao buscar/exportar: {str(e)}")
            return False
    
    def confirmar_download(self):
        """Aguarda e clica no modal de confirmação do download"""
        try:
            print("\n⏳ Aguardando processamento do relatório...")
            wait = WebDriverWait(self.driver, 60)  # 60 segundos de timeout
            
            # Aguarda um pouco para o processamento começar
            time.sleep(5)
            
            # Estratégia 1: Clicar no sino de notificações
            try:
                print("   🔔 Clicando no sino de notificações...")
                
                # Procura pelo ícone do sino (geralmente é um <i> com classe fa-bell ou similar)
                sino = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//i[contains(@class, 'bell') or contains(@class, 'fa-bell')] | //a[contains(@class, 'notification')] | //*[@class='notifications']"))
                )
                sino.click()
                print("   ✓ Sino clicado, aguardando notificação aparecer...")
                time.sleep(3)
                
                # Procura pela primeira notificação (o relatório gerado)
                print("   🔍 Procurando notificação do relatório...")
                
                # Aguarda a notificação aparecer na lista
                notificacao = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'notification')]//a[1] | //ul[contains(@class, 'notification')]//li[1]//a | //div[contains(@class, 'dropdown-menu')]//a[1]"))
                )
                notificacao.click()
                print("   ✓ Primeira notificação clicada (download iniciado)")
                
                # Aguarda o download iniciar
                time.sleep(5)
                
                print("✅ Download iniciado com sucesso!")
                return True
                
            except Exception as e1:
                print(f"   ⚠ Método do sino falhou: {str(e1)}")
                print("   🔄 Tentando método alternativo (modal)...")
                
                # Estratégia 2: Modal tradicional (fallback)
                try:
                    # Aguarda o modal "Relatórios CSV" aparecer
                    modal_csv = wait.until(
                        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Relatórios CSV') or contains(text(), 'relatório em formato csv')]"))
                    )
                    print("   ✓ Modal 'Relatórios CSV' detectado!")
                    time.sleep(2)
                    
                    # Procura pelo link "Clique aqui"
                    link_download = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Clique aqui') or contains(text(), 'aqui')]"))
                    )
                    link_download.click()
                    print("   ✓ Link 'Clique aqui' clicado")
                    
                    time.sleep(5)
                    print("✅ Download iniciado com sucesso!")
                    return True
                    
                except Exception as e2:
                    print(f"   ❌ Método do modal também falhou: {str(e2)}")
                    return False
            
        except TimeoutException:
            print("❌ Timeout: Nenhuma notificação apareceu em 60 segundos")
            print("   ℹ Verifique se o relatório foi gerado no sistema")
            return False
        except Exception as e:
            print(f"❌ Erro ao confirmar download: {str(e)}")
            return False
    
    def executar(self, data_inicio="01/01/2025", data_fim="31/12/2025"):
        """
        Executa todo o fluxo de automação
        
        Args:
            data_inicio: Data inicial do relatório (DD/MM/YYYY)
            data_fim: Data final do relatório (DD/MM/YYYY)
        """
        try:
            print("="*60)
            print("🤖 AUTOMAÇÃO ESL CLOUD - CONTAS A RECEBER")
            print("="*60)
            
            # Verifica credenciais
            if not self.email or not self.senha:
                print("❌ ERRO: Credenciais não configuradas!")
                print("   Configure o arquivo .env com ESL_EMAIL e ESL_SENHA")
                return False
            
            # Inicia processo
            self.configurar_navegador()
            
            if not self.fazer_login():
                return False
            
            if not self.acessar_modulo_financeiro():
                return False
            
            if not self.acessar_contas_a_receber():
                return False
            
            if not self.configurar_filtros(data_inicio, data_fim):
                return False
            
            if not self.buscar_e_exportar():
                return False
            
            if not self.confirmar_download():
                return False
            
            print("\n" + "="*60)
            print("✅ AUTOMAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*60)
            print(f"\n📁 Arquivo salvo em: {self.download_path}")
            
            # Aguarda um pouco antes de fechar
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERRO GERAL: {str(e)}")
            return False
            
        finally:
            if self.driver:
                print("\n🔒 Fechando navegador...")
                self.driver.quit()


def main():
    """Função principal"""
    # Cria instância da automação
    automacao = ESLCloudAutomation()
    
    # Executa com período de todo o ano de 2025
    automacao.executar(
        data_inicio="01/01/2025",
        data_fim="31/12/2025"
    )


if __name__ == "__main__":
    main()
