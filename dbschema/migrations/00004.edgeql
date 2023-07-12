CREATE MIGRATION m1ofahzbxozdwjuwsnbcahnm6lpbdsogkh2sx5zlsqdpg7a4rpdbhq
    ONTO m1fon5snvsoak6do5pikjqnt74auup3hkegpshefoynvvqs536j4kq
{
  ALTER TYPE default::IsTenantData {
      ALTER LINK tenant {
          ON TARGET DELETE DELETE SOURCE;
      };
  };
};
