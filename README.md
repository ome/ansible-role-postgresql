Postgresql
==========

[![Build Status](https://travis-ci.org/ome/ansible-role-postgresql.svg)](https://travis-ci.org/ome/ansible-role-postgresql)
[![Ansible Role](https://img.shields.io/ansible/role/41080.svg)](https://galaxy.ansible.com/ome/postgresql/)

Install upstream PostgreSQL server.

Optionally creates users and databases.
If you wish to use your distribution's packages then do not use this role.


Role Variables
--------------

Defaults: `defaults/main.yml`

- `postgresql_version`: The PostgreSQL major version: `9.6`, `10`, `11`, `12`
- `postgresql_package_version`: The PostgreSQL full version, leave this empty to use the latest minor release from `postgresql_version`, ignored on Ubuntu

The following parameters will be ignored if `postgresql_install_server: False`:
- `postgresql_databases`: List of dictionaries of databases.
  Items should be of the form:
  - `name`: Database name
  - `owner`: Owner role (optional)
  - `lc_collate`: Collation order (LC_COLLATE) to use in the database
  - `lc_ctype`: Character classification (LC_CTYPE) to use in the database
  - `encoding`: Encoding of the database, default `UTF-8`
  - `template`: Template used to create the database
  - `restrict`: If `True` revoke default `PUBLIC` privileges from database and `public` schema, default `False`
- `postgresql_users`: List of dictionaries of users.
  Items should be of the form:
  - `user`: Database username
  - `password`: Database user password
  - `databases`: List of databases that user can connect to, required but can be empty `[]`
  - `roles`: Role attribute flags, optional
  If you want the user to have restricted access see the section below on Restricted users.
- `postgresql_server_listen`: Listen on these interfaces, default `localhost`, use `'*'` for all
- `postgresql_server_conf`: Dictionary of additional postgresql.conf options
- `postgresql_server_auth_local`: Whether to allow the default postgres local authentication (default `True`)
- `postgresql_server_auth`: List of dictionaries of authorisation parameters, if omitted the default local authentication only will be enabled. Items should be of the form:
  - `database`: Name of the database
  - `user`: Username
  - `address`: Address from which connections will be made
  - `method`: Ignore this unless you really know what you are doing
- `postgresql_server_chown_datadir`: If `True` recursively reset the owner and group of the postgres datadir, default `False`, use this when you have an existing datadir with incorrect owner/group


Restricted databases
--------------------

In general it is not possible to create users with restricted access (e.g. read-only users) until a schema has been populated.
This role optionally removes the default PUBLIC privileges from all databases, then grants:
- `ALL` privileges to the database owner if specified (`postgresql_databases[].owner`)
- `CONNECT` privilege to the database, and `USAGE` privilege on the `public` schema, to databases listed for each user (`postgresql_users[].databases`)

If you wish to created a restricted user set the `databases` field in `postgresql_users` to `[]`, and use the [Ansible `postgresql_privs`](http://docs.ansible.com/ansible/latest/postgresql_privs_module.html) module to grant access after the database schema has been created.

An example can be seen in [`playbook.yml`](playbook.yml).


Example Playbook
----------------

    # Simple example relying on the default Postgres PUBLIC privileges
    # which allow access to all users
    - hosts: localhost
      roles:
      - role: postgresql
        postgresql_server_listen: "'*'"
        postgresql_server_auth:
        - database: publicdb
          user: alice
          address: 192.168.1.0/24
        postgresql_databases:
        - name: publicdb
        postgresql_users:
        - user: alice
          password: alice123
          databases: []


    # Advanced example with no default access to databases
    # This sets up minimal privileges for `bob`, you will need to configure
    # additional privileges yourself
    - hosts: localhost
      roles:
      - postgresql
      vars:
      - postgresql_databases:
        - name: secretdb
          owner: alice
          restrict: True
      - postgresql_users:
        - user: alice
          password: alice123
          databases: [secretdb]
        - user: bob
          password: bob123
          databases: []


Author Information
------------------

ome-devel@lists.openmicroscopy.org.uk
