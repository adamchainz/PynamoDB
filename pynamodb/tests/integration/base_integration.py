"""
Runs tests against dynamodb
"""
from __future__ import print_function
import time
from pynamodb.connection import Connection
from pynamodb.types import STRING, HASH, RANGE

table_name = 'pynamodb-ci'
conn = Connection()

# For use with a fake dynamodb connection
# See: http://aws.amazon.com/dynamodb/developer-resources/
#conn = Connection(host='http://localhost:8000')

print("conn.describe_table...")
table = conn.describe_table(table_name)

if table is None:
    params = {
        'read_capacity_units': 1,
        'write_capacity_units': 1,
        'attribute_definitions': [
            {
                'attribute_type': STRING,
                'attribute_name': 'Forum'
            },
            {
                'attribute_type': STRING,
                'attribute_name': 'Thread'
            },
            {
                'attribute_type': STRING,
                'attribute_name': 'AltKey'
            }
        ],
        'key_schema': [
            {
                'key_type': HASH,
                'attribute_name': 'Forum'
            },
            {
                'key_type': RANGE,
                'attribute_name': 'Thread'
            }
        ],
        'global_secondary_indexes': [
            {
                'index_name': 'alt-index',
                'key_schema': [
                    {
                        'KeyType': 'HASH',
                        'AttributeName': 'AltKey'
                    }
                ],
                'projection': {
                    'ProjectionType': 'KEYS_ONLY'
                },
                'provisioned_throughput': {
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                }
            }
        ],
        'local_secondary_indexes': [
            {
                'index_name': 'view-index',
                'key_schema': [
                    {
                        'KeyType': 'HASH',
                        'AttributeName': 'number'
                    }
                ],
                'projection': {
                    'ProjectionType': 'KEYS_ONLY'
                }
            }
        ]
    }
    print("conn.create_table...")
    conn.create_table(table_name, **params)

while table is None:
    time.sleep(2)
    table = conn.describe_table(table_name)
while table['TableStatus'] == 'CREATING':
    time.sleep(2)
    table = conn.describe_table(table_name)
print("conn.list_tables")
conn.list_tables()
print("conn.update_table...")

#conn.update_table(table_name, read_capacity_units=2, write_capacity_units=2)
table = conn.describe_table(table_name)
while table['TableStatus'] != 'ACTIVE':
    time.sleep(2)
    table = conn.describe_table(table_name)

print("conn.put_item")
conn.put_item(
    table_name,
    'item1-hash',
    range_key='item1-range',
    attributes={'foo': {'S': 'bar'}},
    expected={'Forum': {'Exists': False}}
)
conn.get_item(
    table_name,
    'item1-hash',
    range_key='item1-range'
)
conn.delete_item(
    table_name,
    'item1-hash',
    range_key='item1-range'
)

items = []
for i in range(10):
    items.append(
        {"Forum": "FooForum", "Thread": "thread-{0}".format(i)}
    )
print("conn.batch_write_items...")
conn.batch_write_item(
    table_name,
    put_items=items
)
print("conn.batch_get_items...")
data = conn.batch_get_item(
    table_name,
    items
)
print("conn.query...")
conn.query(
    table_name,
    "FooForum",
    key_conditions={'Thread': {'ComparisonOperator': 'BEGINS_WITH', 'AttributeValueList': ['thread']}}
)
print("conn.scan...")
conn.scan(
    table_name,
)
print("conn.delete_table...")
#conn.delete_table(table_name)
