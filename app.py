from flask import Flask, request
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.sql.expression import func

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "main_new.db"

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{BASE_DIR / 'main_new.db'}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.app_context().push()

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class AuthorModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32))
    surname = db.Column(db.String(32))
    quotes = db.relationship("QuoteModel", backref="author", lazy="dynamic", cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("name", "surname", name="full name"),)

    def to_dict(self):
        return class_to_dict(self)


class QuoteModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey(AuthorModel.id))
    text = db.Column(db.String(255), unique=False)

    def __init__(self, author, text):
        self.author_id = author.id
        self.text = text

    def to_dict(self):
        quotes_dict = class_to_dict(self)
        quotes_dict["author"] = self.author.to_dict()
        del quotes_dict["author_id"]
        return quotes_dict


def class_to_dict(some_class):
    return {col.name: getattr(some_class, col.name) for col in some_class.__table__.columns}


def list_to_dict(values):
    new_dict = []
    for value in values:
        new_dict.append(value.to_dict())
    return new_dict


# AUTHOR handlers
@app.route("/authors")
def get_authors():
    authors = AuthorModel.query.all()
    return list_to_dict(authors), 200


@app.route("/authors/<int:author_id>", methods=["GET"])
def get_author_by_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is not None:
        return author.to_dict(), 200
    return f"Author with id={author_id} not found", 404


@app.route("/authors", methods=["POST"])
def create_author():
    author_data = request.json
    result = AuthorModel.query.filter_by(**author_data).first()
    if result is None:
        author = AuthorModel(**author_data)
        db.session.add(author)
        db.session.commit()
        return author.to_dict(), 200
    return f"Author with such name already exists.", 400


@app.route("/authors/<int:author_id>", methods=["PUT"])
def edit_author(author_id):
    author_data = request.json
    author = AuthorModel.query.get(author_id)
    if author is not None:
        author_dict = author.to_dict()
        author_dict.update(author_data)
        author_check = dict()
        author_check["name"] = author_dict["name"]
        author_check["surname"] = author_dict["surname"]
        result = AuthorModel.query.filter_by(**author_check).first()
        if result is None:
            for key, value in author_data.items():
                setattr(author, key, value)
            db.session.commit()
            return author.to_dict(), 200
        return f"You can't update author's name. Author with such name already exists.", 400
    return f"Author with id={author_id} not found", 404


@app.route("/authors/<int:author_id>", methods=["DELETE"])
def delete_author(author_id):
    author = AuthorModel.query.get(author_id)
    if author is not None:
        db.session.delete(author)
        db.session.commit()
        return f"Author with id {author_id} is deleted.", 200
    return f"Author with id={author_id} not found.", 404


# QUOTES handlers
@app.route("/quotes")
def get_quotes():
    quotes = QuoteModel.query.all()
    return list_to_dict(quotes), 200


@app.route("/quotes/<int:quote_id>", methods=["GET"])
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is not None:
        return quote.to_dict(), 200
    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/count", methods=["GET"])
def quotes_counter():
    quotes_number = QuoteModel.query.count()
    return {"count": quotes_number}, 200


@app.route("/quotes/random", methods=["GET"])
def get_random_quote():
    quote = QuoteModel.query.order_by(func.random()).first()
    return quote.to_dict(), 200


@app.route("/authors/<int:author_id>/quotes", methods=["GET"])
def get_quotes_by_authors_id(author_id):
    author = AuthorModel.query.get(author_id)
    if author is not None:
        quotes = QuoteModel.query.filter(QuoteModel.author_id == author_id).all()
        return list_to_dict(quotes), 200
    return f"Author with id={author_id} not found", 404


@app.route("/authors/<int:author_id>/quotes", methods=["POST"])
def create_quote(author_id):
    author = AuthorModel.query.get(author_id)
    if author is not None:
        new_data = request.json
        new_quote = QuoteModel(author, **new_data)
        db.session.add(new_quote)
        db.session.commit()
        return new_quote.to_dict(), 201
    return f"Unable to add a quote. Author with id={author_id} not found", 404


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_data = request.json
    quote = QuoteModel.query.get(quote_id)
    if quote is not None:
        for key, value in new_data.items():
            setattr(quote, key, value)
        db.session.commit()
        return quote.to_dict(), 200
    return f"Quote with id={quote_id} not found", 404


@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is not None:
        db.session.delete(quote)
        db.session.commit()
        return f"Quote with id {quote_id} is deleted.", 200
        # return "", 204
    return f"Quote with id={quote_id} not found.", 404


# @app.route("/quotes/search", methods=["GET"])
# def search():
#     args = request.args
#     args.to_dict()
#     quotes = QuoteModel.query.filter_by(**args).all()
#     if quotes:
#         return some_quotes_to_dict(quotes)
#     return f"Quotes with such parameters not found.", 404


if __name__ == "__main__":
    app.run(debug=True)
