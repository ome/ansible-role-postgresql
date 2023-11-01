import os
import testinfra.utils.ansible_runner
from datetime import datetime, timedelta
from utils import get_version

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('extra_options')


def test_server_additional_config(host):
    version = get_version(host)
    if host.system_info.distribution == 'rocky':
        configfile = '/var/lib/pgsql/{version}/data/postgresql.conf'
    else:
        configfile = '/etc/postgresql/{version}/main/postgresql.conf'
    f = host.file(configfile.format(version=version)).content_string
    lines = f.split('\n')
    assert "shared_preload_libraries = 'pg_stat_statements'" in lines
    assert "log_filename = 'postgresql-%F.log'" in lines


def test_server_log_file_name(host):
    # Check previous day too in case this is run at midnight
    version = get_version(host)
    if host.system_info.distribution == 'rocky':
        logdir = '/var/lib/pgsql/{version}/data/pg_log'
    else:
        logdir = '/var/lib/postgresql/{version}/main/pg_log'
    date1 = datetime.today()
    date0 = date1 - timedelta(days=1)
    logdir = logdir.format(version=version)
    file1 = '%s/postgresql-%s.log' % (logdir, date1.strftime('%F'))
    file0 = '%s/postgresql-%s.log' % (logdir, date0.strftime('%F'))
    assert host.file(file1).is_file or host.file(file0).is_file
