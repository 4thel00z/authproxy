SELECT Role {name,scopes,tenant,created_at}
FILTER
.name = <str>$name AND .tenant.name = <str>$tenant LIMIT 1;
