from .fields import Integer, ForeignField
from .utils import get_variables
from pysql import database


class Model:
    id = Integer(unique=True, not__null=True)

    def generate_sql(self):
        sql = "CREATE TABLE IF NOT EXISTS " + self.__class__.__name__ + "( \n"
        for v in get_variables(self):
            if v != 'values':
                sql += f"\t{getattr(self, v).generate_sql(v)}\n"
        sql = sql.strip().removesuffix(',') + "\n);"
        return sql

    def __init__(self, **kwargs):
        self.values = kwargs

    def __validate_field(self, v, value):
        if value == None:
            if getattr(self, v).not__null:
                raise Exception(f"{self.__class__.__name__}.{v} can not be NULL")

        if isinstance(value, Model):
            value = value.values['id']
        return True if value != None else False, value

    def create(self):
        def generate_sql(values):
            VALUES = str(tuple(values.values())).replace(',)', ')')
            KEYS = str(tuple(values.keys())).replace(',)', ')').replace("'", '')
            sql = f"INSERT INTO {self.__class__.__name__}{KEYS} VALUES{VALUES}"
            return sql

        values = {}
        variables = get_variables(self)
        variables.remove('id')
        variables.remove('values')

        for v in variables:
            valid, value = self.__validate_field(v, self.values[v] if v in self.values.keys() else None)
            if valid: values[v] = value

        d = database.Database()
        id = d.create_object(generate_sql(values))
        self.values['id'] = id
        d.close()
        return id

    def delete(self):
        sql = f"DELETE FROM {self.__class__.__name__} WHERE id={self.values['id']};"
        d = database.Database()
        d.execute(sql)
        d.close()

    def update(self, **kwargs):
        def generate_sql(values):
            sql = f"UPDATE {self.__class__.__name__} SET "
            for v in values:
                sql += f"{v}="
                if type(values[v]) == str:
                    sql += f"'{values[v]}',"
            return sql.removesuffix(',')

        values = {}
        for v in self.values:
            if v in kwargs:
                valid, value = self.__validate_field(v, kwargs[v])
                if valid:
                    values[v] = value
                    self.values[v] = value

        d = database.Database()
        sql = generate_sql(self.values) + f" WHERE id={self.values['id']};"
        d.execute(sql)
        d.close()

    @classmethod
    def fetch(cls, query):
        variables = get_variables(cls)
        keys = str(variables).replace(']', '').replace('[', '').replace("'", '')
        sql = f"SELECT {keys} FROM {cls.__name__} WHERE {query};"
        d = database.Database()
        data = d.execute(sql)
        d.close()
        objs = []
        for d in data:
            result = {}
            for i, key in enumerate(variables):
                obj = getattr(cls, key)
                if isinstance(obj, ForeignField):
                    result[key] = obj.refers_to.get(id=d[i])
                else:
                    result[key] = d[i]
            obj = cls()
            obj.values = result
            objs.append(obj)
        return objs

    @classmethod
    def get(cls, id):
        variables = get_variables(cls)
        keys = str(variables).replace(']', '').replace('[', '').replace("'", '')

        sql = f"SELECT {keys} FROM {cls.__name__} WHERE id={id} ORDER BY id;"

        d = database.Database()
        data = d.execute(sql)
        d.close()

        result = {}
        if len(data) > 0:
            for i, key in enumerate(variables):
                obj = getattr(cls, key)
                if isinstance(obj, ForeignField):
                    result[key] = obj.refers_to.get(id=data[0][i])
                else:
                    result[key] = data[0][i]
            obj = cls()
            obj.values = result
            return obj
        return None

    def join(self, foreign_class, foreign_field, join_type="INNER JOIN", group_by=None):
        self_variables = get_variables(self)
        self_variables.remove("values")
        foreign_variables = get_variables(foreign_class)
        self_variables = [self.__class__.__name__ + '.' + a for a in self_variables]
        foreign_variables = [foreign_class.__name__ + '.' + a for a in foreign_variables]
        sql = f"SELECT {','.join(self_variables)},{','.join(foreign_variables)} FROM {self.__class__.__name__} INNER JOIN {foreign_class.__name__} ON {foreign_class.__name__}.id={self.__class__.__name__}.{foreign_field}"
        if group_by != None:
            sql += " GROUP BY " + group_by
        d = database.Database()
        data = d.execute(sql)
        d.close()
        return data
