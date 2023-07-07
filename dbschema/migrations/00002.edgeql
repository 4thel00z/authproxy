CREATE MIGRATION m1yumre3dfslprqjp3tgdcacpskjk2svyremboy7mwmze2fy7iwnjq
    ONTO m1l4fn45zy2ntpjq42bbu5ghnz2yflxeove7oed3t2kdvaevwekhrq
{
  CREATE TYPE default::Role EXTENDING default::Auditable, default::IsTenantData {
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE REQUIRED PROPERTY scopes: array<std::str> {
          SET default := (<array<std::str>>[]);
      };
  };
};
