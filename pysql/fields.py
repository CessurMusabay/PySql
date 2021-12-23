from .utils import get_variables


class OnDelete:
    set_null = "SET NULL"
    cascade = "CASCADE"


class DataType:
    def __init__(self, data_type, default, unique, not__null):
        self.__type = data_type
        self.unique = unique
        self.not__null = not__null
        self.default = default

        if unique and not not__null:
            raise Exception(f"{self.__type} unique value have to be not null too.")

    def generate_sql(self, variable_name):
        default = None
        if variable_name == "id":
            return "id INT AUTO_INCREMENT PRIMARY KEY,"

        sql = f"{variable_name} {self.__type}"
        for v in get_variables(self):
            if getattr(self, v):
                if v == "default":
                    default = getattr(self, v)
                    continue
                sql += f" {v.upper()}".replace('__', ' ')
            # print(v.upper().replace('_',''),getattr(self,v))
        if default != None:
            sql += f" DEFAULT {default}"
        return sql + ','


class Integer(DataType):
    def __init__(self, unique=False, not__null=False, default: int = None):
        super().__init__('INT', unique=unique, not__null=not__null, default=default)


class VarChar(DataType):
    def __init__(self, max_length, unique=False, not__null=False, default: str = None):
        super().__init__(f'VARCHAR({max_length})', unique=unique, not__null=not__null, default=default)


class Text(DataType):
    def __init__(self, unique=False, not__null=False, default: str = None):
        super().__init__(f'TEXT', unique=unique, not__null=not__null, default=default)


class ForeignField(DataType):
    def __init__(self, refers_to, on_delete, not_null=False):
        super().__init__("FOREIGN", None, False, False)
        self.refers_to = refers_to
        self.not__null = not_null
        self.on_delete = on_delete

        if self.on_delete == OnDelete.set_null and self.not__null:
            raise Exception("on_delete can not be set_null when object is non nullable")


    def generate_sql(self, variable_name):
        return f"{variable_name} INT{' NOT NULL' if self.not__null else ''},\n\tFOREIGN KEY({variable_name}) REFERENCES {self.refers_to.__name__}(id) ON DELETE {self.on_delete},"
