# -*- coding:utf-8 -*-

from __future__ import print_function, unicode_literals

from fabric.api import env, run, local, runs_once, lcd, cd

env.use_ssh_config = True
env.app_name = 'aws-eb-docker-django-skeleton'
env.docker_repository = '{}.dkr.ecr.ap-northeast-1.amazonaws.com/{}'.format(
    '856604848915', env.app_name)


@runs_once
def build():
    """Build docker image"""
    local('docker build -t {} .'.format(env.app_name))


@runs_once
def up():
    """Run docker container for debug (Non AWS)"""
    local('docker-compose up -d')


@runs_once
def down():
    """Run docker container for debug (Non AWS)"""
    local('docker-compose down')


@runs_once
def push():
    """Push docker image to AWS ECS"""
    local('docker tag {}:latest {}:latest'.format(
        env.app_name, env.docker_repository))

    local('docker push {}:latest'.format(
        env.docker_repository))


@runs_once
def bash():
    """Join container shell"""
    result = local('docker ps --quiet --filter name={}'.format(
        env.app_name), capture=True)
    result = result.strip()
    if result:
        local('docker exec -it {} /bin/bash'.format(env.app_name))
    else:
        local('docker-compose run {} /bin/bash'.format(env.app_name))


@runs_once
def login_ecr():
    """login ecr"""
    result = local('aws ecr get-login --region ap-northeast-1', capture=True)
    local(result)


@runs_once
def manage(subcommands=""):
    """Run django manage.py

    fab manage:"migrate --list"
    """
    result = local('docker ps --quiet --filter name={}'.format(
        env.app_name), capture=True)

    command = '/bin/bash -c "cd /var/django/{}/{}; ./manage.py {}"'.format(
        env.app_name, env.app_name, subcommands
    )

    result = result.strip()
    if result:
        local('docker exec -it {} {}'.format(
            env.app_name, command))
    else:
        local('docker-compose run {} {}'.format(
            env.app_name, command))


@runs_once
def runserver():
    """Run django testserver"""
    command = '/bin/bash -c "cd /var/django/{}/{}; ./manage.py runserver 0.0.0.0:80"'.format(
        env.app_name, env.app_name
    )

    local('docker-compose run {} {}'.format(env.app_name, command))
