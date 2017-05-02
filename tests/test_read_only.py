import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


@pytest.mark.parametrize("name,password,table,should_pass", [
    ('alice', 'alice123', "regular", True),
    ('alice', 'alice123', "password", True),
    ('charles', 'charles123', "regular", True),
    ('charles', 'charles123', "password", False),
])
def test_query(Command, name, password, table, should_pass):
    sql = "SELECT * FROM " + table
    txt = 'env PGPASSWORD=%s psql publicdb -h localhost -U %s -c "%s" -At'
    try:
        Command.check_output(txt % (password, name, sql))
        assert should_pass
    except:
        assert not should_pass
