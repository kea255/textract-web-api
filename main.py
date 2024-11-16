import os
import secrets
import tempfile
from datetime import datetime as dt

import textract
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from pydantic import BaseModel

# Placeholder for the version - to be updated with the CI process
__version__ = '0.0.2'


class ConvertResult(BaseModel):
    result: str
    text: str
    text_length: int
    file_name: str
    messages: str


app = FastAPI()
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

    attempts = 1
    while attempts >= 0:
        try:
            _text = textract.process(_tmp_file_name,language='rus').decode(encoding)
            if len(_text.strip())<10:
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
