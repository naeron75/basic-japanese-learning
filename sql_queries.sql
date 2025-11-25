select jlpt_level, avg(stroke_count) from jlpt_vocabulary
group by jlpt_level;

select jlpt_level, avg(num_characters) from jlpt_vocabulary
group by jlpt_level;

select jlpt_level, count(*) from jlpt_vocabulary
group by jlpt_level; 

select radical_basis, radical_meaning, count(*) as kanji_count from kanji
group by radical_basis, radical_meaning
order by kanji_count desc;

select kanji, translation, count from kanji
order by count desc;