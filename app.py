from flask import Flask, request, render_template_string
import requests
import base64
import os
import json
from datetime import datetime

app = Flask(__name__)

# کلید API - اینجا قرار بده
HF_API_TOKEN = "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"  # جایگزین کن با توکن واقعی
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

def translate_to_english(text):
    """ترجمه ساده فارسی به انگلیسی"""
    dictionary = {
        'گربه': 'cat', 'سگ': 'dog', 'طبیعت': 'nature', 'شهر': 'city',
        'دریا': 'sea', 'کوه': 'mountain', 'جنگل': 'forest', 'گل': 'flower',
        'ستاره': 'star', 'ماه': 'moon', 'خورشید': 'sun', 'درخت': 'tree',
        'فضا': 'space', 'سیاره': 'planet', 'غذا': 'food', 'پیتزا': 'pizza'
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

HTML_HOME = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>سازنده عکس هوش مصنوعی واقعی</title>
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
            border-radius: 20px;display: inline-block;
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
            padding: 15px 30px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 سازنده عکس هوش مصنوعی واقعی</h1>
        <div class="ai-badge">Powered by Stable Diffusion AI</div>
        <p style="color: #666; margin-bottom: 25px;">متن خود را وارد کنید و با هوش مصنوعی عکس واقعی تولید کنید!</p>
        
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
        </div><div style="margin-top: 20px; color: #666;">
            <p>ایده‌های سریع:</p>
            <div>
                <span class="example-tag" onclick="setExample('یک گربه سفید در جنگل')">🐱 گربه در جنگل</span>
                <span class="example-tag" onclick="setExample('منظره کوهستان با برف')">🏔️ کوهستان</span>
                <span class="example-tag" onclick="setExample('شهر آینده نگر در شب')">🌃 شهر آینده</span>
            </div>
        </div>
        
        <div class="features">
            <h3>✨ ویژگی‌ها:</h3>
            <ul>
                <li>تولید عکس واقعی با هوش مصنوعی</li>
                <li>پشتیبانی از سبک‌های مختلف</li>
                <li>ترجمه خودکار فارسی به انگلیسی</li>
                <li>طراحی پیشرفته و ریسپانسیو</li>
            </ul>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loading').style.display = 'block';
        }
        
        function setExample(text) {
            document.querySelector('textarea').value = text;
        }
        
        console.log("🚀 سازنده عکس هوش مصنوعی آماده است!");
    </script>
</body>
</html>
'''

HTML_RESULT = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>عکس تولید شده با هوش مصنوعی</title>
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
        }
        .success-header {
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
        }</style>
</head>
<body>
    <div class="container">
        <div class="success-header">
            <h1 style="margin: 0; font-size: 28px;">🎉 عکس هوش مصنوعی تولید شد!</h1>
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
            <p>می‌توانید از Hugging Face token رایگان استفاده کنید.</p>
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
            <a href="/" class="btn">🔄 تولید عکس جدید</a>
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return HTML_HOME

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        text = request.form['text']
        style = request.form.get('style', 'realistic')
        
        print(f"🎨 دریافت درخواست: {text}")
        print(f"🎭 سبک: {style}")
        
        # تولید عکس
        image_url, image_type = get_smart_image(text, style)
        
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
            <a href="/" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">
                بازگشت به صفحه اصلی
            </a>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(debug=False)