from flask import Flask, render_template, request, send_file, jsonify
import requests
import io
import base64
import random
import time
import os
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'ai-image-generator-secret-key-2024'

class SmartImageGenerator:
    def init(self):
        self.sample_images = {
            'گربه': "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
            'سگ': "https://cdn.pixabay.com/photo/2018/05/07/10/48/husky-3380548_1280.jpg",
            'طبیعت': "https://cdn.pixabay.com/photo/2015/12/01/20/28/forest-1072828_1280.jpg",
            'شهر': "https://cdn.pixabay.com/photo/2017/04/10/07/07/new-york-2217671_1280.jpg",
            'دریا': "https://cdn.pixabay.com/photo/2015/03/09/18/34/beach-666122_1280.jpg",
            'کوه': "https://cdn.pixabay.com/photo/2016/08/11/23/55/mountains-1587287_1280.jpg",
            'فضا': "https://cdn.pixabay.com/photo/2011/12/14/12/11/astronaut-11080_1280.jpg",
            'ماشین': "https://cdn.pixabay.com/photo/2015/05/28/23/12/auto-788747_1280.jpg",
            'غذا': "https://cdn.pixabay.com/photo/2017/01/26/02/06/platter-2009590_1280.jpg",
            'ورزش': "https://cdn.pixabay.com/photo/2017/07/02/19/24/dumbbells-2465478_1280.jpg"
        }
        
    def analyze_text(self, text):
        """آنالیز متن و تشخیص موضوع"""
        text_lower = text.lower()
        
        categories = {
            'حیوانات': ['گربه', 'سگ', 'حیوان', 'پرنده', 'ماهی', 'اسب', 'cat', 'dog'],
            'طبیعت': ['طبیعت', 'جنگل', 'کوه', 'دریا', 'رودخانه', 'درخت', 'گل', 'nature'],
            'شهری': ['شهر', 'ساختمان', 'ماشین', 'خیابان', 'برج', 'city'],
            'فضا': ['فضا', 'سیاره', 'ستاره', 'ماه', 'خورشید', 'space'],
            'غذا': ['غذا', 'پیتزا', 'burger', 'میوه', 'food'],
            'ورزش': ['ورزش', 'فوتبال', 'بسکتبال', 'تنیس', 'sport']
        }
        
        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category
        
        return 'عمومی'
    
    def get_smart_image(self, text):
        """دریافت عکس هوشمند بر اساس متن"""
        category = self.analyze_text(text)
        
        category_images = {
            'حیوانات': ['گربه', 'سگ'],
            'طبیعت': ['طبیعت', 'دریا', 'کوه'],
            'شهری': ['شهر', 'ماشین'],
            'فضا': ['فضا'],
            'غذا': ['غذا'],
            'ورزش': ['ورزش'],
            'عمومی': ['طبیعت', 'شهر', 'فضا']
        }
        
        available_images = category_images.get(category, ['طبیعت', 'شهر'])
        selected_key = random.choice(available_images)
        
        return self.sample_images[selected_key]
    
    def generate_image_data(self, text):
        """تولید داده عکس"""
        image_url = self.get_smart_image(text)
        
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            img_data = base64.b64encode(response.content).decode()
            return {
                'success': True,
                'image_data': f"data:image/jpeg;base64,{img_data}",
                'image_url': image_url,
                'category': self.analyze_text(text)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Initialize image generator
image_gen = SmartImageGenerator()

@app.route('/')
def home():
    """صفحه اصلی"""
    return '''
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>سازنده عکس هوشمند - نسخه نهایی</title>
        <style>
            body { 
                font-family: Tahoma, sans-serif; 
                text-align: center; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                min-height: 100vh;
            }
            .container { 
                background: white; 
                padding: 40px;border-radius: 20px; 
                display: inline-block;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                max-width: 500px;
                margin: 30px auto;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            .version {
                background: #4CAF50;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-size: 12px;
                display: inline-block;
                margin-bottom: 20px;
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
                background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
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
            <h1>🎨 سازنده عکس هوشمند</h1>
            <div class="version">نسخه ۱.۰ - نهایی</div>
            <p style="color: #666;">هر ایده‌ای رو به عکس تبدیل کن!</p>
            
            <form action="/generate" method="POST">
                <textarea name="text" placeholder="بنویسید: یک گربه سفید در جنگل جادویی..." required></textarea>
                
                <select name="style">
                    <option value="realistic">📷 واقعی</option>
                    <option value="artistic">🎨 هنری</option>
                    <option value="fantasy">🧙 فانتزی</option>
                </select>
                
                <button type="submit">🤖 تولید عکس هوشمند</button>
            </form>
            
            <div class="features">
                <h3>✨ ویژگی‌های نسخه نهایی:</h3>
                <ul>
                    <li>تشخیص هوشمند موضوع</li>
                    <li>انتخاب خودکار عکس مرتبط</li>
                    <li>طراحی ریسپانسیو</li>
                    <li>قابلیت دانلود</li>
                    <li>آماده deploy</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate_image():
    """تولید عکس"""
    try:
        text = request.form['text']
        style = request.form.get('style', 'realistic')
        
        print(f"🎨 درخواست جدید: {text}")
        
        # تولید عکس
        result = image_gen.generate_image_data(text)
        
        if result['success']:
            return f'''
            <!DOCTYPE html>
            <html dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>عکس تولید شده</title>
                <style>
                    body {{ 
                        font-family: Tahoma, sans-serif; 
                        text-align: center; 
                        padding: 20px;background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
                        margin: 0;
                        min-height: 100vh;
                    }}
                    .container {{ 
                        background: white; 
                        padding: 40px; 
                        border-radius: 20px; 
                        display: inline-block;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                        max-width: 700px;
                        margin: 30px auto;
                    }}
                    .success-header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 25px;
                        border-radius: 15px;
                        margin-bottom: 25px;
                    }}
                    img {{ 
                        max-width: 100%; 
                        max-height: 500px;
                        border-radius: 15px; 
                        margin: 25px 0; 
                        border: 5px solid #f8f9fa;
                        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
                    }}
                    .btn {{ 
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
                    }}
                    .btn:hover {{
                        transform: translateY(-2px);
                    }}
                    .info-box {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 10px;
                        margin: 20px 0;
                        text-align: right;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-header">
                        <h1 style="margin: 0;">🎉 عکس تولید شد!</h1>
                        <p>سازنده عکس هوشمند - نسخه نهایی</p>
                    </div>
                    
                    <div class="info-box">
                        <p><strong>متن شما:</strong> "{text}"</p>
                        <p><strong>سبک:</strong> {style}</p>
                        <p><strong>دسته‌بندی:</strong> {result['category']}</p>
                    </div>
                    
                    <div>
                        <img src="{result['image_data']}" alt="عکس تولید شده">
                    </div>
                    
                    <div>
                        <form action="/download" method="POST" style="display: inline;">
                            <input type="hidden" name="image_data" value="{result['image_data']}">
                            <button type="submit" class="btn">💾 دانلود عکس</button>
                        </form>
                        
                        <a href="/" class="btn">🔄 تولید عکس جدید</a>
                    </div>
                </div>
            </body>
            </html>
            '''
        else:
            return f'''
            <!DOCTYPE html>
            <html dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>خطا</title>
                <style>
                    body {{ font-family: Tahoma; text-align: center; padding: 50px; background: #f8f9fa; }}
                    .error {{ 
                        background: white; 
                        padding: 40px; 
                        border-radius: 15px; 
                        display: inline-block;
                        color: #dc3545;border-left: 5px solid #dc3545;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h1>❌ خطا در تولید عکس</h1>
                    <p>{result['error']}</p>
                    <a href="/" style="padding: 12px 25px; background: #667eea; color: white; text-decoration: none; border-radius: 8px;">بازگشت</a>
                </div>
            </body>
            </html>
            '''
    
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>خطا</title>
        </head>
        <body style="font-family: Tahoma; text-align: center; padding: 50px;">
            <h1 style="color: red;">❌ خطا</h1>
            <p>{str(e)}</p>
            <a href="/" style="padding: 10px 20px; background: blue; color: white; text-decoration: none;">بازگشت</a>
        </body>
        </html>
        '''

@app.route('/download', methods=['POST'])
def download_image():
    """دانلود عکس"""
    try:
        image_data = request.form['image_data'].replace('data:image/jpeg;base64,', '')
        image_bytes = base64.b64decode(image_data)
        
        filename = f"ai_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        return send_file(
            io.BytesIO(image_bytes),
            as_attachment=True,
            download_name=filename,
            mimetype='image/jpeg'
        )
    except Exception as e:
        return f"خطا در دانلود: {e}"

@app.route('/health')
def health_check():
    """بررسی سلامت سرور"""
    return jsonify({
        'status': 'healthy', 
        'service': 'AI Image Generator',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    # برای خروجی نهایی، دیباگ رو غیرفعال کن
    debug = False
    print(f"🚀 سازنده عکس هوشمند - نسخه نهایی")
    print(f"🌐 آدرس: http://localhost:{port}")
    print(f"🔧 حالت دیباگ: {debug}")
    print(f"📦 آماده برای deploy...")
    
    app.run(host='0.0.0.0', port=port, debug=False)