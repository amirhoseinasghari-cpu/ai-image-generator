# auth.py - سیستم مدیریت کاربران
import json
import hashlib
import os
from datetime import datetime

class UserManager:
    def init(self):
        self.users_file = "users.json"
        self.images_file = "user_images.json"
        self.load_data()
    
    def load_data(self):
        if not os.path.exists(self.users_file):
            self.users = {}
            self.save_users()
        else:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        
        if not os.path.exists(self.images_file):
            self.user_images = {}
            self.save_images()
        else:
            with open(self.images_file, 'r', encoding='utf-8') as f:
                self.user_images = json.load(f)
    
    def save_users(self):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def save_images(self):
        with open(self.images_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_images, f, ensure_ascii=False, indent=2)
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, email, password, name):
        if email in self.users:
            return False, "این ایمیل قبلاً ثبت شده است"
        
        self.users[email] = {
            'password': self.hash_password(password),
            'name': name,
            'created_at': datetime.now().isoformat(),
            'plan': 'free',
            'images_today': 0,
            'last_reset': datetime.now().date().isoformat()
        }
        self.save_users()
        return True, "ثبت نام موفقیت‌آمیز بود"
    
    def login(self, email, password):
        if email not in self.users:
            return False, "کاربری با این ایمیل یافت نشد"
        
        if self.users[email]['password'] != self.hash_password(password):
            return False, "رمز عبور اشتباه است"
        
        self.reset_daily_limit(email)
        return True, "ورود موفقیت‌آمیز بود"
    
    def reset_daily_limit(self, email):
        today = datetime.now().date().isoformat()
        if self.users[email]['last_reset'] != today:
            self.users[email]['images_today'] = 0
            self.users[email]['last_reset'] = today
            self.save_users()
    
    def can_generate_image(self, email):
        if self.users[email]['plan'] == 'premium':
            return True, ""
        
        self.reset_daily_limit(email)
        if self.users[email]['images_today'] < 5:
            return True, ""
        else:
            return False, "محدودیت روزانه! شما ۵ عکس رایگان امروز را استفاده کرده‌اید."
    
    def record_image_generation(self, email, prompt, image_data):
        self.reset_daily_limit(email)
        self.users[email]['images_today'] += 1
        
        if email not in self.user_images:
            self.user_images[email] = []
        
        self.user_images[email].append({
            'prompt': prompt,
            'image_data': image_data,
            'created_at': datetime.now().isoformat()
        })
        
        self.save_users()
        self.save_images()
    
    def get_user_images(self, email):
        return self.user_images.get(email, [])