import base64
import os
import re
import sys

import requests
import rsa

username = os.environ['INPUT_GITEE-USERNAME']
password = os.environ['INPUT_GITEE-PASSWORD']
repo = os.environ['INPUT_GITEE-REPO']
branch = os.environ['INPUT_BRANCH']
directory = os.environ['INPUT_DIRECTORY']
https = os.environ['INPUT_HTTPS']

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIrn+WB2Yi4ABAL5Tq6E09tumY
qVTFdpU01kCDUmClczJOCGZriLNMrshmN9NJxazpqizPthwS1OIK3HwRLEP9D3GL
7gCnvN6lpIpoVwppWd65f/rK2ewv6dstN0fCmtVj4WsLUchWlgNuVTfWljiBK/Dc
YkfslRZzCq5Fl3ooowIDAQAB
-----END PUBLIC KEY-----"""


def get_csrf_token(html):
    return re.search(
        '<meta content="authenticity_token" name="csrf-param" />(.*?)'
        '<meta content="(.*?)" name="csrf-token" />', html, re.S).group(2)


class Spider:

    def __init__(self, username, password,
                 repo, branch='master', directory='', https=True):
        self.session = requests.session()
        self.username = username
        self.password = password
        self.repo = repo
        self.branch = branch
        self.directory = directory
        self.https = https

    def login(self):
        login_index_url = 'https://gitee.com/login'
        check_login_url = 'https://gitee.com/check_user_login'
        form_data = {'user_login': self.username}

        index_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;'
                      'q=0.9,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Host': 'gitee.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/80.0.3987.149 Safari/537.36'
        }
        try:
            resp = self.session.get(login_index_url, headers=index_headers)
            csrf_token = get_csrf_token(resp.text)
            headers = {
                'Referer': 'https://gitee.com/login',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': csrf_token,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/80.0.3987.149 Safari/537.36'
            }
            self.session.post(check_login_url, headers=headers, data=form_data)
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
            self.session.post(login_index_url,
                              headers=index_headers,
                              data=form_data)
        except Exception as e:
            print(f'::set-output name=result::{e}')
            sys.exit(1)

    def build_pages(self):
        pages_url = f'https://gitee.com/{self.repo}/pages'
        rebuild_url = f'https://gitee.com/{self.repo}/pages/rebuild'
        try:
            pages = self.session.get(pages_url)
            csrf_token = get_csrf_token(pages.text)

            headers = {
                'Content-Type':
                    'application/x-www-form-urlencoded; charset=UTF-8',
                'Referer': pages_url,
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRF-Token': csrf_token
            }
            form_data = {
                'branch': self.branch,
                'build_directory': self.directory,
                'force_https': self.https
            }
            self.session.post(pages_url, headers=headers, data=form_data)
            status_code = self.session.post(rebuild_url,
                                            headers=headers,
                                            data=form_data).status_code
            print(f'::set-output name=result::{status_code}')
        except Exception as e:
            print(f'::set-output name=result::{e}')
            sys.exit(1)

    def run(self):
        self.login()
        self.build_pages()


if __name__ == '__main__':
    spider = Spider(username, password, repo, branch, directory, https)
    spider.run()
