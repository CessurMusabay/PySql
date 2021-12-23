from pysql.fields import Integer, VarChar, ForeignField, OnDelete,Text
from pysql.models import Model
from pysql.utils import create_tables


class User(Model):
    username = VarChar(max_length=128)
    password = VarChar(max_length=128)
    email = VarChar(max_length=64)


class Review(Model):
    review = VarChar(max_length=256, not__null=True)
    point = Integer()
    user = ForeignField(refers_to=User, on_delete=OnDelete.cascade)
    content = Text()


if __name__ == '__main__':
    create_tables([

        User(),
        Review(),
    ])
    for obj in User.fetch("username LIKE " + f"'c%'"):
        print(obj.values)








