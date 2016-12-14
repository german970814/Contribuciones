from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run
import random

REPO_URL = 'https://german970814@bitbucket.org/ingeniarte/contribuciones.git'


def deploy():
    site_folder = '/home/%s/webapps/contribuciones' % (env.user)
    source_folder = site_folder + '/source'
    _create_directory_structure_if_necessary(site_folder)
    _get_latest_source(source_folder)
    _update_settings(source_folder, env.host)
    _update_virtualenv(env.user, env.host, source_folder)
    _update_static_files(source_folder, env.user, env.host)
    _update_database(source_folder, env.user, env.host)
    _restart_gunicorn_server(env.user)

def _create_directory_structure_if_necessary(site_folder):
    for subfolder in ('static', 'source', 'media'):
        run('mkdir -p %s/%s' % (site_folder, subfolder))

def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % (source_folder,))
    else:
        run('git clone %s %s' % (REPO_URL, source_folder))

    current_commit = local("git log origin/master -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_settings(source_folder, site_name):
    settings_path = source_folder + '/digitacion/settings.py'
    sed(settings_path, "DEBUG = True", "DEBUG = False")
    sed(settings_path,
        'ALLOWED_HOSTS =.+$',
        'ALLOWED_HOSTS = ["%s"]' % (site_name,)
        )

    secret_key_file = source_folder + '/digitacion/secret_key.py'
    if not exists(secret_key_file):
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
        append(secret_key_file, "SECRET_KEY = '%s'" % (key,))

    append(settings_path, '\nfrom .secret_key import SECRET_KEY')


def _update_virtualenv(user, site_name, source_folder):
    virtualenv_folder = '/home/%s/.envs/contribuciones' % (user,)
    if not exists(virtualenv_folder + '/bin/pip'):
        run('virtualenv --python=python3 %s' % (virtualenv_folder,))

    run('%s/bin/pip install -r %s/requirements.txt' % (
        virtualenv_folder, source_folder
    ))


def _update_static_files(source_folder, user, site_name):
    run('cd %s && /home/%s/.envs/contribuciones/bin/python3 manage.py collectstatic --noinput' % (
        source_folder, user
    ))


def _update_database(source_folder, user, site_name):
    run('cd %s && /home/%s/.envs/contribuciones/bin/python3 manage.py migrate --noinput' % (
        source_folder, user, site_name
    ))


def _restart_gunicorn_server(user):
    run('/home/%s/bin/supervisorctl -c /home/%s/etc/supervisord.conf restart contribuciones' % (user, user))
    run('/home/%s/bin/supervisorctl -c /home/%s/etc/supervisord.conf status contribuciones' % (user, user))
