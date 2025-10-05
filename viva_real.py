import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service

link_exemplo = 'https://www.vivareal.com.br/imovel/galpao-deposito-armazem-vila-ema-zona-leste-sao-paulo-com-garagem-300m2-aluguel-RS6000-id-2840728067/?source=ranking%2Crp'
link_inicial = 'https://www.vivareal.com.br/aluguel/sp/guarulhos/galpao_comercial/?transacao=aluguel&onde=%2CS%C3%A3o+Paulo%2CGuarulhos%2C%2C%2C%2C%2Ccity%2CBR%3ESao+Paulo%3ENULL%3EGuarulhos%2C-23.454314%2C-46.533664%2C&tipos=galpao_comercial'

class Scrap_Viva():
    def __init__(self, link_inicial):
        driver_path = r"C:\Users\macen\Downloads\edgedriver_win64\msedgedriver.exe"
        self.service = Service(driver_path)
        self.options = Options()
        self.driver = webdriver.Edge(service=self.service, options = self.options)
        self.driver.get(link_inicial)
        self.bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        self.link_inicial = link_inicial
        self.link_externo = link_inicial
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.vivareal.com.br/imovel/galpao']")
        self.links = [el.get_attribute("href") for el in elements]
        self.items = {
            'ID': [],
            'Aluguel': [],
            'Condominios': [],
            'Metros': [],
            'Local': []
        }

    def request(self, link):
        driver_path = r"C:\Users\macen\Downloads\edgedriver_win64\msedgedriver.exe"
        time.sleep(10)
        #self.driver.execute_script("window.scrollTo(1, document.body.scrollHeight);") #scrollar para baixo para carregar os imóveis
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        half_height = total_height / 2
        self.driver.execute_script(f"window.scrollTo(0, {half_height});")
        self.service = Service(driver_path)
        self.options = Options()
        self.driver = webdriver.Edge(service=self.service, options=self.options)  # Reabre com novo User-Agent
        self.driver.get(link)
        self.bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        time.sleep(5)

    def search(self):
        tags = self.bs.find_all('p', class_='value-item__value')
        if len(tags) >= 2:
            aluguel = tags[0].text
            condominio = tags[1].text
        else:
            aluguel, condominio = None, None

        metros = self.bs.find('span', class_='amenities-item-text')
        metros = metros.text if metros else None

        local = self.bs.find('p', {'class': "location-address__text",
                                   'data-testid': 'location-address'})
        local = local.text if local else None

        id_tag = self.bs.find('p', {'data-cy': 'ldp-propertyCodes-txt'})
        id_ = id_tag.text if id_tag else None

        self.items['ID'].append(id_)
        self.items['Aluguel'].append(aluguel)
        self.items['Condominios'].append(condominio)
        self.items['Metros'].append(metros)
        self.items['Local'].append(local)

    def show(self):
        for i in range(len(self.items['ID'])):
            print(f"ID: {self.items['ID'][i]}")
            print(f"Aluguel: {self.items['Aluguel'][i]}")
            print(f"Condomínio: {self.items['Condominios'][i]}")
            print(f"Metros: {self.items['Metros'][i]}")
            print(f"Local: {self.items['Local'][i]}")
            print("-" * 30)

    def get_links(self):
        WebDriverWait(self.driver, 10).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "a[href^='https://www.vivareal.com.br/imovel/galpao']")
    )
)        #self.driver.execute_script("window.scrollTo(8, document.body.scrollHeight);") #scrollar para baixo para carregar os imóveis
        #wait = WebDriverWait(self.driver, 10)
        #wait.until(
        #EC.presence_of_element_located(
        #(By.CLASS_NAME, "olx-core-carousel__viewport h-full")
    #)
#)
        # pega todos os links dentro dessa seção
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.vivareal.com.br/imovel/galpao']")
        self.links = [el.get_attribute("href") for el in elements]

        print(self.links)

    def segue_links(self):
        for page_num in range(1, 50):
            self.get_links()
            self.link_externo = self.link_inicial + '&pagina={}'.format(page_num)
            self.request(self.link_externo)
            time.sleep(5)
            for link in self.links:
                time.sleep(5)
                self.request(link)
                WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "value-item__value"))
)
                self.search()
                self.show()
                
viva = Scrap_Viva(link_inicial)
viva.get_links()
viva.segue_links()