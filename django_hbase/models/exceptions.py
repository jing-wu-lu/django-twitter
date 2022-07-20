class EmptyColumnError(Exception):
    pass


class BadRowKeyError(Exception):

    def __str__(self):
        return 'created_at is missing in row key'

