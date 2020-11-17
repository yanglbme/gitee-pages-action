import os
import sys

from app.action import Action

if __name__ == '__main__':
    username = os.environ.get('INPUT_GITEE-USERNAME')
    password = os.environ.get('INPUT_GITEE-PASSWORD')
    repo = os.environ.get('INPUT_GITEE-REPO')
    branch = os.environ.get('INPUT_BRANCH')
    directory = os.environ.get('INPUT_DIRECTORY')
    https = os.environ.get('INPUT_HTTPS')
    action = Action(username, password, repo,
                    branch, directory, https)
    try:
        action.run()
        print('rebuild Gitee Pages successfully')
    except Exception as e:
        print(f'::error::{e}')
        sys.exit(1)
