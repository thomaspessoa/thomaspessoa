from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
from datetime import datetime

# Initialize extensions but don't associate with an app yet
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'

# --- User Model (with UserMixin) ---
class User(UserMixin, db.Model): # db.Model will be resolved once db is initialized with app
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False) # Increased length for hash
    role = db.Column(db.String(20), nullable=False, default='driver') # 'admin' or 'driver'

    def __repr__(self):
        return f'<User {self.username}>'
    
    # get_id() is provided by UserMixin if primary key is 'id'
    # is_authenticated, is_active, is_anonymous are also provided by UserMixin
    # trips backref will be added by Trip model

# --- Trip Model ---
class Trip(db.Model): # db.Model will be resolved once db is initialized with app
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule = db.Column(db.String(255), nullable=True) # Increased length
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending') # e.g., 'pending', 'active', 'completed'
    current_latitude = db.Column(db.Float, nullable=True)
    current_longitude = db.Column(db.Float, nullable=True)
    last_location_update = db.Column(db.DateTime, nullable=True)

    # Relationship to User (Driver)
    driver = db.relationship('User', backref=db.backref('trips', lazy=True))

    def __repr__(self):
        return f'<Trip {self.id} by Driver {self.driver_id} - Status: {self.status}>'

# --- User Loader for Flask-Login ---
# This needs to be defined within create_app or registered with login_manager after app init
# For simplicity, we'll define it globally but it's tied to login_manager instance.
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id)) # Updated to use Session.get()

# --- Database Initialization Function ---
def init_database(app_instance):
    with app_instance.app_context():
        # This uses the db_file_path from the app_instance's config
        db_file_path_local = app_instance.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        db_dir = os.path.dirname(db_file_path_local)
        
        if not app_instance.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:': # Only create dir if not in-memory
            if db_dir and not os.path.exists(db_dir): # Check if db_dir is not empty (not root path)
                os.makedirs(db_dir)
                print(f"Created '{db_dir}' directory.")
        
        db.create_all() 

        # Check if default users need to be added
        if not User.query.filter_by(username='admin').first():
            hashed_password_admin = generate_password_hash('admin_password', method='pbkdf2:sha256')
            default_admin = User(username='admin', password=hashed_password_admin, role='admin')
            db.session.add(default_admin)
            print("Default admin user created with hashed password.")

        if not User.query.filter_by(username='driver1').first():
            hashed_password_driver = generate_password_hash('driver_password', method='pbkdf2:sha256')
            default_driver = User(username='driver1', password=hashed_password_driver, role='driver')
            db.session.add(default_driver)
            print("Default driver (driver1) user created with hashed password.")
        
        db.session.commit()
        print("Database initialization complete. Users checked/added.")

def create_app(config_name='default'):
    app = Flask(__name__)

    # --- Configuration ---
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SECRET_KEY'] = 'test_secret_key_for_testing_create_app'
        app.config['LOGIN_DISABLED'] = False
    else: # Default/Production configuration
        app.secret_key = os.urandom(24)
        BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        db_file_path_local = os.path.join(BASE_DIR, 'database', 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file_path_local
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Initialize Extensions ---
    db.init_app(app)
    login_manager.init_app(app)

    # --- Routes ---
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif current_user.role == 'driver':
                return redirect(url_for('driver_dashboard'))
            else:
                return redirect(url_for('dashboard')) # Fallback generic dashboard
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('driver_dashboard'))

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Logged in successfully!', 'success')
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'driver':
                    return redirect(url_for('driver_dashboard'))
                else:
                    return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password. Please try again.', 'danger')
                return redirect(url_for('login'))
                
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html')

    @app.route('/admin')
    @login_required
    def admin_dashboard():
        if current_user.role != 'admin':
            flash('Access denied: Admins only.', 'danger')
            abort(403)
        active_trips = Trip.query.filter_by(status='active').all()
        return render_template('admin_dashboard.html', active_trips=active_trips)

    @app.route('/driver')
    @login_required
    def driver_dashboard():
        if current_user.role != 'driver':
            flash('Access denied: Drivers only.', 'danger')
            abort(403)
        active_trip = Trip.query.filter_by(driver_id=current_user.id, status='active').first()
        return render_template('driver_dashboard.html', active_trip=active_trip)

    @app.route('/start_trip', methods=['POST'])
    @login_required
    def start_trip():
        if current_user.role != 'driver':
            flash('Access denied: Drivers only.', 'danger')
            abort(403)
        existing_active_trip = Trip.query.filter_by(driver_id=current_user.id, status='active').first()
        if existing_active_trip:
            flash('You already have an active trip. Please end it before starting a new one.', 'warning')
            return redirect(url_for('driver_dashboard'))
        schedule_data = request.form.get('schedule')
        if not schedule_data or not schedule_data.strip():
            flash('Schedule information is required to start a trip.', 'danger')
            return redirect(url_for('driver_dashboard'))
        new_trip = Trip(
            driver_id=current_user.id,
            schedule=schedule_data,
            start_time=datetime.utcnow(),
            status='active'
        )
        db.session.add(new_trip)
        db.session.commit()
        flash('Trip started successfully!', 'success')
        return redirect(url_for('driver_dashboard'))

    @app.route('/end_trip', methods=['POST'])
    @login_required
    def end_trip():
        if current_user.role != 'driver':
            flash('Access denied: Drivers only.', 'danger')
            abort(403)
        active_trip = Trip.query.filter_by(driver_id=current_user.id, status='active').first()
        if active_trip:
            active_trip.end_time = datetime.utcnow()
            active_trip.status = 'completed'
            db.session.commit()
            flash('Trip ended successfully.', 'success')
        else:
            flash('No active trip found to end.', 'warning')
        return redirect(url_for('driver_dashboard'))

    @app.route('/update_location', methods=['POST'])
    @login_required
    def update_location():
        if current_user.role != 'driver':
            return jsonify({'status': 'error', 'message': 'Access denied: Drivers only.'}), 403
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({'status': 'error', 'message': 'Missing latitude or longitude.'}), 400
        active_trip = Trip.query.filter_by(driver_id=current_user.id, status='active').first()
        if not active_trip:
            return jsonify({'status': 'error', 'message': 'No active trip found.'}), 404
        try:
            active_trip.current_latitude = float(data['latitude'])
            active_trip.current_longitude = float(data['longitude'])
            active_trip.last_location_update = datetime.utcnow()
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Location updated.'})
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Invalid latitude or longitude format.'}), 400
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating location: {e}") # Use app.logger
            return jsonify({'status': 'error', 'message': 'Server error updating location.'}), 500
            
    @app.route('/api/active_buses_locations', methods=['GET'])
    @login_required
    def active_buses_locations():
        if current_user.role != 'admin':
            return jsonify({'status': 'error', 'message': 'Access denied: Admins only.'}), 403
        active_trips_with_location = Trip.query.filter(
            Trip.status == 'active',
            Trip.current_latitude.isnot(None),
            Trip.current_longitude.isnot(None)
        ).all()
        buses_data = []
        for trip in active_trips_with_location:
            buses_data.append({
                'trip_id': trip.id,
                'driver_username': trip.driver.username if trip.driver else 'Unknown Driver',
                'latitude': trip.current_latitude,
                'longitude': trip.current_longitude,
                'schedule': trip.schedule,
                'last_update': trip.last_location_update.strftime('%Y-%m-%d %H:%M:%S UTC') if trip.last_location_update else 'N/A'
            })
        return jsonify(buses_data)

    return app

# --- Main Execution ---
if __name__ == '__main__':
    app_instance = create_app()
    init_database(app_instance) # Initialize DB with the app instance
    app_instance.run(host='0.0.0.0', port=8080, debug=True)
