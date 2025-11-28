import pandas as pd
from collections import Counter
from jisho_api.kanji import Kanji
from concurrent.futures import ThreadPoolExecutor

def is_kanji(char):
    return (
        '\u4e00' <= char <= '\u9faf' or  # CJK Unified Ideographs
        '\u3400' <= char <= '\u4dbf'    # CJK Unified Ideographs Extension A
    )

def kana_to_romaji(text):
    if not isinstance(text, str):
        return None
    
    i = 0
    result = []
    length = len(text)

    while i < length:
        # Handle small tsu: っ or ッ
        if text[i] in ['っ', 'ッ']:
            # Look ahead to next kana (digraph or monograph)
            if i + 2 <= length and text[i+1:i+3] in digraphs:
                # double first consonant of romaji
                next_romaji = digraphs[text[i+1:i+3]]
                result.append(next_romaji[0])
                i += 1
                continue
            elif i + 1 < length and text[i+1] in monographs:
                next_romaji = monographs[text[i+1]]
                result.append(next_romaji[0])
                i += 1
                continue
            else:
                # Lone small tsu — rare — ignore
                i += 1
                continue

        # Digraph (e.g. ちゃ, きゃ)
        if i + 2 <= length and text[i:i+2] in digraphs:
            result.append(digraphs[text[i:i+2]])
            i += 2
            continue

        # Monograph
        if text[i] in monographs:
            result.append(monographs[text[i]])
            i += 1
            continue

        # Unknown character (kanji or punctuation) → keep as-is or skip
        result.append(text[i])
        i += 1

    return ''.join(result)

def calculate_word_stroke_count(word, stroke_map):
    '''
    Calculates the total stroke count for a Japanese word by summing strokes
    of every individual character element.
    '''
    total_strokes = 0
    for char in str(word): # Ensure word is treated as a string
        # Retrieves stroke count from the map, defaults to 0 if the character is not found
        count = stroke_map.get(char, 0) 
        total_strokes += count
    return total_strokes

def get_kanji_info_safe(kanji):
    try:
        r = Kanji.request(kanji)
        return {
            'strokes': r.data.strokes,
            'translation': r.data.main_meanings,
            'kun_readings': r.data.main_readings.kun,
            'on_readings': r.data.main_readings.on,
            'radical_basis': r.data.radical.basis,
            'radical_meaning': r.data.radical.meaning
        }
    except:
        return {
            'strokes': None,
            'translation': None,
            'kun_readings': None,
            'on_readings': None,
            'radical_basis': None,
            'radical_meaning': None
        }


jlpt_df=pd.read_csv('dataset/jlpt_vocab_raw.csv').rename(columns={
    'Original':'word',
    'Furigana':'furigana',
    'English':'translation',
    'JLPT Level':'jlpt_level'
})

jlpt_df['furigana'] = jlpt_df['furigana'].fillna(jlpt_df['word'])

kanji_list = jlpt_df['word'].apply(
    lambda w: [c for c in w if is_kanji(c)]
)

all_kanji = [kanji for sublist in kanji_list for kanji in sublist]

kanji_counts = Counter(all_kanji)

kanji_df = pd.DataFrame.from_dict(kanji_counts, orient='index', columns=['count']).reset_index().rename(columns={'index':'kanji'})

kana_df=pd.read_csv('dataset/kana_romaji.csv')

kana_map = {}

for _, row in kana_df.iterrows():
    kana_map[row['kana']] = row['romaji']

digraphs = {k: v for k, v in kana_map.items() if len(k) == 2}
monographs = {k: v for k, v in kana_map.items() if len(k) == 1}

jlpt_df['romaji'] = jlpt_df['furigana'].apply(kana_to_romaji)

jlpt_df['num_characters'] = jlpt_df['word'].apply(lambda x: len(str(x)))

kanji_list = kanji_df['kanji'].tolist()

with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(get_kanji_info_safe, kanji_list))

kanji_info_df = pd.DataFrame(results)

kanji_df = pd.concat([kanji_df, kanji_info_df], axis=1)

# Create a map for Kanji stroke counts (Character -> Count)
kanji_map = kanji_df.set_index('kanji')['strokes'].to_dict()

# Create a map for Kana stroke counts (Character -> Count)
kana_map = kana_df.set_index('kana')['stroke_count'].to_dict()

# Combine both maps into a single lookup dictionary
stroke_count_map = {**kanji_map, **kana_map}

jlpt_df['stroke_count'] = jlpt_df['word'].apply(
    lambda x: calculate_word_stroke_count(x, stroke_count_map)
)

kanji_df['translation']=kanji_df['translation'].apply(', '.join)
kanji_df['kun_readings']=kanji_df['kun_readings'].astype(str).str.replace("'", '').str.lstrip('[').str.rstrip(']')
kanji_df['on_readings']=kanji_df['on_readings'].astype(str).str.replace("'", '').str.lstrip('[').str.rstrip(']')
kanji_df['radical_meaning']=kanji_df['radical_meaning'].astype(str).str.rstrip(',')
kanji_df['kun_romaji']=kanji_df['kun_readings'].apply(kana_to_romaji)
kanji_df['on_romaji']=kanji_df['on_readings'].apply(kana_to_romaji)

jlpt_df.to_csv('dataset/jlpt_vocab_clean.csv', index=False)
kanji_df.to_csv('dataset/kanji_clean.csv', index=False)