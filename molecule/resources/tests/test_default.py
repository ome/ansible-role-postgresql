import os
import pytest
import testinfra.utils.ansible_runner
import uuid
from re import match
from utils import get_version

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


# Server

@pytest.mark.parametrize("name,expected_db", [
    ('publicdb', 'publicdb|{lang}.UTF-8|{lang}.UTF-8'),
    ('secretdb', 'secretdb|{lang}.UTF-8|{lang}.UTF-8')
])
def test_databases(host, name, expected_db):
    sql = ("SELECT datname,datcollate,datctype FROM pg_database "
           "WHERE datname='%s'" % name)
    with host.sudo('postgres'):
        out = host.check_output('psql postgres -c "%s" -At' % sql)

    if host.system_info.distribution == 'rocky':
        lang = 'en_US'
    else:
        lang = 'C'
    assert out == expected_db.format(lang=lang)


def test_server_listen(host):
    version = get_version(host)
    if host.system_info.distribution == 'rocky':
        configfile = '/var/lib/pgsql/{version}/data/postgresql.conf'
    else:
        configfile = '/etc/postgresql/{version}/main/postgresql.conf'
    with host.sudo():
        value = configfile.format(version=version)
        f = host.file(value).content_string

    count_listen_addresses = 0
    for line in f.split('\n'):
        if match(r'\s*listen_addresses', line):
            count_listen_addresses += 1
            listen_addresses = line
    assert count_listen_addresses == 1

    assert listen_addresses == "listen_addresses = localhost"


def test_psql_version(host):
    ver = get_version(host)
    out = host.check_output('psql --version')
    assert out.startswith('psql (PostgreSQL) {}.'.format(ver))


# Create

def createdb(host, db, should_pass, password, name):
    try:
        host.check_output(
            'env PGPASSWORD=%s createdb -h localhost -U %s "%s"' %
            (password, name, db))
        assert should_pass
    except Exception:
        assert not should_pass


@pytest.mark.parametrize("name,password,should_pass", [
    ('tester', 'tester123', True),
    ('alice', 'alice123', False),
    ('bob', 'bob123', True),
    ('charles', 'charles123', False),
])
def test_create(host, name, password, should_pass):
    rnd = str(uuid.uuid4())
    createdb(host, rnd, should_pass, password, name)


# Privileges

def psql(host, database, sql, name):
    password = name + '123'
    return host.run(
        'env PGPASSWORD=%s psql %s -h localhost -U %s -c "%s" -At' %
        (password, database, name, sql))


@pytest.mark.parametrize("name,expected_roles", [
    ('tester', 'tester|t|t|f|f|t|f|-1|********||f||'),
    ('alice', 'alice|f|t|f|f|t|f|-1|********||f||'),
    ('bob', 'bob|f|t|f|t|t|f|-1|********||f||'),
])
def test_user_roles(host, name, expected_roles):
    sql = "SELECT * FROM pg_roles WHERE rolname='%s'" % name
    with host.sudo('postgres'):
        out = host.check_output('psql postgres -c "%s" -At' % sql)
    # Everything except the UID at the end
    assert out.startswith(expected_roles)


# Owner and users with SELECT privileges can read
@pytest.mark.parametrize("name,database,table,should_pass", [
    ('tester', 'publicdb', "regular", True),
    ('tester', 'secretdb', "regular", True),
    ('tester', 'secretdb', "password", True),

    ('alice', 'publicdb', "regular", False),
    ('alice', 'secretdb', "regular", True),
    ('alice', 'secretdb', "password", True),

    ('bob', 'publicdb', "regular", True),
    ('bob', 'secretdb', "regular", True),
    ('bob', 'secretdb', "password", False),

    ('charles', 'publicdb', "regular", False),
    ('charles', 'secretdb', "regular", False),
    ('charles', 'secretdb', "password", False),
])
def test_select(host, name, database, table, should_pass):
    sql = "SELECT * FROM " + table
    c = psql(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
    else:
        assert c.rc > 0
        assert 'permission denied' in c.stderr


@pytest.mark.parametrize("name,database,should_pass", [
    ('tester', 'publicdb', True),
    ('tester', 'secretdb', True),

    ('alice', 'publicdb', False),
    ('alice', 'secretdb', True),

    ('bob', 'publicdb', False),
    ('bob', 'secretdb', False),

    ('charles', 'publicdb', False),
    ('charles', 'secretdb', False),
])
def test_create_table(host, name, database, should_pass):
    rnd = 'table_' + str(uuid.uuid4()).replace('-', '')
    sql = "CREATE TABLE %s (text text primary key);" % rnd
    c = psql(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
        assert 'CREATE TABLE' in c.stdout
    else:
        assert c.rc > 0


@pytest.mark.parametrize("name,database,table,should_pass", [
    ('tester', 'publicdb', "regular", True),
    ('tester', 'secretdb', "regular", True),
    ('tester', 'secretdb', "password", True),

    ('alice', 'publicdb', "regular", False),
    ('alice', 'secretdb', "regular", True),
    ('alice', 'secretdb', "password", True),

    ('bob', 'publicdb', "regular", False),
    ('bob', 'secretdb', "regular", False),
    ('bob', 'secretdb', "password", False),

    ('charles', 'publicdb', "regular", False),
    ('charles', 'secretdb', "regular", False),
    ('charles', 'secretdb', "password", False),
])
def test_modify(host, name, database, table, should_pass):
    rnd = str(uuid.uuid4())

    sql = "insert into %s values ('%s')" % (table, rnd)
    c = psql(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
    else:
        assert c.rc > 0
        assert 'permission denied' in c.stderr

    sql = "delete from %s" % table
    c = psql(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
    else:
        assert c.rc > 0
        assert 'permission denied' in c.stderr
