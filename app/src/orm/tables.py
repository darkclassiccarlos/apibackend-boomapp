from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Float

from ..settings import meta, engine


alert_types_table = Table(
    "AlertTypes",
    meta,
    Column("id", Integer),
    Column("name", String(100)),
    Column("identifier", String(100)),
    Column("parentID", Integer),
    Column("position", Integer),
    Column("isActive", Boolean),
    schema = "dbo"
)


alerts_table = Table(
    "Alerts",
    meta,
    Column("id", Integer),
    Column("name", String(500)),
    Column("alertTypeId", Integer),
    Column("alertGroupId", Integer),
    Column("isActive", Boolean),
    Column("description", String(500)),
    Column("position", Integer),
    Column("hasNotifications", Boolean),
    schema = "dbo"
)

alerts_groups = Table(
    "AlertGroups",
    meta,
    Column("id", Integer),
    Column("position", Integer),
    Column("parentID", Integer),
    Column("name", String(500)),
    Column("isActive", Boolean),
    schema = "dbo"
)

alerts_lic_table = Table(
    "AlertLicenses",
    meta,
    Column("customerLicenseId", Integer),
    Column("alertId", Integer),
    Column("creationDate", DateTime),
    schema = "dbo"
)

customer_lic_table = Table(
    "CustomerLicenses",
    meta,
    Column("id", Integer),
    Column("customerId", Integer),
    Column("masterLicensesProviderId", Integer),
    Column("parentId", Integer),
    Column("netsuiteServiceId", Integer),
    Column("licenseNumber", Integer),
    Column("licenseCode", String(100)),
    Column("providerPurchaseDate", DateTime),
    Column("creationDate", DateTime),
    Column("isActive", Boolean),
    schema = "dbo"
)



# Tablas para el listado general de office 365

customer_table = Table(
    "Customers",
    meta,
    Column("id", Integer),
    Column("name", String(200)),
    Column("countryId", Integer),
    Column("netsuiteCustomerId", Integer),
    Column("customerTypesId", Integer),
    Column("isActive", Boolean),
    schema = "dbo"
)


office_details_table = Table(
    "Office365Details",
    meta,
    Column("id", Integer),
    Column("companyname", String(200)),
    Column("customerIdPlatform", String(50)),
    Column("contractId", String(50)),
    Column("productDisplayName", String(300)),
    Column("billingStartDateToday", String(50)),
    Column("actualChargeInterval", String(50)),
    Column("daysBilled", String(50)),
    Column("billableParameters", String(200)),
    Column("costsofUnit", Float),
    Column("udrcValue", Float),
    Column("seats", Float),
    Column("costs", Float),
    Column("region", String(50)),    
    Column("customerLicenceId", Integer),
    Column("accountId", Integer),
    schema = "dbo"
)


master_license_provider_table = Table(
    "MasterLicenseProvider",
    meta,
    Column("id", Integer),
    Column("providerId", Integer),
    Column("licensingMasterId", Integer),
    Column("providerRegionId", Integer),
    Column("isActive", Boolean),
    schema = "dbo"
)


licensing_master_table = Table(
    "LicensingMaster",
    meta,
    Column("id", Integer),
    Column("name", String(50)),
    Column("description", String(200)),
    Column("typeLicenseId", Integer),
    Column("isActive", Boolean),
    schema = "dbo"
)



provider_region_table = Table(
    "ProviderRegion",
    meta,
    Column("id", Integer),
    Column("name", String(200)),
    Column("isActive", Boolean),
    schema = "dbo"
)


rules_table = Table(
    "AlertRules",
    meta,
    Column("id", Integer),
    Column("idAlert", Integer),
    Column("name", String(50)),
    Column("condition", String(50)),
    Column("value", Integer),
    Column("isPercentage", Boolean),  
    Column("color", String(50)),
    Column("isActive", Boolean),  
    Column("secondCondition", String(50)),
    Column("secondValue", Integer),
    schema = "dbo"
)


areas_table = Table(
    "Areas",
    meta,
    Column("id", Integer),
    Column("name", String(50)),
    Column("identifier", String(50)),
    schema = "dbo"
)


areasalerts_table = Table(
    "AlertsAreas",
    meta,
    Column("idAlert", Integer),
    Column("idArea", Integer),
    schema = "dbo"
)


meta.create_all(engine)
