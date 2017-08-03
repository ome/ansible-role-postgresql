import testinfra.utils.ansible_runner
from datetime import datetime, timedelta

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('postgresql-96-*')


def test_server_additional_config(File, Sudo):
    f = File('/var/lib/pgsql/9.6/data/postgresql.conf').content_string
    lines = f.split('\n')
    assert "shared_preload_libraries = 'pg_stat_statements'" in lines
    assert "log_filename = 'postgresql-%F.log'" in lines


def test_server_log_file_name(File, Sudo):
    # Check previous day too in case this is run at midnight
    date1 = datetime.today()
    date0 = date1 - timedelta(days=1)
    logdir = '/var/lib/pgsql/9.6/data/pg_log'
    file1 = '%s/postgresql-%s.log' % (logdir, date1.strftime('%F'))
    file0 = '%s/postgresql-%s.log' % (logdir, date0.strftime('%F'))
    assert File(file1).is_file or File(file0).is_file
