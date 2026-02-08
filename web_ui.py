"""
Web-based Configuration UI for EROME Automation
Modern Flask application with HTML/CSS/JS interface
"""
import os
from flask import Flask, render_template, request, jsonify
from pathlib import Path
import subprocess
import sys
import threading
from datetime import datetime
from db import LOCAL_DATABASE_URI, db
from models import Profile, AutomationState, Job

# Import config for defaults
try:
    import config
    DEFAULT_IMAGEMAGICK = str(config.IMAGEMAGICK_PATH)
    DEFAULT_HANDBRAKE = str(config.HANDBRAKE_CLI_PATH)
    DEFAULT_IMAGE_QUALITY_MIN = config.IMAGE_QUALITY_MIN
    DEFAULT_IMAGE_QUALITY_MAX = config.IMAGE_QUALITY_MAX
    DEFAULT_VIDEO_RF_MIN = config.VIDEO_RF_MIN
    DEFAULT_VIDEO_RF_MAX = config.VIDEO_RF_MAX
    DEFAULT_ENCODER_PRESETS = ','.join(config.VIDEO_ENCODER_PRESETS)
    DEFAULT_IMAGES_PER_POST = config.IMAGES_PER_POST
    DEFAULT_VIDEOS_PER_POST = config.VIDEOS_PER_POST
except:
    DEFAULT_IMAGEMAGICK = ''
    DEFAULT_HANDBRAKE = ''
    DEFAULT_IMAGE_QUALITY_MIN = 85
    DEFAULT_IMAGE_QUALITY_MAX = 99
    DEFAULT_VIDEO_RF_MIN = 17.5
    DEFAULT_VIDEO_RF_MAX = 29
    DEFAULT_ENCODER_PRESETS = 'veryfast,faster,fast,medium,slow'
    DEFAULT_IMAGES_PER_POST = 2
    DEFAULT_VIDEOS_PER_POST = 1


def create_app():
    """Application factory function."""
    app = Flask(__name__)
    
    # Load configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", LOCAL_DATABASE_URI)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'erome-automation-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print('Initialized the database.')
    
    return app


# Create app instance
app = create_app()


@app.route('/')
def index():
    """Main dashboard"""
    # Pass config defaults to template
    defaults = {
        'imagemagick_path': DEFAULT_IMAGEMAGICK,
        'handbrake_path': DEFAULT_HANDBRAKE,
        'credentials_file': 'credentials.json',
        'token_file': 'token.pickle',
        'image_quality_min': DEFAULT_IMAGE_QUALITY_MIN,
        'image_quality_max': DEFAULT_IMAGE_QUALITY_MAX,
        'video_rf_min': DEFAULT_VIDEO_RF_MIN,
        'video_rf_max': DEFAULT_VIDEO_RF_MAX,
        'encoder_presets': DEFAULT_ENCODER_PRESETS,
        'images_per_post': DEFAULT_IMAGES_PER_POST,
        'videos_per_post': DEFAULT_VIDEOS_PER_POST
    }
    return render_template('index.html', defaults=defaults)


@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles"""
    profiles = Profile.query.order_by(Profile.created_at.desc()).all()
    return jsonify([p.to_dict() for p in profiles])


@app.route('/api/profiles/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Get specific profile"""
    profile = Profile.query.get(profile_id)
    if profile:
        return jsonify(profile.to_dict())
    return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create new profile"""
    data = request.json
    
    print(f"Received profile creation request: {data}")
    
    if not data.get('name'):
        return jsonify({'error': 'Profile name is required'}), 400
    
    # Check if profile already exists
    if Profile.query.filter_by(name=data['name']).first():
        return jsonify({'error': 'Profile already exists'}), 400
    
    try:
        # Create new profile with defaults for missing fields
        profile = Profile(
            name=data['name'],
            download_folder_id=data.get('download_folder_id', ''),
            upload_folder_id=data.get('upload_folder_id', ''),
            download_post_start=data.get('download_post_start'),
            download_post_end=data.get('download_post_end'),
            credentials_file=data.get('credentials_file', 'credentials.json'),
            token_file=data.get('token_file', 'token.pickle'),
            delete_source=data.get('delete_source', False),
            image_quality_min=data.get('image_quality_min', DEFAULT_IMAGE_QUALITY_MIN),
            image_quality_max=data.get('image_quality_max', DEFAULT_IMAGE_QUALITY_MAX),
            video_rf_min=data.get('video_rf_min', DEFAULT_VIDEO_RF_MIN),
            video_rf_max=data.get('video_rf_max', DEFAULT_VIDEO_RF_MAX),
            encoder_presets=data.get('encoder_presets', DEFAULT_ENCODER_PRESETS),
            current_post_number=data.get('current_post_number', 360),
            set_value=data.get('set_value', 360),
            max_post=data.get('max_post', 10000),
            images_per_post=data.get('images_per_post', DEFAULT_IMAGES_PER_POST),
            videos_per_post=data.get('videos_per_post', DEFAULT_VIDEOS_PER_POST),
            enable_webhook=data.get('enable_webhook', False),
            webhook_url=data.get('webhook_url', ''),
            state_file=f"automation_state_{data['name'].lower().replace(' ', '_')}.json"
        )
        db.session.add(profile)
        db.session.flush()  # Get the profile ID
        
        # Create initial automation state
        state = AutomationState(
            profile_id=profile.id,
            current_post=data.get('current_post', 0),
            next_trigger_post=data.get('current_post', 0) + data.get('set_value', 360),
            posts_until_trigger=data.get('set_value', 360)
        )
        db.session.add(state)
        db.session.commit()
        
        print(f"Profile created successfully with ID: {profile.id}")
        return jsonify({'message': 'Profile created successfully', 'id': profile.id}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating profile: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to create profile: {str(e)}'}), 400


@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """Update profile"""
    profile = Profile.query.get(profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    data = request.json
    
    try:
        # Update profile fields
        for key in ['download_folder_id', 'upload_folder_id', 'download_post_start', 
                    'download_post_end', 'credentials_file', 'token_file', 'delete_source',
                    'image_quality_min', 'image_quality_max',
                    'video_rf_min', 'video_rf_max', 'encoder_presets',
                    'current_post_number', 'set_value', 'max_post', 'images_per_post',
                    'videos_per_post', 'enable_webhook', 'webhook_url']:
            if key in data:
                setattr(profile, key, data[key])
        
        # Update automation state if current_post is provided
        if 'current_post' in data and profile.automation_state:
            profile.automation_state.current_post = data['current_post']
            profile.automation_state.next_trigger_post = data['current_post'] + profile.set_value
            profile.automation_state.posts_until_trigger = profile.set_value
        
        profile.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Update failed: {str(e)}'}), 400


@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete profile"""
    profile = Profile.query.get(profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    try:
        db.session.delete(profile)
        db.session.commit()
        return jsonify({'message': 'Profile deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete failed: {str(e)}'}), 400


@app.route('/api/profiles/<int:profile_id>/state', methods=['GET'])
def get_profile_state(profile_id):
    """Get automation state for profile"""
    state = AutomationState.query.filter_by(profile_id=profile_id).first()
    return jsonify(state.to_dict() if state else {})


@app.route('/api/profiles/<int:profile_id>/reset-state', methods=['POST'])
def reset_profile_state(profile_id):
    """Reset automation state"""
    profile = Profile.query.get(profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    try:
        if profile.automation_state:
            state = profile.automation_state
            state.current_post = 0
            state.next_trigger_post = profile.set_value
            state.posts_until_trigger = profile.set_value
            state.total_posts_created = 0
            state.renewal_count = 0
            state.last_successful_post = None
            state.last_renewal_date = None
            db.session.commit()
        return jsonify({'message': 'State reset successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Reset failed: {str(e)}'}), 400


@app.route('/api/profiles/<int:profile_id>/run', methods=['POST'])
def run_profile(profile_id):
    """Create job for automation (to be picked up by worker bot)"""
    profile = Profile.query.get(profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    force = request.json.get('force', False) if request.json else False
    
    try:
        # Create job in database
        job = Job(
            profile_id=profile_id,
            force_run=force,
            status='pending'
        )
        db.session.add(job)
        db.session.commit()
        
        return jsonify({
            'message': f'Job created for profile ({"force run" if force else "normal run"})',
            'job_id': job.id,
            'status': 'pending'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create job: {str(e)}'}), 500


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    job = Job.query.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job.to_dict())


@app.route('/api/profiles/<int:profile_id>/jobs', methods=['GET'])
def get_profile_jobs(profile_id):
    """Get recent jobs for a profile"""
    limit = request.args.get('limit', 10, type=int)
    jobs = Job.query.filter_by(profile_id=profile_id).order_by(Job.created_at.desc()).limit(limit).all()
    return jsonify([j.to_dict() for j in jobs])


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get automation logs"""
    log_file = Path("automation_log.txt")
    if log_file.exists():
        with open(log_file, 'r') as f:
            logs = f.read()
        return jsonify({'logs': logs})
    return jsonify({'logs': 'No logs available'})


@app.route('/api/webhook/start', methods=['POST'])
def start_webhook():
    """Start webhook server"""
    def start():
        subprocess.Popen([sys.executable, 'webhook_server.py'])
    
    thread = threading.Thread(target=start, daemon=True)
    thread.start()
    
    return jsonify({'message': 'Webhook server starting...'})


if __name__ == '__main__':
    # Get port from environment variable (Render.com sets PORT)
    port = int(os.environ.get('PORT', 5001))
    
    print("=" * 60)
    print("EROME AUTOMATION - WEB CONFIGURATION UI")
    print("=" * 60)
    print("Starting web interface...")
    print(f"Access at: http://0.0.0.0:{port}")
    print(f"Database: {os.environ.get('DATABASE_URL', 'SQLite (local)')[:50]}...")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
