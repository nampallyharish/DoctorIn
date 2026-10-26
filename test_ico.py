from PIL import Image
try:
    im = Image.open('frontend/public/favicon.ico')
    print('ICO format:', im.format, 'size:', im.size)
except Exception as e:
    print('ICO error:', e)
try:
    im2 = Image.open('frontend/public/favicon.png')
    print('PNG format:', im2.format, 'size:', im2.size)
except Exception as e:
    print('PNG error:', e)
