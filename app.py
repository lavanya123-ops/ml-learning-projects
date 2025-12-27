#1.importing libraries
from flask import Flask,render_template,request,redirect,url_for,flash #render_template: to display any webpage
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

#2.creating the object of Flask class
app=Flask(__name__)
app.config['SECRET_KEY'] = '1357d'  # Replace with a strong key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# DB and Login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Loading the Models
import pickle
with open('models/stroke_rf_model.pkl','rb')as file:
    rf_model=pickle.load(file)



# User-defined Function for Prediction
def predict_stroke(gender='Male',age=56,hypertension='Yes',heart_disease='Yes',ever_married='Yes',work_type='Private',avg_glucose_level=123.45,bmi=78.4,smoking_status='smokes',resident_type='Urban'):
    lst=[]
    #gender
    if gender=='Female':
        lst=lst+[0]
    elif gender=='Male':
        lst=lst+[1]
    elif gender=='Other':
        lst=lst+[2]

    #age
    lst=lst+[age]
    
    #hypertension
    if hypertension=='Yes':
        lst=lst+[1]
    elif hypertension=='No':
        lst=lst+[0]
    
    #heart_disease
    if heart_disease=='Yes':
        lst=lst+[1]
    elif heart_disease=='No':
        lst=lst+[0]

    #ever_married
    if ever_married=='Yes':
        lst=lst+[1]
    elif ever_married=='No':
        lst=lst+[0]
    
    #work_type
    work_type=lb_worktype.transform([work_type])
    lst=lst+list(work_type)
    
    #avg_glucose_level and bmi
    lst=lst+[avg_glucose_level,bmi]

    #smoking_status
    smoking_status=lb_smoking.transform([smoking_status])
    lst=lst+list(smoking_status)

    #resident_type
    if resident_type=='Rural':
        lst=lst+[1,0]
    elif resident_type=='Urban':
        lst=lst+[0,1]

    result=rf_model.predict([lst])
    if result==[0]:
        return 'Person is not having the stroke'
    elif result==[1]:
        return 'Person may be suffering from stroke'
    

#3.creating the route

# index
@app.route("/")  #@app.route("/",methods=['GET','POST']) #By default it takes 'GET'
@login_required
def index():
    return render_template("index.html")

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered.', 'warning')
            return redirect(url_for('register'))

        # Create new user
        new_user = User(email=email, password=generate_password_hash(password, method='pbkdf2:sha256'))

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')


# Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route("/predict",methods=['POST'])
@login_required
def predict():
    if request.method=='POST':
        gender=request.form.get('gender')
        age=request.form.get('age')
        hypertension=request.form.get('hypertension')
        heart_disease=request.form.get('heart_disease')
        ever_married=request.form.get('ever_married')
        work_type=request.form.get('work_type')
        avg_glucose_level=request.form.get('avg_glucose_level')
        bmi=request.form.get('bmi')
        smoking_status=request.form.get('smoking_status')
        residence_type=request.form.get('residence_type')

        result=predict_stroke(gender,age,hypertension,heart_disease,ever_married,work_type,avg_glucose_level,bmi,smoking_status,resident_type=residence_type)
        return render_template('index.html',prediction=result)
    return "Prediction"



if __name__=="__main__":
    with app.app_context():
        if not os.path.exists('users.db'):
            db.create_all()
    app.run(debug=True,port=4500)