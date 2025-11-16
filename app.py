from flask import Flask, request, render_template_string
import requests
import base64
import os
import json
from datetime import datetime

app = Flask(__name__)

# عکس‌های نمونه پشتیبان
SAMPLE_IMAGES = {
    'گربه': "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
    'سگ': "https://cdn.pixabay.com/photo/2018/05/07/10/48/husky-3380548_1280.jpg",
    'طبیعت': "https://cdn.pixabay.com/photo/2015/12/01/20/28/forest-1072828_1280.jpg",
    'شهر': "https://cdn.pixabay.com/photo/2017/04/10/07/07/new-york-2217671_1280.jpg",
    'فضا': "https://cdn.pixabay.com/photo/2011/12/14/12/11/astronaut-11080_1280.jpg",
    'غذا': "https://cdn.pixabay.com/photo/2017/01/26/02/06/platter-2009590_1280.jpg"
}

HTML_HOME = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سازنده عکس هوش مصنوعی</title>
    <style>
        body { 
            font-family: Tahoma; 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            min-height: 100vh;
        }
        .container { 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            display: inline-block;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 500px;
            margin: 30px auto;
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .ai-badge {
            background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            display: inline-block;
            margin: 10px 0;
        }
        textarea { 
            width: 100%; 
            height: 120px; 
            padding: 15px; 
            margin: 15px 0; 
            border: 2px solid #ddd;
            border-radius: 10px;
            font-family: Tahoma;
            font-size: 16px;
            resize: vertical;
        }
        select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
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
        }
        .features {
            margin-top: 20px;
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
        <div class="ai-badge">نسخه پیشرفته - با قابلیت‌های جدید</div>
        <p style="color: #666;">هر ایده‌ای رو به عکس تبدیل کن!</p>
        
        <form action="/generate" method="POST">
            <textarea name="text" placeholder="بنویسید: یک گربه سفید در جنگل جادویی، منظره کوهستان با برف، شهر آینده نگر در شب..." required></textarea>
            
            <select name="style">
                <option value="realistic">📷 واقعی</option>
                <option value="artistic">🎨 هنری</option>
                <option value="fantasy">🧙 فانتزی</option>
                <option value="anime">🇯🇵 انیمه</option>
            </select>
            
            <button type="submit">🤖 تولید عکس با هوش مصنوعی</button>
        </form><div class="features">
            <h3>✨ ویژگی‌های جدید:</h3>
            <ul>
                <li>پشتیبانی از سبک‌های مختلف</li>
                <li>طراحی پیشرفته‌تر</li>
                <li>سیستم هوشمندتر</li>
                <li>به‌زودی: هوش مصنوعی واقعی</li>
            </ul>
        </div>
    </div>
</body>
</html>
'''

HTML_RESULT = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>نتیجه تولید عکس</title>
    <style>
        body { 
            font-family: Tahoma; 
            text-align: center; 
            padding: 20px; 
            background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
            margin: 0;
            min-height: 100vh;
        }
        .container { 
            background: white; 
            padding: 40px; 
            border-radius: 15px; 
            display: inline-block;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-width: 700px;
            margin: 30px auto;
        }
        .success-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        img { 
            max-width: 100%; 
            max-height: 500px;
            border-radius: 10px; 
            margin: 20px 0; 
            border: 3px solid #f0f0f0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .btn { 
            padding: 12px 25px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white; 
            text-decoration: none; 
            margin: 10px; 
            display: inline-block;
            border-radius: 8px;
            transition: transform 0.2s;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .info-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-header">
            <h1 style="margin: 0;">🎉 عکس تولید شد!</h1>
            <p>سازنده عکس هوش مصنوعی - نسخه پیشرفته</p>
        </div>
        
        <div class="info-box">
            <p><strong>متن شما:</strong> "{{ text }}"</p>
            <p><strong>سبک:</strong> {{ style }}</p>
            <p><strong>زمان:</strong> {{ time }}</p>
        </div>
        
        <div>
            <img src="{{ image_url }}" alt="عکس تولید شده">
        </div>
        
        <div>
            <a href="/" class="btn">🔄 تولید عکس جدید</a>
        </div>
    </div>
</body>
</html>
'''

def get_smart_image(text, style):
    """انتخاب هوشمند عکس بر اساس متن و سبک"""
    text_lower = text.lower()
    
    # تشخیص خودکار موضوع
    if any(word in text_lower for word in ['گربه', 'cat']):
        return SAMPLE_IMAGES['گربه']
    elif any(word in text_lower for word in ['سگ', 'dog']):
        return SAMPLE_IMAGES['سگ']
    elif any(word in text_lower for word in ['طبیعت', 'جنگل', 'کوه', 'nature']):
        return SAMPLE_IMAGES['طبیعت']
    elif any(word in text_lower for word in ['شهر', 'city', 'building']):
        return SAMPLE_IMAGES['شهر']
    elif any(word in text_lower for word in ['فضا', 'space', 'سیاره']):
        return SAMPLE_IMAGES['فضا']
    elif any(word in text_lower for word in ['غذا', 'food', 'پیتزا']):
        return SAMPLE_IMAGES['غذا']
    else:
        return SAMPLE_IMAGES['طبیعت']

@app.route('/')
def home():
    return HTML_HOME

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        text = request.form['text']
        style = request.form.get('style', 'realistic')
        
        # تولید عکس
        image_url = get_smart_image(text, style)
        
        return render_template_string(
            HTML_RESULT, 
            text=text, 
            style=style,
            image_url=image_url,
            time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    
    except Exception as e:return f'''
        <html dir="rtl">
        <body style="font-family: Tahoma; text-align: center; padding: 50px;">
            <h1 style="color: red;">❌ خطا</h1>
            <p>خطا در تولید عکس: {str(e)}</p>
            <a href="/" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">
                بازگشت به صفحه اصلی
            </a>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(debug=False)