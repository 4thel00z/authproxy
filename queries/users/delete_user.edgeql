DELETE User FILTER .username = <str>$username AND .tenant = (SELECT Tenant FILTER Tenant.name = <str> $tenant);
