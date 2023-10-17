# 基于Python-Flask的ddddocr服务
2023年10月17日 更新指定验证码长度 "lenth":4

## 使用方法：

通过 JSON 格式 post 相关参数至服务器进行识别。

|      参数     |     名称      |     备注      |
|--------------|---------------|---------------|
| url          | 验证码图片链接 |url与imgdata必须有一个 |
| header        | 所需headers   | 可为空|
| imgdata      | base64格式图片数据| url与imgdata必须有一个|
|     |     |digit:纯数字 |
| |     |alpha:纯字母 |
|comp  |  验证码组成     |alnum:数字+字母 |
|       |       |all:任意字符串|
|       |       |可为空:默认alnum|
| |       |1:验证码 |
| ocr_type |   模式(可为空，默认1)    |2:点选|
|       |       |3:滑块|
## 返回结果

{

	"code": 1, //状态码：1，正常；0，失败
  
	"result": "9897", //验证码
  
	"cookies": {}, //验证码链接返回的cookies
  
	"msg": "success" //状态：success，成功；failure，失败
  }

  ## 安装方式

git clone https://github.com/qlql765/ocr.git

cd ocr

pip install -r requirements.txt

python3 main.py #前台运行

nohup python3 main.py &   #后台运行

ps aux | grep python   #查看后台运行的python，然后kill命令停止后台运行

## 错误解决

如果出现AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'

那么就卸载pillow的10.0.0版本，然后安装9.5.0版本

pip uninstall -y Pillow

pip install Pillow==9.5.0
