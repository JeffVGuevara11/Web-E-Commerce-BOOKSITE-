from werkzeug.security import check_password_hash # type: ignore
from flask_login import UserMixin # type: ignore
#Biblioteca para crear contraseña hasheada
#generate_password_hash


class User(UserMixin):
    #Constructor para pasar los datos del usuario
    def __init__(self, id, username, password, fullname="") -> None:
        self.id = id
        self.username = username
        self.password = password
        self.fullname = fullname
    
    #Descencriptamos la contraseña hasheada
    @classmethod
    def check_password(self, hashed_password, password):
        return  check_password_hash(hashed_password, password)

#Hasheamos una contraseña usando la biblioteca importada
#print(generate_password_hash("753951"))



    