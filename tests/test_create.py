import testinfra.utils.ansible_runner
import pytest
import uuid

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')

CMD = 'env PGPASSWORD=%s createdb -h localhost -U %s "%s"'


def run(Command, db, should_pass, password, name):
    try:
        Command.check_output(CMD % (password, name, db))
        assert should_pass
    except:
        assert not should_pass


@pytest.mark.parametrize("name,password,should_pass", [
    ('alice', 'alice123', False),
    ('bob', 'bob123', True),
    ('charles', 'charles123', False),
])
def test_create(Command, name, password, should_pass):
    rnd = str(uuid.uuid4())
    run(Command, rnd, should_pass, password, name)
