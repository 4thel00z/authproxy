CREATE MIGRATION m1l4fn45zy2ntpjq42bbu5ghnz2yflxeove7oed3t2kdvaevwekhrq
    ONTO initial
{
  CREATE ABSTRACT TYPE default::Auditable {
      CREATE REQUIRED PROPERTY created_at: std::datetime {
          SET default := (std::datetime_current());
          SET readonly := true;
      };
      CREATE REQUIRED PROPERTY updated_at: std::datetime {
          SET default := (std::datetime_current());
      };
  };
  CREATE TYPE default::Tenant EXTENDING default::Auditable {
      CREATE REQUIRED PROPERTY name: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE ABSTRACT TYPE default::IsTenantData {
      CREATE REQUIRED LINK tenant: default::Tenant;
      CREATE ANNOTATION std::description := 'This is a type to use for data that needs tenant access scope/semantics';
  };
  CREATE TYPE default::User EXTENDING default::Auditable, default::IsTenantData {
      CREATE REQUIRED PROPERTY username: std::str;
      CREATE CONSTRAINT std::exclusive ON ((.tenant, .username));
      CREATE REQUIRED PROPERTY disabled: std::bool {
          SET default := false;
      };
      CREATE REQUIRED PROPERTY email: std::str;
      CREATE REQUIRED PROPERTY first_name: std::str;
      CREATE REQUIRED PROPERTY last_name: std::str;
      CREATE REQUIRED PROPERTY password_hash: std::str;
  };
  CREATE ABSTRACT TYPE default::IsUserData {
      CREATE ANNOTATION std::description := 'This is a type to use for data that needs user access scope/semantics';
      CREATE REQUIRED LINK user: default::User;
  };
};
