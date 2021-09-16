import json
import codecs


class DoubleDict(dict):
    def __init__(self, **kwargs):
        super(DoubleDict, self).__init__(**kwargs)
        self.current_key = None

    def __getitem__(self, y):
        self.current_key = y
        return super(DoubleDict, self).__getitem__(y)


string = 'abcdefghigklmnopqrstuvwzyzABCDEFGHIJKLMNOPQRSTUVWZXY1234567890'
emails = ['@qq.com', '@163.com', '@outlook.com', '@gmail.com']
password = 1234
code_img_path = 'img/'
object_url = 'https://lovecar.fullofhouse.com/forum.php?fromuid=1106246'
proxy_source_url = r'http://www.guopersonal.cn:19775/'
drive_path = 'D:/ProgramFiles/Driver_Notes/MicrosoftWebDriver.exe'
thread_num = 8
xpaths = {'跳转注册': r'/html/body/div[5]/div/div[1]/form/div/div/table/tbody/tr[2]/td[4]/a',
          '同意按钮': r'/html/body/div[1]/div/table/tbody/tr[2]/td[2]/p/button[1]',
          '用户名输入框': r'/html/body/div[6]/div/div[2]/div[1]/form/div[1]/div/div/div[1]/table/tbody/tr/td[1]/input',
          '密码输入框': r'/html/body/div[6]/div/div[2]/div[1]/form/div[1]/div/div/div[2]/table/tbody/tr/td[1]/input',
          '确认密码输入框': r'/html/body/div[6]/div/div[2]/div[1]/form/div[1]/div/div/div[3]/table/tbody/tr/td[1]/input',
          '邮箱输入框': r'/html/body/div[6]/div/div[2]/div[1]/form/div[1]/div/div/div[4]/table/tbody/tr/td[1]/input',
          '验证码输入框': r"//table/tbody/tr/td/input[contains(@name, 'seccodeverify')]",
          '验证码图片': r'/html/body/div[6]/div/div[2]/div[1]/form/div[1]/div/div/span/div/table/tbody/tr/td/span[2]/img',
          '注册按钮': r'/html/body/div[6]/div/div[2]/div[1]/form/div[2]/div/table/tbody/tr/td[1]/span/button',
          '注册提示信息': '/html/body/div[1]/div[2]/table/tbody/tr/td[2]/div/i'
          }


config = {
    'string': string, 'emails': emails, 'password': password, 'code_img_path': code_img_path,
    'object_url': object_url, 'proxy_source_url': proxy_source_url, 'drive_path': drive_path, 'thread_num': thread_num,
    'xpaths': xpaths
}


def save_json():
    json_path = 'config.json'
    with codecs.open(json_path, mode='w', encoding='utf-8') as f:
        s = json.dumps(config, sort_keys=True, indent=4, ensure_ascii=False)
        f.write(s)


def load_json():
    json_path = 'config.json'
    with codecs.open(json_path, mode='r', encoding='utf-8') as f:
        s = json.load(f)
        for k in config.keys():
            if k not in s.keys():
                print('加载配置文件失败，{:}项不存在'.format(k))
                exit(-1)
            if k == 'xpaths':
                d = DoubleDict()
                d.update(s[k])
                s[k] = d
            config[k] = s[k]
        print('加载配置文件成功')
# save_json()
load_json()