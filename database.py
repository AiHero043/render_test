"""
Database models for EROME Automation profiles
PostgreSQL database for storing multiple profile configurations
"""
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import json
try:
    import psycopg2
    from psycopg2 import pool
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    # Fallback to SQLite if psycopg2 not available
    import sqlite3

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
    # Fallback defaults if config.py doesn't exist
    DEFAULT_IMAGEMAGICK = ''
    DEFAULT_HANDBRAKE = ''
    DEFAULT_IMAGE_QUALITY_MIN = 85
    DEFAULT_IMAGE_QUALITY_MAX = 99
    DEFAULT_VIDEO_RF_MIN = 17.5
    DEFAULT_VIDEO_RF_MAX = 29
    DEFAULT_ENCODER_PRESETS = 'veryfast,faster,fast,medium,slow'
    DEFAULT_IMAGES_PER_POST = 2
    DEFAULT_VIDEOS_PER_POST = 1


class ProfileDatabase:
    """Manages profile storage in PostgreSQL/SQLite database"""
    
    def __init__(self, db_url: str = None):
        # Get database URL from environment or parameter
        self.db_url = db_url or os.environ.get('DATABASE_URL', 'sqlite:///profiles.db')
        
        # Determine database type
        if self.db_url.startswith('postgresql://') or self.db_url.startswith('postgres://'):
            if not POSTGRES_AVAILABLE:
                raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
            self.db_type = 'postgres'
            # Create connection pool for PostgreSQL
            self.pool = psycopg2.pool.SimpleConnectionPool(1, 10, self.db_url)
        else:
            self.db_type = 'sqlite'
            # Extract path from sqlite URL
            self.db_path = Path(self.db_url.replace('sqlite:///', ''))
        
        self.init_database()
    
    def get_connection(self):
        """Get database connection based on type"""
        if self.db_type == 'postgres':
            return self.pool.getconn()
        else:
            return sqlite3.connect(self.db_path)
    
    def return_connection(self, conn):
        """Return connection to pool (for PostgreSQL)"""
        if self.db_type == 'postgres':
            self.pool.putconn(conn)
        else:
            conn.close()
    
    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Use appropriate placeholder syntax
        placeholder = '%s' if self.db_type == 'postgres' else '?'
        
        if self.db_type == 'postgres':
            # PostgreSQL schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    download_folder_id TEXT NOT NULL,
                    upload_folder_id TEXT NOT NULL,
                    download_dir TEXT NOT NULL,
                    output_dir TEXT NOT NULL,
                    renewed_images_dir TEXT NOT NULL,
                    renewed_videos_dir TEXT NOT NULL,
                    download_post_start INTEGER,
                    download_post_end INTEGER,
                    credentials_file TEXT DEFAULT 'credentials.json',
                    token_file TEXT DEFAULT 'token.pickle',
                    delete_source BOOLEAN DEFAULT FALSE,
                    imagemagick_path TEXT,
                    image_quality_min INTEGER DEFAULT 85,
                    image_quality_max INTEGER DEFAULT 99,
                    handbrake_path TEXT,
                    video_rf_min REAL DEFAULT 17.5,
                    video_rf_max REAL DEFAULT 29,
                    encoder_presets TEXT DEFAULT 'veryfast,faster,fast,medium,slow',
                    current_post_number INTEGER DEFAULT 360,
                    set_value INTEGER DEFAULT 360,
                    max_post INTEGER DEFAULT 10000,
                    images_per_post INTEGER DEFAULT 2,
                    videos_per_post INTEGER DEFAULT 1,
                    enable_webhook BOOLEAN DEFAULT FALSE,
                    webhook_url TEXT,
                    state_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automation_states (
                    id SERIAL PRIMARY KEY,
                    profile_id INTEGER NOT NULL,
                    current_post INTEGER DEFAULT 0,
                    next_trigger_post INTEGER DEFAULT 360,
                    posts_until_trigger INTEGER DEFAULT 360,
                    total_posts_created INTEGER DEFAULT 0,
                    renewal_count INTEGER DEFAULT 0,
                    last_successful_post INTEGER,
                    last_renewal_date TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id SERIAL PRIMARY KEY,
                    profile_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    force_run BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            ''')
        else:
            # SQLite schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    download_folder_id TEXT NOT NULL,
                    upload_folder_id TEXT NOT NULL,
                    download_dir TEXT NOT NULL,
                    output_dir TEXT NOT NULL,
                    renewed_images_dir TEXT NOT NULL,
                    renewed_videos_dir TEXT NOT NULL,
                    download_post_start INTEGER,
                    download_post_end INTEGER,
                    credentials_file TEXT DEFAULT 'credentials.json',
                    token_file TEXT DEFAULT 'token.pickle',
                    delete_source BOOLEAN DEFAULT 0,
                    imagemagick_path TEXT,
                    image_quality_min INTEGER DEFAULT 85,
                    image_quality_max INTEGER DEFAULT 99,
                    handbrake_path TEXT,
                    video_rf_min REAL DEFAULT 17.5,
                    video_rf_max REAL DEFAULT 29,
                    encoder_presets TEXT DEFAULT 'veryfast,faster,fast,medium,slow',
                    current_post_number INTEGER DEFAULT 360,
                    set_value INTEGER DEFAULT 360,
                    max_post INTEGER DEFAULT 10000,
                    images_per_post INTEGER DEFAULT 2,
                    videos_per_post INTEGER DEFAULT 1,
                    enable_webhook BOOLEAN DEFAULT 0,
                    webhook_url TEXT,
                    state_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS automation_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    current_post INTEGER DEFAULT 0,
                    next_trigger_post INTEGER DEFAULT 360,
                    posts_until_trigger INTEGER DEFAULT 360,
                    total_posts_created INTEGER DEFAULT 0,
                    renewal_count INTEGER DEFAULT 0,
                    last_successful_post INTEGER,
                    last_renewal_date TIMESTAMP,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id INTEGER NOT NULL,
                    status TEXT DEFAULT 'pending',
                    force_run BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE
                )
            ''')
        
        conn.commit()
        self.return_connection(conn)
    
    def create_profile(self, profile_data: Dict) -> bool:
        """Create a new profile"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Use appropriate placeholder
            ph = '%s' if self.db_type == 'postgres' else '?'
            
            query = f'''
                INSERT INTO profiles (
                    name, download_folder_id, upload_folder_id,
                    download_dir, output_dir, renewed_images_dir, renewed_videos_dir,
                    download_post_start, download_post_end,
                    credentials_file, token_file, delete_source,
                    imagemagick_path, image_quality_min, image_quality_max,
                    handbrake_path, video_rf_min, video_rf_max, encoder_presets,
                    current_post_number, set_value, max_post,
                    images_per_post, videos_per_post,
                    enable_webhook, webhook_url, state_file
                ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
            '''
            
            cursor.execute(query, (
                profile_data['name'],
                profile_data['download_folder_id'],
                profile_data['upload_folder_id'],
                profile_data['download_dir'],
                profile_data['output_dir'],
                profile_data['renewed_images_dir'],
                profile_data['renewed_videos_dir'],
                profile_data.get('download_post_start'),
                profile_data.get('download_post_end'),
                profile_data.get('credentials_file', 'credentials.json'),
                profile_data.get('token_file', 'token.pickle'),
                profile_data.get('delete_source', False),
                profile_data.get('imagemagick_path', DEFAULT_IMAGEMAGICK),
                profile_data.get('image_quality_min', DEFAULT_IMAGE_QUALITY_MIN),
                profile_data.get('image_quality_max', DEFAULT_IMAGE_QUALITY_MAX),
                profile_data.get('handbrake_path', DEFAULT_HANDBRAKE),
                profile_data.get('video_rf_min', DEFAULT_VIDEO_RF_MIN),
                profile_data.get('video_rf_max', DEFAULT_VIDEO_RF_MAX),
                profile_data.get('encoder_presets', DEFAULT_ENCODER_PRESETS),
                profile_data.get('current_post_number', 360),
                profile_data.get('set_value', 360),
                profile_data.get('max_post', 10000),
                profile_data.get('images_per_post', DEFAULT_IMAGES_PER_POST),
                profile_data.get('videos_per_post', DEFAULT_VIDEOS_PER_POST),
                profile_data.get('enable_webhook', False),
                profile_data.get('webhook_url', ''),
                f"automation_state_{profile_data['name'].lower().replace(' ', '_')}.json"
            ))
            
            # Get last inserted ID
            if self.db_type == 'postgres':
                cursor.execute('SELECT lastval()')
                profile_id = cursor.fetchone()[0]
            else:
                profile_id = cursor.lastrowid
            
            # Create initial state
            state_query = f'''
                INSERT INTO automation_states (profile_id, current_post, next_trigger_post, posts_until_trigger)
                VALUES ({ph}, {ph}, {ph}, {ph})
            '''
            cursor.execute(state_query, (profile_id, 0, profile_data.get('set_value', 360), profile_data.get('set_value', 360)))
            
            conn.commit()
            self.return_connection(conn)
            return True
        except Exception as e:
            print(f"Error creating profile: {e}")
            if self.db_type == 'postgres':
                conn.rollback()
                self.return_connection(conn)
            return False
    
    def get_all_profiles(self) -> List[Dict]:
        """Get all profiles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM profiles ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        if self.db_type == 'postgres':
            # PostgreSQL returns tuples, get column names
            columns = [desc[0] for desc in cursor.description]
            profiles = [dict(zip(columns, row)) for row in rows]
        else:
            conn.row_factory = sqlite3.Row
            profiles = [dict(row) for row in rows]
        
        self.return_connection(conn)
        return profiles
    
    def get_profile(self, profile_id: int) -> Optional[Dict]:
        """Get a specific profile"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        ph = '%s' if self.db_type == 'postgres' else '?'
        
        cursor.execute(f'SELECT * FROM profiles WHERE id = {ph}', (profile_id,))
        row = cursor.fetchone()
        
        if row:
            if self.db_type == 'postgres':
                columns = [desc[0] for desc in cursor.description]
                profile = dict(zip(columns, row))
            else:
                conn.row_factory = sqlite3.Row
                profile = dict(row)
            
            # Get state
            cursor.execute(f'SELECT * FROM automation_states WHERE profile_id = {ph}', (profile_id,))
            state_row = cursor.fetchone()
            if state_row:
                if self.db_type == 'postgres':
                    state_columns = [desc[0] for desc in cursor.description]
                    profile['state'] = dict(zip(state_columns, state_row))
                else:
                    profile['state'] = dict(state_row)
        
        self.return_connection(conn)
        
        return profile if row else None
    
    def get_profile_by_name(self, name: str) -> Optional[Dict]:
        """Get a profile by name"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM profiles WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        profile = dict(row) if row else None
        conn.close()
        
        return profile
    
    def update_profile(self, profile_id: int, profile_data: Dict) -> bool:
        """Update an existing profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE profiles SET
                    download_folder_id = ?, upload_folder_id = ?,
                    download_dir = ?, output_dir = ?, renewed_images_dir = ?, renewed_videos_dir = ?,
                    download_post_start = ?, download_post_end = ?,
                    credentials_file = ?, token_file = ?, delete_source = ?,
                    imagemagick_path = ?, image_quality_min = ?, image_quality_max = ?,
                    handbrake_path = ?, video_rf_min = ?, video_rf_max = ?, encoder_presets = ?,
                    current_post_number = ?, set_value = ?, max_post = ?,
                    images_per_post = ?, videos_per_post = ?,
                    enable_webhook = ?, webhook_url = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                profile_data['download_folder_id'],
                profile_data['upload_folder_id'],
                profile_data['download_dir'],
                profile_data['output_dir'],
                profile_data['renewed_images_dir'],
                profile_data['renewed_videos_dir'],
                profile_data.get('download_post_start'),
                profile_data.get('download_post_end'),
                profile_data.get('credentials_file', 'credentials.json'),
                profile_data.get('token_file', 'token.pickle'),
                profile_data.get('delete_source', False),
                profile_data.get('imagemagick_path', DEFAULT_IMAGEMAGICK),
                profile_data.get('image_quality_min', DEFAULT_IMAGE_QUALITY_MIN),
                profile_data.get('image_quality_max', DEFAULT_IMAGE_QUALITY_MAX),
                profile_data.get('handbrake_path', DEFAULT_HANDBRAKE),
                profile_data.get('video_rf_min', DEFAULT_VIDEO_RF_MIN),
                profile_data.get('video_rf_max', DEFAULT_VIDEO_RF_MAX),
                profile_data.get('encoder_presets', DEFAULT_ENCODER_PRESETS),
                profile_data.get('current_post_number', 360),
                profile_data.get('set_value', 360),
                profile_data.get('max_post', 10000),
                profile_data.get('images_per_post', DEFAULT_IMAGES_PER_POST),
                profile_data.get('videos_per_post', DEFAULT_VIDEOS_PER_POST),
                profile_data.get('enable_webhook', False),
                profile_data.get('webhook_url', ''),
                profile_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating profile: {e}")
            return False
    
    def delete_profile(self, profile_id: int) -> bool:
        """Delete a profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM profiles WHERE id = ?', (profile_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting profile: {e}")
            return False
    
    def update_state(self, profile_id: int, state_data: Dict) -> bool:
        """Update automation state for a profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE automation_states SET
                    current_post = ?,
                    next_trigger_post = ?,
                    posts_until_trigger = ?,
                    total_posts_created = ?,
                    renewal_count = ?,
                    last_successful_post = ?,
                    last_renewal_date = ?
                WHERE profile_id = ?
            ''', (
                state_data.get('current_post'),
                state_data.get('next_trigger_post'),
                state_data.get('posts_until_trigger'),
                state_data.get('total_posts_created'),
                state_data.get('renewal_count'),
                state_data.get('last_successful_post'),
                state_data.get('last_renewal_date'),
                profile_id
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating state: {e}")
            return False
    
    def reset_state(self, profile_id: int) -> bool:
        """Reset automation state for a profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get set_value from profile
            cursor.execute('SELECT set_value FROM profiles WHERE id = ?', (profile_id,))
            row = cursor.fetchone()
            set_value = row[0] if row else 360
            
            cursor.execute('''
                UPDATE automation_states SET
                    current_post = 0,
                    next_trigger_post = ?,
                    posts_until_trigger = ?,
                    total_posts_created = 0,
                    renewal_count = 0,
                    last_successful_post = NULL,
                    last_renewal_date = NULL
                WHERE profile_id = ?
            ''', (set_value, set_value, profile_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error resetting state: {e}")
            return False
    
    # Job management methods
    def create_job(self, profile_id: int, force_run: bool = False) -> Optional[int]:
        """Create a new job for a profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO jobs (profile_id, status, force_run)
                VALUES (?, 'pending', ?)
            ''', (profile_id, force_run))
            
            job_id = cursor.lastrowid
            conn.commit()
            conn.close()
            return job_id
        except Exception as e:
            print(f"Error creating job: {e}")
            return None
    
    def get_pending_job(self) -> Optional[Dict]:
        """Get the next pending job"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM jobs
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error getting pending job: {e}")
            return None
    
    def update_job_status(self, job_id: int, status: str, error_message: str = None) -> bool:
        """Update job status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status == 'running':
                cursor.execute('''
                    UPDATE jobs SET status = ?, started_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, job_id))
            elif status in ['completed', 'failed']:
                cursor.execute('''
                    UPDATE jobs SET status = ?, completed_at = CURRENT_TIMESTAMP, error_message = ?
                    WHERE id = ?
                ''', (status, error_message, job_id))
            else:
                cursor.execute('''
                    UPDATE jobs SET status = ?
                    WHERE id = ?
                ''', (status, job_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating job status: {e}")
            return False
    
    def get_job(self, job_id: int) -> Optional[Dict]:
        """Get job by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM jobs WHERE id = ?', (job_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return dict(row)
            return None
        except Exception as e:
            print(f"Error getting job: {e}")
            return None
    
    def get_profile_jobs(self, profile_id: int, limit: int = 10) -> List[Dict]:
        """Get recent jobs for a profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM jobs
                WHERE profile_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (profile_id, limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"Error getting profile jobs: {e}")
            return []
