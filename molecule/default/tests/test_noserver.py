import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('postgresql-noserver')


def test_packages(Package):
    assert Package('postgresql96').is_installed
    assert not Package('postgresql96-server').is_installed
