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


def test_server_listen(File, Sudo, TestinfraBackend):
    host = TestinfraBackend.get_hostname()
    ver = match('postgresql-(\d)(\d)-\w+', host).group(1, 2)
    with Sudo():
        f = File('/var/lib/pgsql/%s.%s/data/postgresql.conf' % ver
                 ).content_string

    count_listen_addresses = 0
    for line in f.split('\n'):
        if match('\s*listen_addresses', line):
            count_listen_addresses += 1
            listen_addresses = line
    assert count_listen_addresses == 1

    if host == 'postgresql-94-all':
        assert listen_addresses == "listen_addresses = '*'"
    else:
        assert listen_addresses == "listen_addresses = localhost"
