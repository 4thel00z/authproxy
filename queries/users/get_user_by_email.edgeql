SELECT User {
	id,
	username,
	email,
	first_name,
	last_name,
	password_hash,
	disabled
} FILTER .email = <str>$email;
