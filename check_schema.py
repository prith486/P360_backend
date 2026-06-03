import os
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv

load_dotenv('c:\\Users\\PRIHTVIRAJ\\Desktop\\P360_BACKEND\\placement360-backend\\.env')
db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)
inspector = inspect(engine)

tables = [
    'students',
    'faculty',
    'questions',
    'assessments',
    'assessment_questions',
    'assessment_attempts',
    'submissions',
    'admin_activity_log'
]

print("--- SCHEMA DUMP ---")
for table in tables:
    print(f"\nTABLE: {table}")
    if not inspector.has_table(table):
         print("NOT FOUND")
         continue
    
    columns = inspector.get_columns(table)
    pk = inspector.get_pk_constraint(table)
    fks = inspector.get_foreign_keys(table)
    
    pk_cols = pk['constrained_columns'] if pk else []
    
    for col in columns:
        col_name = col['name']
        col_type = col['type']
        nullable = col['nullable']
        default = col.get('default')
        
        flags = []
        if col_name in pk_cols:
            flags.append("PK")
        for fk in fks:
            if col_name in fk['constrained_columns']:
                flags.append(f"FK -> {fk['referred_table']}.{fk['referred_columns'][fk['constrained_columns'].index(col_name)]}")
        
        nullable_str = "NULL" if nullable else "NOT NULL"
        default_str = f"DEFAULT {default}" if default is not None else ""
        flags_str = f"[{', '.join(flags)}]" if flags else ""
        
        print(f"  - {col_name} ({col_type}): {nullable_str} {default_str} {flags_str}")

print("\n--- ENUMS ---")
with engine.connect() as conn:
    enums = conn.execute(text("SELECT t.typname, e.enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid = t.oid ORDER BY t.typname, e.enumsortorder")).fetchall()
    enum_dict = {}
    for enum_name, enum_val in enums:
        if enum_name not in enum_dict:
             enum_dict[enum_name] = []
        enum_dict[enum_name].append(enum_val)
    
    for enum_name, enum_vals in enum_dict.items():
         print(f"{enum_name}: {', '.join(enum_vals)}")

print("\n--- INDEXES ---")
for table in tables:
    if not inspector.has_table(table): continue
    indexes = inspector.get_indexes(table)
    if indexes:
       print(f"\nIndexes for {table}:")
       for idx in indexes:
           # Postgres inspector sometimes provides dialect_options
           opts = idx.get('dialect_options', {}).get('postgresql_using', 'btree')
           print(f"  - {idx['name']} (using {opts}): cols={idx['column_names']}, unique={idx['unique']}")
