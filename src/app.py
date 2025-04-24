from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response # type: ignore
from config import config
#Nos permite proteger el login
from flask_wtf import CSRFProtect # type: ignore
from flask_mysqldb import MySQL # type: ignore
#login_user permite logear o iniciar sesion de un usuario
#logout_user permite cerrar la sesion del usuario
#login_required permite bloquear rutas si no hay un inicio de sesion de un usuario
from flask_login import LoginManager, login_user, logout_user, login_required, current_user # type: ignore
from werkzeug.security import generate_password_hash  # type: ignore
from validate_email_address  import validate_email # type: ignore


#Models:
from models.ModelUser import ModelUser

#Entities:
from models.entities.User import User

app = Flask(__name__)

csrf = CSRFProtect()

db = MySQL(app)

login_manager_app = LoginManager(app)

@login_manager_app.user_loader
def load_user(id):
    return ModelUser.get_by_id(db, id)


@app.route('/home')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('biblioteca_admin'))
    response = make_response(render_template('home.html'))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def index():
    #redireccionamos la ruta principal directamente a la vista home
    return redirect(url_for('home'))

@app.route('/login/createUser', methods = ['GET','POST'])
def createUser():
    if current_user.is_authenticated:
        return redirect(url_for('biblioteca_admin'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name', '')  # opcional

        if not username.endswith('@gmail.com'):
            flash('El correo debe ser de Gmail (@gmail.com)')
            return redirect(url_for('createUser'))

        # Verifica si ya existe el usuario
        cursor = db.connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        existing = cursor.fetchone()
        cursor.close()

        if existing:
            flash('Este usuario ya está registrado.')
            return redirect(url_for('createUser'))

        # Crear el usuario
        try:
            ModelUser.create_user(db, username, password, name)
            flash('Usuario creado correctamente')
        except Exception as e:
            db.connection.rollback()
            flash(f'Error al crear el usuario: {str(e)}')

        return redirect(url_for('createUser'))

    # GET: Mostrar la página de creación
    Object_created = ModelUser.list_user(db)
    response = make_response(render_template('createUser.html', data=Object_created))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

#AGREGAR, ELIMINAR Y EDITAR UN LIBRO

@app.route('/admin_libros/Administraciondelibros/RegistrarLibro', methods = ['POST'])
def addLibro():
    titulo = request.form['titulo']
    autor = request.form['autor']
    editorial = request.form['editorial']
    anio_publicacion = request.form['anio_publicacion']
    genero = request.form['genero']
    descripcion = request.form['descripcion']
    imagen = request.form['imagen']
    
    if titulo and autor and editorial and anio_publicacion and genero and descripcion and imagen:
        cursor = db.connection.cursor()
        sql = "INSERT INTO libro (titulo, autor, editorial, anio_publicacion, genero, descripcion, imagen) VALUES (%s, %s, %s,%s, %s, %s,%s)"
        data = (titulo, autor, editorial, anio_publicacion, genero, descripcion, imagen)
        cursor.execute(sql, data)
        db.connection.commit()
        return redirect(url_for('Administraciondelibros'))
    else:
        flash("Es obligatorio el llenado de todos los campos para el registro del libro")
        return redirect(url_for('Administraciondelibros'))
    

@app.route('/delete/<string:id>')
def delete(id):
    
    '''cursor1 =db.connection.cursor()
    sql = "UPDATE libro SET id_usuario = NULL WHERE id_usuario=%s"
    data = (id,)
    cursor1.execute(sql, data)
    db.connection.commit()'''
    
    cursor2 = db.connection.cursor()
    sql = "DELETE FROM libro WHERE id=%s"
    data = (id,)
    cursor2.execute(sql, data)
    db.connection.commit()
    
    return redirect(url_for('Administraciondelibros'))

@app.route('/edit/<string:id>', methods =['POST'])
def edit(id):
    
    titulo = request.form['titulo']
    autor = request.form['autor']
    editorial = request.form['editorial']
    anio_publicacion = request.form['anio_publicacion']
    genero = request.form['genero']
    descripcion = request.form['descripcion']
    imagen = request.form['imagen']
    
    if titulo and autor and editorial and anio_publicacion and genero and descripcion and imagen:
        cursor= db.connection.cursor()
        sql = "UPDATE libro SET titulo = %s, autor = %s, editorial = %s, anio_publicacion = %s, genero = %s, descripcion = %s, imagen = %s WHERE id = %s"
        data = (titulo, autor, editorial, anio_publicacion, genero, descripcion, imagen, id)
        cursor.execute(sql,data)
        db.connection.commit()
        flash('✅ Cambios guardados correctamente', 'success')
        return redirect(url_for('Administraciondelibros'))
    
#BUSCADOR DE LIBROS
@app.route('/home/libros/buscarlibro', methods = ['GET','POST'])
def buscarlibro():
    libro_buscado = request.form['buscador']
    
    cursor = db.connection.cursor()
    sql = "SELECT * FROM libro where libro.titulo = %s OR libro.genero = %s OR libro.autor = %s"
    cursor.execute(sql,(libro_buscado, libro_buscado, libro_buscado))
    libros = cursor.fetchall()
    columns = ['id', 'titulo', 'autor', 'editorial', 'anio_publicacion', 'genero', 'descripcion', 'imagen']
    libro_encontrado = [dict(zip(columns, libro)) for libro in libros ]
    cursor.close()
    
    response = make_response(render_template('libros.html', libros=libro_encontrado))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

#FILTRO DE CATEGORIA DE LIBROS
@app.route('/home/libros/Categorias', methods = ['GET','POST'])
def categorialibros():
    
    categoria = request.form["categoria"]
    
    cursor = db.connection.cursor()
    sql = "SELECT * FROM libro WHERE libro.genero = %s"
    cursor.execute(sql, (categoria,))
    libros = cursor.fetchall()
    columns = ['id', 'titulo', 'autor', 'editorial', 'anio_publicacion', 'genero', 'descripcion', 'imagen']
    libros_encontrados = [dict(zip(columns, libro)) for libro in libros]
    
    response = make_response(render_template('libros.html', libros=libros_encontrados))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/protected')
#Anotacion que obliga a que se inicie sesion un usuario para acceder a esta URL protegida
def protected():
    return "<h1>Esta es una vista solo para usuarios autentificados</h1>"
#Error 401: Consiste cuando se quiere acceder a una pagina o URL protegida con login_required y no ah iniciado sesion
def status_401(error):
    return redirect(url_for('login'))

#Error 401: Consiste cuando se quiere acceder a una pagina o URL, la cual no existe
def status_404(error):
    return "<h1>Pagina no encontrada</h1>",404



@app.route('/login', methods=['GET','POST'])
def login():    
    if current_user.is_authenticated:
        return redirect(url_for('biblioteca_admin'))
    #Validamos si la vista esta en modo obtener datos datos osea post
    if request.method == 'POST':
        #Pasamos los datos capturados en las casillas de texto al constructor     
        user = User(0,request.form['username'],request.form['password'])
        logged_user = ModelUser.login(db,user)
        if logged_user != None:
            #Validamos si el password es correcto
            if logged_user.password:
                #Almacenamos el usuario logeado
                login_user(logged_user)
                
                id_usuario = logged_user.id
                
                #if id_usuario != 13:
                return redirect(url_for('biblioteca_admin'))
                #else:
                    #return redirect(url_for('Administraciondelibros'))
            else:
                flash("Invalid password ...")
                #return render_template('auth/login.html')
        else:
            flash("User not found ...")
            #return render_template('auth/login.html')
                
    response = make_response(render_template('auth/login.html'))
    # Evita que el navegador almacene en caché la página de login
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response
    
@app.route('/admin/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


#SECCION DEL MENU PRINCIPAL

@app.route('/home/libros')
def libros():
    
    if current_user.is_authenticated:
        return redirect(url_for('biblioteca_admin'))
    
    cursor = db.connection.cursor()
    sql = "SELECT * FROM libro"
    cursor.execute(sql,)
    libros = cursor.fetchall()
    columns = ['id', 'titulo', 'autor', 'editorial', 'anio_publicacion', 'genero', 'descripcion', 'imagen']
    libros_dict = [dict(zip(columns, libro)) for libro in libros ]
    cursor.close
    
    #session['lista_libros'] = libros_dict 
    
    response = make_response(render_template('libros.html', libros=libros_dict))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/home/libros/Agregarlibro', methods = ['POST'])
@login_required
def Agregarlibro():
    user_id = current_user.id
    libro_id =  request.form['id_libro']
    
    cursor = db.connection.cursor()
    
    # Validamos si ya cuenta con el libro
    Validarlibro_sql = "SELECT * FROM user_libro WHERE user_id = %s AND libro_id = %s"
    cursor.execute(Validarlibro_sql, (user_id, libro_id))
    existente = cursor.fetchone()   
    
    if not existente:
        sql = "INSERT INTO user_libro (user_id, libro_id) VALUES (%s, %s)"
        data = (user_id, libro_id)
        cursor.execute(sql,data)
        db.connection.commit()
        return redirect(url_for('admin_mislibros'))


#SECCION USUARIO

@app.route('/admin_mislibros')
@login_required
def admin_mislibros():
    user_id = current_user.id
    
    #print(f"user_id: {user_id}")
    
    cursor = db.connection.cursor()
    sql = "SELECT libro.* FROM libro JOIN user_libro ON libro.id = user_libro.libro_id WHERE user_libro.user_id = %s"
    data = (user_id,)
    cursor.execute(sql,data)
    libros = cursor.fetchall()
    
    columns = ['id', 'titulo', 'autor', 'editorial', 'anio_publicacion', 'genero', 'descripcion', 'imagen']
    libros_dict = [dict(zip(columns, libro)) for libro in libros]
    
    cursor.close()
    
    return render_template('admin/mislibros.html', libros=libros_dict)

@app.route('/admin/biblioteca')
def biblioteca_admin():    
    cursor = db.connection.cursor()
    sql = "SELECT * FROM libro"
    cursor.execute(sql,)
    libros = cursor.fetchall()
    columns = ['id', 'titulo', 'autor', 'editorial', 'anio_publicacion', 'genero', 'descripcion', 'imagen']
    libros_dict = [dict(zip(columns, libro)) for libro in libros ]
    cursor.close
    
    return render_template('admin/biblioteca_admin.html', libros=libros_dict)

@app.route('/admin/home')
def home_admin():
    return render_template('admin/home_admin.html')

#Administracion de libros

@app.route('/admin_libros/Administraciondelibros')
def Administraciondelibros():
    cursor = db.connection.cursor()
    sql = "SELECT * FROM libro"
    cursor.execute(sql,)
    libros = cursor.fetchall()
    columns = ['id', 'titulo', 'autor', 'editorial', 'anio_publicacion', 'genero', 'descripcion', 'imagen']
    libros_dict = [dict(zip(columns, libro)) for libro in libros ]
    cursor.close
    
    response = make_response(render_template('admin_libros/PanelControl_libros.html', libros = libros_dict))
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    #Registramos los errores
    app.config.from_object(config['development'])
    csrf.init_app(app) 
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    
    app.run()
    

