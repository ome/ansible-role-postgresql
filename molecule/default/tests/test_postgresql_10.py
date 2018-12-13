import os
import testinfra.utils.ansible_runner
from datetime import datetime, timedelta

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('postgresql-10-*')


def test_server_additional_config(host):
    f = host.file('/var/lib/pgsql/10/data/postgresql.conf').content_string
    lines = f.split('\n')
    assert "shared_preload_libraries = 'pg_stat_statements'" in lines
    assert "log_filename = 'postgresql-%F.log'" in lines


def test_server_log_file_name(host):
    # Check previous day too in case this is run at midnight
    date1 = datetime.today()
    date0 = date1 - timedelta(days=1)
    logdir = '/var/lib/pgsql/10/data/pg_log'
    file1 = '%s/postgresql-%s.log' % (logdir, date1.strftime('%F'))
    file0 = '%s/postgresql-%s.log' % (logdir, date0.strftime('%F'))
    assert host.file(file1).is_file or host.file(file0).is_file
