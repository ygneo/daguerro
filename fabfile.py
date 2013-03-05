from fabric.api import *

env.hosts = ['ygneo@barresfotonatura.com']
env['project_path'] = "~/django_projects/barres-site/barres/"
env['python_path'] = "/home/ygneo/.virtualenvs/daguerro/bin/python"
env['pip_path'] = "/home/ygneo/.virtualenvs/daguerro/bin/pip"


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
    run('%s install -r %spip_requirements.txt' % 
        (env['pip_path'], env['project_path']))
    with cd(env['project_path']):
        _run_manage('migrate') 
        _run_manage('collectstatic') 
    reload_apache()


def _run_manage(command):
    run("%s ./manage.py %s" % (env['python_path'], command))
