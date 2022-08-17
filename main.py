from actions_toolkit import core

from app import log
from app.action import Action

author = {
    'name': 'Yang Libin',
    'link': 'https://github.com/yanglbme'
}
marketplace = 'https://github.com/marketplace/actions/gitee-pages-action'

log.info(f'Welcome to use Gitee Pages Action ❤\n\n'
         f'📕 Getting Started Guide: {marketplace}\n'
         f'📣 Maintained by {author["name"]}: {author["link"]}\n')

try:
    username = core.get_input('gitee-username', required=True)
    password = core.get_input('gitee-password', required=True)
    repo = core.get_input('gitee-repo', required=True)

    branch = core.get_input('branch')
    directory = core.get_input('directory')
    https = core.get_input('https')

    action = Action(username, password, repo, branch, directory, https)

    action.login()
    log.info('Login successfully')

    action.rebuild_pages()
    log.info('Rebuild Gitee Pages successfully')

    log.info('Success, thanks for using @yanglbme/gitee-pages-action!')
except Exception as e:
    log.set_failed(str(e))
