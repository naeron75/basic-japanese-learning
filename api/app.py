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
    # 1. Check for single-item search (using the 'term' parameter)
    search_term = request.args.get('term')

    if search_term:
        word_data = Word.query.filter_by(word=search_term).first()
        if word_data:
            return jsonify(word_data.to_dict())
        else:
            return jsonify({"message": f"Word '{search_term}' not found."}), 404

    # 2. List, Filter, and Paginate logic (runs if 'term' is NOT provided)
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        jlpt_level = request.args.get('jlpt_level') # The parameter causing your current issue

        query = Word.query

        # Apply filtering (jlpt_level)
        if jlpt_level:
            query = query.filter_by(jlpt_level=jlpt_level)

        # Apply pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # 3. Process and return the paginated results
        # This will correctly handle an empty result set (e.g., if no N5 words exist)
        results = [word.to_dict() for word in pagination.items]

        # This is the guaranteed return path for the list view
        return jsonify({
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'words': results
        })

    except Exception as e:
        # Catch unexpected database or processing errors
        print(f"An unexpected error occurred in get_words list view: {e}")
        return jsonify({"message": "An internal server error occurred.", "error": str(e)}), 500

@app.route('/kanji', methods=['GET'])
def get_kanji():
    # 1. Check for single-item search
    search_term = request.args.get('term')

    if search_term:
        kanji_data = Kanji.query.filter_by(character=search_term).first()
        if kanji_data:
            return jsonify(kanji_data.to_dict_with_words())
        else:
            return jsonify({"message": f"Kanji character '{search_term}' not found."}), 404

    # 2. List, Filter, and Paginate logic (only runs if 'term' is NOT provided)
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        min_strokes = request.args.get('min_strokes', type=int)

        query = Kanji.query

        # Apply filtering (e.g., min_strokes)
        if min_strokes:
            query = query.filter(Kanji.strokes >= min_strokes)

        # Apply pagination
        # If the page number is out of range, error_out=False prevents an exception
        # and returns an empty result set, which is correctly handled below.
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # 3. Process and return the paginated results
        results = [kanji.to_dict() for kanji in pagination.items]
        
        # This is the guaranteed return path for the list view
        return jsonify({
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_pages': pagination.pages,
            'total_items': pagination.total,
            'kanji': results
        })

    except Exception as e:
        # This catches any unexpected errors during database interaction or processing
        print(f"An unexpected error occurred in get_kanji list view: {e}")
        return jsonify({"message": "An internal server error occurred.", "error": str(e)}), 500