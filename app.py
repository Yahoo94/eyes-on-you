# @Time : 2024/11/25 20:40
# @Author : YaHoo94
from config import load_config, get_logger
from eyes.Server import Server
from notice.email.EmailServer import init_smtp, close_smtp


def init_servers():
    server_classes = Server.__subclasses__()
    for server_class in server_classes:
        logger.info(f'开始初始化{server_class.__name__}')
        server_instance = server_class()
        logger.info(f'开始启动{server_class.__name__}')
        server_instance._start_timer_()


if __name__ == '__main__':
    try:
        load_config()
        logger = get_logger()
        logger.info('配置初始化结束')
        logger.info('开始初始化smtp邮件服务')
        init_smtp()
        logger.info('完成初始化smtp邮件服务')
        logger.info('开始初始化servers服务')
        init_servers()
    except (KeyboardInterrupt, Exception) as e:
        print(e)
        close_smtp()
