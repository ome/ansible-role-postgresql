# Changes in Version 5

## Summary of breaking changes

- PostgreSQL 11 is no longer supported by this role.
- PostgreSQL 9.5 is no longer supported by this role.
- `postgresql_install_server` is removed, the server is always configured, use `ome.postgresql_client` to install just the client.
- `postgresql_install_extensions` is removed, extension packages are always installed.


# Changes in Version 4

## Summary of breaking changes

- `postgresql_version` is now a required variable. The previous default of "9.4" is no longer supported.

  See [README.md](README.md) for full documentation

# Changes in Version 3

## Summary of breaking changes

- `postgresql.conf` is templated instead of making in-line modifications to the distribution configuration
- `CONNECT` and `public` schema `USAGE` privileges are explicitly granted to database users
- `postgresql_users_databases` has been replaced by two variables which are both required
  - `postgresql_databases`: The databases to be created
  - `postgresql_users`: The users to be created, and the databases they have access to

  See [README.md](README.md) for full documentation


# Changes in Version 2

## Summary of breaking changes
- PostgreSQL 9.3 is no longer supported
