DELETE Role
FILTER
.name = <str>$name AND .tenant.name = <str>$tenant LIMIT 1;
