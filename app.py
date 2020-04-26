from flask import Flask, render_template, request, flash, url_for, redirect, \
    abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "super secret key"

ENV = 'dev'

if ENV == 'dev':
     app.debug = True
     app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/fitmarc'
else:
    app.debug = False

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column('todo_id', db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    text = db.Column(db.String)
    done = db.Column(db.Boolean)
    pub_date = db.Column(db.DateTime)

    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.done = False
        self.pub_date = datetime.utcnow()

class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(200), unique=True)
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())
    def __init__(self, user, rating, comments):

        self.user = user
        self.rating = rating
        self.comments=comments

class Register(db.Model):
    __tablename__ = 'register'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    gender = db.Column(db.String(5))
    bday = db.Column(db.String(200))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer)
    email = db.Column(db.String(200), unique=True)
    goal = db.Column(db.String(200))

    def __init__(self, name, gender, bday, weight, height , email, goal):

        self.name = name
        self.gender = gender
        self.bday = bday
        self.weight = weight
        self.height = height
        self.email = email
        self.goal = goal 

class Info(db.Model):
    __tablename__ = 'info'
    id = db.Column(db.Integer, primary_key=True)
    meal = db.Column(db.String(200))
    item = db.Column(db.String(200))
    consumed = db.Column(db.Integer)
    burned = db.Column(db.Text())

    def __init__(self, meal, item, consumed, burned):
        self.meal = meal
        self.item = item
        self.consumed = consumed
        self.burned = burned

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<E-mail %r>' % self.email

@app.route("/")
def home():
      return render_template('home.html')

@app.route("/feedback")
def feedback():
    return render_template('feedback.html')

@app.route("/email")
def email():
    return render_template('email.html')

@app.route("/info")
def info():
    return render_template('info.html')

@app.route("/register")
def register():
    return render_template('register.html')

@app.route('/goals')
def goals():
    return render_template('goals.html')

@app.route('/index')
def index():
    return render_template('index.html',
        todos=Todo.query.order_by(Todo.pub_date.desc()).all()
    )

@app.route('/new', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':
        if not request.form['title']:
            flash('Title is required', 'error')
        elif not request.form['text']:
            flash('Text is required', 'error')
        else:
            todo = Todo(request.form['title'], request.form['text'])
            db.session.add(todo)
            db.session.commit()
            flash(u'Todo item was successfully created')
            return redirect(url_for('index'))
    return render_template('new.html')

@app.route('/todos/<int:todo_id>', methods = ['GET' , 'POST'])
def show_or_update(todo_id):
    todo_item = Todo.query.get(todo_id)
    if request.method == 'GET':
        return render_template('view.html',todo=todo_item)
    todo_item.title = request.form['title']
    todo_item.text  = request.form['text']
    todo_item.done  = ('done.%d' % todo_id) in request.form
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = None
    if request.method == 'POST':
        email = request.form['email']
        if email == '':
             return render_template('email.html', message='Please enter the required fields')
         # Check that email does not already exist
    if not db.session.query(User).filter(User.email == email).count():
            reg = User(email)
            db.session.add(reg)
            db.session.commit()
            return render_template('email.html', message='Enter E-mail once again.')
    return render_template('info.html')

@app.route('/submit',methods=['POST'])
def submit():
    if request.method == 'POST':
        user=request.form['user']
        rating=request.form['rating']
        comments=request.form['comments']
        print(user,rating,comments)
        
    if user == '' or comments == '':
        return render_template('feedback.html', message='Please enter the required fields')
    if db.session.query(Feedback).filter(Feedback.user==user).count() == 0:
        data = Feedback(user, rating, comments)
        db.session.add(data)
        db.session.commit()
        return render_template('success.html')
    return render_template('feedback.html', message='You have successfully submitted feedback')

@app.route('/add',methods=['POST'])
def add():
    if request.method == 'POST':
        meal = request.form['meal']
        item=request.form['item']
        consumed=request.form['consumed']
        burned=request.form['burned']
        print(meal,item,consumed,burned)
        
    if meal == '' or item == '':
        return render_template('info.html', message='Please enter the required fields')
    if db.session.query(Info).filter(Info.item==item).count() == 0:
        data = Info(meal,item,consumed,burned)
        db.session.add(data)
        db.session.commit()
        return render_template('info.html', message='Successfully added')
    return render_template('info.html', message='You have successfully added data')

@app.route('/register',methods=['POST'])
def registeration():
    if request.method == 'POST':
        name = request.form['name']
        gender=request.form['gender']
        bday=request.form['bday']
        weight=request.form['weight']
        height=request.form['height']
        email=request.form['email']
        goal=request.form['goal']
        print(name,gender,bday,weight,height,email,goal)
        
    if name == '' or goal == '':
        return render_template('register.html', message='Please enter the required fields')
    if db.session.query(Register).filter(Register.name==name).count() == 0:
        data = Register(name,gender,bday,weight,height,email,goal)
        db.session.add(data)
        db.session.commit()
        return render_template('home.html')
    return render_template('home.html', message='You have successfully added data')
        
if __name__ == '__main__':
    app.debug = True
    app.run()
