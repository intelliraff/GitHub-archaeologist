from flask import Flask,request,make_response,session,render_template,jsonify,redirect,url_for
import jwt
from datetime import datetime,timedelta,timezone
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

import os
from dotenv import load_dotenv

load_dotenv()
import requests

app=Flask(__name__)


app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///data.db'
db=SQLAlchemy(app)

def token_required(func):

    @wraps(func)
    def decorate(*args, **kwargs):

        token = request.args.get('token')

        if not token:
            return jsonify({'Alert': 'Token is missing'})

        try:
            jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

        except Exception:
            return jsonify({'Alert': 'Invalid token'})

        return func(*args, **kwargs)

    return decorate


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.Text)

    def __repr__(self):
        return f'{self.username}: {self.password}'

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    repo_name = db.Column(db.String(100))
    owner = db.Column(db.String(100))

    health_score = db.Column(db.Integer)
    status = db.Column(db.String(20))

    checked_at = db.Column(db.DateTime)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )


@app.route('/')
def home():

    token = session.get('token')

    if token:
        try:
            jwt.decode(
                token,
                app.config['SECRET_KEY'],
                algorithms=["HS256"]
            )

            return redirect('/dashboard')

        except:
            session.clear()

    return render_template('login.html')
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/history')
def history():

    token = session.get('token')

    if not token:
        return redirect('/')

    try:
        jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )
    except:
        session.clear()
        return redirect('/')

    current_user = User.query.filter_by(
        username=session.get('username')
    ).first()

    analyses = Analysis.query.filter_by(
        user_id=current_user.id
    ).all()

    result = []

    for a in analyses:
        result.append({
            "repo": a.repo_name,
            "owner": a.owner,
            "health": a.health_score,
            "status": a.status
        })

    return jsonify(result)





@app.route('/auth')
@token_required
def auth():
    return 'JWT verified! Welcome onboard!'


@app.route('/dashboard')
def dashboard():

    token = session.get('token')

    if not token:
        return redirect('/')

    try:
        jwt.decode(
            token,
            app.config['SECRET_KEY'],
            algorithms=["HS256"]
        )

    except:
        session.clear()
        return redirect('/')

    return render_template(
        'dashboard.html',
        username=session.get('username')
    )


@app.route('/login', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(
        username=username
    ).first()

    if user:
        if check_password_hash(user.password, password):

            session['logged_in'] = True

            token = jwt.encode(
                {
                    'user': username,
                    'exp': datetime.now(timezone.utc) + timedelta(minutes=5)
                },
                app.config['SECRET_KEY'],
                algorithm="HS256"
            )

            session['logged_in'] = True
            session['username'] = username
            session['token']=token

            return redirect(url_for('dashboard'))

        return jsonify({
            "status": "Wrong password"
        })

    hashed_password = generate_password_hash(password)

    new_user = User(
        username=username,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    token = jwt.encode(
        {
            'user': username,
            'exp': datetime.now(timezone.utc) + timedelta(minutes=5)
        },
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )

    session['logged_in'] = True
    session['username'] = username
    session['token'] = token

    return redirect(url_for('dashboard'))


class Repo(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    github_url=db.Column(db.String(900))
    owner=db.Column(db.String(30))
    repo=db.Column(db.String(50),unique=True)
    stars=db.Column(db.Integer)
    forks=db.Column(db.Integer)
    issues=db.Column(db.String(200))
    language=db.Column(db.String(100))
    updated_at=db.Column(db.String(100))

    def __repr__(self):
        return f'All the details: \n1.{self.github_url} \n2.{self.repo}-{self.stars}⭐️'



@app.route('/link',methods=['POST'])
def userrepo():
    if not session.get('logged_in'):
        return redirect('/')
    url=request.form['url']
    try:
        acc=url.rstrip('/').split('/')
        user=acc[-2]
        repo=acc[-1] 
        apiurl=f'https://api.github.com/repos/{user}/{repo}'
        totalurl=f'https://api.github.com/users/{user}/repos'

        response1=requests.get(apiurl)
        data1 = response1.json()

        details=Repo(
            github_url=apiurl,
            owner= data1['owner']['login'],
            repo= data1['name'],
            stars= data1['stargazers_count'],
            forks= data1['forks_count'],
            issues= data1['open_issues_count'],
            language=data1['language'],
            updated_at=data1['updated_at'])
        
        existing = Repo.query.filter_by(
            repo=data1['name']
        ).first()

        if not existing:
            db.session.add(details)
            db.session.commit()

        #time check
        now=datetime.now(timezone.utc)
        up=datetime.strptime(data1['updated_at'],"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        diff=(now-up).days
        if diff<7:
            status='active🌱'
        elif diff<30:
            status='slow🚸'
        else:
            status='abandoned🆘'

        #contributors check
        contributorsurl=f'https://api.github.com/repos/{user}/{repo}/contributors'
        response2=requests.get(contributorsurl)
        data2=response2.json()
        noofcon=len(data2)

        total = sum(c["contributions"] for c in data2)
        if total > 0:
            for c in data2:
                c['percentage'] = round(
                    c["contributions"] / total * 100,
                    2
                )
        #health
        score=100
        if status=='abandoned🆘': score-=20
        elif status=='slow🚸': score-=10
        if noofcon<2: score-=15
        if data1['open_issues_count']>100: score-=10

        current_user = User.query.filter_by(
            username=session.get('username')
        ).first()

        if current_user:
            analysis = Analysis(
                repo_name=data1['name'],
                owner=data1['owner']['login'],
                health_score=score,
                status=status,
                checked_at=datetime.now(timezone.utc),
                user_id=current_user.id
            )

            db.session.add(analysis)
            db.session.commit()

        commits_url = f"https://api.github.com/repos/{user}/{repo}/commits"
        issues_url = f"https://api.github.com/repos/{user}/{repo}/issues?state=all"



        return jsonify({
            'owner':data1['owner']['login'],
            'repo':data1['name'],
            'status':status,
            'no_of_contributors':noofcon,
            'contributors': data2,
            'health_score':f'{score}/100'

        })


    except Exception as e:
        return jsonify({'error':str(e)})

@app.route('/allrepos')
def display():
    all_repos=Repo.query.all()
    result=[]
    for repo in all_repos:
        result.append({
            'owner':repo.owner,
            'repo_name':repo.repo,
            'stars':repo.stars,
            'forks':repo.forks
        })
    return result


@app.route('/Usertable')
def displayuser():
    users=User.query.all()
    result=[]
    for user in users:
        result.append(
            {
                'username':user.username,
                'password':user.password
            }
        )
    return result





if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)