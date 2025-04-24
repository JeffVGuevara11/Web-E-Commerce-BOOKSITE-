from .entities.User import User
from werkzeug.security import generate_password_hash # type: ignore


class ModelUser():
    @classmethod
    def login(self, db, user):
        try:
            cursor = db.connection.cursor()
            #los datos devueltos con esta consulta SQL son devueltos en forma de tupla
            sql = """SELECT  id, username, password, fullname FROM user where  username = '{}'""".format(user.username)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user= User(row[0],row[1],User.check_password(row[2], user.password),row[3])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def get_by_id(self, db, id):
        try:
            cursor = db.connection.cursor()
            sql = "SELECT id, username, fullname FROM user where id = {}".format(id)
            cursor.execute(sql)
            #Regresamos una unica dupla con los datos de la consulta 
            row = cursor.fetchone()
            if row != None:
                return User(row[0], row[1], None, row[2])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)
        
    @classmethod
    def list_user(cls, db):
        cursor  = db.connection.cursor()
        cursor.execute("SELECT * FROM  user")
        #Guardamos una lista de tuplas con todas las filas consultadas mediante la query
        myresult = cursor.fetchall()
        #Convertimos los datos a diccionario
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in myresult:
            insertObject.append(dict(zip(columnNames, record)))
        cursor.close()
        return insertObject
    
    @classmethod
    def create_user(cls, db, username, password, fullname=""):
        cursor = db.connection.cursor()
        try:
            # Hasheamos la contraseña antes de guardarla
            hashed_password = generate_password_hash(password)
            cursor.execute("""
                INSERT INTO user (username, password, fullname)
                VALUES (%s, %s, %s)
            """, (username, hashed_password, fullname))
            db.connection.commit()
        except Exception as e:
            db.connection.rollback()
            raise e
        finally:
            cursor.close()
        
        
        