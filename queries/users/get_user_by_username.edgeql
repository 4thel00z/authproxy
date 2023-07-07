SELECT User {
	id,
	username,
	email,
	first_name,
	last_name,
	password_hash,
	disabled,
	tenant: {
	 name
	},
	roles: {
	  name,
	  scopes
	}
} FILTER .username = <str>$username AND .tenant.name = <str>$tenant LIMIT 1;
