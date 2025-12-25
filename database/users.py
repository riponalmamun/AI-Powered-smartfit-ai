import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
from config import settings

class UserDatabase:
    def __init__(self):
        self.users_dir = settings.USER_DATA_DIR
        self.users_dir.mkdir(exist_ok=True)
    
    def _get_user_file(self, user_id: str) -> Path:
        return self.users_dir / f"{user_id}.json"
    
    def create_user_profile(self, user_id: str, detected_info: Dict) -> Dict:
        user_profile = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'detected_profile': detected_info,
            'preferences': {
                'styles': {},
                'colors': {}
            },
            'interaction_history': [],
            'total_tryons': 0,
            'saved_favorites': []
        }
        
        self._save_user(user_profile)
        return user_profile
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        user_file = self._get_user_file(user_id)
        
        if user_file.exists():
            with open(user_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def update_user_profile(self, user_id: str, updates: Dict) -> bool:
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            return False
        
        user_profile.update(updates)
        user_profile['last_active'] = datetime.now().isoformat()
        
        self._save_user(user_profile)
        return True
    
    def _save_user(self, user_profile: Dict):
        user_file = self._get_user_file(user_profile['user_id'])
        with open(user_file, 'w') as f:
            json.dump(user_profile, f, indent=2)
    
    def add_interaction(self, user_id: str, interaction: Dict) -> bool:
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            return False
        
        interaction['timestamp'] = datetime.now().isoformat()
        user_profile['interaction_history'].append(interaction)
        
        if interaction.get('action') == 'tried_on':
            user_profile['total_tryons'] = user_profile.get('total_tryons', 0) + 1
        
        self._save_user(user_profile)
        return True
    
    def add_favorite(self, user_id: str, favorite: Dict) -> bool:
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            return False
        
        if 'saved_favorites' not in user_profile:
            user_profile['saved_favorites'] = []
        
        favorite['saved_at'] = datetime.now().isoformat()
        user_profile['saved_favorites'].append(favorite)
        
        self._save_user(user_profile)
        return True
    
    def get_user_favorites(self, user_id: str) -> list:
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            return []
        
        return user_profile.get('saved_favorites', [])
    
    def get_user_history(self, user_id: str) -> list:
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            return []
        
        return user_profile.get('interaction_history', [])
    
    def update_preferences(self, user_id: str, preferences: Dict) -> bool:
        user_profile = self.get_user_profile(user_id)
        
        if not user_profile:
            return False
        
        if 'preferences' not in user_profile:
            user_profile['preferences'] = {'styles': {}, 'colors': {}}
        
        user_profile['preferences'].update(preferences)
        
        self._save_user(user_profile)
        return True
    
    def delete_user(self, user_id: str) -> bool:
        user_file = self._get_user_file(user_id)
        
        if user_file.exists():
            user_file.unlink()
            return True
        
        return False

user_db = UserDatabase()