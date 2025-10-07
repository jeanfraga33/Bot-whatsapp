from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json  # Para salvar/carregar sessão

# Dicionário de palavras-chave e respostas personalizadas
# Adicione mais entradas conforme necessário (case-insensitive)
RESPONSES = {
    "oi": "Olá! Bem-vindo ao autoatendimento. Digite 'ajuda' para opções.",
    "ajuda": "Opções disponíveis:\n- 'preço': Veja nossos preços.\n- 'contato': Fale com um atendente.",
    "preço": "Nossos preços: Plano Básico R$ 29,90/mês. Digite 'mais' para detalhes.",
    "contato": "Entre em contato: suporte@exemplo.com ou (11) 99999-9999.",
    "mais": "Detalhes do plano: Inclui 100 mensagens/dia. Interesse? Digite 'sim'.",
    "sim": "Ótimo! Um atendente entrará em contato em breve.",
    "default": "Desculpe, não entendi. Digite 'ajuda' para ver opções."
}

# Configurações do Chrome (headless para VPS)
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo sem interface
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--user-data-dir=/tmp/chrome-user-data")  # Diretório para sessão
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
    return driver

# Função para carregar/salvar sessão (para evitar re-scan de QR toda vez)
SESSION_FILE = "whatsapp_session.json"

def load_session(driver):
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            session = json.load(f)
        for cookie in session['cookies']:
            driver.add_cookie(cookie)
        driver.refresh()
        return True
    return False

def save_session(driver):
    cookies = driver.get_cookies()
    session = {'cookies': cookies}
    with open(SESSION_FILE, 'w') as f:
        json.dump(session, f)

import os  # Adicione isso no topo se não tiver

# Função principal do bot
def main():
    driver = setup_driver()
    
    # Carrega sessão se existir
    driver.get("https://web.whatsapp.com")
    if not load_session(driver):
        print("Primeira execução: Abra um navegador local, acesse web.whatsapp.com, escaneie o QR com seu celular e execute novamente.")
        input("Pressione Enter após escanear...")
        save_session(driver)
    
    wait = WebDriverWait(driver, 60)
    
    print("Bot iniciado. Monitorando mensagens...")
    
    while True:
        try:
            # Espera por novas mensagens (seletor do WhatsApp Web)
            messages = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='textbox']")))
            
            # Procura por mensagens não lidas (ajuste seletor se necessário)
            unread_chats = driver.find_elements(By.CSS_SELECTOR, "span[data-icon='msg-dblcheck']")
            
            for chat in unread_chats:
                # Clica no chat para abrir (simplificado; ajuste para chats específicos)
                chat.click()
                time.sleep(2)
                
                # Pega a última mensagem recebida
                last_message_elem = driver.find_elements(By.CSS_SELECTOR, "div.message-in span.selectable-text")[-1]
                message_text = last_message_elem.text.lower().strip()
                
                if message_text:
                    print(f"Mensagem recebida: {message_text}")
                    
                    # Verifica palavra-chave e responde
                    response = RESPONSES.get(message_text, RESPONSES["default"])
                    
                    # Clica na caixa de texto e envia resposta
                    input_box = driver.find_element(By.CSS_SELECTOR, "div[role='textbox']")
                    input_box.click()
                    input_box.send_keys(response)
                    input_box.send_keys(Keys.ENTER)  # Precisa importar Keys: from selenium.webdriver.common.keys import Keys
                    
                    print(f"Resposta enviada: {response}")
                    
            time.sleep(5)  # Verifica a cada 5 segundos (ajuste para performance)
            
        except Exception as e:
            print(f"Erro: {e}")
            time.sleep(10)
    
    driver.quit()

if __name__ == "__main__":
    from selenium.webdriver.common.keys import Keys  # Adicione no topo
    main()
