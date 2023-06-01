# encoding=utf-8
import io
import json
import uvicorn
import ddddocr
import requests
from PIL import Image
from base64 import b64decode
from fastapi import FastAPI, File, UploadFile, Body
from fastapi.responses import HTMLResponse, FileResponse


class Ocr():
    ocr = ddddocr.DdddOcr(show_ad=False)
    det = ddddocr.DdddOcr(det=True, show_ad=False)
    slide = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)

    @staticmethod
    def code_image(img: bytes, comp):
        retry = 1
        while retry < 5:
            result = Ocr.ocr.classification(img)
            if comp == 'digit':
                if result.isdigit():
                    break
            elif comp == 'alpha':
                if result.isalpha():
                    break
            elif comp == 'alnum':
                if result.isalnum():
                    break
            else:
                break
            retry += 1
        return result

    @staticmethod
    def det_image(img: bytes):
        return Ocr.det.detection(img)

    @staticmethod
    def slide_image(target_img: bytes, background_img: bytes):
        try:
            imageStream = io.BytesIO(target_img)
            imageFile = Image.open(imageStream)
            background_img = imageFile.crop((0, 300, 240, 450))  # (x1, y1, x2, y2)
            cropped = imageFile.crop((0, 0, 240, 150))  # (x1, y1, x2, y2)
            return Ocr.slide.slide_comparison(ca(cropped), ca(background_img))
        except Exception as e:
            return Ocr.slide.slide_match(target_img, background_img)


def ocr_img(ocr_type, img_bytes, background_img_bytes, comp='alnum'):
    if ocr_type == 1:
        return Ocr.code_image(img_bytes, comp)
    elif ocr_type == 2:
        return Ocr.det_image(img_bytes)
    elif ocr_type == 3:
        return Ocr.slide_image(img_bytes, background_img_bytes)
    else:
        return None


def ca(img):
    img_byte_array = io.BytesIO()
    img.save(img_byte_array, format='PNG', subsampling=0, quality=100)
    img_byte_array = img_byte_array.getvalue()
    return img_byte_array


app = FastAPI()


# 提供 index.html 文件
@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("templates/index.html")


# 设置网页图标
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("templates/favicon.ico")


@app.post("/")
async def process(data: dict = Body(...)):
    # 获取验证码及所需headers
    if 'header' in data:
        header = data['header']
    else:
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'
        }
    if 'url' in data:
        # 为url则下载并获取cookies
        cookies = {}
        url = data['url']
        try:
            r = requests.get(url, headers=header, timeout=30)
            for key, value in r.cookies.items():
                cookies.update({key: value})
            imgdata = r.content
        except:
            return {'code': 0, 'result': None, 'msg': '访问{}超时'.format(url)}
    elif 'imgdata' in data:
        # 为imgdata则base64解码
        imgdata = data['imgdata']
        if imgdata.startswith('data'):
            imgdata = imgdata.split(',', 1)[1]
        imgdata = b64decode(imgdata)
    else:
        # 错误
        return {'code': 0, 'result': None, 'msg': '没有图片'}
    # 获取ocr_type。1：ocr，2：点选，3：滑块。
    if 'ocr_type' in data:
        ocr_type = data['ocr_type']
    else:
        ocr_type = 1
    # 获取comp参数
    if 'comp' in data:
        comp = data['comp']
        if comp not in ['digit', 'alpha', 'alnum']:
            comp = 'alnum'
    else:
        comp = 'alnum'
    try:
        background_imgdata = bytes()
        result = ocr_img(ocr_type, imgdata, background_imgdata, comp)
        if not 'url' in data or cookies == {}:
            return {'code': 1, 'result': result, 'msg': 'success'}
        else:
            return {'code': 1, 'cookies': cookies, 'result': result, 'msg': 'success'}
    except Exception as e:
        return {'code': 0, 'result': None, 'msg': str(e).strip()}


if __name__ == '__main__':
    uvicorn.run(app='main:app', host="0.0.0.0", port=9898, reload=False)