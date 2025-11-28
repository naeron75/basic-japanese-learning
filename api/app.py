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
def get_words():
    # --- NEW SEARCH LOGIC ---
    search_term = request.args.get('term')

    if search_term:
        # Perform the search lookup
        word_data = Word.query.filter_by(word=search_term).first()

        if word_data:
            # If found, return the single word's details
            return jsonify(word_data.to_dict())
        else:
            # If not found
            return jsonify({"message": f"Word '{search_term}' not found."}), 404
    # --- END NEW SEARCH LOGIC ---
    
    # Existing Pagination/List Logic (runs if no 'term' parameter is provided)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    jlpt_level = request.args.get('jlpt_level')

    query = Word.query
    if jlpt_level:
        query = query.filter_by(jlpt_level=jlpt_level)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

@app.route('/kanji', methods=['GET'])
def get_kanji():
    # --- NEW SEARCH LOGIC ---
    search_term = request.args.get('term')

    if search_term:
        # Perform the search lookup by the 'kanji' column
        kanji_data = Kanji.query.filter_by(kanji=search_term).first()

        if kanji_data:
            # If found, return the single Kanji's details
            return jsonify(kanji_data.to_dict())
        else:
            # If not found
            return jsonify({"message": f"Kanji character '{search_term}' not found."}), 404
    # --- END NEW SEARCH LOGIC ---

    # Existing Pagination/List Logic (runs if no 'term' parameter is provided)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    min_strokes = request.args.get('min_strokes', type=int)

    query = Kanji.query
    if min_strokes:
        query = query.filter(Kanji.strokes >= min_strokes)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)