from .database import Database


def get_variables(class_):
    variables = []
    for s in dir(class_):
        if not s.startswith('_'):
            if not callable(getattr(class_, s)):
                variables.append(s)
    return variables


def create_tables(tables: list):
    d = Database()
    d.clear()
    for c in tables:
        d.execute(c.generate_sql())

    d.close()
