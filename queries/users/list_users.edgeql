SELECT User{username,created_at,tenant:{name}, first_name,last_name,email,password_hash,disabled,roles:{scopes,name}} FILTER .tenant = (SELECT Tenant FILTER Tenant.name = <str> $tenant);
