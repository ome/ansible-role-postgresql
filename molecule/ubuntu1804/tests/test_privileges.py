import os
import pytest
import testinfra.utils.ansible_runner
import uuid

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('server')

CMD = 'env PGPASSWORD=%s psql %s -h localhost -U %s -c "%s" -At'


def run(host, database, sql, name):
    password = name + '123'
    return host.run(CMD % (password, database, name, sql))


# Owner and users with SELECT privileges can read
@pytest.mark.parametrize("name,database,table,should_pass", [
    ('alice', 'publicdb', "regular", True),
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
    c = run(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
    else:
        assert c.rc > 0
        assert 'permission denied' in c.stderr


# Default PUBLIC allows anyone with access to create a table
# This is removed if restrict was set
@pytest.mark.parametrize("name,database,should_pass", [
    ('alice', 'publicdb', True),
    ('alice', 'secretdb', True),

    ('bob', 'publicdb', True),
    ('bob', 'secretdb', False),

    # TODO: charles can create tables in publicdb, is this expected?
    ('charles', 'publicdb', True),
    ('charles', 'secretdb', False),
])
def test_create_table(host, name, database, should_pass):
    rnd = 'table_' + str(uuid.uuid4()).replace('-', '')
    sql = "CREATE TABLE %s (text text primary key);" % rnd
    c = run(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
        assert 'CREATE TABLE' in c.stdout
    else:
        assert c.rc > 0


@pytest.mark.parametrize("name,database,table,should_pass", [
    ('alice', 'publicdb', "regular", True),
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
    c = run(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
    else:
        assert c.rc > 0
        assert 'permission denied' in c.stderr

    sql = "delete from %s" % table
    c = run(host, database, sql, name)
    if should_pass:
        assert c.rc == 0
    else:
        assert c.rc > 0
        assert 'permission denied' in c.stderr
