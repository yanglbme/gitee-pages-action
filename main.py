import base64
import os
import random
import re

import requests
import rsa

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIrn+WB2Yi4ABAL5Tq6E09tumY
qVTFdpU01kCDUmClczJOCGZriLNMrshmN9NJxazpqizPthwS1OIK3HwRLEP9D3GL
7gCnvN6lpIpoVwppWd65f/rK2ewv6dstN0fCmtVj4WsLUchWlgNuVTfWljiBK/Dc
YkfslRZzCq5Fl3ooowIDAQAB
-----END PUBLIC KEY-----"""

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; "
    "SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; "
    "SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; "
    "Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; "
    "Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; "
    "Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; "
    ".NET CLR 3.5.30729; .NET CLR 3.0.30729; "
    ".NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; "
    "Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; "
    "InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) "
    "AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) "
    "Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ "
    "(KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; "
    "rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) "
    "Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) "
    "Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) "
    "Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 "
    "(KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) "
    "AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) "
    "Presto/2.9.168 Version/11.52",
]


class Action:
    """Gitee Pages Action"""

    def __init__(self):
        self.session = requests.session()
        self.username = os.environ['INPUT_GITEE-USERNAME']
        self.password = os.environ['INPUT_GITEE-PASSWORD']
        self.repo = os.environ['INPUT_GITEE-REPO']
        self.branch = os.environ.get('INPUT_BRANCH') or 'master'
        self.directory = os.environ.get('INPUT_DIRECTORY') or ''
        self.https = os.environ.get('INPUT_HTTPS') or True

    @staticmethod
    def get_csrf_token(html):
        return re.search(
            '<meta content="authenticity_token" name="csrf-param" />(.*?)'
            '<meta content="(.*?)" name="csrf-token" />', html, re.S).group(2)

    def login(self):
        """登录主入口"""
        login_index_url = 'https://gitee.com/login'
        check_login_url = 'https://gitee.com/check_user_login'
        form_data = {'user_login': self.username}

        index_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'gitee.com',
            'User-Agent': random.choice(USER_AGENTS)
        }
        try:
            resp = self.session.get(login_index_url,
                                    headers=index_headers,
                                    timeout=5)
            csrf_token = self.get_csrf_token(resp.text)
            headers = {
                'Referer': 'https://gitee.com/login',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': csrf_token,
                'User-Agent': random.choice(USER_AGENTS)
            }
            self.session.post(check_login_url,
                              headers=headers,
                              data=form_data,
                              timeout=5)
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
            resp = self.session.post(login_index_url,
                                     headers=index_headers,
                                     data=form_data,
                                     timeout=5)
            return '个人主页' in resp.text or '我的工作台' in resp.text
        except Exception as e:
            print(f'login error occurred, message: {e}')
            return False

    def rebuild_pages(self):
        """重新构建Pages"""
        pages_url = f'https://gitee.com/{self.repo}/pages'
        rebuild_url = f'{pages_url}/rebuild'
        try:
            pages = self.session.get(pages_url)
            csrf_token = self.get_csrf_token(pages.text)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded; '
                                'charset=UTF-8',
                'Referer': pages_url,
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': csrf_token,
                'User-Agent': random.choice(USER_AGENTS)
            }
            form_data = {
                'branch': self.branch,
                'build_directory': self.directory,
                'force_https': self.https
            }
            resp = self.session.post(rebuild_url,
                                     headers=headers,
                                     data=form_data,
                                     timeout=5)
            return resp.status_code == 200
        except Exception as e:
            print(f'deploy error occurred, message: {e}')
            return False

    def run(self):
        res = self.login() and self.rebuild_pages()
        print(f'::set-output name=result::{res}')


if __name__ == '__main__':
    action = Action()
    action.run()
