import base64
import re

import requests
import requests.packages.urllib3
import rsa
from fake_useragent import UserAgent

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIrn+WB2Yi4ABAL5Tq6E09tumY
qVTFdpU01kCDUmClczJOCGZriLNMrshmN9NJxazpqizPthwS1OIK3HwRLEP9D3GL
7gCnvN6lpIpoVwppWd65f/rK2ewv6dstN0fCmtVj4WsLUchWlgNuVTfWljiBK/Dc
YkfslRZzCq5Fl3ooowIDAQAB
-----END PUBLIC KEY-----"""

requests.packages.urllib3.disable_warnings()


class Action:
    """Gitee Pages Action"""

    timeout = 5

    def __init__(self, username, password, repo,
                 branch='master', directory='', https='true'):
        self.session = requests.session()
        self.ua = UserAgent(verify_ssl=False)
        self.username = username
        self.password = password
        self.repo = repo
        self.branch = branch
        self.directory = directory
        self.https = https

    @staticmethod
    def get_csrf_token(html: str) -> str:
        res = re.search(
            '<meta content="authenticity_token" name="csrf-param" />(.*?)'
            '<meta content="(.*?)" name="csrf-token" />', html, re.S)
        if res is None:
            raise Exception('deploy error occurred, '
                            'please check your input `gitee-repo`')
        return res.group(2)

    def login(self):
        login_index_url = 'https://gitee.com/login'
        check_login_url = 'https://gitee.com/check_user_login'
        form_data = {'user_login': self.username}

        index_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'gitee.com',
            'User-Agent': self.ua.random
        }

        resp = self.session.get(url=login_index_url,
                                headers=index_headers,
                                timeout=Action.timeout,
                                verify=False)
        csrf_token = Action.get_csrf_token(resp.text)
        headers = {
            'Referer': 'https://gitee.com/login',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token,
            'User-Agent': self.ua.random
        }
        self.session.post(url=check_login_url,
                          headers=headers,
                          data=form_data,
                          timeout=Action.timeout,
                          verify=False)
        data = f'{csrf_token}$gitee${self.password}'
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(PUBLIC_KEY.encode())
        encrypt_data = rsa.encrypt(data.encode(), pubkey)
        encrypt_data = base64.b64encode(encrypt_data).decode()

        form_data = {
            'encrypt_key': 'password',
            'utf8': '✓',
            'authenticity_token': csrf_token,
            'redirect_to_url': '',
            'user[login]': self.username,
            'encrypt_data[user[password]]': encrypt_data,
            'user[remember_me]': 1
        }
        resp = self.session.post(url=login_index_url,
                                 headers=index_headers,
                                 data=form_data,
                                 timeout=Action.timeout,
                                 verify=False)
        if '"message": "帐号或者密码错误"' in resp.text or \
                '"message": "Invalid email or password."' in resp.text or \
                '"message": "not_found_in_database"' in resp.text or \
                '"message": "not_found_and_show_captcha"' in resp.text:
            raise Exception('wrong username or password, login failed')
        if '"message": "captcha_expired"' in resp.text or \
                '"message": "captcha_fail"' in resp.text:
            raise Exception('need captcha validation, please visit '
                            'https://gitee.com/login, '
                            'login to validate your account')
        if '"message": "phone_captcha_fail"' in resp.text or \
                '当前帐号存在异常登录行为，为确认你的有效身份' in resp.text or \
                '一条包含验证码的信息已发送至你的' in resp.text:
            raise Exception('need phone captcha validation, please follow '
                            'gitee wechat subscription '
                            'and bind your account')
        if not ('个人主页' in resp.text or '我的工作台' in resp.text):
            raise Exception(f'unknown error occurred in login method, '
                            f'resp: {resp.text}')

    def rebuild_pages(self):
        pages_url = f'https://gitee.com/{self.repo}/pages'
        rebuild_url = f'{pages_url}/rebuild'

        pages = self.session.get(pages_url)
        csrf_token = Action.get_csrf_token(pages.text)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; '
                            'charset=UTF-8',
            'Referer': pages_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token,
            'User-Agent': self.ua.random
        }
        form_data = {
            'branch': self.branch,
            'build_directory': self.directory,
            'force_https': self.https
        }
        resp = self.session.post(url=rebuild_url,
                                 headers=headers,
                                 data=form_data,
                                 timeout=Action.timeout,
                                 verify=False)
        if resp.status_code != 200:
            raise Exception(f'rebuild page error, '
                            f'status code: {resp.status_code}')
        if '请勿频繁更新部署，稍等1分钟再试试看' in resp.text:
            raise Exception(f'do not deploy frequently, '
                            f'try again one minute later')

    def run(self):
        self.login()
        self.rebuild_pages()
