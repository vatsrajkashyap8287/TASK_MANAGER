from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from functools import wraps
import os
from dotenv import load_dotenv
from models import db, User, Project, Task

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    print("✅ Database connected and tables created!")

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'member')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'error')
            return redirect(url_for('signup'))
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard'))
        
        flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = get_current_user()
    
    if user.role == 'admin':
        projects = Project.query.all()
        tasks = Task.query.all()
    else:
        projects = Project.query.filter(
            (Project.created_by == user.id) | (Project.members.contains(user))
        ).all()
        tasks = Task.query.filter_by(assigned_to=user.id).all()
    
    overdue = [t for t in tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != 'completed']
    
    stats = {
        'total': len(tasks),
        'pending': len([t for t in tasks if t.status == 'pending']),
        'in_progress': len([t for t in tasks if t.status == 'in_progress']),
        'completed': len([t for t in tasks if t.status == 'completed']),
        'overdue': len(overdue)
    }
    
    return render_template('dashboard.html', user=user, projects=projects[:5], 
                         tasks=tasks[:10], task_stats=stats, overdue_tasks=overdue[:5])

@app.route('/projects')
@login_required
def get_projects():
    user = get_current_user()
    
    if user.role == 'admin':
        projects = Project.query.all()
    else:
        projects = Project.query.filter(
            (Project.created_by == user.id) | (Project.members.contains(user))
        ).all()
    
    all_users = User.query.all()
    return render_template('projects.html', projects=projects, user=user, all_users=all_users)

@app.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    user = get_current_user()
    name = request.form.get('name')
    description = request.form.get('description')
    
    project = Project(name=name, description=description, created_by=user.id)
    db.session.add(project)
    db.session.commit()
    
    flash('Project created!', 'success')
    return redirect(url_for('get_projects'))

@app.route('/projects/<int:project_id>')
@login_required
def get_project(project_id):
    user = get_current_user()
    project = Project.query.get_or_404(project_id)
    
    if user.role != 'admin' and project.created_by != user.id and user not in project.members:
        flash('Access denied!', 'error')
        return redirect(url_for('get_projects'))
    
    tasks = Task.query.filter_by(project_id=project_id).all()
    all_users = User.query.all()
    
    return render_template('project_detail.html', project=project, tasks=tasks, 
                         team_members=project.members, all_users=all_users, user=user)

@app.route('/projects/<int:project_id>/add-member', methods=['POST'])
@login_required
def add_member(project_id):
    project = Project.query.get_or_404(project_id)
    member_id = request.form.get('member_id')
    
    member = User.query.get(member_id)
    if member and member not in project.members:
        project.members.append(member)
        db.session.commit()
        flash('Member added!', 'success')
    
    return redirect(url_for('get_project', project_id=project_id))

@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    user = get_current_user()
    project = Project.query.get_or_404(project_id)
    
    if user.role != 'admin' and project.created_by != user.id:
        flash('Access denied!', 'error')
        return redirect(url_for('get_projects'))
    
    Task.query.filter_by(project_id=project_id).delete()
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted!', 'success')
    return redirect(url_for('get_projects'))

@app.route('/tasks/create', methods=['POST'])
@login_required
def create_task():
    user = get_current_user()
    
    title = request.form.get('title')
    description = request.form.get('description')
    project_id = request.form.get('project_id')
    assigned_to = request.form.get('assigned_to')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority', 'medium')
    
    due_date_obj = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
    
    task = Task(
        title=title, description=description, project_id=project_id,
        assigned_to=assigned_to, created_by=user.id, due_date=due_date_obj, priority=priority
    )
    db.session.add(task)
    db.session.commit()
    
    flash('Task created!', 'success')
    return redirect(url_for('get_project', project_id=project_id))

@app.route('/tasks/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    status = request.form.get('status')
    
    if status:
        task.status = status
        task.updated_at = datetime.utcnow()
        db.session.commit()
    
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    
    db.session.delete(task)
    db.session.commit()
    
    flash('Task deleted!', 'success')
    return redirect(url_for('get_project', project_id=project_id))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)