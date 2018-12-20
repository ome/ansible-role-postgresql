import testinfra.utils.ansible_runner
import os
import pytest
from re import match
from utils import get_version

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('server')


@pytest.mark.parametrize("name,expected_db", [
    ('publicdb', 'publicdb|en_US.UTF-8|en_US.UTF-8'),
    ('secretdb', 'secretdb|en_US.UTF-8|en_US.UTF-8')
])
def test_databases(host, name, expected_db):
    sql = ("SELECT datname,datcollate,datctype FROM pg_database "
           "WHERE datname='%s'" % name)
    with host.sudo('postgres'):
        out = host.check_output('psql postgres -c "%s" -At' % sql)
    assert out == expected_db


def test_server_listen(host):
    hostname = host.backend.get_hostname()
    ver = get_version(hostname)
    with host.sudo():
        value = '/var/lib/pgsql/%s/data/postgresql.conf' % ver
        f = host.file(value).content_string

    count_listen_addresses = 0
    for line in f.split('\n'):
        if match('\s*listen_addresses', line):
            count_listen_addresses += 1
            listen_addresses = line
    assert count_listen_addresses == 1

    if hostname == 'postgresql-94-all':
        assert listen_addresses == "listen_addresses = '*'"
    else:
        assert listen_addresses == "listen_addresses = localhost"
