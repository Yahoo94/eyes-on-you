# @Time : 2024/11/26 20:41
# @Author : YaHoo94

from config import get_config, get_logger
from threading import Timer


class Server():

    def __init__(self):
        config = get_config()
        self.server_name = 'base_server'
        self.save = config.get('common_save')
        self.interval = config.get('common_interval')
        self.logger = get_logger()

    def _start_timer_(self):
        try:
            Timer(self.interval * 60, self._start_loop_).start()
        except Exception as e:
            self.logger.error(e)
            self._start_loop_()

    def _start_loop_(self):
        self.start()
        self.logger.info(f'{self.server_name}:本次查看结束！')
        self._start_timer_()

    def start(self):
        self.check(None)

    def check(self, contents,**kwargs):
        # notice_title, notice_content=self.create_notice(args)
        # send_email(notice_title, notice_content)
        # self.save(args)
        pass

    def create_notice(self, content,**kwargs):
        return 'eyes on you title', 'eyes on you content'

    def save_local(self, content,**kwargs):
        pass
