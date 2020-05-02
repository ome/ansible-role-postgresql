# Enumerate instead of parsing so we pick up errors if a host is added/changed
ver_lookup = {
    "postgresql-96-c7": ("9.6", "centos"),
    "postgresql-10-c7": ("10", "centos"),
    "postgresql-11-c7": ("11", "centos"),
    "postgresql-12-c7": ("12", "centos"),

    "postgresql-96-u1804": ("9.6", "ubuntu"),
    "postgresql-10-u1804": ("10", "ubuntu"),
    "postgresql-11-u1804": ("11", "ubuntu"),
    "postgresql-12-u1804": ("12", "ubuntu"),
}


def get_distribution(hostname):
    return ver_lookup[hostname][1]


def get_version(hostname):
    return ver_lookup[hostname][0]
