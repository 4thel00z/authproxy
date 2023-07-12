SELECT Role {name,scopes,tenant,created_at}
FILTER
.tenant.name = <str>$tenant;
