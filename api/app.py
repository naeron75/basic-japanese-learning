# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from sqlalchemy import PrimaryKeyConstraint, String, Integer

# --- Resource 1: Word Model ---
class Word(db.Model):
    __tablename__ = 'jlpt_vocabulary' # Assuming you loaded the jlpt_df here

    index = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(255)) 
    jlpt_level = db.Column(db.String(5))
    translation = db.Column(db.String(500))
    stroke_count = db.Column(db.Integer)
    
    # We will use this to link to Kanji (nesting)

    def to_dict(self):
        return {
            'word': self.word,
            'jlpt_level': self.jlpt_level,
            'translation': self.translation,
            'stroke_count': self.stroke_count
        }

# --- Resource 2: Kanji Model ---
class Kanji(db.Model):
    __tablename__ = 'kanji' # Assuming you loaded the kanji_df here

    index = db.Column(db.Integer, primary_key=True)
    kanji = db.Column(db.String(5))
    kun_readings = db.Column(db.String(255))
    on_readings = db.Column(db.String(255))
    count = db.Column(db.Integer)
    strokes = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'kanji': self.kanji,
            'readings': {'kun': self.kun_readings, 'on': self.on_readings},
            'use_count': self.count,
            'stroke_count': self.strokes
        }
    
from flask import request, jsonify, url_for

# Helper function for pagination links
def get_pagination_links(pagination):
    links = {}
    if pagination.has_prev:
        links['prev'] = url_for(request.endpoint, page=pagination.prev_num, **request.args)
    if pagination.has_next:
        links['next'] = url_for(request.endpoint, page=pagination.next_num, **request.args)
    links['first'] = url_for(request.endpoint, page=1, **request.args)
    links['last'] = url_for(request.endpoint, page=pagination.pages, **request.args)
    return links

@app.route('/words', methods=['GET'])
def list_words():
    # 1. Pagination Logic
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', app.config['PER_PAGE'], type=int)
    
    # 2. Filtering Logic (e.g., filter by jlpt_level)
    level_filter = request.args.get('jlpt_level', type=str)
    query = Word.query
    
    if level_filter:
        query = query.filter(Word.jlpt_level == level_filter.upper())
    
    # Execute query with pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepare response data
    words = [word.to_dict() for word in pagination.items]
    
    response = {
        'count': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages,
        '_links': get_pagination_links(pagination),
        'data': words
    }
    return jsonify(response)

@app.route('/words/<word_name>', methods=['GET'])
def get_word(word_name):
    word = db.session.get(Word, word_name)
    if word is None:
        return jsonify({'error': 'Word not found'}), 404
    return jsonify(word.to_dict())

@app.route('/kanji', methods=['GET'])
def list_kanji():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', app.config['PER_PAGE'], type=int)
    
    # Filtering Logic (e.g., filter by minimum stroke count)
    min_strokes = request.args.get('min_strokes', type=int)
    query = Kanji.query
    
    if min_strokes is not None:
        query = query.filter(Kanji.stroke_count >= min_strokes)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    kanji_list = [k.to_dict() for k in pagination.items]
    
    response = {
        'count': pagination.total,
        'page': page,
        '_links': get_pagination_links(pagination),
        'data': kanji_list
    }
    return jsonify(response)

@app.route('/kanji/<char_name>', methods=['GET'])
def get_kanji(char_name):
    kanji = db.session.get(Kanji, char_name)
    if kanji is None:
        return jsonify({'error': 'Kanji not found'}), 404
    
    kanji_data = kanji.to_dict()
    
    # 3. Nesting Logic (Nesting Words using this Kanji)
    # This simulates a join: find words that contain this specific kanji character.
    # Note: This is an inefficient join, but demonstrates nesting capability.
    
    matching_words = db.session.query(Word.word, Word.jlpt_level).filter(
        Word.word.like(f'%{char_name}%')
    ).limit(10).all()

    kanji_data['used_in_words'] = [
        {'word': w, 'jlpt_level': level} for w, level in matching_words
    ]
    
    return jsonify(kanji_data)