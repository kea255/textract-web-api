# textract-web-api
Сервис получения текста из различных форматов стандартных офисных файлов: .doc, .docx, .rtf, .pdf, .xlsx, .tif, .jpg, .png
на основе библиотеки https://textract.readthedocs.io/en/stable/

### Установка
```bash
docker build -t textract-web-api .
docker run --name "textract-web-api" -d -p 8012:8000 textract-web-api
```

### Пример использования
```bash
curl --form file='@1.pdf' http://192.168.0.109:8012/convert
```