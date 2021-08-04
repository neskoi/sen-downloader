import json
import pathlib
import sys
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

def main():
    url = sys.argv[1]
    config = getConfig()
    browser = webdriver.Firefox()
    wait = WebDriverWait(browser, 10)

    goToSite(browser, url)

    totalPages = getTotalPages(browser, wait)

    basePath = config['saveDirectory'] if config['saveDirectory'] != '' else pathlib.Path(__file__).parent
    directoryPath = getSavePath(basePath, browser, wait) 
    
    createFolder(directoryPath)

    for i in range(1, totalPages):
        print('Baixando pagina ' + str(i))

        pageSrc = getPageSrc(browser, wait)

        savePath = f"{directoryPath}\\{config['pageName']}{i}.jpeg"

        downloadPage(pageSrc, savePath)

        if(i != totalPages): goToNextPage(browser, wait) ## TODO remover esse if
    browser.quit()
    print('Finalizado')

def getConfig():
    with open('./config/config.json',) as file:
        config = json.load(file)
    return config

def goToSite(browser, url):
    try:
        browser.get(url)
    except:
        print("Site indisponivel ou URL invalida.")
        browser.quit()
        sys.exit()

def getTotalPages(browser, wait):
    wait.until(presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/span')))
    totalPagesString = browser.execute_script(" return document.querySelector('.page-list').childNodes[2].textContent")
    cleanedTotalPagesString = totalPagesString.replace(" of ", "").replace(" ", "").replace("\n", "")
    totalPages = int(cleanedTotalPagesString) + 1
    return totalPages

def getSavePath(basePath, browser, wait):
    wait.until(presence_of_element_located((By.XPATH, '/html/body/div[5]/a/img')))
    mangaName = browser.find_element_by_xpath('/html/body/ul/li[2]/a').get_attribute('innerText')

    wait.until(presence_of_element_located((By.XPATH, '/html/body/ul/li[3]')))
    chapterName = browser.find_element_by_xpath('/html/body/ul/li[3]').get_attribute('innerText')
    savePath = f"{basePath}\\{mangaName}\\{chapterName}"
    return savePath 

def createFolder(savePath):
    pathlib.Path(savePath).mkdir(parents=True, exist_ok=True) 

def getPageSrc(browser, wait):
    wait.until(presence_of_element_located((By.XPATH, '/html/body/div[5]/a/img')))
    pageElement = browser.find_element_by_xpath('/html/body/div[5]/a/img')
    pageSrc = pageElement.get_attribute('src')
    return pageSrc

def downloadPage(pageSrc, savePath):
    pageRequest = urllib.request.Request(url = pageSrc, headers=headers)
    requestedPage = urllib.request.urlopen(pageRequest)

    with open(savePath, 'wb') as file:
        file.write(requestedPage.read())

def goToNextPage(browser, wait):
    wait.until(presence_of_element_located((By.XPATH, '/html/body/div[3]/div[3]/a[2]')))
    nextPage = browser.find_element_by_xpath('/html/body/div[3]/div[3]/a[2]')
    nextPage.click()

if(len(sys.argv) <= 1):
    print('É preciso passar a URL do manga qual deseja baixar.')
else:
   main()