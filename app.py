from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Task, login_manager
from forms import RegisterForm, LoginForm, TaskForm
from s3_utils import upload_file_to_s3


app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# ------------------ ROUTES ------------------

@app.route("/")
def home():
    return "<h1>Welcome to Task Manager</h1><a href='/login'>Login</a> or <a href='/register'>Register</a>"

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("Username already exists.", "warning")
            return redirect(url_for('register'))

        # Create new user
        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Registered successfully!", "success")
        return redirect(url_for('login'))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):

            login_user(user)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    form = TaskForm()
    if form.validate_on_submit():
        file_url = None

        if form.file.data:
            file = form.file.data
            file_url = upload_file_to_s3(file, file.filename)

        task = Task(
            title=form.title.data,
            description=form.description.data,
            file_url=file_url,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash("Task added!", "success")
        return redirect(url_for("dashboard"))

    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard.html", form=form, tasks=tasks)


@app.route("/delete/<int:task_id>")
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You cannot delete someone else's task!", "danger")
        return redirect(url_for("dashboard"))

    db.session.delete(task)
    db.session.commit()
    flash("Task deleted!", "info")
    return redirect(url_for("dashboard"))

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You cannot edit someone else's task!", "danger")
        return redirect(url_for("dashboard"))

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        db.session.commit()
        flash("Task updated!", "success")
        return redirect(url_for("dashboard"))

    return render_template("edit_task.html", form=form)

# -------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures tables are created
    app.run(host="0.0.0.0", port=5000, debug=True)
