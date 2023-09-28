# from sqlalchemy import Column, Table, MetaData
# from sqlalchemy.sql.sqltypes import Integer, String, Boolean, DateTime, Float

# from ..settings import db_manager#, meta, engine


# engine = db_manager.get_engine
# meta = db_manager.get_meta

# users_table = Table(
#     "users",
#     meta,
#     Column("id", Integer),
#     Column("user", String(255)),
#     Column("pass", String(255)),
#     #schema = "dbo"
# )

# alerts_table = Table(
#     "Alerts",
#     meta,
#     Column("id", Integer),
#     Column("name", String(500)),
#     Column("alertTypeId", Integer),
#     Column("alertGroupId", Integer),
#     Column("isActive", Boolean),
#     Column("description", String(500)),
#     Column("position", Integer),
#     Column("hasNotifications", Boolean),
#     schema = "dbo"
# )

# meta.create_all(engine)
