import requests
from bs4 import BeautifulSoup
import pandas as pd
url='https://www.sljfaq.org/afaq/romanization-table.html'
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")
hiragana=[]
katakana=[]

for tr in soup.find_all("tr"):
    # Get the two <span class='bk'> elements
    bk_spans = tr.find_all("span", class_="bk")
    
    # Get the first <td class='romaji'>
    romaji_tds = tr.find_all("td", class_="romaji")
    
    if len(bk_spans) >= 2 and len(romaji_tds) >= 2:
        # Take the second romaji
        second_romaji = romaji_tds[1].text.strip()
        
        hiragana.append([bk_spans[0].text.strip(), second_romaji])
        katakana.append([bk_spans[1].text.strip(), second_romaji])

clean_hiragana = []
clean_katakana = []

for h, k in zip(hiragana[:109], katakana[:109]):
    romaji_h = h[1].split(',')[0].strip()
    romaji_k = k[1].split(',')[0].strip()
    
    clean_hiragana.append([h[0], romaji_h])
    clean_katakana.append([k[0], romaji_k])

hiragana=pd.DataFrame(clean_hiragana, columns=['hiragana', 'romaji'])
katakana=pd.DataFrame(clean_katakana, columns=['katakana', 'romaji'])

kana = pd.merge(hiragana, katakana, on='romaji', how='inner')
clean_kana=kana[["hiragana", "katakana", "romaji"]]
clean_kana.to_csv('kana_romaji.csv')