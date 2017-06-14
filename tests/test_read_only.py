import testinfra.utils.ansible_runner
import pytest
import uuid

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')

CMD = 'env PGPASSWORD=%s psql publicdb -h localhost -U %s -c "%s" -At'


def run(Command, sql, should_pass, password, name):
    try:
        Command.check_output(CMD % (password, name, sql))
        assert should_pass
    except:
        assert not should_pass


@pytest.mark.parametrize("name,password,table,should_pass", [
    ('alice', 'alice123', "regular", True),
    ('alice', 'alice123', "password", True),
    # Charles has not had permissions added due to
    # idempotency issues in molecule.
    ('charles', 'charles123', "regular", False),
    ('charles', 'charles123', "password", False),
])
def test_query(Command, name, password, table, should_pass):
    sql = "SELECT * FROM " + table
    run(Command, sql, should_pass, password, name)


@pytest.mark.parametrize("name,password,table,should_pass", [
    ('alice', 'alice123', "regular", True),
    ('alice', 'alice123', "password", True),
    ('charles', 'charles123', "regular", False),
    ('charles', 'charles123', "password", False),
])
def test_modify(Command, name, password, table, should_pass):
    rnd = str(uuid.uuid4())
    sql = "insert into %s values ('%s')" % (table, rnd)
    run(Command, sql, should_pass, password, name)
    sql = "delete from %s" % table
    run(Command, sql, should_pass, password, name)
