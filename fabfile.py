import os
from fabric.api import *
from fabric.contrib.console import confirm


env.hosts = ['ygneo@barresfotonatura.com']
env.project_package_prefix = 'daguerro'
env.project_package = 'barres'
env.project_root = "/home/ygneo/django_projects/barres-site/"
env.project_path = env.app_root = os.path.join(env.project_root, env.project_package)
env.virtualenv_path = "/home/ygneo/.virtualenvs/daguerro/"
env.project_i18n_apps = ['daguerro', 'website']


def git_status():
    with cd(env.project_path):
        run('git fetch && git status')


def pushpull():
    local("git push origin master")
    with cd(env.project_path):
        run('git pull')

def pulldb():
    filename = 'mysql_dumped.sql'

    with cd(env['project_path']):
        run('mysqldump --defaults-file=".mysqldump_cnf" --single-transaction daguerro > %s' % filename)
        get(filename, '.')
        run('rm %s' % filename)

    if confirm("Load dumped remote data into local DB?"):
        local('mysql --defaults-file=".mysqldump_cnf" daguerro < %s' % filename)



def reloadapp():
    if env.project_package_prefix:
        app_name = "%s-%s" % (env.project_package_prefix, env.project_package)
    else:
        app_name = env.project_package
    run('sudo supervisorctl restart %s' % app_name)


def compilemessages():
    for app in env.project_i18n_apps:
        with cd(os.path.join(env.project_path, app)):
            run("%(virtualenv_path)s/bin/django-admin.py compilemessages" % env)

def pip_install():
    pip_path = os.path.join(env.virtualenv_path, 'bin/pip')
    run('%s install -r %spip_requirements.txt' %
        (pip_path, env.project_path))


def release():
    pushpull()
    with cd(env.project_path):
        _run_manage('migrate')
        _run_manage('collectstatic --noinput')
    reloadapp()
    compilemessages()


def _run_manage(command, prefix=''):
    python_path = os.path.join(env.virtualenv_path, "bin/python")
    run("%s %s %s/manage.py %s" % (prefix, python_path, env.project_path,
                                command))
