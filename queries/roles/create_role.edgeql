INSERT Role {
	name := <str>$tenant,
	scopes := <array<str>>$scopes,
	tenant := (SELECT Tenant FILTER Tenant.name = <str>$tenant_name),
};
