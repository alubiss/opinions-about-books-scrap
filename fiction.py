#!/usr/bin/env python
# coding: utf-8

# Kod do zescrapowania danych dotyczących książek z poratlu goodreads.com oraz steamboatbooks.com
# 
# Otrzymane zmienne:
# 
# -'tytul'
# -'ASIN'
# -'liczba stron'
# -'liczba gwiazdek- ocena książki'
# -'recenzja'
# -"rodzaj książki" (thriller, fiction, historical...)
# -"cena"
# -'rok wydania'
# -'bohaterzy'
# -'główny bohater'
# -'kraj wydania książki'
# -'nagrody zdobyte przez książkę'
# -'liczba nagród'
# -"autor"
# -"format wydania"
# -"nick recenzenta" 
# 
# Uzasadnienie wyboru tematu:
# 
# Dane mogą posłużyć do zbadania czynników wpływających na prawdopodobieństwo otrzymania pozytwnej recenzji.
# 
# W dalszej części możemy również otrzymać zmienną "opiania recenzanta" na podstawie analizy text mining recenzji za pomocą pakietu "textblob" (ocena pozytywna/negatywna); "płeć recenzenta", "płeć autora" oraz "płeć głównego bohatera" za pomocą pakietu "gender", który na podstawie historycznych statystyk przyporządkowuje etykietę male/female.
# 
# W takiej formie dane mogą posłużyć do stworzenia profilu konsumenta na podstawie cech indywidualnych każdej z książek (cena, liczba stron, gatunek, tematyka, format książki), cech i preferencji recenzenta (płec głównego bohatera, sposób pisania poezji/romansów przez kobietę, a thrillerów przez mężczynę- płeć recenzenta), wpływ opinii innych recenzentów na naszą opinię (średnia liczba zdobytych gwiazdek, liczba nagród zdobytych przez książkę). 
# 

# In[7]:


# potrzebne biblioteki
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
import time
from selenium import webdriver
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer
from selenium.webdriver.common.keys import Keys
from collections import OrderedDict
# rodzaje książek, które będą ściągane
typy=["fiction", "thriller", "historical_fiction", "fantasy", "best_of_the_best", "romance", "science_fiction", "horror", "humor", "nonfiction", "autobiography", "biography", "science_technology", "cookbooks", "novels", "poetry", "debut_author", "young_adult_fiction", "childrens", "picture_books"]
factors = [list() for typ in typy]
ISBN=[]
# linki, na których są listy książek do ściągnięcia wg wyżej wymienionych rodzajów
links = ["https://www.goodreads.com/choiceawards/best-fiction-books-2018", "https://www.goodreads.com/choiceawards/best-mystery-thriller-books-2018", "https://www.goodreads.com/choiceawards/best-historical-fiction-books-2018", "https://www.goodreads.com/choiceawards/best-fantasy-books-2018", "https://www.goodreads.com/choiceawards/best-of-the-best-2018", "https://www.goodreads.com/choiceawards/best-romance-books-2018", "https://www.goodreads.com/choiceawards/best-science-fiction-books-2018", "https://www.goodreads.com/choiceawards/best-horror-books-2018", "https://www.goodreads.com/choiceawards/best-humor-books-2018", "https://www.goodreads.com/choiceawards/best-nonfiction-books-2018",
      "https://www.goodreads.com/choiceawards/best-memoir-autobiography-books-2018", "https://www.goodreads.com/choiceawards/best-history-biography-books-2018", "https://www.goodreads.com/choiceawards/best-science-technology-books-2018", "https://www.goodreads.com/choiceawards/best-food-cookbooks-2018", "https://www.goodreads.com/choiceawards/best-graphic-novels-comics-2018", "https://www.goodreads.com/choiceawards/best-poetry-books-2018", "https://www.goodreads.com/choiceawards/best-debut-author-2018", "https://www.goodreads.com/choiceawards/best-young-adult-fiction-books-2018", "https://www.goodreads.com/choiceawards/best-childrens-books-2018", "https://www.goodreads.com/choiceawards/best-picture-books-2018"]

# linki do poszczególnych książek
href=[]
for link in links:
    r=requests.get(link)
    c=r.content
    soup=BeautifulSoup(c,"html.parser")
    titles = soup.find_all("a",{"class":"pollAnswer__bookLink"})
    for item in titles:
        href.append(item["href"])

k=0
for i in range(0,len(typy)):
    for j in range(0+k,20+k):
        factors[i].append("https://www.goodreads.com"+href[j])
    k=k+20

# słownik z nazwą typu i linkami do poszczegołnych książek
named_typy = dict(zip(typy, factors))
# odwołanie do nazw typów
dict_keys=list(named_typy.keys())
print(dict_keys[0])
# linki dla fiction - dict_keys[0]
named_typy[dict_keys[0]]

# otworzenie pierwszej strony z danymi
driver = webdriver.Chrome()
driver.get('https://www.goodreads.com/book/show')
time.sleep(2)
driver.maximize_window()
time.sleep(5)

#logowanie
sign= driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/header/div[1]/div/ul/li[1]/a')
sign.click()

iden = driver.find_element_by_xpath('//*[@id="user_email"]')
time.sleep(1)
iden.send_keys("ola.lubicka@gmail.com")

haslo = driver.find_element_by_xpath('//*[@id="user_password"]')
time.sleep(1)
haslo.send_keys("pomarancze1")

go= driver.find_element_by_xpath('//*[@id="emailForm"]/form/fieldset/div[5]/input')
go.click()


# Ściągamy dane. Dla 20 rodzajów książek, ściągamy po 20 książek.
# Aby widzieć, na jakim etapie ściągania jesteśmy po każej iteracji pętli wyświetla się numer itercji dla danego rodzaju książki (dla każdego typu powinno być 20 książek), numer ASIN książki oraz numer rodzaju książki (od 0 do 19, tyle mamy rodzajów w słowniku). 
# W przypadku, w którym dane dotyczące jakiejś książki się nie ściągną (np.gdy dany plik już istaniał na komputerze, został wcześniej ściągnięty, wystąpi jakiś błąd przy ściąganiu jakiejś obserwacji np. brak danej informacji) wyświetla się sam numer iteracji wg rodzaju i numer rodzaju, bez nr ASIN. Ze ściągniętych poniżej danych, uzyskujemy łącznie 51 000 obserwacji.

# In[41]:


# typów mamy 20, ponumerowane od 0 do 19
# n_typy - służy również do kontroli, który gatunek książki aktualnie się ściąga
n_typy=0
while n_typy < 20:
    # number- do kontroli, która książka została ściągnięta- powinno być po 20 książek każdego rodzaju
    number=0
    # pętla
    # dla każdego linku- książki w poszczegołnym rodzaju:
    for url in named_typy[dict_keys[n_typy]]:
        # try - próbuje ściągać dane i wyświetlić number, n_typy i ASIN, w przypadku, w którym błąd wyświetli n_typy i number
        try:
            driver.get(url);
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, window.scrollY - 200)")
            more = driver.find_element_by_xpath('//*[@id="bookDataBoxShow"]')
            #more.click()
            link =  driver.current_url
            r=requests.get(link)
            c=r.content
            soup=BeautifulSoup(c,"html.parser")
            isbn= soup.find("div",{"class":"infoBoxRowItem"}).find_next('div').text.strip()
            splitted = isbn.split()
            isbn = splitted[1]
            ISBN.append(isbn)
            driver.get('https://www.goodreads.com/book/show');
            m=isbn
            search = driver.find_element_by_xpath('/html/body/div[1]/div[1]/div/header/div[1]/div/div[2]/form/input')
            time.sleep(2)
            # wyszukaj ASIN
            search.send_keys(m)
            # enter
            search.send_keys(u'\ue007')
            link =  driver.current_url

            # pierwsza stronka z danymi dla danej książki
            r=requests.get(link)
            c=r.content
            soup=BeautifulSoup(c,"html.parser")

            # zmienne tytuł, autor, formaty, liczba stron, liczba gwiazdek
            driver.execute_script("window.scrollTo(0, window.scrollY - 200)")
            time.sleep(2)
            more = driver.find_element_by_xpath('//*[@id="bookDataBoxShow"]')
            tytul = soup.find("h1",{"id":"bookTitle"})
            tytul=tytul.get_text()
            autor = soup.find("span",{"itemprop":"name"})
            autor= autor.get_text().strip()
            formaty = soup.find("span",{"itemprop":"bookFormat"})
            formaty= formaty.get_text().strip()
            npages=soup.find("span",{"itemprop":"numberOfPages"})
            npages=npages.get_text()
            stars=soup.find("span",{"itemprop":"ratingValue"})
            stars=stars.get_text()

            # bohaterzy
            try:
                bohaterzy=soup.find("div",text="Characters").find_next('div').text.strip()
                splitted = bohaterzy.split()
                # główny bohater
                bohater= splitted[0]
                #break
            # gdy nie ma wymienionych bohaterów książki
            except:
                bohaterzy = None
                bohater= None

            # kraj publikacji
            try:
                country=soup.find("div",text="setting").find_next('div').text.strip()
                # wartość z nawiasu
                country=country[country.find("(")+1:country.find(")")]
            except:
                country = None

            # nagrody i liczba nagród
            try:   
                # nagrody
                awards=soup.find("div",text="Literary Awards").find_next('div').text.strip()
                # liczba nagród
                number_awards= awards.count(",") + 1
            except:
                awards = 0
                number_awards=0

            # dla każdej książki ściągamy 6 stron recenzji
            n=6
            # ściągamy recenzję i nazwę recenzenta
            osoby=[]
            recenzje=[]
            for i in range(1,n):
                time.sleep(4)
                link =  driver.page_source
                soup=BeautifulSoup(link,"html.parser")
                osoba = soup.find_all("span",{"itemprop":"author"})
                reviews = soup.find_all("div",{"class":"reviewText stacked"})
                #reviews = soup.find_all("span",{"class":"readable"})
                for item in osoba:
                    osoby.append(item.get_text().strip())
                for item in reviews:
                    recenzje.append(item.get_text())

                driver.execute_script("window.scrollTo(0, window.scrollY - 400)")
                time.sleep(2)
                nextPage = driver.find_element_by_class_name("next_page")
                time.sleep(2)
                nextPage.click()
            # w nazwach recenzetnów parokrotnie wyświetlał się również autor książki, zawsze na pierwszej pozycji
            # usuwamy pierwszą pozycje i jej duplikaty
            def remove_values_from_list(the_list, val):
                while val in the_list:
                    the_list.remove(val)
            remove_values_from_list(osoby, osoby[0])

            # ocena czy recenzja jest pozytywna, czy negatywna 
            # 51 tysięcy ocenia się w około 4 dni 
            
            #opinie=[]
            #for item in recenzje:
            #    analysis = TextBlob(item, analyzer=NaiveBayesAnalyzer())
            #   opinie.append(analysis.sentiment.classification)

            tytuly=[]
            #.strip pomija "/n"
            torep= tytul.strip()
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                tytuly.append(i)
            pages=[]
            torep= npages.strip()
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                pages.append(i)
            nstars=[]
            torep= stars.strip()
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                nstars.append(i)
            ISBN=[]
            torep= isbn
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                ISBN.append(i)
            Bohaterzy=[]
            torep= bohaterzy
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                Bohaterzy.append(i)
            Bohater=[]
            torep= bohater
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                Bohater.append(i)
            Kraj=[]
            torep= country
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                Kraj.append(i)
            Nagrody=[]
            torep= awards
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                Nagrody.append(i)
            nnagrod=[]
            torep= number_awards
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                nnagrod.append(i)
            Autor=[]
            torep= autor
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                Autor.append(i)
            Formaty=[]
            torep= formaty
            nrep=len(recenzje)
            for i in range(nrep):
                i=torep
                Formaty.append(i)
            # tabelka 1 z danymi
            ramka1 = pd.DataFrame({'tytul':tytuly,'ISBN':ISBN,'lstron':pages,'stars':nstars,'recenzja':recenzje}) #,'opiania':opinie
            # rozdzielamy kolumny
            ramka3 = pd.DataFrame(ramka1.lstron.str.split(' ',1).tolist(),
                columns = ['npages','pages'])
            # ostateczna wersja tabelki z danymi potrzebnymi do dalszej analizy
            ramka=pd.DataFrame({'tytul':tytuly,'ASIN':ramka1.ISBN,'lstron':ramka3.npages,'stars':nstars,'recenzja':recenzje,'bohaterzy': Bohaterzy, 'bohater': Bohater, 'kraj': Kraj, 'nagrody': Nagrody, 'lnagrod': nnagrod, "autor": Autor, "format": Formaty, "nick": osoby}) 


            # druga stronka z danymi
            driver.get('https://www.steamboatbooks.com/book');
            time.sleep(2)
            search = driver.find_element_by_xpath("//*[@id='edit-search-block-form--2']")
            time.sleep(2)
            search.send_keys(m)
            search.send_keys(u'\ue007')
            link =  driver.current_url


            r=requests.get(link)
            c=r.content
            soup=BeautifulSoup(c,"html.parser")

            # zmienna cena
            try:
                cena = soup.find("div",{"class":"abaproduct-price"})
                cena=cena.get_text().strip()
            except:
                cena = None

            torep= cena
            nrep=len(recenzje)
            price=[]
            for i in range(nrep):
                i=torep
                price.append(i)
            ramka_new2=pd.DataFrame({'cena':price})
            
            # rok wydania książki
            try:
                year=soup.find("fieldset",{"id":"aba-product-details-fieldset"}).text.strip()
                year=year[year.find(",")+2:year.find(",")+6]
            except:
                year = None

            torep= year
            nrep=len(recenzje)
            Year=[]
            for i in range(nrep):
                i=torep
                Year.append(i)
            ramka_new3=pd.DataFrame({'rok':Year})

            # zmienna rodzaj
            typ=dict_keys[n_typy]
            torep= typ
            nrep=len(recenzje)
            rodzaj=[]
            for i in range(nrep):
                i=torep
                rodzaj.append(i)
            ramka_new=pd.DataFrame({'rodzaj':rodzaj})
            ramka=pd.DataFrame({'tytul':tytuly,'ASIN':ramka1.ISBN,'lstron':ramka3.npages,'stars':nstars,'recenzja':recenzje, "rodzaj": ramka_new.rodzaj, "cena":ramka_new2.cena, 'rok':ramka_new3.rok, 'bohaterzy': ramka.bohaterzy, 'główny bohater': ramka.bohater, 'kraj': ramka.kraj, 'nagrody': ramka.nagrody, 'liczba nagród': ramka.lnagrod, "autor": ramka.autor, "format": ramka.format, "nick": ramka.nick }) #'opiania':opinie,
            
            # ramkę z danymi dotyczącymi poszczegolnych książek zapisujemy w formacie json aby zaoszczędzić miejsca
            # ostateczną tabelę ze wszystkimi danymi możemy obejrzeć w pliku excel
            ramka.to_json(ramka.ASIN[1]+".json")
            number=number+1
            print(number,ramka.ASIN[1], n_typy)
        except:
            number=number+1
            print(number, n_typy)
    n_typy=n_typy+1


# In[ ]:




