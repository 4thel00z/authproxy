module default {
	abstract type Auditable {
		required property created_at -> datetime {
			readonly := true;
			default := datetime_current();
		};
		
		required property updated_at -> datetime {
			default := datetime_current();
		};
	}


	abstract type IsUserData {
		annotation description := "This is a type to use for data that needs user access scope/semantics";
		required link user -> User;
	}


	abstract type IsTenantData {
		annotation description := "This is a type to use for data that needs tenant access scope/semantics";
		required link tenant -> Tenant;
	}
	

	type Tenant extending Auditable {
		required property name -> str{
			constraint exclusive;
		};
	}

	type User extending Auditable, IsTenantData {
	    required property username -> str;
	    required property first_name -> str;
	    required property last_name -> str;
	    required property email -> str;
	    required property password_hash -> str;
	    required property disabled -> bool {
		default := false;
	    };
	    constraint exclusive on ( (.tenant, .username) );
	}




}
