import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
     os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('postgresql-noserver')


def test_packages(host):
    assert host.package('postgresql96').is_installed
    assert not host.package('postgresql96-server').is_installed
