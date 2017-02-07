import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('postgresql-94-*')


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


def test_server_hba(File, Sudo, TestinfraBackend):
    host = TestinfraBackend.get_hostname()
    with Sudo():
        alice_publicdb = File('/var/lib/pgsql/9.4/data/pg_hba.conf').contains(
            '^host publicdb alice 192.168.1.0/24 md5$')
    if host == 'postgresql-94-all':
        assert alice_publicdb
    else:
        assert not alice_publicdb
