from actions_toolkit import core

from app.action import Action

if __name__ == '__main__':
    try:
        username = core.get_input('gitee-username', required=True)
        password = core.get_input('gitee-password', required=True)
        repo = core.get_input('gitee-repo', required=True)

        branch = core.get_input('branch') or 'master'
        directory = core.get_input('directory') or ''
        https = core.get_input('https') or 'true'
        action = Action(username, password, repo, branch, directory, https)
        action.run()
    except Exception as e:
        core.set_failed(str(e))
