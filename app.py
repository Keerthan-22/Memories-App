from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import save_memory, get_memories, get_photo, delete_memory, update_memory, get_memory
from users import create_user, authenticate_user, get_user_by_username
import io
import mimetypes

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.secret_key = '123'  # Should be a secure random key in production

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username, user_id):
        self.id = user_id  # Store MongoDB _id as string
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_username(user_id)
    if user:
        return User(user['username'], str(user['_id']))
    return None

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')
        
        try:
            user = create_user(username, email, password)
            if user:
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username or email already exists', 'danger')
        except Exception as e:
            print(f"Error registering user: {e}")
            flash('Registration failed due to server issue', 'danger')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            login_user(User(user['username'], str(user['_id'])))
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/index')
@login_required
def index():
    try:
        memories = list(get_memories(current_user.id))
        print(f"Loaded {len(memories)} memories for user {current_user.username}: {[m['photo_id'] for m in memories]}")
        return render_template('index.html', memories=memories)
    except Exception as e:
        print(f"Error loading memories: {e}")
        return render_template('index.html', memories=[], error="Unable to connect to MongoDB")

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        photo = request.files['photo']
        title = request.form['title']
        date = request.form['date']
        description = request.form['description']
        print(f"Uploading for user {current_user.username}: {photo.filename}, {title}, {date}, {description}")
        if photo:
            try:
                save_memory(photo, title, date, description, current_user.id)
                flash('Memory uploaded successfully!', 'success')
                return redirect(url_for('index'))
            except Exception as e:
                print(f"Error uploading memory: {e}")
                flash('Unable to save memory due to MongoDB issue', 'danger')
                return render_template('upload.html')
    return render_template('upload.html')

@app.route('/photo/<photo_id>')
@login_required
def serve_photo(photo_id):
    try:
        photo_data = get_photo(photo_id)
        if photo_data:
            mime_type, _ = mimetypes.guess_type(photo_data.filename)
            print(f"Serving photo {photo_id} as {mime_type}")
            return send_file(
                io.BytesIO(photo_data.read()),
                mimetype=mime_type or 'image/jpeg'
            )
        print(f"Photo {photo_id} not found")
        return "Photo not found", 404
    except Exception as e:
        print(f"Error serving photo: {e}")
        return "Unable to serve photo due to MongoDB issue", 500

@app.route('/delete/<memory_id>', methods=['POST'])
@login_required
def delete(memory_id):
    try:
        delete_memory(memory_id, current_user.id)
        flash('Memory deleted successfully!', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error deleting memory: {e}")
        flash('Error deleting memory', 'danger')
        return redirect(url_for('index'))

@app.route('/edit/<memory_id>', methods=['GET', 'POST'])
@login_required
def edit(memory_id):
    try:
        memory = get_memory(memory_id, current_user.id)
        if not memory:
            flash('Memory not found or not authorized', 'danger')
            return redirect(url_for('index'))
        if request.method == 'POST':
            title = request.form['title']
            date = request.form['date']
            description = request.form['description']
            photo = request.files.get('photo')
            print(f"Updating memory {memory_id} for user {current_user.username}: {title}, {date}, {description}, Photo: {photo.filename if photo else 'None'}")
            if update_memory(memory_id, title, date, description, photo, current_user.id):
                flash('Memory updated successfully!', 'success')
                return redirect(url_for('index'))
            flash('Error updating memory', 'danger')
            return render_template('edit.html', memory=memory)
        return render_template('edit.html', memory=memory)
    except Exception as e:
        print(f"Error editing memory: {e}")
        flash('Unable to edit memory due to MongoDB issue', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)