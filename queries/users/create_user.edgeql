INSERT User {
  username := <str>$username,
  email := <str>$email,
  first_name := <str>$first_name,
  last_name := <str>$last_name,
  password_hash := <str>$password_hash,
  tenant := (SELECT Tenant FILTER Tenant.name = <str>$tenant_name),
  roles := (SELECT Role FILTER Role.tenant.name = <str>$tenant_name AND Role.name in <str>$roles)
};
