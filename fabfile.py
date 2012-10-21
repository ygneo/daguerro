from fabric.api import *

env.hosts = ['ygneo@barresfotonatura.com']
env['project_path'] = "~/django_projects/barres-site/barres"


def git_status():
    with cd(env['project_path']):
        run('git fetch && git status') 


def pushpull():
    local("git push origin master")
    with cd(env['project_path']):
        run('git pull') 


def reload_apache():
    run('sudo /etc/init.d/apache2 reload') 


def release():
    pushpull()
    with cd(env['project_path']):
        run('./manage.py migrate') 
        run('./manage.py collectstatic') 
    reload_apache()
