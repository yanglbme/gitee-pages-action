import base64
import re

import requests
import rsa
import urllib3
from retry import retry

from app import log
from app.const import domain, ua, timeout, pubkey

urllib3.disable_warnings()


class Action:
    def __init__(self, username: str, password: str,
                 repo: str, branch: str = 'master',
                 directory: str = '', https: str = 'true'):
        self.session = requests.session()
        self.session.keep_alive = False
        self.username = username
        self.password = password
        self.repo = repo.replace(domain, '').strip('/')
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
            raise Exception('Deploy error occurred, please re-run job or check your input `gitee-repo`.')
        return res.group(2)

    @retry((requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.Timeout,
            requests.RequestException),
           tries=4, delay=2, backoff=3)
    def login(self):
        login_index_url = f'{domain}/login'
        check_login_url = f'{domain}/check_user_login'
        form_data = {'user_login': self.username}

        index_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'gitee.com',
            'User-Agent': ua
        }

        resp = self.session.get(url=login_index_url,
                                headers=index_headers,
                                timeout=timeout,
                                verify=False)
        csrf_token = Action.get_csrf_token(resp.text)
        headers = {
            'Referer': login_index_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token,
            'User-Agent': ua
        }
        self.session.post(url=check_login_url,
                          headers=headers,
                          data=form_data,
                          timeout=timeout,
                          verify=False)

        # https://assets.gitee.com/assets/encrypt.js
        separator = '$gitee$'
        data = f'{csrf_token[-8:]}{separator}{self.password}'
        pk = rsa.PublicKey.load_pkcs1_openssl_pem(pubkey.encode())
        encrypt_data = rsa.encrypt(data.encode(), pk)
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
        res = self.session.post(url=login_index_url,
                                headers=index_headers,
                                data=form_data,
                                timeout=timeout,
                                verify=False).text

        case1 = ['"message": "帐号或者密码错误"', '"message": "Invalid email or password."',
                 '"message": "not_found_in_database"', '"message": "not_found_and_show_captcha"']
        case2 = ['"message": "captcha_expired"', '"message": "captcha_fail"']
        case3 = ['"message": "phone_captcha_fail"', '当前帐号存在异常登录行为，为确认你的有效身份',
                 '一条包含验证码的信息已发送至你的', 'A message containing a verification code has been sent to you']
        case4 = ['个人主页', '我的工作台', '我的工作臺', 'Dashboard - Gitee']

        if any(e in res for e in case1):
            raise Exception('Wrong username or password, login failed.')
        if any(e in res for e in case2):
            raise Exception('Need captcha validation, please visit '
                            'https://gitee.com/login, login to validate your account.')
        if any(e in res for e in case3):
            raise Exception('Need phone captcha validation, please follow wechat '
                            'official account "Gitee" to bind account to turn off authentication.')
        if not any(e in res for e in case4):
            raise Exception(f'Unknown error occurred in login method, resp: {res}')

    @retry((requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectTimeout,
            requests.exceptions.ConnectionError,
            requests.Timeout,
            requests.RequestException),
           tries=4, delay=2, backoff=3)
    def rebuild_pages(self):
        if '/' not in self.repo:
            self.repo = f'{self.username}/{self.repo}'

        pages_url = f'{domain}/{self.repo}/pages'
        rebuild_url = f'{pages_url}/rebuild'

        pages = self.session.get(pages_url)
        csrf_token = Action.get_csrf_token(pages.text)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; '
                            'charset=UTF-8',
            'Referer': pages_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token,
            'User-Agent': ua
        }
        form_data = {
            'branch': self.branch,
            'build_directory': self.directory,
            'force_https': self.https
        }
        resp = self.session.post(url=rebuild_url,
                                 headers=headers,
                                 data=form_data,
                                 timeout=timeout,
                                 verify=False)
        if resp.status_code != 200:
            raise Exception(f'Rebuild page error, status code: {resp.status_code}, resp: {resp.text}')
        html = resp.text
        if '正在部署，请耐心等待' in html:
            return
        if '部署失败' in html and '错误信息' in html:
            res = re.search('<p>错误信息:(.*?)<\\\/p>', html, re.S)
            if res:
                raise Exception(res.group(1).strip())
        if '请勿频繁更新部署，稍等1分钟再试试看' in html:
            raise Exception('Do not deploy frequently, try again one minute later.')
        if '仓库持有者未实名认证，不允许部署 pages 服务' in html:
            raise Exception('The repository owner is not authenticated and is not allowed to deploy pages services.')
        log.warning(f'Unknown html: {html}')

    def run(self):
        self.login()
        self.rebuild_pages()
