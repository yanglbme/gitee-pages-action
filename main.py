import os
import sys

from app.action import Action

if __name__ == '__main__':
    input_username = os.environ.get('INPUT_GITEE-USERNAME')
    input_password = os.environ.get('INPUT_GITEE-PASSWORD')
    input_repo = os.environ.get('INPUT_GITEE-REPO')
    input_branch = os.environ.get('INPUT_BRANCH')
    input_directory = os.environ.get('INPUT_DIRECTORY')
    input_https = os.environ.get('INPUT_HTTPS')
    action = Action(input_username, input_password, input_repo,
                    input_branch, input_directory, input_https)
    try:
        action.run()
        print('rebuild Gitee Pages successfully')
    except Exception as e:
        print(f'::error::{e}')
        sys.exit(1)
