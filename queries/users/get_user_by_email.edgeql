SELECT User {
	id,
	username,
	email,
	first_name,
	last_name,
	password_hash,
	disabled,
	roles: { name, scopes},
	tenant: { name }
} FILTER .email = <str>$email AND .tenant.name = <str>$tenant LIMIT 1; 
