def get_version(host):
    variables = host.ansible.get_variables()
    return variables["postgresql_version"]
