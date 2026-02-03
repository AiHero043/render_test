"""
Web-based Configuration UI for EROME Automation
Modern Flask application with HTML/CSS/JS interface
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from pathlib import Path
import subprocess
import sys
import threading
from database import ProfileDatabase
import config

app = Flask(__name__)
db = ProfileDatabase()


@app.route('/')
def index():
    """Main dashboard"""
    # Pass config defaults to template
    defaults = {
        'imagemagick_path': str(config.IMAGEMAGICK_PATH),
        'handbrake_path': str(config.HANDBRAKE_CLI_PATH),
        'credentials_file': str(config.CREDENTIALS_FILE),
        'token_file': str(config.TOKEN_FILE),
        'image_quality_min': config.IMAGE_QUALITY_MIN,
        'image_quality_max': config.IMAGE_QUALITY_MAX,
        'video_rf_min': config.VIDEO_RF_MIN,
        'video_rf_max': config.VIDEO_RF_MAX,
        'encoder_presets': ','.join(config.VIDEO_ENCODER_PRESETS),
        'images_per_post': config.IMAGES_PER_POST,
        'videos_per_post': config.VIDEOS_PER_POST
    }
    return render_template('index.html', defaults=defaults)


@app.route('/api/profiles', methods=['GET'])
def get_profiles():
    """Get all profiles"""
    profiles = db.get_all_profiles()
    return jsonify(profiles)


@app.route('/api/profiles/<int:profile_id>', methods=['GET'])
def get_profile(profile_id):
    """Get specific profile"""
    profile = db.get_profile(profile_id)
    if profile:
        return jsonify(profile)
    return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/profiles', methods=['POST'])
def create_profile():
    """Create new profile"""
    data = request.json
    
    if not data.get('name'):
        return jsonify({'error': 'Profile name is required'}), 400
    
    if db.create_profile(data):
        return jsonify({'message': 'Profile created successfully'}), 201
    return jsonify({'error': 'Profile already exists or creation failed'}), 400


@app.route('/api/profiles/<int:profile_id>', methods=['PUT'])
def update_profile(profile_id):
    """Update profile"""
    data = request.json
    
    if db.update_profile(profile_id, data):
        return jsonify({'message': 'Profile updated successfully'})
    return jsonify({'error': 'Update failed'}), 400


@app.route('/api/profiles/<int:profile_id>', methods=['DELETE'])
def delete_profile(profile_id):
    """Delete profile"""
    if db.delete_profile(profile_id):
        return jsonify({'message': 'Profile deleted successfully'})
    return jsonify({'error': 'Delete failed'}), 400


@app.route('/api/profiles/<int:profile_id>/reset-state', methods=['POST'])
def reset_profile_state(profile_id):
    """Reset automation state"""
    if db.reset_state(profile_id):
        return jsonify({'message': 'State reset successfully'})
    return jsonify({'error': 'Reset failed'}), 400


@app.route('/api/profiles/<int:profile_id>/run', methods=['POST'])
def run_profile(profile_id):
    """Create job for automation (to be picked up by worker bot)"""
    profile = db.get_profile(profile_id)
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    force = request.json.get('force', False) if request.json else False
    
    # Create job in database
    job_id = db.create_job(profile_id, force_run=force)
    
    if job_id:
        return jsonify({
            'message': f'Job created for profile ({"force run" if force else "normal run"})',
            'job_id': job_id,
            'status': 'pending'
        })
    else:
        return jsonify({'error': 'Failed to create job'}), 500


@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get job status"""
    job = db.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


@app.route('/api/profiles/<int:profile_id>/jobs', methods=['GET'])
def get_profile_jobs(profile_id):
    """Get recent jobs for a profile"""
    limit = request.args.get('limit', 10, type=int)
    jobs = db.get_profile_jobs(profile_id, limit)
    return jsonify(jobs)


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
    print("=" * 60)
    print("EROME AUTOMATION - WEB CONFIGURATION UI")
    print("=" * 60)
    print("Starting web interface...")
    print("Access at: http://localhost:5001")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
