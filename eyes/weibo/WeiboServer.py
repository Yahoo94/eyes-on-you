# @Time : 2024/11/25 20:40
# @Author : YaHoo94
import os.path
import re
import time
import requests
from config import get_config
from eyes.Server import Server
from notice.email.EmailServer import send_email
from typing import List


class WeiboServer(Server):

    def __init__(self):
        super().__init__()
        config = get_config()
        self.server_name = 'weibo_server'
        self.weibo_url_prefix = config.get('weibo_url_prefix')
        self.weibo_targets = config.get('weibo_targets')

        if config.get('weibo_save') is not None:
            self.save = config.get('weibo_save')
        if config.get('weibo_interval') is not None:
            self.interval = config.get('weibo_interval')

    def start(self):
        for target in self.weibo_targets:
            weibo_url = self.weibo_url_prefix + target
            response_for_containerid = requests.get(weibo_url)
            json = response_for_containerid.json()
            tabs = json.get('data').get('tabsInfo').get('tabs')
            containerid = None
            for i in tabs:
                if i['title'] == '微博':
                    containerid = i['containerid']
                    break
            if not containerid:
                self.logger.error('未找到微博containerid')
                raise Exception('未找到微博containerid')
            weibo_url += '&containerid=' + containerid;
            newres = requests.get(weibo_url)
            cards = newres.json().get('data').get('cards')
            self.check(cards)

    # 检查拿到的动态是否是新发的
    def check(self, contents: dict,**kwargs):
        now = time.time()
        for card in contents:
            mblog = card.get('mblog')
            target_name = mblog.get('user').get('screen_name')
            created_at_int = time.mktime(time.strptime(mblog.get('created_at'), '%a %b %d %H:%M:%S %z %Y')) # 时间戳
            if now - (self.interval * 60 * 1000) < created_at_int:
                self.logger.info(f'WeiboServer找到一条新微博！来自 {target_name} !')
                # 提前获取保存路径 为转发微博（sub_mblog）准备
                config = get_config()
                save_path = config.get('save_path')  # "save_path": "./result/"
                save_path += 'weibo/'  # "save_path": "./result/weibo/"
                created_at_str = str(mblog.get('created_at'))  # "Sun Nov 24 20:09:10 +0800 2024"
                post_id = mblog.get('id')
                save_path += target_name + '/' + '-'.join(created_at_str.split(' ')[:3]) + '/' + post_id + '/'  # "./result/weibo/{target_name}/{created_at}{post_id}/"
                medias = self.get_medias(mblog)
                notice_title, notice_content = self.create_notice(mblog,is_sub=False,save_path=save_path,medias=medias)

                # 若是转发的微博，则会有新的一个卡片需要解析
                sub_mblog = mblog.get('retweeted_status')
                sub_medias={'pics':set(),'videos':set()}
                if sub_mblog is not None:
                    sub_medias=self.get_medias(sub_mblog)
                    _, sub_content = self.create_notice(sub_mblog, is_sub=True, save_path=save_path,medias=sub_medias)
                    notice_content += """
                            <p> -------------------以下是转发的微博原文--------------</p><br>
                            """ + sub_content

                # send_email(notice_title, notice_content)
                if self.save:
                    mblog['text']=notice_content
                    union_medias={}
                    union_medias['pics']=medias.get('pics').union(sub_medias.get('pics'))
                    union_medias['videos']=medias.get('videos').union(sub_medias.get('videos'))
                    self.save_local(mblog,save_path=save_path,medias=union_medias)
                self.logger.info('保存完成！')

    def create_notice(self, mblog: dict,**kwargs):
        self.logger.info('WeiboServer:create_notice开始创建微博内容！')
        target_name = mblog.get('user').get('screen_name')
        text = mblog.get('text')
        # 发布于xx
        region_name = mblog.get('region_name')
        if region_name is None:
            region_name = '发布于 微博'
        notice_title = f'您关注的用户{target_name},在 {region_name.split(" ")[1]} 发布了新内容！'
        # 所有图片
        is_sub = kwargs.get('is_sub')
        if not is_sub:
            notice_content = """
        <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Eyes On You</title>
                </head>
            <body>
                <h1>我会一直盯着你！</h1>
        """
        else:
            notice_content = ''
        notice_content += f"""
                <p> {target_name} 微博内容:<br>{text}</p><br>
        """
        medias = kwargs.get('medias')
        pic_urls = medias.get('pics')
        if pic_urls and len(pic_urls) > 0:
            notice_content += f"""
            <p> {target_name} 微博图片:<br>
            """
            for pic_url in pic_urls:
                pic_html = f"""<img src={pic_url} /> <br>"""
                notice_content += pic_html
        video_urls = medias.get('videos')
        if video_urls and len(video_urls) > 0:
            notice_content += f"""
                        <p> {target_name} 微博视频:<br>
                        """
            for video_url in video_urls:
                video_html = f"""
                            <video width="640" height="360" controls>
                                <source src="{video_url}" type="video/mp4">
                            </video> <br>
                            """
                notice_content += video_html

        if not is_sub:
            notice_content+="""</body></html>"""
        return notice_title, notice_content

    def save_local(self, mblog: dict,**kwargs):
        self.logger.info('WeiboServer开始保存！')
        save_path=kwargs.get('save_path')
        # 获取文本内容，此处的文本是html
        text = str(mblog.get('text'))
        # 创建保存目录
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        headers = {
            'referer': 'https://mail.qq.com/'
        }
        medias = kwargs.get('medias')
        pic_urls = medias.get('pics')
        if pic_urls and len(pic_urls) > 0:
            self.logger.info('开始保存图片')
            for pic_url in pic_urls:
                pic_name = pic_url.split('/')[-1]
                res = requests.get(pic_url, headers=headers)
                with open(save_path + pic_name, 'wb') as f:
                    f.write(res.content)
                # 如果保存了图，就替换html内容，读取图片
                pattern = rf'("http.*/{pic_name}.*")'
                text=re.sub(pattern,'./' + pic_name,text)

        video_urls = medias.get('videos')
        if video_urls:
            self.logger.info('开始保存视频')
            for video_url in video_urls:
                if str(video_url).endswith('mov'):
                    video_name = video_url.split('%')[-1]
                else:
                    video_name = video_url.split('?')[0].split('/')[-1]
                with open(save_path + video_name, 'wb') as f:
                    res = requests.get(video_url)
                    for chunk in res.iter_content(chunk_size=1024):
                        f.write(chunk)
                    # 如果保存了图，就替换html内容，读取图片
                    pattern = rf'("http.*/{video_name}.*")'
                    text = re.sub(pattern, './' + video_name, text)

        # 替换完成后保存为html文件

        with open(save_path + f'/weibo.html', 'wb') as f:
            self.logger.info('开始保存html格式的微博内容')
            f.write(text.encode())

    def get_medias(self, mblog: dict) -> dict:
        pic_num = mblog.get('pic_num')
        if pic_num is None:
            pic_num=-1
        pic_urls = set()
        videos_urls = set()
        pics = mblog.get('pics')
        if pic_num > 0:
            for pic in pics:
                type = pic.get('type')
                if not type:
                    large_pic = pic.get('large')
                    if large_pic is not None:
                        pic_url=large_pic.get('url')
                    else:
                        pic_url = pic.get('url')
                    pic_urls.add(pic_url)
                elif type=='video':
                    stream_url=pic.get('videoSrc')
                    videos_urls.add(stream_url)
                elif type=='livephoto':
                    stream_url = pic.get('videoSrc')
                    videos_urls.add(stream_url)
        elif pic_num == 0:
            page_info = mblog.get('page_info')
            if page_info:
                type = page_info.get('type')
                if type and "video" == type:
                    media_info = page_info.get('media_info')
                    stream_url_hd = media_info.get('stream_url_hd')
                    stream_url = stream_url_hd or media_info.get('stream_url')
                    videos_urls.add(stream_url)
        medias={"pics":pic_urls,"videos":videos_urls}
        return medias