# eyes-on-you
## 使用说明
1. 安装python环境（略）
2. pip安装requests库（略）
3. 复制config-temple.json 并修改配置项目
4. python app.py

## 配置项目说明
```yaml
 "email_address": "111@qq.com",  #发送的邮箱的地址
  "email_smtp_secret": "1ads",  #smtp授权码
  "smtp_server": "smtp.qq.com",  #smtp服务器地址
  "smtp_port": 465,  #smtp服务器端口
  "email_receiver": ["asdf@qq.com"],  #接受消息的邮箱列表

  "common_interval":5,  #通用设置 定时间隔  建议大于等于1的整数
  "common_save":false,  #通用配置 是否保存

  "weibo_targets": ["123456789"], #微博配置 查看的目标
  "weibo_interval": 5, #微博配置 查看间隔
  "weibo_save": true  #微博配置 是否保存 微博服务中 weibo_xxx配置优先级高于common_xxx配置

```