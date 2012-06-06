from fabric.api import *

env.hosts = ['ygneo@barresfotonatura.com']
env['project_path'] = "~/django_projects/barres"

def git_status():
    with cd(env['project_path']):
        run('cd ~/django_projects/barres; git status') 

def pushpull():
    local("git push origin master")
    with cd(env['project_path']):
        run('cd ~/django_projects/barres; git pull') 


def reload_apache():
    run('sudo /etc/init.d/apache2 reload') 


def release():
    pushpull()
    reload_apache()
