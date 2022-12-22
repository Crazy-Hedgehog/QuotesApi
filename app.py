from flask import Flask, request
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql.expression import func

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "main_new.db"

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'main_new.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.app_context().push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    quotes = db.relationship('QuoteModel', backref='author', lazy='dynamic', cascade="all, delete-orphan")

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {"id": self.id,
                "name": self.name
                }


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        return {"id": self.id,
                "author": self.author.to_dict(),
                "tex": self.text
                }


def some_quotes_to_dict(quotes):
    quotes_dict = []
    for quote in quotes:
        quotes_dict.append(quote.to_dict())
    return quotes_dict


# AUTHOR handlers



# QUOTES handlers

@app.route('/quotes')
def get_quotes():
    quotes = QuoteModel.query.all()
    return some_quotes_to_dict(quotes), 200


@app.route('/quotes/<int:quote_id>', methods=['GET'])
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is not None:
        return quote.to_dict(), 200
    return f'Quote with id={quote_id} not found', 404


@app.route('/quotes/count', methods=['GET'])
def quotes_counter():
    quotes_number = QuoteModel.query.count()
    return {"count": quotes_number}, 200


@app.route('/quotes/random', methods=['GET'])
def get_random_quote():
    quote = QuoteModel.query.order_by(func.random()).first()
    return quote.to_dict(), 200


@app.route('/quotes', methods=['POST'])
def create_quote():
    new_data = request.json
    new_quote = QuoteModel(**new_data)
    db.session.add(new_quote)
    db.session.commit()
    return new_quote.to_dict(), 201


@app.route('/quotes/<int:quote_id>', methods=['PUT'])
def edit_quote(quote_id):
    new_data = request.json
    quote = QuoteModel.query.get(quote_id)
    if quote is not None:
        for key, value in new_data.items():
            if key == "rate" and (value > 5 or value < 1):
                setattr(quote, key, 1)
            else:
                setattr(quote, key, value)
        db.session.commit()
        return quote.to_dict(), 200
    return f'Quote with id={quote_id} not found', 404


@app.route("/quotes/<int:quote_id>", methods=['DELETE'])
def delete(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is not None:
        db.session.delete(quote)
        db.session.commit()
        return f"Quote with id {quote_id} is deleted.", 200
    return f'Quote with id={quote_id} not found.', 404


@app.route('/quotes/search', methods=['GET'])
def search():
    args = request.args
    args.to_dict()
    quotes = QuoteModel.query.filter_by(**args).all()
    if quotes:
        return some_quotes_to_dict(quotes)
    return f'Quotes with such parameters not found.', 404


if __name__ == '__main__':
    app.run(debug=True)
