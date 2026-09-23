import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('publish_lock', Path(__file__).resolve().parents[1] / 'tools/publish_source_lock.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class PublicationPRTests(unittest.TestCase):
    def test_reject_scope_expansion(self):
        m.allowed_files([m.LOCK])
        for files in ([], [m.LOCK, 'src/worker.mjs'], ['private.txt']):
            with self.assertRaises(RuntimeError): m.allowed_files(files)

    def test_only_exact_head_dispatched_runs_count(self):
        runs = [dict(id=1, head_sha='a', event='workflow_dispatch'),
                dict(id=2, head_sha='b', event='workflow_dispatch'),
                dict(id=3, head_sha='a', event='pull_request')]
        self.assertEqual(m.select_run(runs, 'a')['id'], 1)
        self.assertIsNone(m.select_run(runs, 'c'))

    def test_failure_does_not_echo_provider_output(self):
        from subprocess import CompletedProcess
        with patch.object(m.subprocess, 'run', return_value=CompletedProcess([],1,'secret-value','secret-value')):
            for call in (lambda:m.run('gh','api'),lambda:m.api('repos/test','POST',{'x':'y'})):
                with self.assertRaises(RuntimeError) as failure: call()
                self.assertNotIn('secret-value', str(failure.exception))

    def test_verified_pr_merges_but_drift_or_failed_ci_stops(self):
        for mode in ('success', 'drift', 'failed'):
            mutations = []
            def command(*args):
                if args[:3] == ('git', 'diff', '--name-only'): return m.LOCK
                if args[:3] == ('git', 'rev-parse', 'HEAD'): return 'a'*40
                return ''
            def github(path, method='GET', data=None):
                if method != 'GET': mutations.append((path,method))
                if '/runs?' in path:
                    return {'workflow_runs':[dict(id=1,head_sha='a'*40,event='workflow_dispatch',status='completed',conclusion='failure' if mode=='failed' else 'success')]}
                if '/pulls?' in path: return []
                if path.endswith('/pulls'): return {'number':1,'html_url':'https://example.test/pr/1'}
                if path.endswith('/pulls/1'): return {'head':{'sha':('b' if mode=='drift' else 'a')*40},'base':{'ref':'main'}}
                if '/files?' in path: return [{'filename':m.LOCK}]
                if path.endswith('/merge'): return {'merged':True,'sha':'c'*40}
                return None
            with patch.dict(m.os.environ,{'GITHUB_REPOSITORY':'owner/repo','GITHUB_RUN_ID':'1'}), patch.object(m,'run',side_effect=command), patch.object(m,'api',side_effect=github):
                if mode=='success': m.main()
                else:
                    with self.assertRaises(RuntimeError): m.main()
            self.assertEqual(any(path.endswith('/merge') for path,_ in mutations),mode=='success')

if __name__ == '__main__': unittest.main()
