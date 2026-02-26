import os
import sys
import django
from django.conf import settings
from django.db import connections
from django.core.management import call_command
from unittest.mock import MagicMock, PropertyMock

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Patch the connection
connection = connections['default']
connection.ensure_connection = MagicMock()
connection.connect = MagicMock()
connection.close = MagicMock()
connection._cursor = MagicMock()

# Mock the cursor context manager
cursor_mock = MagicMock()
connection.cursor = MagicMock()
connection.cursor.return_value.__enter__.return_value = cursor_mock
connection._cursor = MagicMock(return_value=cursor_mock)

def side_effect_mogrify(query, params=None):
    q_str = query.decode('utf-8') if isinstance(query, bytes) else query
    if params is None:
        return q_str.encode('utf-8')
    
    # Simple interpolation for %s
    try:
        quoted_params = []
        for p in params:
            if isinstance(p, str):
                quoted_params.append(f"'{p}'")
            elif p is None:
                quoted_params.append('NULL')
            else:
                quoted_params.append(str(p))
        return (q_str % tuple(quoted_params)).encode('utf-8')
    except Exception:
        # If interpolation fails, return query with placeholders (better than MagicMock)
        return q_str.encode('utf-8')

cursor_mock.mogrify.side_effect = side_effect_mogrify

# Mock features
# We need to ensure we don't trigger actual DB inspection
connection.features.has_native_uuid_field = True
connection.features.supports_json_field = True
connection.features.supports_timezones = True
# Mock pg_version to a high number (e.g., 150000)
type(connection).pg_version = PropertyMock(return_value=150000)

# Also mock get_sequences which might be called
connection.ops.get_sequences = MagicMock(return_value=[])

from django.db.migrations.executor import MigrationExecutor

# Use Executor to get the plan
executor = MigrationExecutor(connection)
targets = executor.loader.graph.leaf_nodes()
full_plan = executor.migration_plan(targets)

print(f"Found {len(full_plan)} migrations to generate SQL for.")

with open('schema.sql', 'w') as f:
    for migration, backwards in full_plan:
        app_label = migration.app_label
        migration_name = migration.name
        
        # print(f"Generating SQL for {app_label} {migration_name}...")
        
        from io import StringIO
        out = StringIO()
        
        try:
            # We call sqlmigrate directly
            call_command('sqlmigrate', app_label, migration_name, stdout=out)
            sql = out.getvalue()
            f.write(f"-- {app_label} {migration_name}\n")
            f.write(sql)
            f.write("\n\n")
        except Exception as e:
            print(f"Error generating SQL for {app_label} {migration_name}: {e}")

