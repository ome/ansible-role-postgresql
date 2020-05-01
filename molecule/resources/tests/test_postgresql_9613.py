import testinfra.utils.ansible_runner
import os

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('postgresql-96-c7')


def test_full_version(host):
    out1 = host.check_output('psql --version')
    assert out1 == 'psql (PostgreSQL) 9.6.13'
    out2 = host.check_output('/usr/pgsql-9.6/bin/pg_ctl --version')
    assert out2 == 'pg_ctl (PostgreSQL) 9.6.13'
