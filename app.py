import os
from flask import Flask, render_template, flash, redirect, url_for, session, request,  logging
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from passlib.hash import sha256_crypt
from functools import wraps



app = Flask(__name__)

app.secret_key ="mysecretkey"
# Config MySQL
app.config['MYSQL_HOST'] = 'url'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your-password'
app.config['MYSQL_DB'] = 'redkitty'

# init MYSQL
mysql = MySQL(app)

# Upload Post Photo
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 2 * 1024 * 1024 #limit the maximum file payload to 2MB
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
#Articles = Articles()
# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#Index
@app.route('/')
def index():
     #Create cursor
    cur = mysql.connection.cursor()

    #Get Articles
    result = cur.execute("SELECT * FROM articles ORDER BY create_date DESC")

    articles = cur.fetchall()

    if result > 0:
        return render_template('home.html', articles = articles)
    else:
        msg = 'No Articles Found'
        return render_template('home.html')
    #Close connection
    cur.close()

# Register Form Class
class RegisterForm(Form):
    username = StringField('Profile Name', [validators.Length(min=4, max=25)])
    email = StringField('Your Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create cursor
        cur = mysql.connection.cursor()

        #check if user already exists
        result = cur.execute("SELECT * FROM user WHERE email = %s", [email])

        if result > 0:
            flash('User with this email already exists', 'danger')
            return redirect(url_for('register'))
        else:
            # Execute query
            cur.execute("INSERT INTO user(username, email, password) VALUES(%s, %s, %s)", (username, email, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

#User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create DictCursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM user WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data[3]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password) and request.form['username'] == data[1]:
                #Passedd
                session['logged_in'] = True
                session['username'] = username
                print(session)
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error = error)
            #Close connecton
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error = error)
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash ('You are now logged out', 'success')
    return redirect(url_for('login'))

#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #Create cursor
    cur = mysql.connection.cursor()

    #Get Articles
    result = cur.execute("SELECT * FROM articles WHERE author = %s ORDER BY create_date DESC ", [session['username']] )

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles = articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html')
    #Close connection
    cur.close()

@app.errorhandler(RequestEntityTooLarge)
def too_large(e):
       # pass through HTTP errors
    if isinstance(e, RequestEntityTooLarge):
        return render_template("add_article.html", error=e)
        
    

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS
#Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    if request.method == "POST":
        title = request.form["title"]
        bookTitle = request.form["bookTitle"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."
        elif not bookTitle: 
            error = "Book Title is Required"
        elif not body:
            error = "Post Content is required"

        if error is not None:
            return render_template("add_article.html", error=error)

        file = request.files['file']
        filename = secure_filename(file.filename)
        if not file:
            error ='Please Choose a Post Image'
        elif not allowed_file(file.filename):
            error ='File Formats allowed: png, jpg, jpeg'
        elif too_large(file):
            error ='File is too large'
        if error is not None:
            return render_template("add_article.html", error=error) 
        else:             
            file.save(os.path.join(UPLOAD_FOLDER, filename))   
            #Create Cursor
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO articles(author, title, bookTitle, photo, body) VALUES(%s, %s, %s, %s, %s)", (session['username'], title, bookTitle, filename, body ))
            mysql.connection.commit()
            #Close Connectiın
            cur.close()

            flash('Article Created', 'success')
            return redirect(url_for("dashboard"))
    return render_template("add_article.html")
    
#Edit Article
class EditArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    bookTitle = StringField('Book Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    #Create Cursor
    cur = mysql.connection.cursor()

    #Get user by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()

    #Get form
    form = EditArticleForm(request.form)

    #Populate article form Fields
    form.title.data = article[2]
    form.bookTitle.data = article[3]
    form.body.data = article[5]

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        bookTitle = request.form['bookTitle']
        body = request.form['body']

        #Create Cursor
        cur = mysql.connection.cursor()

        #execute
        cur.execute("UPDATE articles SET title=%s, bookTitle=%s, body=%s WHERE id = %s", (title, bookTitle, body, id))

        #Commit to DB
        mysql.connection.commit()

        #Close Connectiın
        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', article=article, form=form)

#Delete article
@app.route('/delete_article/<string:id>', methods = ['POST', 'GET'])
@is_logged_in
def delete_article(id):
    #Create Cursor
    cur = mysql.connection.cursor()

    #Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])

    #Commit to DB
    mysql.connection.commit()

    #Close Connectiın
    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
