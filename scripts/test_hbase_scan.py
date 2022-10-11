from friendships.hbase_models import HBaseFollowing

table = HBaseFollowing.get_table()


def print_rows(rows):
    for row_key, row_data in rows:
        print(row_key, row_data)


rows = table.scan()
print_rows(rows)
# row_start default is the first row in the table
rows = table.scan(row_start=b'1000000000000000:1658351458551032', limit=1)
print_rows(rows)
rows = table.scan(row_prefix=b'1000000000000000', limit=2)
print_rows(rows)

# iterate from the end up
rows = table.scan(row_start=b'1000000000000000:1658351458551032', limit=1, reverse=True)
print_rows(rows)

# pseudo code:
# for row_start -> row_stop:
#     if reverse:
#         row_start--
#     else:
#         row_start++