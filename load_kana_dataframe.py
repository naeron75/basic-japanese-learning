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
    
    clean_hiragana.append([h[0], romaji_h, 'hiragana'])
    clean_katakana.append([k[0], romaji_k, 'katakana'])

hiragana=pd.DataFrame(clean_hiragana, columns=['kana', 'romaji', 'type'])
katakana=pd.DataFrame(clean_katakana, columns=['kana', 'romaji', 'type'])

kana = pd.concat([hiragana, katakana], ignore_index=True)

kana_stroke_count=[
    3,2,2,2,3,
    3,3,1,3,2,
    5,5,3,5,4,
    2,1,2,3,1,
    4,3,4,5,3,
    4,2,1,1,2,
    6,4,3,3,4,
    4,3,2,2,1,
    3,1,4,1,4,
    5,3,6,3,6,
    4,2,5,2,5,
    3,2,3,2,3,
    3,2,2,
    2,2,1,2,1,
    2,1,1,3,
    1,
    6,5,5,
    8,7,7,
    4,3,3,
    6,5,5,
    5,4,4,
    7,6,6,
    6,5,5,
    4,3,3,
    6,5,5,
    5,4,4,
    5,4,4,
    5,4,4,
    2,2,3,3,3,
    2,3,2,3,2,
    4,5,4,5,4,
    3,3,2,2,2,
    5,5,4,4,4,
    3,3,3,3,2,
    5,5,5,5,4,
    2,2,2,4,1,
    2,2,1,1,4,
    4,4,3,3,6,
    3,3,2,2,5,
    2,3,2,2,3,
    2,2,3,
    2,2,2,1,3,
    2,3,3,3,
    2,
    5,5,6,
    7,7,8,
    5,5,6,
    7,7,8,
    5,5,6,
    7,7,8,
    4,4,5,
    4,4,5,
    6,6,7,
    5,5,6,
    5,5,6,
    4,4,5


]
kana['stroke_count']=kana_stroke_count

small_kana_data = {
    'kana': [
        # Small Hiragana
        'ゃ', 'ゅ', 'ょ', 'っ', 'ぁ', 'ぃ', 'ぅ', 'ぇ', 'ぉ', 
        # Small Katakana
        'ャ', 'ュ', 'ョ', 'ッ', 'ァ', 'ィ', 'ゥ', 'ェ', 'ォ'
    ],
    'romaji': ['','','','','','','','','','','','','','','','','',''],
    'type': [
        # Type
        'hiragana', 'hiragana', 'hiragana', 'hiragana', 'hiragana', 'hiragana', 'hiragana', 'hiragana', 'hiragana',
        'katakana', 'katakana', 'katakana', 'katakana', 'katakana', 'katakana', 'katakana', 'katakana', 'katakana'
    ],
    'stroke_count': [
        # Hiragana Strokes
        3, 2, 2, 1, 3, 2, 2, 2, 3, 
        # Katakana Strokes (using the same standard counts for similar forms)
        2, 2, 3, 3, 2, 2, 3, 3, 3
    ]
    
}

small_kana_df = pd.DataFrame(small_kana_data)

kana_df = pd.concat([kana, small_kana_df], ignore_index=True)

kana_df.to_csv('basic-japanese-learning/dataset/kana_romaji.csv', index=False)