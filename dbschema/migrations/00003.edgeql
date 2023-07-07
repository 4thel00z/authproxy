CREATE MIGRATION m1fon5snvsoak6do5pikjqnt74auup3hkegpshefoynvvqs536j4kq
    ONTO m1yumre3dfslprqjp3tgdcacpskjk2svyremboy7mwmze2fy7iwnjq
{
  ALTER TYPE default::Auditable {
      ALTER PROPERTY updated_at {
          CREATE REWRITE
              UPDATE 
              USING (std::datetime_of_statement());
      };
  };
  ALTER TYPE default::User {
      CREATE MULTI LINK roles: default::Role;
  };
};
