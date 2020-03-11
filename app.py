from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import ModelSchema
from marshmallow import fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///api.db"
db = SQLAlchemy(app)

class Author (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    specialisation = db.Column(db.String(50))

    #The below method creates a new object with the data and then returns the created object.
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def __init__(self, name, specialisation):
        self.name = name
        self.specialisation = specialisation
    def __repr__(self):
      return '<Product %d>' % self.id
db.create_all()

#The below code maps the variable attribute of Author class to field objects, and in Meta, we define the model to relate to our schema. So this should help us return JSON from SQLAlchemy.
class AuthorSchema(ModelSchema):
    class Meta(ModelSchema.Meta):
        model = Author
        sqla_session = db.session

    id = fields.Number(dump_only=True)
    name = fields.String(required=True)
    specialisation = fields.String(required=True)

#In this method, we are fetching all the authors in the DB, dumping it in the AuthorSchema, and returning the result in JSON.
#The following code for the GET all the authors
@app.route('/authors', methods = ['GET'])
def index():
    get_authors = Author.query.all()
    author_schema = AuthorSchema(many=True)
    authors = author_schema.dump(get_authors)
    return make_response(jsonify({"authors": authors}))

#The following code for the GET author by ID endpoint
@app.route('/authors/<id>', methods = ['GET'])
def get_author_by_id(id):
    get_author = Author.query.get(id)
    author_schema = AuthorSchema()
    author = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))


#The following code for the ADD a new author
@app.route('/authors', methods = ['POST'])
def create_author():
    data = request.get_json()
    print(data)
    author_schema = AuthorSchema()
    author = author_schema.load(data)
    result = author_schema.dump(author)
    res = Author(name=data['name'], specialisation = data['specialisation'])
    db.session.add(res)
    db.session.commit()
    return make_response(jsonify({"author": result}),201)


#The following code for the UPDATE author by ID endpoint
@app.route('/authors/<id>', methods = ['PUT'])
def update_author_by_id(id):
    data = request.get_json()
    get_author = Author.query.get(id)
    if data.get('specialisation'):
        get_author.specialisation = data['specialisation']
    if data.get('name'):
        get_author.name = data['name']
    db.session.add(get_author)
    db.session.commit()
    author_schema = AuthorSchema(only=['id', 'name',
    'specialisation'])
    author = author_schema.dump(get_author)
    return make_response(jsonify({"author": author}))

#The following code for the DELETE author by ID endpoint
@app.route('/authors/<id>', methods = ['DELETE'])
def delete_author_by_id(id):
    get_author = Author.query.get(id)
    db.session.delete(get_author)
    db.session.commit()
    return make_response("Author is deleted",204)

if __name__ == "__main__":
    app.run(debug=True)
