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
