from flask import Flask
from models import db, User, Task  # import the db and models
import os   #used to check if the database file exists or not
from flask import render_template, request, redirect, url_for, session, jsonify
from flask_migrate import Migrate  #for db updation without losing existing data
from datetime import datetime

app = Flask(__name__)  #Creates Flask app instance
app.secret_key = 'your_secret_key'   #required for session management, keeps track of the logged-in user. session['user_id'] stores the current user’s ID

#db configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///task.db'   #creates a new file named 'task.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   #Disable warning messages/unnecessary overhead

#Initialize the db with app
db.init_app(app)

#Create database and its tables if it doesn’t exist
with app.app_context():
    db.create_all()
    print("Database created successfully!")

migrate = Migrate(app, db) #initialize db data migration




# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fullname = request.form['fullname']

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists!"

        # Create new user
        new_user = User(username=username, password=password, fullname=fullname)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# ---------------- LOGIN ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.fullname  # store username for Dashboard welcome message
            return redirect(url_for('dashboard'))
        return "Invalid username or password!"
    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    # Ensure user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)  # get the user object, this helps in dashboard.html to fetch the fullname
    # Get all tasks for the logged-in user
    tasks = Task.query.filter_by(user_id=user_id).all()

    # Organize tasks by status
    task_status = {'To Do': [], 'In Progress': [], 'Done': []}
    for task in tasks:
        task_status[task.status].append(task)
    return render_template('dashboard.html', task_status=task_status, username=user.fullname) 

# ---------------- ADD TASK ----------------
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    title = request.form['title']
    description = request.form['description']
    status = request.form['status']
    estimate_start = request.form['estimate_start']
    estimate_end = request.form['estimate_end']
    user_id = session['user_id']

    # Convert date strings to Python date objects
    est_start = datetime.strptime(estimate_start, "%Y-%m-%d").date()
    est_end = datetime.strptime(estimate_end, "%Y-%m-%d").date()

    new_task = Task(title=title, description=description, status=status, user_id=user_id, estimate_start=est_start,
        estimate_end=est_end)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ---------------- EDIT TASK ----------------
@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get_or_404(task_id)

    # Ensure only the owner can edit
    if task.user_id != session['user_id']:
        return "You are not allowed to edit this task!"

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        task.status = request.form['status']
        task.estimate_start = datetime.strptime(request.form['estimate_start'], "%Y-%m-%d").date()
        task.estimate_end = datetime.strptime(request.form['estimate_end'], "%Y-%m-%d").date()

        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_task.html', task=task)

# ---------------- DELETE TASK ----------------
@app.route('/delete_task/<int:task_id>')
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        return "You are not allowed to delete this task!"

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('dashboard'))

# ---------------- DONE TASK ----------------
@app.route('/mark_done/<int:task_id>')
def mark_done(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        return "You are not allowed to modify this task!"

    task.status = 'Done'
    db.session.commit()
    return redirect(url_for('dashboard'))

# ---------------- UPDATE STATUS DURING DRAG & DROP ----------------
@app.route('/update_status/<int:task_id>', methods=['POST'])
def update_status(task_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    task = Task.query.get_or_404(task_id)
    if task.user_id != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403

    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['To Do', 'In Progress', 'Done']:
        return jsonify({'error': 'Invalid status'}), 400

    task.status = new_status
    db.session.commit()
    return jsonify({'success': True})

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # remove user from session
    session.pop('username', None)
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)