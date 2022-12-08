from flask import Flask
from flask import request
import random
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


def add_edit_rating(quote):
    rating = quote['rating'] if 'rating' in quote.keys() else 1
    quote['rating'] = rating if 0 < rating < 6 and 'rating' in quote.keys() else 1
    return quote


def find_quote_by_id(quote_id):
    for quote in quotes:
        if quote['id'] == quote_id:
            return quote


@app.route('/quotes')
def get_quotes():
    select_quotes = "SELECT * from quotes"
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    values = cursor.fetchall()
    keys = ['id', 'author', 'text']
    quotes = []
    for value in values:
        quote = dict(zip(keys, value))
        quotes.append(quote)
    cursor.close()
    connection.close()
    return quotes, 200


@app.route('/quotes/<int:quote_id>', methods=['GET'])
def get_quote_by_id(quote_id):
    select_quotes = f"SELECT * from quotes WHERE id = {quote_id}"
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    values = cursor.fetchone()
    if values:
        keys = ['id', 'author', 'text']
        quote = dict(zip(keys, values))
        cursor.close()
        connection.close()
        return quote, 200
    return f'Quote with id={quote_id} not found', 404


@app.route('/quotes/count', methods=['GET'])
def quotes_counter():
    select_quotes = f"SELECT COUNT(*) as counter from quotes"
    connection = sqlite3.connect("test.db")
    cursor = connection.cursor()
    cursor.execute(select_quotes)
    value = cursor.fetchone()
    key = ['count']
    counter = dict(zip(key, value))
    cursor.close()
    connection.close()
    return counter, 200


@app.route('/quotes/random')
def get_random_quote():
   return random.choice(quotes)


@app.route('/quotes', methods=['POST'])
def create_quote():
    data = request.json
    new_quote = data
    new_quote['id'] = quotes[-1]['id'] + 1
    add_edit_rating(new_quote)
    quotes.append(new_quote)
    return new_quote, 201


@app.route('/quotes/<int:quote_id>', methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json
    quote = find_quote_by_id(quote_id)
    if quote:
        for key, value in new_data.items():
            quote[key] = new_data[key]
        add_edit_rating(quote)
        return quote, 200
    return f'Quote with id={quote_id} not found', 404


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    quote = find_quote_by_id(quote_id)
    if quote:
        quotes.remove(quote)
        return f"Quote with id {quote_id} is deleted.", 200
    return f'Quote with id={quote_id} not found.', 404


@app.route('/search', methods=['GET'])
def search():
    args = request.args
    args.to_dict()
    search_quotes = []
    for quote in quotes:
        i = len(args)
        for key, value in args.items():
            if key == 'rating':
                value = int(value)
            if quote[key] != value:
                break
            if i == 1 and quote[key] == value:
                search_quotes.append(quote)
            i -= 1
    return search_quotes


if __name__ == '__main__':
   app.run(debug=True)
