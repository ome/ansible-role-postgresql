import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('postgresql-9[56]-*')


# In postgres 9.5 rolcatupdate was removed and rolbypassrls added
@pytest.mark.parametrize("name,expected_roles", [
    ('alice', 'alice|f|t|f|f|t|f|-1|********||f||'),
    ('bob', 'bob|f|t|f|t|t|f|-1|********||f||'),
])
def test_user_roles(Sudo, Command, name, expected_roles):
    sql = "SELECT * FROM pg_roles WHERE rolname='%s'" % name
    with Sudo('postgres'):
        out = Command.check_output('psql postgres -c "%s" -At' % sql)
    # Everything except the UID at the end
    print out
    assert out.startswith(expected_roles)
