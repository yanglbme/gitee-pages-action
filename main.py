import os
import re

import requests

repo = os.environ['INPUT_GITEE-REPO']
cookie = os.environ['INPUT_GITEE-LOGIN-COOKIE']
branch = os.environ['INPUT_BRANCH']
directory = os.environ['INPUT_DIRECTORY']
https = os.environ['INPUT_HTTPS']


def spider():
    pages_url = f'https://gitee.com/{repo}/pages'
    rebuild_url = f'https://gitee.com/{repo}/pages/rebuild'
    headers = {
        'Cookie': cookie
    }
    try:
        pages = requests.get(pages_url, headers=headers)
        csrf_token = re.search('<meta content="authenticity_token" name="csrf-param" />(.*?)'
                               '<meta content="(.*?)" name="csrf-token" />', pages.text, re.S).group(2)

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': cookie,
            'Referer': pages_url,
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-Token': csrf_token
        }
        form_data = {
            'branch': branch,
            'build_directory': directory,
            'force_https': https
        }
        requests.post(pages_url, headers=headers, data=form_data)
        status_code = requests.post(rebuild_url, headers=headers, data=form_data).status_code
        print(f'::set-output name=result::{status_code}')
    except Exception as e:
        print(f'::set-output name=result::{e}')


if __name__ == "__main__":
    spider()
