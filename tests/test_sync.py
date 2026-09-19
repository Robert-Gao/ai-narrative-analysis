import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('sync', Path(__file__).resolve().parents[1] / 'tools/sync.py')
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.remote = self.root / 'remote.git'
        run('git', 'init', '--bare', '--initial-branch=main', str(self.remote))
        self.a, self.b = self.root / 'a', self.root / 'b'
        run('git', 'clone', str(self.remote), str(self.a))
        self.config(self.a)
        (self.a / 'SKILL.md').write_text('---\nname: ai-narrative-analysis\ndescription: Research\n---\n\n# Test\n\nOriginal\n')
        run('git', 'add', '.', cwd=self.a)
        run('git', 'commit', '-m', 'initial', cwd=self.a)
        run('git', 'push', 'origin', 'main', cwd=self.a)
        run('git', 'clone', str(self.remote), str(self.b))
        self.config(self.b)

    def tearDown(self):
        self.temp.cleanup()

    def config(self, repo):
        run('git', 'config', 'user.name', 'Sync Test', cwd=repo)
        run('git', 'config', 'user.email', 'test@example.invalid', cwd=repo)

    def tick(self, repo):
        sync.tick(repo, self.root / (repo.name + '-state'), debounce=0, expected_remote=str(self.remote))

    def edit(self, repo, value):
        p = repo / 'SKILL.md'
        p.write_text(p.read_text().replace('Original', value))

    def test_two_way_push_and_pull(self):
        self.edit(self.a, 'Computer A')
        self.tick(self.a)
        self.tick(self.a)
        self.tick(self.b)
        self.assertIn('Computer A', (self.b / 'SKILL.md').read_text())
        (self.b / 'README.md').write_text('Computer B contribution')
        self.tick(self.b)
        self.tick(self.b)
        self.tick(self.a)
        self.assertEqual((self.a / 'README.md').read_text(), 'Computer B contribution')

    def test_divergent_nonoverlapping_edits_merge(self):
        self.edit(self.a, 'Computer A')
        (self.b / 'README.md').write_text('Computer B')
        self.tick(self.a)
        self.tick(self.a)
        self.tick(self.b)
        self.tick(self.b)
        self.tick(self.a)
        self.assertIn('Computer A', (self.b / 'SKILL.md').read_text())
        self.assertEqual((self.a / 'README.md').read_text(), 'Computer B')

    def test_conflict_preserves_commits_and_pauses(self):
        self.edit(self.a, 'Computer A')
        self.edit(self.b, 'Computer B')
        self.tick(self.a)
        self.tick(self.a)
        self.tick(self.b)
        self.tick(self.b)
        self.assertTrue((self.root / 'b-state/PAUSED').exists())
        self.assertIn('<<<<<<<', (self.b / 'SKILL.md').read_text())
        self.assertIn('Computer B', run('git', 'show', 'HEAD:SKILL.md', cwd=self.b))
        self.assertIn('Computer A', run('git', 'show', 'origin/main:SKILL.md', cwd=self.b))

    def test_unknown_file_is_not_published(self):
        (self.a / 'interviews.txt').write_text('private research')
        self.tick(self.a)
        self.assertNotIn('interviews.txt', run('git', 'ls-files', cwd=self.a))
        self.assertIn('allowlist', (self.root / 'a-state/status.txt').read_text())

    def test_invalid_skill_not_committed(self):
        (self.a / 'SKILL.md').write_text('unfinished')
        self.tick(self.a)
        with self.assertRaises(ValueError):
            self.tick(self.a)
        self.assertIn('Original', run('git', 'show', 'HEAD:SKILL.md', cwd=self.a))

    def test_remote_script_change_requires_review(self):
        (self.a / 'tools').mkdir()
        (self.a / 'tools/new.py').write_text('print("new")')
        run('git', 'add', '.', cwd=self.a)
        run('git', 'commit', '-m', 'maintenance', cwd=self.a)
        run('git', 'push', 'origin', 'main', cwd=self.a)
        self.tick(self.b)
        self.assertTrue((self.root / 'b-state/PAUSED').exists())
        self.assertFalse((self.b / 'tools/new.py').exists())

    def test_staged_changes_not_claimed(self):
        self.edit(self.a, 'Manually staged')
        run('git', 'add', 'SKILL.md', cwd=self.a)
        self.tick(self.a)
        self.assertIn('Original', run('git', 'show', 'HEAD:SKILL.md', cwd=self.a))
        self.assertIn('staged changes', (self.root / 'a-state/status.txt').read_text())


if __name__ == '__main__':
    unittest.main()
