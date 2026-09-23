import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from publication_outputs import build_local, snapshot, digest
from refresh_public_site_sources import resolve_event

REPO = 'ChongLiuPhil/Personal-Publishing-Framework'

class EventTests(unittest.TestCase):
    def getter(self, status='ahead'):
        def get(url):
            if '/compare/' in url: return json.dumps({'status':status}).encode()
            if '/commits/' in url: return json.dumps({'sha':'b'*40}).encode()
            return json.dumps({'private':False,'default_branch':'main'}).encode()
        return get
    def test_duplicate_and_delayed_events_converge(self):
        for sha in ('a'*40, 'b'*40):
            self.assertEqual(resolve_event(REPO,'main',sha,self.getter()), 'b'*40)
    def test_wrong_repo_branch_sha_rejected_before_network(self):
        for args in [('evil/repo','main','a'*40),(REPO,'preview','a'*40),(REPO,'main','main')]:
            with self.assertRaises(ValueError): resolve_event(*args, get=lambda _: self.fail('network'))
    def test_unrelated_commit_rejected(self):
        with self.assertRaises(ValueError): resolve_event(REPO,'main','a'*40,self.getter('diverged'))
    def test_private_or_branch_drift_rejected(self):
        for meta in ({'private':True,'default_branch':'main'},{'private':False,'default_branch':'other'}):
            with self.assertRaises(ValueError): resolve_event(REPO,'main','a'*40,lambda _:json.dumps(meta).encode())

class OutputTests(unittest.TestCase):
    def spec(self, kind='static-directory'):
        return {'repository':REPO,'visibility':'public','mount':'/publications/demo/',
                'source_directory':'.','output_directory':'public','build':{'kind':kind,'version':'1.10.18'}}
    def test_complete_directory_add_delete_binary_and_private_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); out=root/'public';out.mkdir()
            (out/'index.html').write_text('<h1>Book</h1>')
            (root/'private.txt').write_text('must stay private')
            before=digest(build_local(root,self.spec()))
            (out/'image.png').write_bytes(b'\x89PNG\x00\xff')
            after=build_local(root,self.spec())
            self.assertIn('image.png',after); self.assertNotIn('private.txt',after)
            self.assertNotEqual(before,digest(after))
            (out/'image.png').unlink()
            self.assertEqual(before,digest(build_local(root,self.spec())))
    def test_symlink_and_hidden_output_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'index.html').write_text('ok')
            (root/'link').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError): snapshot(root)
            (root/'link').unlink();(root/'.env').write_text('secret')
            with self.assertRaises(ValueError): snapshot(root)
    def test_quarto_failure_and_credentials_not_forwarded(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch('publication_outputs.subprocess.check_output',return_value='1.10.18'), patch('publication_outputs.subprocess.run') as run:
                run.return_value.returncode=1
                with patch.dict('os.environ',{'STARTER_SYNC_TOKEN':'test-secret','CLOUDFLARE_API_TOKEN':'test-secret'}):
                    with self.assertRaisesRegex(ValueError,'build failed'): build_local(Path(tmp),self.spec('quarto'))
                env=run.call_args.kwargs['env']
                self.assertNotIn('STARTER_SYNC_TOKEN',env); self.assertNotIn('CLOUDFLARE_API_TOKEN',env)
    def test_output_path_traversal_rejected(self):
        spec=self.spec();spec['output_directory']='../private'
        with self.assertRaises(ValueError): build_local(Path('/tmp'),spec)

class NotificationTests(unittest.TestCase):
    def script(self):
        path=Path(__file__).resolve().parents[1]/'templates/notify-starter.yml'
        import textwrap
        return textwrap.dedent(path.read_text().split('        run: |\n',1)[1])
    def test_missing_secret_fails_without_network(self):
        with patch.dict('os.environ',{},clear=True), patch('urllib.request.urlopen') as send:
            with self.assertRaisesRegex(SystemExit,'missing'):
                exec(self.script(),{})
            send.assert_not_called()
    def test_expired_secret_reports_status_not_secret(self):
        from urllib.error import HTTPError
        env={'STARTER_SYNC_TOKEN':'not-a-real-secret','SOURCE_REPOSITORY':REPO,'SOURCE_BRANCH':'main','SOURCE_REVISION':'a'*40}
        with patch.dict('os.environ',env,clear=True), patch('urllib.request.urlopen',side_effect=HTTPError('https://api.github.com',401,'Unauthorized',{},None)):
            with self.assertRaises(SystemExit) as error: exec(self.script(),{})
        self.assertIn('401',str(error.exception));self.assertNotIn(env['STARTER_SYNC_TOKEN'],str(error.exception))
    def test_acceptance_is_not_deployment_and_payload_has_only_identity(self):
        import contextlib, io
        env={'STARTER_SYNC_TOKEN':'not-a-real-secret','SOURCE_REPOSITORY':REPO,'SOURCE_BRANCH':'main','SOURCE_REVISION':'a'*40}
        with patch.dict('os.environ',env,clear=True), patch('urllib.request.urlopen') as send:
            send.return_value.__enter__.return_value.status=204
            output=io.StringIO()
            with contextlib.redirect_stdout(output): exec(self.script(),{})
            request=send.call_args.args[0]
            payload=json.loads(request.data)
        self.assertEqual(payload['ref'],'main')
        self.assertEqual(set(payload['inputs']),{'repository','branch','revision'})
        self.assertNotIn(env['STARTER_SYNC_TOKEN'],output.getvalue())
        self.assertIn('not deployment confirmation',output.getvalue())
