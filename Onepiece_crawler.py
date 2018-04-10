# -*- coding:utf-8 -*-

import re
import queue
import random
import requests

from time import sleep
from threading import Thread
from bs4 import BeautifulSoup


class OnePiece(object):
    def __init__(self):
        self.url = 'http://op.hanhande.com/shtml/op_wz/list_2602_{}.shtml'
        self.q = queue.Queue()
        self.picture_link = []

    def html_parse(self, num):
        try:
            url_make = self.url.format(num)
            html = requests.get(url_make, timeout=10)
            soup = BeautifulSoup(html.content, 'lxml')
            ul_tag = soup.find_all('ul', class_='spic pic1')
            soup1 = BeautifulSoup(str(ul_tag[0]), 'lxml')

            for counter, li_tag in enumerate(soup1.find_all('li')):
                soup2 = BeautifulSoup(str(li_tag), 'lxml')
                a_tag = soup2.find_all('a')
                href_list = re.findall(re.compile('href="(.+?)"'), str(a_tag))
                if len(href_list) != 0:
                    print('第 ' + str(num) + ' 页: ----第 ' + str(counter + 1)
                          + '个链接：' + href_list[0] + ' ----')
                    self.q.put(href_list[0])
            sleep(random.randint(2, 3))
        except requests.ConnectionError:
            pass

    def picture_parse(self):
            try:
                sub_url = self.q.get()
                sub_url_base = sub_url[:-6]
                for page in range(1, 10):
                    sub_url_new = sub_url_base + '_' + str(page) + '.shtml'

                    html2 = requests.get(sub_url_new)
                    if html2.status_code == 200:
                        soup = BeautifulSoup(html2.content, 'lxml')
                        div_tag = soup.find_all('div', id='pictureContent')
                        soup1 = BeautifulSoup(str(div_tag[0]), 'lxml')

                        for img_tag in soup1.find_all('img', src=re.compile('.+?')):
                            soup3 = BeautifulSoup(str(img_tag), 'lxml')
                            if soup3.img['src'] is not None:
                                self.picture_link.append(soup3.img['src'])
                                print(str('----' + soup3.img['alt']) + '链接 : '
                                      + str(soup3.img['src']) + ' ----')
                        sleep(random.randint(2, 3))
                    else:
                        pass
            except requests.ConnectionError:
                pass

    def picture_store(self):
        try:
            for num, link in enumerate(set(self.picture_link)):
                html3 = requests.get(link)
                picture_path = 'D:\Pictures_Downloaded\\' + 'pic' + str(num+1) + '.jpg'
                with open(picture_path, 'wb') as f:
                    f.write(html3.content)
        except requests.ConnectionError:
            pass

    def main(self):
        page_num = 2
        threads_0 = []
        for i in range(1, page_num):
            t = Thread(target=self.html_parse, args=(i,), name='Thread-0')
            threads_0.append(t)
        for i in range(len(threads_0)):
            threads_0[i].start()
        for i in range(len(threads_0)):
            threads_0[i].join()

        threads_1 = []
        for i in range(self.q.qsize()):
            t1 = Thread(target=self.picture_parse, args=(), name='Thread-1')
            threads_1.append(t1)
        for i in range(len(threads_1)):
            threads_1[i].start()
        for i in range(len(threads_1)):
            threads_1[i].join()

        self.picture_store()


if __name__ == '__main__':
    spider = OnePiece()
    spider.main()
