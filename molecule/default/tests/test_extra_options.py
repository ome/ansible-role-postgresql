import os
import testinfra.utils.ansible_runner
from datetime import datetime, timedelta
from re import match

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('extra_options')


def test_server_additional_config(host):
    hostname = host.backend.get_hostname()
    ver = match('postgresql-(\d+\.?\d+)-\w+', hostname).group(1)
    f = host.file(
        '/var/lib/pgsql/%s/data/postgresql.conf' % ver).content_string
    lines = f.split('\n')
    assert "shared_preload_libraries = 'pg_stat_statements'" in lines
    assert "log_filename = 'postgresql-%F.log'" in lines


def test_server_log_file_name(host):
    # Check previous day too in case this is run at midnight
    hostname = host.backend.get_hostname()
    ver = match('postgresql-(\d+\.?\d+)-\w+', hostname).group(1)
    date1 = datetime.today()
    date0 = date1 - timedelta(days=1)
    logdir = '/var/lib/pgsql/%s/data/pg_log' % ver
    file1 = '%s/postgresql-%s.log' % (logdir, date1.strftime('%F'))
    file0 = '%s/postgresql-%s.log' % (logdir, date0.strftime('%F'))
    assert host.file(file1).is_file or host.file(file0).is_file
