import os

from actions_toolkit import core

from app import log
from app.action import Action

os.environ['INPUT_GITEE-USERNAME'] = 'yanglbme'
os.environ['INPUT_GITEE-PASSWORD'] = '***'
os.environ['INPUT_GITEE-REPO'] = 'yanglbme/reading'
os.environ['INPUT_BRANCH'] = 'main'

try:
    username = core.get_input('gitee-username', required=True)
    password = core.get_input('gitee-password', required=True)
    repo = core.get_input('gitee-repo', required=True)
    branch = core.get_input('branch')

    action = Action(username, password, repo, branch)
    action.run()
except Exception as e:
    log.set_failed(str(e))
