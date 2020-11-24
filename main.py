from actions_toolkit import core

from app.action import Action

if __name__ == '__main__':
    username = core.get_input('gitee-username')
    password = core.get_input('gitee-password')
    repo = core.get_input('gitee-repo')
    branch = core.get_input('branch', required=False)
    directory = core.get_input('directory', required=False)
    https = core.get_input('https', required=False)
    action = Action(username, password, repo, branch, directory, https)
    try:
        action.run()
        core.info('Rebuild Gitee Pages successfully.')
    except Exception as e:
        core.set_failed(str(e))
