# textract-web-api
Сервис получения текста из различных форматов стандартных офисных файлов: .doc, .docx, .rtf, .pdf, .xlsx, .tif, .jpg, .png
на основе библиотеки https://textract.readthedocs.io/en/stable/

### Установка
```bash
docker build -t textract-web-api .
docker run --name "textract-web-api" -d -p 8012:8000 textract-web-api
```
или
```bash
docker run --name "textract-web-api" -d -p 8012:8000 kea255/textract-web-api
```

### Пример использования bash
```bash
curl --form file='@1.pdf' http://192.168.0.109:8012/convert
```

### Пример использования php
```php
$url = "http://192.168.0.109:8012/convert";
$file = __DIR__.'/1.pdf'; 

$ch = curl_init($url);
curl_setopt_array($ch, [
	CURLOPT_RETURNTRANSFER => 1,
	CURLOPT_FOLLOWLOCATION => true,
	CURLOPT_SSL_VERIFYPEER => 0,
	CURLOPT_POST => true,
	CURLOPT_POSTFIELDS => ['file' => new CURLFile($file)]
]);
$out = curl_exec($ch);
$info = curl_getinfo($ch);
curl_close($ch);
if($info['http_code']==200){
	print_r(json_decode($out,true));
}
```