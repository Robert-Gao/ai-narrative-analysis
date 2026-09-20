#!/usr/bin/env python3
"""Conservative two-way Git sync. Installed runner is a reviewed local copy."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

PUBLIC_FILES = {'SKILL.md', 'README.md', 'LICENSE', 'CITATION.cff', 'agents/openai.yaml'}
REMOTE = 'https://github.com/Robert-Gao/ai-narrative-analysis.git'


def allowed(name):
    p = Path(name)
    return name in PUBLIC_FILES or (p.parts[0] == 'references' and p.suffix == '.md'
                                   and not any(x.startswith('.') for x in p.parts))


def git(repo, *args, check=True):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GIT_MERGE_AUTOEDIT='no')
    result = subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-C', str(repo), *args],
                            capture_output=True, text=True, timeout=45, env=env)
    if check and result.returncode:
        # Avoid storing remote URLs, tokens or diff contents in logs.
        raise RuntimeError('Git %s failed (exit %s); inspect manually in the repository.' %
                           (args[0], result.returncode) + ' ' + re.sub(r'https://[^ ]+', '[remote]', result.stderr)[:300])
    return result


def names(output):
    return {x for x in output.split('\0') if x}


def changed(repo):
    return (names(git(repo, 'diff', '--name-only', '-z', 'HEAD').stdout) |
            names(git(repo, 'ls-files', '--others', '--exclude-standard', '-z').stdout))


def validate(repo):
    """Basic content checks, not a scientific or complete YAML validator."""
    main = repo / 'SKILL.md'
    if main.is_symlink() or not main.is_file():
        raise ValueError('SKILL.md must be a regular file')
    text = main.read_text()
    if not re.search(r'^---\nname: ai-narrative-analysis\ndescription: .+\n---', text):
        raise ValueError('Required skill frontmatter is missing or malformed')
    for p in repo.rglob('*'):
        relative = p.relative_to(repo)
        if relative.parts[0] == '.git' or not allowed(str(relative)):
            continue
        if p.is_symlink() or any(parent.is_symlink() for parent in p.parents if repo in parent.parents):
            raise ValueError('Symlink inside published skill content: ' + str(relative))
        if not p.is_file() or p.stat().st_size > 1024 * 1024:
            raise ValueError('Invalid or oversized skill content: ' + str(relative))
        contents = p.read_text()
        if re.search(r'^(<<<<<<< |=======\s*$|>>>>>>> )', contents, re.M):
            raise ValueError('Merge marker: ' + str(relative))
        if re.search(r'(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN .*PRIVATE KEY-----)', contents):
            raise ValueError('Possible credential in public content: ' + str(relative))
        if p.suffix == '.md':
            for target in re.findall(r'\]\(([^)]+)\)', contents):
                if target.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                dest = (p.parent / target.split('#')[0]).resolve()
                if repo.resolve() not in dest.parents or not dest.exists():
                    raise ValueError('Broken or external local link: ' + str(relative))


def fingerprint(repo, files):
    h = hashlib.sha256()
    for name in sorted(files):
        h.update(name.encode())
        p = repo / name
        if p.is_symlink():
            raise ValueError('Will not publish symlinks')
        h.update(p.read_bytes() if p.is_file() else b'<deleted>')
    return h.hexdigest()


def report(state, message):
    status = state / 'status.txt'
    old = status.read_text().split('\n', 1)[-1] if status.exists() else ''
    if old != message:
        line = datetime.datetime.now().astimezone().isoformat() + '\n' + message
        status.write_text(line)
        print(line, flush=True)


def pause(state, message):
    (state / 'PAUSED').write_text(message)
    report(state, 'PAUSED: ' + message)


def tick(repo, state, debounce=30, expected_remote=REMOTE):
    state.mkdir(parents=True, exist_ok=True)
    if (state / 'PAUSED').exists():
        report(state, 'PAUSED: ' + (state / 'PAUSED').read_text())
        return
    if git(repo, 'remote', 'get-url', 'origin').stdout.strip() != expected_remote:
        pause(state, 'Unexpected origin; no sync performed.')
        return
    if git(repo, 'branch', '--show-current').stdout.strip() != 'main':
        report(state, 'WAIT: only main is synchronized.')
        return
    gitdir = Path(git(repo, 'rev-parse', '--absolute-git-dir').stdout.strip())
    if any((gitdir / x).exists() for x in ['MERGE_HEAD', 'rebase-merge', 'rebase-apply', 'CHERRY_PICK_HEAD']):
        pause(state, 'Git operation or conflict in progress. Finish it before resuming.')
        return
    if git(repo, 'diff', '--cached', '--name-only').stdout.strip():
        report(state, 'WAIT: staged changes belong to you; commit or unstage them first.')
        return
    files = changed(repo)
    if any(not allowed(n) for n in files):
        report(state, 'WAIT: files outside auto-sync allowlist need a manual commit.')
        return
    snapshot = state / 'pending.json'
    if files:
        digest = fingerprint(repo, files)
        prior = json.loads(snapshot.read_text()) if snapshot.exists() else {}
        if prior.get('digest') != digest:
            snapshot.write_text(json.dumps({'digest': digest, 'since': time.time()}))
            report(state, 'WAIT: waiting for edits to settle (30 seconds).')
            return
        if time.time() - prior['since'] < debounce:
            return
        validate(repo)
        git(repo, 'add', '-A', '--', *sorted(files))
        # Git index captures a coherent snapshot; never merge over later edits.
        git(repo, 'commit', '-m', 'sync: update AI narrative research skill', '--no-gpg-sign')
        snapshot.unlink(missing_ok=True)
    if changed(repo):
        report(state, 'WAIT: new edits detected; remote merge deferred.')
        return
    git(repo, 'fetch', 'origin', 'main')
    # Stop before auto-merging remote executable changes; installer uses a pinned copy.
    remote_changes = names(git(repo, 'diff', '--name-only', '-z', 'HEAD...origin/main').stdout)
    if any(n.startswith(('tools/', 'tests/', '.github/')) for n in remote_changes):
        pause(state, 'Remote maintenance scripts changed. Review and merge manually, then reinstall sync.')
        return
    result = git(repo, 'merge', '--no-edit', 'origin/main', check=False)
    if result.returncode:
        pause(state, 'Merge stopped. Both versions are preserved; resolve the conflict manually.')
        return
    if changed(repo):
        report(state, 'WAIT: edits arrived during sync; retry next cycle.')
        return
    try:
        validate(repo)
    except Exception as exc:
        pause(state, 'Content validation failed after merge: ' + str(exc))
        return
    git(repo, 'push', 'origin', 'HEAD:main')
    report(state, 'OK: local main and GitHub synchronized.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--state', required=True, type=Path)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    args.state.mkdir(parents=True, exist_ok=True)
    with (args.state / 'sync.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        if args.resume:
            (args.state / 'PAUSED').unlink(missing_ok=True)
        try:
            tick(args.repo, args.state)
        except Exception as exc:
            report(args.state, 'RETRY: ' + str(exc))


if __name__ == '__main__':
    main()
