# @Time : 2024/11/25 20:45
# @Author : YaHoo94
import json
import os
import logging

available_setting = {
    # email配置
    "email_address": "",
    "email_smtp_secret": "",
    "smtp_server": "",
    "smtp_port": None,
    "email_receiver": [],

    # 通用配置
    "common_interval": 5,
    "common_save": False,

    # 可选微博设置
    # 视奸目标们
    "weibo_targets": [""],
    # 视奸间隔（单位分钟）
    "weibo_interval": 5,
    # 是否保存至本地
    "weibo_save": False
}
default_setting = {
    # 默认微博设置
    "weibo_url_prefix": "https://m.weibo.cn/api/container/getIndex?type=uid&value=",
    # 默认保存路径
    "save_path": "./result/"
}


class Config(dict):
    def __init__(self, available_setting=None):
        super().__init__()
        if available_setting is None:
            available_setting = {}
        for k, v in available_setting.items():
            self[k] = v
        for k, v in default_setting.items():
            self[k] = v

    def __getitem__(self, key):
        if key not in available_setting and key not in default_setting:
            raise Exception("不存在的设置项：{}".format(key))
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if key not in available_setting and key not in default_setting:
            raise Exception("禁止的设置项：{}".format(key))
        return super().__setitem__(key, value)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError as e:
            return default
        except Exception as e:
            raise e


def load_config():
    global logger
    log_path = './logs/eyes-on-you.log'
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    df = logging.Formatter(fmt='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                           datefmt='%Y-%m-%d %H:%M:%S')
    fh = logging.FileHandler(log_path, mode='a', encoding='utf-8', )
    fh.setFormatter(df)
    sh = logging.StreamHandler()
    logger = logging.getLogger()
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.setLevel(logging.INFO)
    logger.info('开始初始化，加载配置load_config...')

    global config
    config_path = "./config.json"
    if not os.path.exists(config_path):
        logger.info('未找到config.json，使用config-template.json作为配置文件')
        config_path = "./config-template.json"
    else:
        logger.info('使用config.json作为配置文件')
    with open(config_path, mode="r", encoding="utf-8") as f:

        config = Config(json.loads(f.read()))


def get_config():
    return config


def get_logger():
    return logger
