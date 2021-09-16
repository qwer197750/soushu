import random
import traceback
import time
import threading
import requests
import selenium
from PIL import Image
from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from googlenet.identify_verification_code import identify
from load import config
string = config['string']
emails = config['emails']
password = config['password']
code_img_path = config['code_img_path']
object_url = config['object_url']
proxy_source_url = config['proxy_source_url']
drive_path = config['drive_path']
thread_num = config['thread_num']
xpaths = config['xpaths']


def get_proxy():
    return requests.get(proxy_source_url+'/all').json()


def get_https_proxy():
    print('获取代理IP中')
    ps = get_proxy()
    https_proxy = []
    for p in ps:
        https = p['https']
        if https is not None and https is True:
            https_proxy.append({'http': 'http://'+p['proxy'],
                                'https': 'https://'+p['proxy'],
                                'ip': p['proxy']
                                })
    print('获取代理IP完毕，共{:}个IP'.format(len(https_proxy)))
    return https_proxy


def register(url, drive_path, proxy=None, print=None, id=''):
    options = EdgeOptions()
    options.use_chromium = True
    options.add_argument('headless')
    if proxy is not None:
        options.add_argument('proxy-server={:}'.format(proxy['ip']))
    options.page_load_strategy ='none'
    browser = Edge(executable_path=drive_path, options=options)
    try:
        # browser.set_window_size(1200, 800)
        browser.get(url)
        try:
            go_register = browser.find_element_by_xpath(xpaths['跳转注册'])
            browser.get(go_register.get_attribute('href'))
            agree_btn = browser.find_element_by_xpath(xpaths['同意按钮'])
            agree_btn.click()
            name_input = browser.find_element_by_xpath(xpaths['用户名输入框'])
            password_input = browser.find_element_by_xpath(xpaths['密码输入框'])
            re_password_input = browser.find_element_by_xpath(xpaths['确认密码输入框'])
            email_input = browser.find_element_by_xpath(xpaths['邮箱输入框'])
            time.sleep(1)
            code_input = browser.find_element_by_xpath(xpaths['验证码输入框'])
            code_img = browser.find_element_by_xpath(xpaths['验证码图片'])
            register_btn = browser.find_element_by_xpath(xpaths['注册按钮'])
        except selenium.common.exceptions.NoSuchElementException as ex:
            print('通过xpath定位时，{:}元素未找到'.format(xpaths.current_key))
            return -1

        name = ''.join([random.choice(string) for i in range(8)])
        email = ''.join([random.choice(string) for i in range(5)]) + random.choice(emails)
        name_input.send_keys(name)
        password_input.send_keys(password)
        re_password_input.send_keys(password)
        email_input.send_keys(email)


        # browser.get_screenshot_as_file(code_img_path + 's.png')
        # left = int(code_img.location['x'])
        # top = int(code_img.location['y'])
        # right = int(code_img.location['x'] + code_img.size['width'])
        # bottom = int(code_img.location['y'] + code_img.size['height'])

        # # 通过Image处理图像
        # im = Image.open(code_img_path + 's.png')
        # im = im.crop((left, top, right, bottom))
        # im.save(code_img_path + 'code.png')


        code_img.screenshot(code_img_path + 'code{:}.png'.format(id))

        code = identify(code_img_path + 'code{:}.png'.format(id))
        print(code)
        code_input.send_keys(code)
        register_btn.click()
        register_info = None
        for i in range(6):
            try:
                register_info = browser.find_element_by_xpath(xpaths['注册提示信息'])
                break
            except selenium.common.exceptions.NoSuchElementException as ex:
                register_info = None
            time.sleep(0.5)
        if register_info is None:
            print('通过xpath定位时，{:}元素未找到'.format(xpaths.current_key))
            return -1
        print(register_info.get_attribute('innerHTML'))
        print('注册完成')

    except:
        print(traceback.format_exc())
        browser.close()
        return -1
    browser.close()
    return 0


def proxy_test(proxys, test_url):
    rp = []
    print('代理IP测试中')
    for proxy in proxys:
        try:
            print('测试：{:}'.format(proxy))
            requests.get(test_url, proxies=proxy, timeout=5)
            rp.append(proxy)
            print('测试通过')
        except requests.exceptions.ConnectTimeout or requests.exceptions.ReadTimeout:
            print('连接超时，测试不通过')
            # a = requests.get(proxy_source_url+'/delete?proxy=host:{:}'.format(proxy['ip']))
        except requests.exceptions.ProxyError:
            print('代理错误，测试不通过')
        except Exception as ex:
            traceback.print_exc()
            print('测试不通过')

    print('经过测试，有{:}个IP可用'.format(len(rp)))
    return rp


class ProxyThread(threading.Thread):
    thread_pool = []
    lock = threading.Lock()

    def __init__(self, id, proxy):
        threading.Thread.__init__(self)
        self.s = []
        self.id = id
        self.proxy = proxy

    @classmethod
    def is_pool_null(cls):
        return len(cls.thread_pool) == 0

    @classmethod
    def join(cls):
        while len(cls.thread_pool) > 0:
            time.sleep(0.1)


    @classmethod
    def __add_thread__(cls, td):
        cls.lock.acquire()
        cls.thread_pool.append(td)
        cls.lock.release()

    @classmethod
    def __remove_thread__(cls, td):
        cls.lock.acquire()
        try:
            cls.thread_pool.remove(td)
        except:
            pass
        cls.lock.release()

    def run(self):
        print('thread_{:}：启动'.format(self.id))
        ProxyThread.__add_thread__(self)
        try:
            register(object_url, drive_path, self.proxy, print=self.xprint, id=self.id)
        except Exception as ex:
            print('thread_{:}出现异常：{:}'.format(self.id, str(ex)))
        for s in self.s:
            print('thread_{:}：{:}'.format(self.id, s))
        ProxyThread.__remove_thread__(self)
        print('thread_{:}：结束'.format(self.id))

    def xprint(self, s):
        self.s.append(s)


if __name__ == '__main__':
    # register(url=object_url, drive_path=drive_path, proxy=None, print=print)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    proxys = get_https_proxy()
    rp = proxy_test(proxys, object_url)
    i = 1
    print('多线程启动中')
    for proxy in rp:
        while len(ProxyThread.thread_pool) >= thread_num:
            time.sleep(0.1)
        thread = ProxyThread(id=i, proxy=proxy)
        i += 1
        thread.start()
    ProxyThread.join()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


