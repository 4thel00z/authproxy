INSERT Role {
	name := <str>$name,
	scopes := <array<str>>$scopes,
	tenant := (SELECT Tenant FILTER Tenant.name = <str>$tenant),
};
