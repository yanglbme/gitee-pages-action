import base64
import os
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
    def get_csrf_token(html):
        return re.search(
            '<meta content="authenticity_token" name="csrf-param" />(.*?)'
            '<meta content="(.*?)" name="csrf-token" />', html, re.S).group(2)

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
        try:
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
            return '个人主页' in resp.text or '我的工作台' in resp.text
        except Exception as e:
            print(f'login error occurred, message: {e}')
            exit(1)

    def rebuild_pages(self):
        pages_url = f'https://gitee.com/{self.repo}/pages'
        rebuild_url = f'{pages_url}/rebuild'
        try:
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
            return resp.status_code == 200
        except Exception as e:
            print(f'deploy error occurred, message: {e}')
            exit(1)

    def run(self):
        res = self.login() and self.rebuild_pages()
        print(f'::set-output name=result::{res}')


if __name__ == '__main__':
    input_username = os.environ.get('INPUT_GITEE-USERNAME')
    input_password = os.environ.get('INPUT_GITEE-PASSWORD')
    input_repo = os.environ.get('INPUT_GITEE-REPO')
    input_branch = os.environ.get('INPUT_BRANCH')
    input_directory = os.environ.get('INPUT_DIRECTORY')
    input_https = os.environ.get('INPUT_HTTPS')
    action = Action(input_username, input_password, input_repo,
                    input_branch, input_directory, input_https)
    action.run()
