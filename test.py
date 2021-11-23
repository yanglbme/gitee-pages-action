from app.action import Action

username = 'yanglbme'
password = '***'
repo = 'yanglbme/reading'
branch = 'main'

action = Action(username, password, repo, branch)
action.run()
