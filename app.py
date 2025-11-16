from flask import Flask, request, render_template_string, session, redirect, url_for
import requests
import base64
import os
import json
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ai-image-generator-secret-key-2024'  # برای sessionها

# کلید API - اینجا قرار بده
HF_API_TOKEN = "hk_your_token_here"  # جایگزین کن با توکن واقعی
HF_API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"

# عکس‌های نمونه برای وقتی که API کار نمی‌کند
SAMPLE_IMAGES = {
    'گربه': "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
    'سگ': "https://cdn.pixabay.com/photo/2018/05/07/10/48/husky-3380548_1280.jpg",
    'طبیعت': "https://cdn.pixabay.com/photo/2015/12/01/20/28/forest-1072828_1280.jpg",
    'شهر': "https://cdn.pixabay.com/photo/2017/04/10/07/07/new-york-2217671_1280.jpg",
    'فضا': "https://cdn.pixabay.com/photo/2011/12/14/12/11/astronaut-11080_1280.jpg",
    'غذا': "https://cdn.pixabay.com/photo/2017/01/26/02/06/platter-2009590_1280.jpg"
}

class UserManager:
    def init(self):
        self.users_file = "users.json"
        self.images_file = "user_images.json"
        self.load_data()
    
    def load_data(self):
        """بارگذاری داده‌ها از فایل"""
        if not os.path.exists(self.users_file):
            self.users = {}
            self.save_users()
        else:
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except:
                self.users = {}
        
        if not os.path.exists(self.images_file):
            self.user_images = {}
            self.save_images()
        else:
            try:
                with open(self.images_file, 'r', encoding='utf-8') as f:
                    self.user_images = json.load(f)
            except:
                self.user_images = {}
    
    def save_users(self):
        """ذخیره کاربران"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def save_images(self):
        """ذخیره عکس‌های کاربران"""
        try:
            with open(self.images_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_images, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def hash_password(self, password):
        """هش کردن رمز عبور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self, email, password, name):
        """ثبت نام کاربر جدید"""
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
        """ورود کاربر"""
        if email not in self.users:
            return False, "کاربری با این ایمیل یافت نشد"
        
        if self.users[email]['password'] != self.hash_password(password):
            return False, "رمز عبور اشتباه است"
        
        # بررسی reset روزانه
        self.reset_daily_limit(email)
        return True, "ورود موفقیت‌آمیز بود"
    
    def reset_daily_limit(self, email):
        """بازنشانی محدودیت روزانه"""
        today = datetime.now().date().isoformat()
        if self.users[email]['last_reset'] != today:
            self.users[email]['images_today'] = 0
            self.users[email]['last_reset'] = today
            self.save_users()
    
    def can_generate_image(self, email):
        """آیا کاربر می‌تواند عکس تولید کند؟"""
        if email not in self.users:
            return False, "لطفاً اول وارد شوید"
        
        if self.users[email]['plan'] == 'premium':
            return True, ""
        self.reset_daily_limit(email)
        if self.users[email]['images_today'] < 5:  # 5 عکس رایگان در روز
            return True, ""
        else:
            return False, "محدودیت روزانه! شما ۵ عکس رایگان امروز را استفاده کرده‌اید. فردا دوباره امتحان کنید."
    
    def record_image_generation(self, email, prompt, image_url):
        """ثبت تولید عکس جدید"""
        self.reset_daily_limit(email)
        self.users[email]['images_today'] += 1
        
        if email not in self.user_images:
            self.user_images[email] = []
        
        self.user_images[email].append({
            'prompt': prompt,
            'image_url': image_url,
            'created_at': datetime.now().isoformat()
        })
        
        # فقط ۵۰ عکس آخر رو نگه دار
        if len(self.user_images[email]) > 50:
            self.user_images[email] = self.user_images[email][-50:]
        
        self.save_users()
        self.save_images()
    
    def get_user_images(self, email):
        """دریافت تاریخچه عکس‌های کاربر"""
        return self.user_images.get(email, [])

# Initialize user manager
user_manager = UserManager()

def translate_to_english(text):
    """ترجمه ساده فارسی به انگلیسی"""
    dictionary = {
        'گربه': 'cat', 'سگ': 'dog', 'طبیعت': 'nature', 'شهر': 'city',
        'دریا': 'sea', 'کوه': 'mountain', 'جنگل': 'forest', 'گل': 'flower',
        'ستاره': 'star', 'ماه': 'moon', 'خورشید': 'sun', 'درخت': 'tree',
        'فضا': 'space', 'سیاره': 'planet', 'غذا': 'food', 'پیتزا': 'pizza',
        'ماشین': 'car', 'خانه': 'house', 'باغ': 'garden', 'رودخانه': 'river'
    }
    
    for persian, english in dictionary.items():
        text = text.replace(persian, english)
    
    return text

def optimize_prompt(text, style):
    """بهینه‌سازی prompt برای نتایج بهتر"""
    text_en = translate_to_english(text)
    
    # اضافه کردن کلمات کلیدی کیفیت
    quality_words = "high quality, detailed, sharp focus, professional, 4k"
    
    # نگاشت سبک‌ها
    style_mapping = {
        'realistic': 'photorealistic, realistic, professional photography',
        'artistic': 'digital art, concept art, artistic, creative',
        'fantasy': 'fantasy, magical, mystical, dreamy',
        'anime': 'anime style, japanese animation, vibrant'
    }
    
    style_en = style_mapping.get(style, 'digital art')
    
    return f"{text_en}, {style_en}, {quality_words}"

def generate_ai_image(prompt):
    """تولید عکس با هوش مصنوعی واقعی"""
    try:
        headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
        
        print(f"🔄 ارسال درخواست به Hugging Face...")
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ عکس با موفقیت تولید شد!")
            return response.content
        else:
            print(f"❌ خطای API: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ خطا در ارتباط با API: {e}")
        return None

def get_smart_image(text, style):
    """دریافت عکس - اول AI، اگر نشد نمونه"""
    # اول سعی کن با AI تولید کنی
    prompt = optimize_prompt(text, style)
    print(f"🎯 Prompt: {prompt}")
    
    ai_image = generate_ai_image(prompt)
    
    if ai_image:
        # تبدیل عکس AI به base64
        img_data = base64.b64encode(ai_image).decode()
        return f"data:image/png;base64,{img_data}", "ai"
    else:
        # اگر AI کار نکرد، از عکس نمونه استفاده کن
        text_lower = text.lower()
        for keyword, url in SAMPLE_IMAGES.items():
            if keyword in text_lower:
                return url, "sample"
        return SAMPLE_IMAGES['طبیعت'], "sample"

# HTML Templates
HTML_HOME = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سازنده عکس هوش مصنوعی</title>
    <style>
        body { 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            padding: 20px;background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            min-height: 100vh;
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 40px; 
            border-radius: 20px; 
            display: inline-block;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 500px;
            margin: 30px auto;
            color: #333;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .btn { 
            padding: 15px 30px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            text-decoration: none; 
            margin: 10px; 
            display: inline-block;
            border-radius: 10px;
            transition: transform 0.2s;
            border: none;
            cursor: pointer;
            font-size: 16px;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .btn-secondary {
            background: linear-gradient(135deg, #00b09b, #96c93d);
        }
        .features {
            margin-top: 25px;
            text-align: right;
            color: #666;
        }
        .features li {
            margin: 8px 0;
            list-style-type: none;
        }
        .features li:before {
            content: "✅ ";
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 سازنده عکس هوش مصنوعی</h1>
        <p style="color: #666; margin-bottom: 25px;">برای استفاده از برنامه، لطفاً وارد شوید یا ثبت نام کنید</p>
        
        <div>
            <a href="/login" class="btn">🔐 ورود به حساب</a>
            <a href="/register" class="btn btn-secondary">📝 ثبت نام جدید</a>
        </div>
        
        <div class="features">
            <h3>✨ ویژگی‌های برنامه:</h3>
            <ul>
                <li>تولید عکس با هوش مصنوعی</li>
                <li>سیستم کاربران پیشرفته</li>
                <li>تاریخچه عکس‌های تولید شده</li>
                <li>۵ عکس رایگان در روز</li>
                <li>پنل کاربری شخصی</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

HTML_LOGIN = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود به حساب</title>
    <style>
        body { 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            min-height: 100vh;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 40px; 
            border-radius: 20px; 
            display: inline-block;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 400px;
            margin: 30px auto;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 0;
        }
        .link {
            color: #667eea;
            text-decoration: none;
            margin: 10px 0;
            display: block;
        }</style>
</head>
<body>
    <div class="container">
        <h1>🔐 ورود به حساب</h1>
        <form method="POST">
            <input type="email" name="email" placeholder="ایمیل" required>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <button type="submit">ورود به حساب</button>
        </form>
        <a href="/register" class="link">حساب کاربری ندارید؟ ثبت نام کنید</a>
        <a href="/" class="link">بازگشت به صفحه اصلی</a>
    </div>
</body>
</html>
'''

HTML_REGISTER = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ثبت نام جدید</title>
    <style>
        body { 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            min-height: 100vh;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 40px; 
            border-radius: 20px; 
            display: inline-block;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 400px;
            margin: 30px auto;
        }
        input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #00b09b, #96c93d);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            cursor: pointer;
            margin: 10px 0;
        }
        .link {
            color: #667eea;
            text-decoration: none;
            margin: 10px 0;
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 ثبت نام جدید</h1>
        <form method="POST">
            <input type="text" name="name" placeholder="نام کامل" required>
            <input type="email" name="email" placeholder="ایمیل" required>
            <input type="password" name="password" placeholder="رمز عبور" required>
            <button type="submit">ثبت نام</button>
        </form>
        <a href="/login" class="link">قبلاً حساب دارید؟ وارد شوید</a>
        <a href="/" class="link">بازگشت به صفحه اصلی</a>
    </div>
</body>
</html>
'''

HTML_DASHBOARD = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>پنل کاربری</title>
    <style>
        body { 
            font-family: Tahoma, sans-serif; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            min-height: 100vh;
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 30px; 
            border-radius: 15px; 
            max-width: 800px;
            margin: 20px auto;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: center;
        }
        .btn { 
            padding: 12px 25px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            text-decoration: none; 
            margin: 5px; 
            display: inline-block;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }.btn-success {
            background: linear-gradient(135deg, #00b09b, #96c93d);
        }
        .btn-danger {
            background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        }
        .history-item {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-right: 4px solid #667eea;
        }
        .limit-warning {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            border: 1px solid #ffeaa7;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="margin: 0;">👋 خوش آمدید، {{ user_name }}</h1>
            <p style="margin: 10px 0 0 0;">{{ user_email }}</p>
        </div>

        <div class="stats">
            <h3>📊 آمار امروز</h3>
            <p>تعداد عکس‌های تولید شده: <strong>{{ images_today }}/5</strong></p>
            {% if can_generate %}
                <p style="color: green;">✅ می‌توانید عکس جدید تولید کنید</p>
            {% else %}
                <div class="limit-warning">
                    ❌ {{ limit_message }}
                </div>
            {% endif %}
        </div>

        <div style="text-align: center; margin: 20px 0;">
            {% if can_generate %}
                <a href="/generate" class="btn btn-success">🎨 تولید عکس جدید</a>
            {% else %}
                <a href="/generate" class="btn" style="background: #ccc; cursor: not-allowed;">🎨 تولید عکس جدید</a>
            {% endif %}
            <a href="/logout" class="btn btn-danger">🚪 خروج</a>
        </div>

        <div>
            <h3>📷 تاریخچه عکس‌های شما</h3>
            {% if user_images %}
                {% for img in user_images %}
                <div class="history-item">
                    <p style="margin: 0 0 5px 0;"><strong>{{ img.prompt }}</strong></p>
                    <p style="margin: 0; color: #666; font-size: 14px;">{{ img.created_at[:16] }}</p>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #666;">هنوز هیچ عکسی تولید نکرده‌اید</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
'''

HTML_GENERATE = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تولید عکس جدید</title>
    <style>
        body { 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            min-height: 100vh;
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 40px; 
            border-radius: 20px; 
            display: inline-block;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 500px;
            margin: 30px auto;
            color: #333;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .ai-badge {
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            color: white;
            padding: 8px 20px;
            border-radius: 25px;
            font-size: 14px;
            display: inline-block;
            margin: 10px 0;
            font-weight: bold;
        }
        textarea { 
            width: 100%; 
            height: 120px; 
            margin: 20px 0; 
            padding: 15px; 
            border: 2px solid #ddd;
            border-radius: 10px;
            font-family: Tahoma;
            font-size: 16px;
            resize: vertical;
        }
        select {
            width: 100%;
            padding: 12px;
            margin: 15px 0;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        button { 
            padding: 15px 30px;background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            border: none; 
            cursor: pointer; 
            font-size: 18px;
            border-radius: 10px;
            transition: transform 0.2s;
            margin: 10px 0;
            width: 100%;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .loading {
            display: none;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            color: #667eea;
        }
        .example-tag {
            background: #e9ecef;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            display: inline-block;
            cursor: pointer;
            transition: all 0.3s;
        }
        .example-tag:hover {
            background: #667eea;
            color: white;
        }
        .btn-back {
            padding: 10px 20px;
            background: #6c757d;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            display: inline-block;
            margin: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 تولید عکس جدید</h1>
        <div class="ai-badge">۵ عکس رایگان در روز</div>
        
        <form action="/generate" method="POST" onsubmit="showLoading()">
            <textarea name="text" placeholder="بنویسید: یک گربه سفید در جنگل جادویی، منظره کوهستان با برف، شهر آینده نگر در شب..." required></textarea>
            
            <select name="style">
                <option value="realistic">📷 واقعی</option>
                <option value="artistic">🎨 هنری</option>
                <option value="fantasy">🧙 فانتزی</option>
                <option value="anime">🇯🇵 انیمه</option>
            </select>
            
            <button type="submit">
                <span style="font-size: 20px;">🤖</span> تولید عکس با هوش مصنوعی
            </button>
        </form>
        
        <div id="loading" class="loading">
            <div style="font-size: 24px; margin-bottom: 10px;">⏳</div>
            <p>در حال تولید عکس با هوش مصنوعی...</p>
            <p style="font-size: 14px; color: #999;">لطفاً ۲۰-۳۰ ثانیه صبر کنید</p>
        </div>
        
        <div style="margin-top: 20px; color: #666;">
            <p>ایده‌های سریع:</p>
            <div>
                <span class="example-tag" onclick="setExample('یک گربه سفید در جنگل')">🐱 گربه در جنگل</span>
                <span class="example-tag" onclick="setExample('منظره کوهستان با برف')">🏔️ کوهستان</span>
                <span class="example-tag" onclick="setExample('شهر آینده نگر در شب')">🌃 شهر آینده</span>
            </div>
        </div>
        
        <a href="/dashboard" class="btn-back">← بازگشت به پنل کاربری</a>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function setExample(text) {
            document.querySelector('textarea').value = text;
        }
    </script>
</body>
</html>
'''

HTML_RESULT = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>عکس تولید شده</title>
    <style>
        body { 
            font-family: Tahoma, sans-serif; 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            min-height: 100vh;
            color: white;
        }
        .container { 
            background: rgba(255,255,255,0.95); 
            padding: 40px; 
            border-radius: 20px; 
            display: inline-block;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            max-width: 700px;
            margin: 30px auto;
            color: #333;
        }.success-header {
            background: linear-gradient(135deg, #00b09b, #96c93d);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
        }
        .ai-powered {
            background: #ff6b6b;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            display: inline-block;
            margin: 10px 0;
        }
        .sample-notice {
            background: #fff3cd;
            color: #856404;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid #ffeaa7;
        }
        img { 
            max-width: 100%; 
            max-height: 500px;
            border-radius: 15px; 
            margin: 25px 0; 
            border: 5px solid white;
            box-shadow: 0 15px 35px rgba(0,0,0,0.3);
            transition: transform 0.3s;
        }
        img:hover {
            transform: scale(1.02);
        }
        .btn { 
            padding: 12px 30px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            text-decoration: none; 
            margin: 10px; 
            display: inline-block;
            border-radius: 8px;
            transition: transform 0.2s;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .info-box {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: right;
            border-right: 5px solid #667eea;
        }
        .tech-info {
            background: #e9ecef;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            font-size: 14px;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-header">
            <h1 style="margin: 0; font-size: 28px;">🎉 عکس تولید شد!</h1>
            {% if image_type == "ai" %}
                <div class="ai-powered">تولید شده با Stable Diffusion AI</div>
            {% else %}
                <div class="ai-powered">عکس نمونه هوشمند</div>
            {% endif %}
        </div>
        
        <div class="info-box">
            <h3 style="margin: 0 0 10px 0;">📝 درخواست شما:</h3>
            <p style="margin: 0; font-size: 18px;"><strong>"{{ text }}"</strong></p>
            <p style="margin: 10px 0 0 0; color: #666;">سبک: {{ style }} | زمان: {{ time }}</p>
        </div>
        
        {% if image_type == "sample" %}
        <div class="sample-notice">
            <h3>💡 توجه:</h3>
            <p>این یک عکس نمونه است. برای استفاده از هوش مصنوعی واقعی، نیاز به API Key داریم.</p>
        </div>
        {% endif %}
        
        <div>
            <img src="{{ image_url }}" alt="عکس تولید شده">
        </div>
        
        <div class="tech-info">
            <strong>🔧 اطلاعات فنی:</strong><br>
            {% if image_type == "ai" %}
            • مدل: Stable Diffusion v1.5<br>
            • پردازش: هوش مصنوعی واقعی<br>
            {% else %}
            • الگوریتم: انتخاب هوشمند<br>
            • پردازش: نمونه‌های از پیش آماده<br>
            {% endif %}
            • کیفیت: HD<br>
            • سرویس: Hugging Face API
        </div>
        
        <div>
            <a href="/generate" class="btn">🔄 تولید عکس جدید</a>
            <a href="/dashboard" class="btn" style="background: linear-gradient(135deg, #00b09b, #96c93d);">📊 پنل کاربری</a>
        </div>
    </div>
</body>
</html>
'''

# Routes
@app.route('/')
def home():
    if 'user' in session:
        return redirect('/dashboard')
    return HTML_HOME

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect('/dashboard')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        success, message = user_manager.register(email, password, name)
        if success:
            session['user'] = email
            return redirect('/dashboard')
        else:
            return f'''
            <html dir="rtl">
            <head><meta charset="UTF-8"><title>خطا</title></head>
            <body style="font-family: Tahoma; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ خطا در ثبت نام</h1>
                <p>{message}</p>
                <a href="/register" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">
                    بازگشت
                </a>
            </body>
            </html>
            '''
    
    return HTML_REGISTER

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect('/dashboard')
    
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        success, message = user_manager.login(email, password)
        if success:
            session['user'] = email
            return redirect('/dashboard')
        else:
            return f'''
            <html dir="rtl">
            <head><meta charset="UTF-8"><title>خطا</title></head>
            <body style="font-family: Tahoma; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ خطا در ورود</h1>
                <p>{message}</p>
                <a href="/login" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">
                    بازگشت
                </a>
            </body>
            </html>
            '''
    
    return HTML_LOGIN

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    
    user_email = session['user']
    user_data = user_manager.users[user_email]
    user_images = user_manager.get_user_images(user_email)
    can_generate, limit_message = user_manager.can_generate_image(user_email)
    
    # معکوس کردن لیست برای نمایش جدیدترین عکس‌ها اول
    user_images.reverse()
    
    return render_template_string(
        HTML_DASHBOARD,
        user_name=user_data['name'],
        user_email=user_email,
        images_today=user_data['images_today'],
        can_generate=can_generate,
        limit_message=limit_message,
        user_images=user_images[:10]  # فقط ۱۰ عکس آخر
    )

@app.route('/generate', methods=['GET', 'POST'])
def generate_image():
    if 'user' not in session:
        return redirect('/login')
    
    user_email = session['user']
    
    # بررسی محدودیت
    can_generate, message = user_manager.can_generate_image(user_email)
    if request.method == 'GET' and not can_generate:
        return f'''
        <html dir="rtl">
        <head><meta charset="UTF-8"><title>محدودیت</title></head>
        <body style="font-family: Tahoma; text-align: center; padding: 50px;">
            <h1 style="color: orange;">⚠️ محدودیت روزانه</h1>
            <p>{message}</p>
            <a href="/dashboard" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">
                بازگشت به پنل کاربری
            </a>
        </body>
        </html>
        '''
    
    if request.method == 'POST':
        try:
            text = request.form['text']
            style = request.form.get('style', 'realistic')
            
            print(f"🎨 دریافت درخواست از {user_email}: {text}")
            
            # تولید عکس
            image_url, image_type = get_smart_image(text, style)
            
            # ثبت در تاریخچه کاربر
            user_manager.record_image_generation(user_email, text, image_url)
            
            return render_template_string(
                HTML_RESULT, 
                text=text, 
                style=style,
                image_url=image_url,
                image_type=image_type,
                time=datetime.now().strftime("%H:%M:%S")
            )
        except Exception as e:
            return f'''
            <html dir="rtl">
            <head><meta charset="UTF-8"><title>خطا</title></head>
            <body style="font-family: Tahoma; text-align: center; padding: 50px;">
                <h1 style="color: red;">❌ خطا در تولید عکس</h1>
                <p>{str(e)}</p>
                <a href="/generate" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">
                    تلاش مجدد
                </a>
            </body>
            </html>
            '''
    
    return HTML_GENERATE

@app.route('logout')
def logout():
    session.pop('usre' , None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=False)
