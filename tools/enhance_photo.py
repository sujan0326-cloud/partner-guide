# 저화질 사진 2배 업스케일(EDSR) + 선명도 보정. 사용: python tools/enhance_photo.py 원본.png images/결과.jpg [원본2 결과2 ...]
# 필요: pip install "opencv-contrib-python-headless<5" / 모델: github.com/Saafke/EDSR_Tensorflow 의 models/EDSR_x2.pb (경로는 EDSR_MODEL 환경변수, 기본 /tmp/edsr/models/EDSR_x2.pb). CPU에서 사진 1장 약 2~3분.
import os, sys, cv2, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(os.getenv('EDSR_MODEL', '/tmp/edsr/models/EDSR_x2.pb')); sr.setModel('edsr', 2)
for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
    im = cv2.cvtColor(np.array(Image.open(src).convert('RGB')), cv2.COLOR_RGB2BGR)
    up = sr.upsample(im)
    p = Image.fromarray(cv2.cvtColor(up, cv2.COLOR_BGR2RGB))
    p = p.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    p = ImageEnhance.Contrast(p).enhance(1.04); p = ImageEnhance.Color(p).enhance(1.04)
    p.save(dst, quality=88, optimize=True); print(dst, im.shape[1::-1], '->', p.size)
