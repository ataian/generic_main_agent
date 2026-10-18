#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Nur AST-/Textprüfungen; kein Import oder Start eines Pakethelfers."""
import ast
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'scripts/backup.py').read_text()
tree = ast.parse(source)
ast.parse((ROOT / 'scripts/verify_extract.py').read_text())
assignments = {
    n.targets[0].id: n.value for n in tree.body
    if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)
}
home_dirs = ast.literal_eval(assignments['HOME_DIRS'])
home_node = assignments['HOME_FILES']
assert isinstance(home_node, ast.BinOp) and isinstance(home_node.op, ast.Add)
home_files = ast.literal_eval(home_node.left) + home_dirs
service_files = ast.literal_eval(assignments['SERVICE_FILES'])
assert set(home_dirs) == {'memories', 'skills', 'cron', 'sessions', 'plugins', 'scripts'}
required_home = {'hindsight/config.json', 'maker/environment.json', 'maker/state.json'}
required_service = {'init-db.sh', 'check.py'}
assert required_home <= set(home_files)
assert required_service <= set(service_files)
assert not {'maker', 'hindsight', 'profiles'} & set(home_files)
assert len(home_files) == len(set(home_files))

# Statischer argv enthält nur den Variablennamen, expandiert erst in der Container-Shell.
commands = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name)
            and n.func.value.id == 'subprocess' and n.func.attr == 'run']
assert len(commands) == 2
dump_call = commands[0]
assert isinstance(dump_call.args[0], ast.BinOp)
assert isinstance(dump_call.args[0].left, ast.Name)
assert dump_call.args[0].left.id == 'docker'
argv = ast.literal_eval(dump_call.args[0].right)
assert argv[:3] == ['sh', '-eu', '-c']
assert argv[3] == ('PGPASSWORD="${HINDSIGHT_DB_PASSWORD:?}" exec pg_dump '
                   '-h 127.0.0.1 -U hindsight -d hindsight -Fc -w --no-owner --no-acl')
subprocess.run(['bash', '-n'], input=argv[3], text=True, check=True)
assert '"--user", "postgres", "db"' in source
assert '"unix:///var/run/docker.sock"' in source
assert 'env = {"PATH": os.defpath, "HOME": str(home), "LANG": "C"}' in source
for call in commands:
    options = {k.arg: ast.unparse(k.value) for k in call.keywords}
    assert options['stderr'] == 'subprocess.DEVNULL'
    assert options['check'] == 'True' and options['env'] == 'env'
assert {k.arg: ast.unparse(k.value) for k in dump_call.keywords}['stdout'] == 'out'

scope = (ROOT / 'references/scope.md').read_text()
assert all('`' + name + '`' in scope for name in required_home | required_service)
restore = (ROOT / 'references/restore.md').read_text()
assert 'pgvector/pgvector:0.8.7-pg18-bookworm' in restore
assert '--tmpfs /var/lib/postgresql:rw' in restore
assert 'PGDATA=/var/lib/postgresql/18/docker' in restore
assert '/var/lib/postgresql/data' not in restore
assert 'POSTGRES_HOST_AUTH_METHOD=trust' not in restore
assert '--auth-host=scram-sha-256 --auth-local=scram-sha-256' in restore
assert '--env-file "$TEST_ENV"' in restore
assert 'check.py' in restore and 'Live-API' in restore
assert '--role=hindsight' in restore and '0755' in restore
blocks = re.findall(r'```bash\n(.*?)\n```', restore, re.S)
assert blocks
for block in blocks:
    subprocess.run(['bash', '-n'], input=block, text=True, check=True)
for block in re.findall(r"<<'PY'\n(.*?)\nPY", restore, re.S):
    ast.parse(block)
for path in (ROOT / 'SKILL.md', ROOT / 'references/restore.md'):
    for link in re.findall(r'\]\(([^)]+)\)', path.read_text()):
        if not link.startswith(('https://', 'http://', '#')):
            assert (path.parent / link).exists(), link
assert '30 * 86400' in source
assert '03:00' in (ROOT / 'SKILL.md').read_text()
print('OK: Backup-Allowlist, Container-Auth, PG18-Restore, AST, bash -n und Links statisch geprüft.')
