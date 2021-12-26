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
        class_name = c.__class__.__name__
        d.execute(c.generate_sql())
        d.execute(f"""
            CREATE TRIGGER IF NOT EXISTS on_delete_{class_name} BEFORE DELETE
            ON {class_name}
            FOR EACH ROW
            BEGIN
              INSERT INTO Log(log) VALUES(CONCAT('{class_name}.',OLD.id,' has been deleted'));
            END
        """)

    d.close()
