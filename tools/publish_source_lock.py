#!/usr/bin/env python3
"""Publish a validated source lock through ordinary protected-branch checks."""
import json
import os
import subprocess
import time

WORKFLOWS = ('ecosystem-validation.yml', 'stack-ci.yml', 'public-site-ci.yml')
LOCK = 'site/sources.lock.json'


def run(*args):
    result = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode:
        # Provider output and environment may contain credentials; never echo them.
        raise RuntimeError(f'{args[0]} operation failed; inspect repository permissions or checks')
    return result.stdout.strip()


def api(path, method='GET', data=None):
    args = ['gh', 'api', path, '--method', method]
    if data is None:
        raw = run(*args)
    else:
        result = subprocess.run(args + ['--input', '-'], input=json.dumps(data), text=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode:
            raise RuntimeError('GitHub API operation failed; inspect repository permissions or checks')
        raw = result.stdout
    return json.loads(raw) if raw.strip() else None


def select_run(runs, revision):
    candidates = [r for r in runs if r['head_sha'] == revision and r['event'] == 'workflow_dispatch']
    return max(candidates, key=lambda r: r['id']) if candidates else None


def allowed_files(files):
    if files != [LOCK]:
        raise RuntimeError('Refusing publication: changes exceed the source lock')


def main():
    repo = os.environ['GITHUB_REPOSITORY']
    allowed_files(run('git', 'diff', '--name-only').splitlines())
    if run('git', 'diff', '--cached', '--name-only'):
        raise RuntimeError('Refusing publication: unexpected staged changes')
    run('gh', 'auth', 'setup-git')
    run('git', 'config', 'user.name', 'github-actions[bot]')
    run('git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    date = run('git', 'show', '-s', '--format=%cI', 'HEAD')
    os.environ['GIT_AUTHOR_DATE'] = date
    os.environ['GIT_COMMITTER_DATE'] = date
    run('git', 'add', LOCK)
    run('git', 'commit', '-m', 'Refresh public-site source revisions')
    head = run('git', 'rev-parse', 'HEAD')
    # A fresh branch per immutable commit avoids force-push and cross-run overwrites.
    branch = f'automation/site-sources-{head}'
    run('git', 'push', 'origin', f'HEAD:refs/heads/{branch}')
    pulls = api(f'repos/{repo}/pulls?state=open&head={repo.split("/")[0]}:{branch}')
    pr = pulls[0] if pulls else api(f'repos/{repo}/pulls', 'POST', {
        'title': 'Refresh verified public-site sources', 'head': branch, 'base': 'main',
        'body': 'Automated source-lock update. Rendered outputs were validated before this PR. '
                'All three existing CI workflows are explicitly dispatched on this exact commit. '
                'Merge uses normal branch rules; no bypass or automatic review approval. '
                f'Origin run: https://github.com/{repo}/actions/runs/{os.environ["GITHUB_RUN_ID"]}'})
    print(f'Source update PR: {pr["html_url"]}', flush=True)
    # GITHUB_TOKEN pushes cannot be relied upon to trigger push/PR CI automatically.
    for workflow in WORKFLOWS:
        runs = api(f'repos/{repo}/actions/workflows/{workflow}/runs?event=workflow_dispatch&branch={branch}&per_page=10')['workflow_runs']
        prior = select_run(runs, head)
        if not prior or (prior['status'] == 'completed' and prior['conclusion'] != 'success'):
            api(f'repos/{repo}/actions/workflows/{workflow}/dispatches', 'POST', {'ref': branch})
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        completed = True
        for workflow in WORKFLOWS:
            runs = api(f'repos/{repo}/actions/workflows/{workflow}/runs?event=workflow_dispatch&branch={branch}&per_page=10')['workflow_runs']
            found = select_run(runs, head)
            if not found or found['status'] != 'completed':
                completed = False
            elif found['conclusion'] != 'success':
                raise RuntimeError(f'{workflow} failed; PR preserved for recovery')
        if completed:
            break
        time.sleep(10)
    else:
        raise RuntimeError('CI timed out; PR preserved for recovery')
    current = api(f'repos/{repo}/pulls/{pr["number"]}')
    if current['head']['sha'] != head or current['base']['ref'] != 'main':
        raise RuntimeError('PR identity changed; refusing merge')
    files = api(f'repos/{repo}/pulls/{pr["number"]}/files?per_page=100')
    allowed_files([f['filename'] for f in files])
    merged = api(f'repos/{repo}/pulls/{pr["number"]}/merge', 'PUT', {'sha': head, 'merge_method': 'merge'})
    if not merged.get('merged'):
        raise RuntimeError('Normal branch rules declined merge; PR preserved for recovery')
    print(f'Merged source lock: {merged["sha"]}; provider deployment still requires verification')


if __name__ == '__main__':
    main()
