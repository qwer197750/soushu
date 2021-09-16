import random
import traceback
import time
import threading
import requests
import selenium
import re
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from identify_verification_code import identify
from load import config


# 加载配置信息
string = config['string']
emails = config['emails']
password = config['password']
code_img_path = config['code_img_path']
object_url = config['object_url']
proxy_source_url = config['proxy_source_url']
drive_path = config['drive_path']
thread_num = config['thread_num']
xpaths = config['xpaths']

object_url = 'https://jiuquanshimei.soushu2025.com/member.php?mod=zc'


# 部署服务器
is_linux = re.match('.*linux.*', sys.platform) is not None
print(is_linux)


# 获取所有代理IP
def get_proxy():
    return requests.get(proxy_source_url+'/all').json()


# 仅获取Https代理IP
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


# 初始化浏览器
# drive_path: 谷歌浏览器对应版本驱动，Proxy代理
def init_browser(drive_path, proxy=None):
    options = Options()
    options.add_argument('--headless')
    if is_linux:
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
    if proxy is not None:
        options.add_argument('--proxy-server={:}'.format(proxy['ip']))
    options.page_load_strategy = 'eager'
    browser = webdriver.Chrome(executable_path=drive_path, options=options) if not is_linux else \
        webdriver.Chrome(options=options)
    browser.implicitly_wait(5)
    browser.set_page_load_timeout(15)
    browser.set_script_timeout(15)
    return browser


# 开始随机注册
# browser：初始后的浏览器对象
# url：目标网址
# print：替换的打印函数，用于控制多线程下，打印乱序问题
# id：多线程ID
def register(browser, url, print=None, id=''):
    try:
        # browser.set_window_size(1200, 800)
        for i in range(1000):
            try:
                browser.get(url)
                time.sleep(1.5)
                code_img = browser.find_element_by_xpath(xpaths['验证码图片'])
                code_img.screenshot('img/code_{:}.png'.format(''.join([random.choice(string) for i in range(5)])))
                print(1)
            except selenium.common.exceptions.NoSuchElementException as ex:
                print('通过xpath定位时，{:}元素未找到'.format(xpaths.current_key))

    except Exception:
        print(traceback.format_exc())


def proxy_test(proxys, test_url):
    rp = []
    requests.packages.urllib3.disable_warnings()
    print('代理IP测试中')
    for proxy in proxys:
        try:
            print('测试：{:}'.format(proxy))
            requests.get(test_url, proxies=proxy, timeout=5, verify=False)
            rp.append(proxy)
            print('测试通过')
        except requests.exceptions.ConnectTimeout:
            print('连接超时，测试不通过')
        except requests.exceptions.ReadTimeout:
            print('连接超时，测试不通过')
        except requests.exceptions.ProxyError:
            print('代理错误，测试不通过')
        except Exception as ex:
            traceback.print_exc()
            print('测试不通过')

    print('经过测试，有{:}个IP可用'.format(len(rp)))
    return rp


class ProxyThread(threading.Thread):
    # 线程列表，用于控制多线程，粗略版
    thread_pool = []
    # 判断是否需要停止所有线程
    stop_all = False
    # 锁，用于控制访问本类下所有的类变量
    lock = threading.Lock()

    # 初始化
    def __init__(self, id, proxy):
        threading.Thread.__init__(self)
        # run函数打印的信息转存到此，以防止多线程乱序输出
        self.s = []
        self.id = id
        self.proxy = proxy

    # 判断线程池是否运行完毕
    @classmethod
    def is_pool_null(cls):
        return len(cls.thread_pool) == 0

    # 阻塞主线程，直到当前类线程池中所有线程执行完毕
    # 仅限在主线程调用，子线程中调用将造成死循环
    @classmethod
    def join(cls):
        while len(cls.thread_pool) > 0:
            time.sleep(0.1)
        try:
            # 清理所有的浏览器进程，以防止残留浏览器进程占用大量内存
            browser = init_browser(drive_path=drive_path, proxy=None)
            browser.quit()
        except:
            pass

    # 内部方法，新运行一个线程
    @classmethod
    def __add_thread__(cls, td):
        cls.lock.acquire()
        if cls.stop_all:
            exit()
        cls.thread_pool.append(td)
        cls.lock.release()

    # 内部方法，移除一个线程
    @classmethod
    def __remove_thread__(cls, td):
        cls.lock.acquire()
        try:
            cls.thread_pool.remove(td)
        except:
            pass
        cls.lock.release()

    # 线程主函数
    def run(self):
        print('thread_{:}：启动'.format(self.id))
        ProxyThread.__add_thread__(self)
        max_it = 5
        i = 0
        rs = 0
        browser = None
        # 如果返回0，说明需要重新迭代，那么重新启动，直到最大迭代次数
        while rs == 0 and i < max_it:
            if i > 0:
                print('thread_{:}：重新启动中'.format(self.id))
            i += 1
            try:
                browser = init_browser(drive_path=drive_path, proxy=self.proxy)
                rs = register(browser, object_url, print=self.xprint, id=self.id)
            except Exception as ex:
                print('thread_{:}：出现异常：{:}'.format(self.id, str(ex)))
            finally:
                browser.close()
            for s in self.s:
                print('thread_{:}：{:}'.format(self.id, s))
            self.s.clear()
        ProxyThread.__remove_thread__(self)
        print('thread_{:}：结束'.format(self.id))
        if rs == -1:
            exit()

    # 注入的打印函数，用于替换原先的打印函数，截取打印内容，以便在线程运行结束后统一打印
    def xprint(self, s):
        self.s.append(s)


def main():
    code = 0
    for i in range(0):
        browser = init_browser(drive_path, None)
        code = register(browser, url=object_url, print=print)
        browser.close()
    if code == -1:
        exit()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    proxys = get_https_proxy()
    # proxys = proxy_test(proxys, object_url)
    i = 1
    # proxys = [None, None, None, None, None, None, None]
    print('多线程启动中')
    for proxy in proxys:
        while len(ProxyThread.thread_pool) >= thread_num:
            time.sleep(0.1)
        thread = ProxyThread(id=i, proxy=proxy)
        i += 1
        thread.start()
    ProxyThread.join()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    print('all end')


if __name__ == '__main__':
    main()


