ver_lookup = {
	"postgresql-94-all": "9.4",
	"postgresql-95-localhost": "9.5",
	"postgresql-96-localhost": "9.6",
	"postgresql-10-localhost": "10"

}

def get_version(hostname):

    return ver_lookup[hostname]
