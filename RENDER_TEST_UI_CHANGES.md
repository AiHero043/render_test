# Changes Needed for render_test (UI) Folder

## Overview
The render_test folder contains the web-based UI for managing erome_v3 profiles. To support the new chunk-based renewal system, you need to make changes in **3 files**.

---

## File 1: `models.py` - Add Chunk Tracking Fields

### Location: `d:\projects\freelance\render_test\models.py`

### Changes Needed:

#### A. Update `AutomationState` model class (around line 74-82)

**FIND:**
```python
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
```

**REPLACE WITH:**
```python
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
    
    # Chunk tracking for download ranges
    current_download_start = db.Column(db.Integer, default=None, nullable=True)
    current_download_end = db.Column(db.Integer, default=None, nullable=True)
    chunk_size = db.Column(db.Integer, default=100, nullable=False)
    download_range_start = db.Column(db.Integer, default=1, nullable=False)
    download_range_end = db.Column(db.Integer, default=200, nullable=False)
```

#### B. Update `to_dict()` method in `AutomationState` (around line 84-96)

**FIND:**
```python
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
```

**REPLACE WITH:**
```python
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
            'last_renewal_date': self.last_renewal_date.isoformat() if self.last_renewal_date else None,
            'current_download_start': self.current_download_start,
            'current_download_end': self.current_download_end,
            'chunk_size': self.chunk_size,
            'download_range_start': self.download_range_start,
            'download_range_end': self.download_range_end
        }
```

---

## File 2: `web_ui.py` - Update State Reset Logic

### Location: `d:\projects\freelance\render_test\web_ui.py`

### Changes Needed:

#### Update `reset_profile_state()` function (around line 216-236)

**FIND:**
```python
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
```

**REPLACE WITH:**
```python
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
            # Reset chunk tracking
            state.current_download_start = None
            state.current_download_end = None
            db.session.commit()
        return jsonify({'message': 'State reset successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Reset failed: {str(e)}'}), 400
```

---

## File 3: `templates/index.html` - Add Chunk Info Display (OPTIONAL)

### Location: `d:\projects\freelance\render_test\templates\index.html`

This is **optional** but recommended for visibility. You need to add UI elements to display chunk tracking information in the state section.

### Find the section where automation state is displayed (search for "Automation State" or similar)

**Add this HTML wherever you display the automation state (suggested: after renewal_count):**

```html
<!-- Chunk Tracking Info -->
<div class="state-item">
    <span class="state-label">Current Chunk:</span>
    <span class="state-value" id="current-chunk">-</span>
</div>
<div class="state-item">
    <span class="state-label">Chunk Size:</span>
    <span class="state-value" id="chunk-size">-</span>
</div>
<div class="state-item">
    <span class="state-label">Download Range:</span>
    <span class="state-value" id="download-range">-</span>
</div>
```

### In the JavaScript section, update the state display function

**Find the function that displays state (likely called `displayProfileState` or similar) and add:**

```javascript
// Display chunk tracking info
if (state.current_download_start && state.current_download_end) {
    document.getElementById('current-chunk').textContent = 
        `Posts ${state.current_download_start}-${state.current_download_end}`;
} else {
    document.getElementById('current-chunk').textContent = 'Not initialized';
}

document.getElementById('chunk-size').textContent = state.chunk_size || '100';
document.getElementById('download-range').textContent = 
    `Posts ${state.download_range_start || '?'}-${state.download_range_end || '?'}`;
```

---

## Database Migration (CRITICAL)

**Before running the updated UI**, you MUST run the migration on your database (same as erome_v3):

### For SQLite (local database):
```bash
cd d:/projects/freelance/render_test
python
```

Then in Python:
```python
import sqlite3

conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()

cursor.execute("ALTER TABLE automation_states ADD COLUMN current_download_start INTEGER DEFAULT NULL")
cursor.execute("ALTER TABLE automation_states ADD COLUMN current_download_end INTEGER DEFAULT NULL")
cursor.execute("ALTER TABLE automation_states ADD COLUMN chunk_size INTEGER DEFAULT 100 NOT NULL")
cursor.execute("ALTER TABLE automation_states ADD COLUMN download_range_start INTEGER DEFAULT 1 NOT NULL")
cursor.execute("ALTER TABLE automation_states ADD COLUMN download_range_end INTEGER DEFAULT 200 NOT NULL")

conn.commit()
conn.close()
print("Migration completed!")
```

### OR Copy the migration script:

1. Copy `d:\projects\freelance\erome_v3\run_migration.py` to `d:\projects\freelance\render_test\`
2. Update `DATABASE_PATH` in the script to `"./profiles.db"`
3. Run: `python run_migration.py`

---

## Summary of Changes:

| File | Lines to Change | Purpose |
|------|-----------------|---------|
| `models.py` | Lines ~74-96 | Add 5 new columns and update to_dict() |
| `web_ui.py` | Lines ~216-236 | Reset chunk tracking on state reset |
| `index.html` | Optional | Display chunk info in UI |
| `profiles.db` | Migration | Add 5 new columns to automation_states table |

---

## Testing After Changes:

1. **Run migration** → `python run_migration.py`
2. **Start UI** → `python web_ui.py`
3. **Open browser** → http://localhost:5001
4. **Create/Edit profile** → Should work normally
5. **View state** → Should show chunk info (if you added HTML)
6. **Reset state** → Should reset chunk tracking too
7. **Create job** → Should be picked up by erome_v3 worker

---

## Backward Compatibility:

✅ **All changes are backward compatible**
- Existing profiles will work normally
- New columns have default values
- Old workers will ignore chunk tracking
- No breaking changes to API

---

## What Happens:

1. **UI creates profile** → Includes download_post_start/end, set_value
2. **UI creates job** → Job added to jobs table
3. **erome_v3 worker picks job** → Initializes chunk tracking automatically
4. **First run** → Downloads posts 1-100 (or whatever chunk)
5. **UI shows state** → Displays current chunk (1-100)
6. **After upload** → Chunk advances to 101-200
7. **UI refreshes** → Shows new chunk (101-200)

---

## Need Help?

If you encounter any issues:
1. Check database migration ran successfully
2. Verify all 5 columns exist: `SELECT * FROM automation_states LIMIT 1;`
3. Check browser console for JavaScript errors
4. Check Flask logs for API errors
