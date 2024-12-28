import os
import secrets
import tempfile
from datetime import datetime as dt
from PIL import Image
from pillow_heif import register_heif_opener

import textract
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Placeholder for the version - to be updated with the CI process
__version__ = '0.0.6'


class ConvertResult(BaseModel):
    result: str
    text: str
    text_length: int
    file_name: str
    messages: str

def cyrillic_percentage_broad(text):
    cyrillic_count = 0
    total_characters = len(text)
    if total_characters == 0:
        return 0.0
    for char in text:
        if '\u0400' <= char <= '\u04FF' or '\u0500' <= char <= '\u052F': # Unicode ranges for Cyrillic
            cyrillic_count += 1
    return (cyrillic_count / total_characters) * 100

def fix_image_orientation(image_path):
    image = Image.open(image_path)
    try:
        exif = image._getexif()
        orientation = exif.get(0x0112)  # Получаем тег ориентации
        if orientation == 2:
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            image = image.rotate(180, expand=True)
        elif orientation == 4:
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
        elif orientation == 5:
            image = image.transpose(Image.FLIP_LEFT_RIGHT).rotate(270, expand=True)
        elif orientation == 6:
            image = image.rotate(270, expand=True)
        elif orientation == 7:
            image = image.transpose(Image.FLIP_TOP_BOTTOM).rotate(270)
        elif orientation == 8:
            image = image.rotate(90, expand=True)
        if orientation in [2, 3, 4, 5, 6, 7, 8]:
            image.save(image_path, quality=90)
    except (AttributeError, KeyError, IndexError):
        pass  # Если EXIF-данные отсутствуют, ничего не делаем
    image.close()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
_start_time = dt.now()


@app.get('/')
async def index():
    return {'version': __version__, "start-time": _start_time}


@app.post('/convert', response_model=ConvertResult)
async def convert_file(file: UploadFile = File("file_to_convert"), encoding: str = "utf-8"):
    _text = ""
    _result, _warning_message, _convert_start_time = "success", "", dt.now()

    _, file_extension = os.path.splitext(file.filename)

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as _file:
        _content = await file.read()
        _file.write(_content)
        _tmp_file_name = _file.name

    if file_extension == '.heic':
        register_heif_opener()
        image = Image.open(_tmp_file_name)
        image.save(_tmp_file_name.replace('.heic','.jpg'), format='jpeg')
        os.remove(_tmp_file_name)
        _tmp_file_name = _tmp_file_name.replace('.heic','.jpg')
        
    if file_extension in ['.jpg', '.jpeg']:
        fix_image_orientation(_tmp_file_name)

    attempts = 1
    while attempts >= 0:
        try:
            _text = textract.process(_tmp_file_name,language='rus+eng').decode(encoding)
            if len(_text.strip())<10:
                _text = textract.process(_tmp_file_name,method='tesseract',language='rus+eng').decode(encoding)
            if len(_text.strip())>250 and cyrillic_percentage_broad(_text)<50:
                _text = textract.process(_tmp_file_name,method='tesseract',language='rus').decode(encoding)
            break
        except Exception as e:
            print('Conversion issue:', _tmp_file_name, e)
            _warning_message += f"Conversion issue: {str(e)}\n"
            _result = "warning"

            if "Rich Text" in str(e):
                os.rename(_tmp_file_name, _tmp_file_name + '.rtf')
                _tmp_file_name = _tmp_file_name + '.rtf'
                attempts -= 1
            else:
                _result = "error"
                break

    os.remove(_tmp_file_name)

    return {'result': _result,
            'text': _text,
            'text_length': len(_text.strip()),
            'file_name': file.filename,
            'messages': _warning_message}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
