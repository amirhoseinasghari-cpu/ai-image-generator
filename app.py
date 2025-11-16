from flask import Flask, request, render_template_string
import requests
import base64
import os

app = Flask(__name__)

SAMPLE_IMAGES = {
    'گربه': "https://cdn.pixabay.com/photo/2017/02/20/18/03/cat-2083492_1280.jpg",
    'سگ': "https://cdn.pixabay.com/photo/2018/05/07/10/48/husky-3380548_1280.jpg",
    'طبیعت': "https://cdn.pixabay.com/photo/2015/12/01/20/28/forest-1072828_1280.jpg",
    'شهر': "https://cdn.pixabay.com/photo/2017/04/10/07/07/new-york-2217671_1280.jpg"
}

HTML_HOME = '''
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>سازنده عکس هوشمند</title>
    <style>
        body { font-family: Tahoma; text-align: center; padding: 50px; background: #f0f0f0; }
        .container { background: white; padding: 40px; border-radius: 10px; display: inline-block; }
        textarea { width: 300px; height: 100px; padding: 10px; margin: 10px 0; }
        button { padding: 10px 20px; background: blue; color: white; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 سازنده عکس هوشمند</h1>
        <form action="/generate" method="POST">
            <textarea name="text" placeholder="یک گربه، سگ، طبیعت یا شهر" required></textarea><br>
            <button type="submit">تولید عکس</button>
        </form>
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
        body { font-family: Tahoma; text-align: center; padding: 50px; background: #f0f0f0; }
        .container { background: white; padding: 40px; border-radius: 10px; display: inline-block; }
        img { max-width: 400px; border-radius: 10px; margin: 20px 0; }
        .btn { padding: 10px 20px; background: green; color: white; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>✅ عکس تولید شد!</h1>
        <p>متن شما: "{{ text }}"</p>
        <img src="{{ image_url }}" alt="عکس تولید شده">
        <br><br>
        <a href="/" class="btn">🔄 تولید عکس جدید</a>
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
        
        # انتخاب عکس
        image_url = SAMPLE_IMAGES.get('گربه')
        for keyword, url in SAMPLE_IMAGES.items():
            if keyword in text:
                image_url = url
                break
        
        return render_template_string(HTML_RESULT, text=text, image_url=image_url)
    
    except Exception as e:
        return f'''
        <html dir="rtl">
        <body style="font-family: Tahoma; text-align: center; padding: 50px;">
            <h1>❌ خطا</h1>
            <p>خطا در تولید عکس: {str(e)}</p>
            <a href="/">بازگشت به صفحه اصلی</a>
        </body>
        </html>
        '''

if __name__ == '__main__':
    app.run(debug=False)