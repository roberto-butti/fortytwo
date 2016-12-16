import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
#from flask_pymongo import PyMongo
import flask_admin as admin
from pymongo import MongoClient
import requests
import datetime

from wtforms import form, fields

from flask_admin.form import Select2Widget
from flask_admin.contrib.pymongo import ModelView, filters
from flask_admin.model.fields import InlineFormField, InlineFieldList

app = Flask(__name__)


app.config.from_object(__name__)
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
    DEBUG=True,
    MONGO_HOST='localhost',
    MONGO_PORT='27017',
    MONGO_DBNAME='fortytwo'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

conn = MongoClient()
db = conn.fortytwo








class UserForm(form.Form):
    name = fields.StringField('Name')
    email = fields.StringField('Email')
    password = fields.PasswordField('Password')

class UserView(ModelView):
    column_list = ('name', 'email', 'password')
    column_sortable_list = ('name', 'email', 'password')
    form = UserForm

class QuestionForm(form.Form):
    text = fields.StringField('Question')
    date = fields.DateTimeField('Date')
    answer = fields.StringField('Answer')

class QuestionView(ModelView):
    column_list = ('text', 'date', 'answer')
    column_sortable_list = ('text', 'date', 'answer')
    form = QuestionForm

class TrainingsetForm(form.Form):
    question = fields.StringField('Question')
    answer = fields.StringField('Answer')

class TrainingsetView(ModelView):
    column_list = ('text', 'answer')
    column_sortable_list = ('text', 'answer')
    form = TrainingsetForm

class AnswerForm(form.Form):
    key = fields.StringField('key')
    answer = fields.StringField('Answer')

class AnswerView(ModelView):
    column_list = ('key', 'answer')
    column_sortable_list = ('key', 'answer')
    form = AnswerForm


@app.route('/')
def index():
    last_questions= db.questions.find().sort("timestamp",-1).limit(3)
    return render_template('index.html',last_questions=last_questions)


@app.route('/send', methods=['POST'])
def send():
    text = request.form["text"]
    answer_key = engine(request.form["text"])
    question = {
        "text": text,
        "date": datetime.datetime.utcnow(),
        "answer":answer_key,
        "headers":
            {
                "User-Agent": request.headers["User-Agent"],
                "Accept-Language": request.headers["Accept-Language"],
                "Remote-Address": request.remote_addr
            }
    }
    q_id = db.questions.insert_one(question).inserted_id
    a = db.answers.find_one({"key":answer_key})

    return a["answer"]

def enginemongo(text):
    from textblob.classifiers import NaiveBayesClassifier
    trainingset = db.trainingset.find()
    for t in trainingset:
        t.text



def engine(text):
    from textblob.classifiers import NaiveBayesClassifier
    from textblob.classifiers import MaxEntClassifier
    from textblob.classifiers import NLTKClassifier
    url_train = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQv20P4oKek-rqSJy_2QLKoNOBEeeLQeIP9rZ7FNYftNkgKXw_WIfJRfw5ptYv3HICzWSnyXWTWPLDe/pub?gid=0&single=true&output=csv"
    file_train = "train.csv"
    if not (os.path.isfile(file_train)):
        with open(file_train, 'wb') as handle:
            print("Train loaded from Request:", url_train)
            response = requests.get(url_train, stream=True)
            if not response.ok:
                # Something went wrong
                pass
            for block in response.iter_content(1024):
                handle.write(block)
            handle.close()
            print("Request DONE")
    else:
        print("Train loaded from cache:", file_train)



    with open(file_train, 'r', encoding="utf8") as fp:
        #cl = MaxEntClassifier(fp)

        cl = NaiveBayesClassifier(fp)

    # print(cl.classify("This is an amazing library!"))
    # print(cl.accuracy(test))
    # cl.update(test)
    # print(cl.accuracy(test))

    prob_dist = cl.prob_classify(text)
    print("TEST:", text, " ", prob_dist, " ", prob_dist.max(), " ",
          round(prob_dist.prob("listacompa"), 2), " ",
          round(prob_dist.prob("permessi"), 2),
        round(prob_dist.prob("ipaddress"), 2))
    for a in prob_dist.samples():
        print(a, ":",round(prob_dist.prob(a), 2))
    print(cl.show_informative_features())
    aa = cl.extract_features(text)
    print(aa)
    print("---------------------------------------")

    return cl.classify(text)


print(__name__)
#print(mongo)

if __name__ == 'fortytwo':
    #print(mongo.db())
    # Create admin
    admin = admin.Admin(app, name='FortyTwo')



    # Add views
    admin.add_view(UserView(db.users, 'Users'))
    admin.add_view(QuestionView(db.questions, 'Questions'))
    admin.add_view(TrainingsetView(db.trainingset, 'Training Set'))
    admin.add_view(AnswerView(db.answers, 'Answers'))

    #app.run()

