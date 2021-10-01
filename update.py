import subprocess
from git import Repo, GitCommandError


env = 'prod'
remote_name = 'origin'
branch = {
    'stg': 'dev',
    'prod': 'main',
}
create_migrations = ['python', 'manage.py', 'db', 'migrate']
apply_migrations = ['python', 'manage.py', 'db', 'upgrade']
restart_service = ['systemctl', 'reload', 'gunicorn-traveller.service']
command_sequence = [
    create_migrations,
    apply_migrations,
    restart_service,
]


def check_for_updates(repo, local, remote):
    repo.remotes.origin.fetch()
    commits_behind = repo.iter_commits(f'{local}..{remote}')
    update_count = len(list(commits_behind))
    print(f'{update_count=}')
    return update_count


def main():
    repo = Repo()
    assert not repo.bare

    print('\n# checking for updates')
    local_branch = branch[env]
    remote_branch = f'{remote_name}/{branch[env]}'
    updates_available = check_for_updates(repo, local_branch, remote_branch)
    if not updates_available:
        print('no updates')
        return

    print('\n# pulling updates')
    try:
        pull_results = repo.remotes.origin.pull()
        print(f'{pull_results=}')
    except GitCommandError as e:
        print('Error', e.stderr)

    print('\n# running commands')
    for command in command_sequence:
        try:
            subprocess.run(command)
        except FileNotFoundError as e:
            print('Error', e)

    return


if __name__ == "__main__":
    main()
