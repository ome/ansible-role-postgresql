import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('postgresql-94-all')


def test_server_hba(File, Sudo, TestinfraBackend):
    with Sudo():
        assert File('/var/lib/pgsql/9.4/data/pg_hba.conf').contains(
            '^host publicdb alice 192.168.1.0/24 md5$')
