# models.py
from db import db
from datetime import datetime

class Profile(db.Model):
    __tablename__ = 'profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    download_folder_id = db.Column(db.String, nullable=False)
    upload_folder_id = db.Column(db.String, nullable=False)
    download_dir = db.Column(db.String, nullable=False)
    output_dir = db.Column(db.String, nullable=False)
    renewed_images_dir = db.Column(db.String, nullable=False)
    renewed_videos_dir = db.Column(db.String, nullable=False)
    download_post_start = db.Column(db.Integer)
    download_post_end = db.Column(db.Integer)
    credentials_file = db.Column(db.String, default='credentials.json')
    token_file = db.Column(db.String, default='token.pickle')
    delete_source = db.Column(db.Boolean, default=False)
    imagemagick_path = db.Column(db.String)
    image_quality_min = db.Column(db.Integer, default=85)
    image_quality_max = db.Column(db.Integer, default=99)
    handbrake_path = db.Column(db.String)
    video_rf_min = db.Column(db.Float, default=17.5)
    video_rf_max = db.Column(db.Float, default=29)
    encoder_presets = db.Column(db.String, default='veryfast,faster,fast,medium,slow')
    current_post_number = db.Column(db.Integer, default=360)
    set_value = db.Column(db.Integer, default=360)
    max_post = db.Column(db.Integer, default=10000)
    images_per_post = db.Column(db.Integer, default=2)
    videos_per_post = db.Column(db.Integer, default=1)
    enable_webhook = db.Column(db.Boolean, default=False)
    webhook_url = db.Column(db.String)
    state_file = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    automation_state = db.relationship('AutomationState', backref='profile', uselist=False, cascade='all, delete-orphan')
    jobs = db.relationship('Job', backref='profile', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert profile to dictionary"""
        data = {
            'id': self.id,
            'name': self.name,
            'download_folder_id': self.download_folder_id,
            'upload_folder_id': self.upload_folder_id,
            'download_dir': self.download_dir,
            'output_dir': self.output_dir,
            'renewed_images_dir': self.renewed_images_dir,
            'renewed_videos_dir': self.renewed_videos_dir,
            'download_post_start': self.download_post_start,
            'download_post_end': self.download_post_end,
            'credentials_file': self.credentials_file,
            'token_file': self.token_file,
            'delete_source': self.delete_source,
            'imagemagick_path': self.imagemagick_path,
            'image_quality_min': self.image_quality_min,
            'image_quality_max': self.image_quality_max,
            'handbrake_path': self.handbrake_path,
            'video_rf_min': self.video_rf_min,
            'video_rf_max': self.video_rf_max,
            'encoder_presets': self.encoder_presets,
            'current_post_number': self.current_post_number,
            'set_value': self.set_value,
            'max_post': self.max_post,
            'images_per_post': self.images_per_post,
            'videos_per_post': self.videos_per_post,
            'enable_webhook': self.enable_webhook,
            'webhook_url': self.webhook_url,
            'state_file': self.state_file,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # Include automation state if exists
        if self.automation_state:
            data['state'] = self.automation_state.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<Profile {self.name}>'


class AutomationState(db.Model):
    __tablename__ = 'automation_states'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    current_post = db.Column(db.Integer, default=0)
    next_trigger_post = db.Column(db.Integer, default=360)
    posts_until_trigger = db.Column(db.Integer, default=360)
    total_posts_created = db.Column(db.Integer, default=0)
    renewal_count = db.Column(db.Integer, default=0)
    last_successful_post = db.Column(db.Integer)
    last_renewal_date = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'current_post': self.current_post,
            'next_trigger_post': self.next_trigger_post,
            'posts_until_trigger': self.posts_until_trigger,
            'total_posts_created': self.total_posts_created,
            'renewal_count': self.renewal_count,
            'last_successful_post': self.last_successful_post,
            'last_renewal_date': self.last_renewal_date.isoformat() if self.last_renewal_date else None
        }
    
    def __repr__(self):
        return f'<AutomationState profile_id={self.profile_id}>'


class Job(db.Model):
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=False)
    status = db.Column(db.String, default='pending')
    force_run = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.String)
    
    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'status': self.status,
            'force_run': self.force_run,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<Job {self.id} status={self.status}>'
