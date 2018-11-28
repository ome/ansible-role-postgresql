import testinfra.utils.ansible_runner
import os
import pytest
import uuid

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('server')

CMD = 'env PGPASSWORD=%s createdb -h localhost -U %s "%s"'


def run(host, db, should_pass, password, name):
    try:
        host.check_output(CMD % (password, name, db))
        assert should_pass
    except Exception:
        assert not should_pass


@pytest.mark.parametrize("name,password,should_pass", [
    ('alice', 'alice123', False),
    ('bob', 'bob123', True),
    ('charles', 'charles123', False),
])
def test_create(host, name, password, should_pass):
    rnd = str(uuid.uuid4())
    run(host, rnd, should_pass, password, name)
