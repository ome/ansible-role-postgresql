import testinfra.utils.ansible_runner
import pytest
from re import match

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


@pytest.mark.parametrize("name,expected_db", [
    ('publicdb', 'publicdb|en_US.UTF-8|en_US.UTF-8'),
    ('secretdb', 'secretdb|en_US.UTF-8|en_US.UTF-8')
])
def test_databases(Sudo, Command, name, expected_db):
    sql = ("SELECT datname,datcollate,datctype FROM pg_database "
           "WHERE datname='%s'" % name)
    with Sudo('postgres'):
        out = Command.check_output('psql postgres -c "%s" -At' % sql)
    assert out == expected_db


@pytest.mark.parametrize("name,expected_roles", [
    ('alice', 'alice|f|t|f|f|f|t|f|-1|********|||'),
    ('bob', 'bob|f|t|f|t|f|t|f|-1|********|||'),
])
def test_user_roles(Sudo, Command, name, expected_roles):
    sql = "SELECT * FROM pg_roles WHERE rolname='%s'" % name
    with Sudo('postgres'):
        out = Command.check_output('psql postgres -c "%s" -At' % sql)
    # Everything except the UID at the end
    assert out.startswith(expected_roles)


def test_server_listen(File, Sudo, TestinfraBackend):
    host = TestinfraBackend.get_hostname()
    with Sudo():
        f = File('/var/lib/pgsql/9.4/data/postgresql.conf').content_string

    count_listen_addresses = 0
    for line in f.split('\n'):
        if match('\s*listen_addresses', line):
            count_listen_addresses += 1
            listen_addresses = line
    assert count_listen_addresses == 1

    if host == 'postgresql-94-all':
        assert listen_addresses == "listen_addresses = '\*'"
    else:
        assert listen_addresses == "listen_addresses = localhost"
