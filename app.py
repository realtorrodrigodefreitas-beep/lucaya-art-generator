from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import base64, io, os

app = Flask(__name__)

SERIF = '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf'
SERIF_I = '/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf'
SANS = '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
SANS_B = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'

def hex_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2],16) for i in (0,2,4))

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    img_b64 = data['image_base64']
    config = data['config']
    SIZE, M = 1080, 72
    img = Image.open(io.BytesIO(base64.b64decode(img_b64))).convert('RGB')
    w,h = img.size
    s = max(SIZE/w, SIZE/h)
    img = img.resize((int(w*s),int(h*s)), Image.LANCZOS)
    nw,nh = img.size
    img = img.crop(((nw-SIZE)//2,(nh-SIZE)//2,(nw+SIZE)//2,(nh+SIZE)//2))
    r,g,b,a = config.get('overlay',[8,20,35,165])
    ov = Image.new('RGBA',(SIZE,SIZE),(r,g,b,a))
    img = Image.alpha_composite(img.convert('RGBA'),ov).convert('RGB')
    draw = ImageDraw.Draw(img)
    ac = hex_rgb(config.get('accent','#C9A84C'))
    fc = hex_rgb(config.get('fc','#F0EDE6'))
    draw.text((M,M), config.get('badge','LUCAYA VILLAGE'), font=ImageFont.truetype(SANS,24), fill=ac)
    draw.rectangle([M,M+32,M+44,M+36], fill=ac)
    lh, cy = 116, (SIZE-116*3)//2-20
    draw.text((M,cy), config.get('h1',''), font=ImageFont.truetype(SERIF,108), fill=fc)
    draw.text((M,cy+lh), config.get('h2',''), font=ImageFont.truetype(SERIF,108), fill=fc)
    draw.text((M,cy+lh*2), config.get('h3',''), font=ImageFont.truetype(SERIF_I,108), fill=ac)
    by = SIZE-M-100
    draw.text((M,by), config.get('sub',''), font=ImageFont.truetype(SANS,30), fill=fc)
    cta = config.get('cta','LINK IN BIO')
    cf = ImageFont.truetype(SANS_B,22)
    bb = draw.textbbox((0,0),cta,font=cf)
    cw = bb[2]-bb[0]+48
    draw.rounded_rectangle([M,by+48,M+cw,by+90],radius=21,outline=ac,width=2)
    draw.text((M+24,by+57),cta,font=cf,fill=ac)
    buf = io.BytesIO()
    img.save(buf,'JPEG',quality=95)
    return jsonify({'image_base64': base64.b64encode(buf.getvalue()).decode()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',8000)))