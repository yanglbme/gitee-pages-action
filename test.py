from app.action import Action

username = 'yanglbme'
password = '*******'
repo = 'doocs/advanced-java'
branch = 'main'

action = Action(username, password, repo, branch)
action.run()
