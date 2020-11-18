import os
import sys

from app.action import Action


def get_input(name: str, required: bool = True) -> str:
    name = f'INPUT_{name.replace(" ", "_").upper()}'
    val = os.environ.get(name) or ''
    if required and not val:
        raise Exception(f'Input required and not supplied: {name}')
    return val.strip()


if __name__ == '__main__':
    username = get_input('gitee-username')
    password = get_input('gitee-password')
    repo = get_input('gitee-repo')
    branch = get_input('branch', required=False)
    directory = get_input('directory', required=False)
    https = get_input('https', required=False)
    action = Action(username, password, repo, branch, directory, https)
    try:
        action.run()
        print('rebuild Gitee Pages successfully')
    except Exception as e:
        print(f'::error::{e}')
        sys.exit(1)
