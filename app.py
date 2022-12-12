from flask import Flask, request, g
import sqlite3
from pathlib import Path


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def find_quote_by_id(quote_id):
    select_quotes = f"SELECT * from quotes WHERE id = ?"
    cursor = get_db().cursor()
    cursor.execute(select_quotes, (quote_id,))
    value = cursor.fetchone()
    return value


def to_dict(values):
    keys = ['id', 'author', 'text']
    return dict(zip(keys, values))


@app.route('/quotes')
def get_quotes():
    select_quotes = "SELECT * from quotes"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    values = cursor.fetchall()
    quotes = []
    for value in values:
        quote = to_dict(value)
        quotes.append(quote)
    return quotes, 200


@app.route('/quotes/<int:quote_id>', methods=['GET'])
def get_quote_by_id(quote_id):
    quote = find_quote_by_id(quote_id)
    if quote is not None:
        return to_dict(quote), 200
    return f'Quote with id={quote_id} not found', 404


@app.route('/quotes/count', methods=['GET'])
def quotes_counter():
    select_quotes = f"SELECT COUNT(*) as counter from quotes"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    value = cursor.fetchone()
    key = ['count']
    counter = dict(zip(key, value))
    return counter, 200


@app.route('/quotes/random', methods=['GET'])
def get_random_quote():
    select_quotes = f"SELECT * from quotes ORDER BY random() LIMIT 1"
    cursor = get_db().cursor()
    cursor.execute(select_quotes)
    quote = cursor.fetchone()
    quote = to_dict(quote)
    return quote, 200


@app.route('/quotes', methods=['POST'])
def create_quote():
    data = request.json
    create_quote = "INSERT INTO quotes (author,text) VALUES (?, ?)"
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(create_quote, (data["author"], data["text"]))
    connection.commit()
    new_quote = data
    new_quote["id"] = cursor.lastrowid
    return new_quote, 201


@app.route('/quotes/<int:quote_id>', methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json
    connection = get_db()
    cursor = connection.cursor()
    for key in new_data.keys():
        update_quote = f"""
        UPDATE quotes 
        SET {key} = ?
        WHERE id = ? ;
        """
        cursor.execute(update_quote, (new_data[key], quote_id))
    connection.commit()
    if cursor.rowcount != 0:
        new_quote = find_quote_by_id(quote_id)
        return to_dict(new_quote), 200
    return f'Quote with id={quote_id} not found', 404


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    delete_quote = "DELETE FROM quotes WHERE id = ?"
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute(delete_quote, (quote_id,))
    connection.commit()
    if cursor.rowcount != 0:
        return f"Quote with id {quote_id} is deleted.", 200
    return f'Quote with id={quote_id} not found.', 404


if __name__ == '__main__':
   app.run(debug=True)
