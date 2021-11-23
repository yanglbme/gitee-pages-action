import base64
import re

import requests
import requests.packages.urllib3
import rsa
from actions_toolkit import core
from retry import retry

from app.util import now

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIrn+WB2Yi4ABAL5Tq6E09tumY
qVTFdpU01kCDUmClczJOCGZriLNMrshmN9NJxazpqizPthwS1OIK3HwRLEP9D3GL
7gCnvN6lpIpoVwppWd65f/rK2ewv6dstN0fCmtVj4WsLUchWlgNuVTfWljiBK/Dc
YkfslRZzCq5Fl3ooowIDAQAB
-----END PUBLIC KEY-----"""

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36'

requests.packages.urllib3.disable_warnings()


class Action:
    """Gitee Pages Action"""

    timeout = 6
    domain = 'https://gitee.com'

    def __init__(self, username: str, password: str,
                 repo: str, branch: str = 'master',
                 directory: str = '', https: str = 'true'):
        self.session = requests.session()
        self.username = username
        self.password = password
        self.repo = repo.strip('/')
        self.branch = branch
        self.directory = directory
        self.https = https

    @staticmethod
    def get_csrf_token(html: str) -> str:
        res1 = re.search(
            '<meta name="csrf-param" content="authenticity_token" />(.*?)'
            '<meta name="csrf-token" content="(.*?)" />', html, re.S)
        res2 = re.search(
            '<meta content="authenticity_token" name="csrf-param" />(.*?)'
            '<meta content="(.*?)" name="csrf-token" />', html, re.S)
        res = res1 or res2
        if res is None:
            raise Exception(f'[{now()}] Deploy error occurred, '
                            'please check your input `gitee-repo`.')
        return res.group(2)

    @retry((requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError),
           tries=3, delay=1, backoff=2)
    def login(self):
        login_index_url = f'{Action.domain}/login'
        check_login_url = f'{Action.domain}/check_user_login'
        form_data = {'user_login': self.username}

        index_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'gitee.com',
            'User-Agent': USER_AGENT
        }

        resp = self.session.get(url=login_index_url,
                                headers=index_headers,
                                timeout=Action.timeout,
                                verify=False)
        csrf_token = Action.get_csrf_token(resp.text)
        headers = {
            'Referer': login_index_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token,
            'User-Agent': USER_AGENT
        }
        self.session.post(url=check_login_url,
                          headers=headers,
                          data=form_data,
                          timeout=Action.timeout,
                          verify=False)

        # https://assets.gitee.com/assets/encrypt.js
        separator = '$gitee$'
        data = f'{csrf_token[-8:]}{separator}{self.password}'
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
            raise Exception(f'[{now()}] Wrong username or password, login failed.')
        if '"message": "captcha_expired"' in resp.text or \
                '"message": "captcha_fail"' in resp.text:
            raise Exception(f'[{now()}] Need captcha validation, please visit '
                            'https://gitee.com/login, '
                            'login to validate your account.')
        if '"message": "phone_captcha_fail"' in resp.text or \
                '当前帐号存在异常登录行为，为确认你的有效身份' in resp.text or \
                '一条包含验证码的信息已发送至你的' in resp.text or \
                'A message containing a verification code has been sent to you' in resp.text:
            raise Exception(f'[{now()}] Need phone captcha validation, please follow wechat '
                            'official account "Gitee" to bind account to turn off authentication.')
        if not ('个人主页' in resp.text or
                '我的工作台' in resp.text or
                '我的工作臺' in resp.text or
                'Dashboard - Gitee' in resp.text):
            raise Exception(f'[{now()}] Unknown error occurred in login method, '
                            f'resp: {resp.text}')
        core.info(f'[{now()}] Login successfully')

    @retry((requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError),
           tries=3, delay=1)
    def rebuild_pages(self):
        if '/' not in self.repo:
            self.repo = f'{self.username}/{self.repo}'
        pages_url = f'{Action.domain}/{self.repo}/pages'
        rebuild_url = f'{pages_url}/rebuild'

        pages = self.session.get(pages_url)
        csrf_token = Action.get_csrf_token(pages.text)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; '
                            'charset=UTF-8',
            'Referer': pages_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token,
            'User-Agent': USER_AGENT
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
            raise Exception(f'[{now()}] Rebuild page error, '
                            f'status code: {resp.status_code}.')
        if '请勿频繁更新部署，稍等1分钟再试试看' in resp.text:
            raise Exception(f'[{now()}] Do not deploy frequently, '
                            f'try again one minute later.')
        core.info(f'[{now()}] Rebuild Gitee Pages successfully')

    def run(self):
        core.info('Welcome to use Gitee Pages Action ❤\n\n'
                  '📕 Getting Started Guide: https://github.com/marketplace/actions/gitee-pages-action\n'
                  '📣 Maintained by Yang Libin: https://github.com/yanglbme\n')
        self.login()
        self.rebuild_pages()
        core.info(f'[{now()}] Success, thanks for using @yanglbme/gitee-pages-action!')
