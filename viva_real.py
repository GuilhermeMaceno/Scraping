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
import pandas as pd
import openpyxl

link_exemplo = 'https://www.vivareal.com.br/imovel/galpao-deposito-armazem-vila-ema-zona-leste-sao-paulo-com-garagem-300m2-aluguel-RS6000-id-2840728067/?source=ranking%2Crp'
link_inicial = r'https://www.vivareal.com.br/aluguel/sp/sao-paulo/zona-oeste/barra-funda/galpao_comercial/?transacao=aluguel&onde=%2CS%C3%A3o+Paulo%2CS%C3%A3o+Paulo%2CZona+Oeste%2CBarra+Funda%2C%2C%2Cneighborhood%2CBR%3ESao+Paulo%3ENULL%3ESao+Paulo%3EZona+Oeste%3EBarra+Funda%2C-23.522342%2C-46.661303%2C&tipos=galpao_comercial&areaMinima=1500'
class Scrap_Viva():
    def __init__(self, link_inicial):
        driver_path = r"C:\Users\macen\Downloads\edgedriver_win64\msedgedriver.exe"
        self.service = Service(driver_path)
        self.options = Options()
        self.options.add_experimental_option("excludeSwitches", ["enable-logging"]) #Chato pra caralho
        self.driver = webdriver.Edge(service=self.service, options = self.options)
        self.driver.get(link_inicial)
        self.bs = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        self.link_inicial = link_inicial
        self.link_externo = link_inicial
        self.links = []
        self.vistos = set()
        self.df = pd.DataFrame(columns=['ID', 'Aluguel', 'Condominios', 'Metros', 'Local', 'Link', 'Atualização'])

    def request(self, link):
        driver_path = r"C:\Users\macen\Downloads\edgedriver_win64\msedgedriver.exe"
        time.sleep(5)
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

        atualização_tag = self.bs.find('span', {'data-testid': 'listing-created-date'})
        atualização = atualização_tag.text if atualização_tag else None

        link_atual = self.driver.current_url 

        dados = {
        'ID': id_,
        'Aluguel': aluguel,
        'Condominios': condominio,
        'Metros': metros,
        'Local': local,
        'Link': link_atual,
        'Atualização': atualização
    }

        # adiciona no DataFrame
        self.df = pd.concat([self.df, pd.DataFrame([dados])], ignore_index=True)
        self.df.to_excel("imoveis_barra_funda_vivareal_2.xlsx", index=False, engine="openpyxl")

    def show(self):
        print(self.df.tail(1))

    def get_links(self):
        WebDriverWait(self.driver, 10).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, "a[href^='https://www.vivareal.com.br/imovel/galpao']")
    )
)        
        # pega todos os links dentro dessa seção
        elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href^='https://www.vivareal.com.br/imovel/galpao']")
        self.links = [el.get_attribute("href") for el in elements]
        print(self.links)

    def segue_links(self):
        for page_num in range(1, 99):
            print(f'Página {page_num}')
            self.get_links()
            time.sleep(5)
            for link in self.links:
                if link not in self.vistos:
                    time.sleep(4)
                    self.request(link)
                    WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "value-item__value")))
                    self.search()
                    self.show()
            self.link_externo = self.link_inicial + '&pagina={}'.format(page_num)
            self.request(self.link_externo)
            self.vistos.update(self.links)
                
viva = Scrap_Viva(link_inicial)
viva.segue_links()