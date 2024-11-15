from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

con = sqlite3.connect("telefonos.db")
cursor = con.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS repuestos (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   modelo TEXT NOT NULL,
                   marca TEXT NOT NULL,
                   repuesto TEXT NOT NULL,
                   precio INTEGER NOT NULL
                   )
    """)
con.commit()

cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
id INTEGER PRIMARY KEY AUTOINCREMENT,
usuario TEXT NOT NULL,
contrasena TEXT NOT NULL)
""")
con.commit()
cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES ("Hans", "H1q2w3e4r."))
con.commit()
con.close()



app = Flask(__name__)
app.secret_key = "H1q2w3e4r."


@app.route('/')
def index():
    return  render_template('busqueda.html')

@app.route('/buscar', methods = ['GET', 'POST'])
def buscar():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if  request.method == 'POST':
        modelo = request.form['modelo']
        sql = "SELECT * FROM repuestos WHERE modelo = ?"
        cursor.execute(sql, (modelo.lower(),))
        con.commit()
        res = cursor.fetchall()
        if res:
            return render_template("busqueda.html", resultado = res)
        else:
            return  render_template("busqueda.html", mensaje = "Modelo No encontrado!")
    else:
        return   render_template('404.html')
       


@app.route('/login_vista')
def vista_login():
    return render_template("login.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    pas = "H1q2w3e4r."
    hashed = generate_password_hash(pas)
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if request.method == 'POST':
        usuario = request.form['username']
        password =  request.form['password']
        user = cursor.execute("SELECT contrasena FROM usuarios WHERE usuario = ?", (usuario, )).fetchone()
        con.commit()
        if user and check_password_hash(user[0], password):
            session['user_id'] = usuario
            return  render_template("admin.html")
        else:
            return  render_template('login.html', mensaje = False)
    else:
        return render_template('404.html')

@app.route('/administrador')
def vista_administrador():
    if 'user_id' in session:
        return render_template('404.html')
    return render_template("admin.html")

@app.route('/create')
def vista_agregar():
    if "user_id" not in session:
        return render_template("404.html")
    return render_template('create.html')

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if request.method == 'POST':
        modelo = request.form['modelo']
        marca = request.form['marca']
        repuesto = request.form['repuesto']
        precio = request.form['precio']
        resultado = cursor.execute("INSERT INTO repuestos (modelo, marca, repuesto, precio) VALUES (?, ?, ?, ?)", (modelo, marca, repuesto, precio))
        con.commit()
        if resultado:
            return render_template('create.html', mensaje = "Repuesto agregado con exito")
        else:
            return render_template('create.html', mensaje = "Error al agregar el repuesto")
    else:
        return render_template('404.html')


@app.route('/editar')
def  vista_editar():
    if "user_id" not in session:
        return render_template('404.html')
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM repuestos")
    resultado = cursor.fetchall()
    return  render_template('editar.html', resultado = resultado)


@app.route('/editar', methods=['GET', 'POST'])
def  editar():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if request.method == 'POST':
        id = request.form['id']
        modelo = request.form['modelo']
        marca = request.form['marca']
        repuesto = request.form['repuesto']
        precio = request.form['precio']
        resultado = cursor.execute("UPDATE repuestos SET modelo = ?, marca = ?, repuesto = ?, precio = ? WHERE id = ?",  (modelo, marca, repuesto, precio, id))
        con.commit()
        cursor.fetchall()
        if resultado:
            return render_template('editar.html', mensaje = "Repuesto editado con exito")
        else:
            return  render_template('editar.html', mensaje = "Error al editar el repuesto")
    else:
        return render_template('404.html')


@app.route('/delete')
def vista_borrar():
    if "user_id" not in session:
        return render_template('404.html')
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM repuestos")
    resultado = cursor.fetchall()
    return  render_template('delete.html', resultado = resultado)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if  request.method == 'POST':
        id = request.form['id']
        resultado = cursor.execute("DELETE FROM repuestos WHERE id = ?", id)
        con.commit()
        if resultado:
            return render_template('delete.html', mensaje = "Repuesto eliminado con exito")
        
    else:
        render_template('404.html')



#####################################################
# Rutas para la vista de administrador crud
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return render_template("404.html")
    return render_template("admin.html")


@app.route('/user')
def user():
    if "user_id" not in session:
        return render_template("404.html")
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    cursor.execute("SELECT * FROM usuarios")
    con.commit()
    usuarios = cursor.fetchall()
    if usuarios:
        return render_template("/admin/ver_usuarios.html", usuarios = usuarios)
    else:
        return render_template('/admin/ver_usuarios.html', msg="No hay usuarios disponibles")



@app.route('/agregar_admin')
def ver_agregar():
    if "user_id" not in session:
        return render_template("404.html")
    return render_template('/admin/create_user.html')

@app.route('/agregar_ad', methods = ['GET','POST'])
def agregar_ad():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if request.method == 'POST':
        usuario = request.form['usuario']
        password = request.form['password']
        hashed = generate_password_hash(password)
        resultado = cursor.execute("INSERT INTO usuarios (usuario, contrasena) VALUES (?, ?)", (usuario, hashed))
        con.commit()
        if resultado:
            return render_template('admin.html', mensaje = "Usuario agregado con exito")
        else:
            return render_template("admin.html", mensaje="No agregado")


@app.route('/editar_user')
def vista_editar_user():
    if "user_id" not in session:
        return render_template("404.html")
    return render_template('/admin/editar_usuario.html')

@app.route('/editar_user', methods=['POST'])
def editar_user():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if request.method == 'POST':
        id_user = request.form['id_user']
        usuario = request.form['usuario']
        password = request.form['password']
        new_pas = generate_password_hash(password)
        res = cursor.execute("UPDATE usuarios SET usuario = ?, contrasena = ? WHERE id = ?", (usuario, new_pas, id_user))
        con.commit()
        if res:
            return render_template('admin.html', mensaje = "Usuario editado con exito")
        else:
            return render_template("admin.html", mensaje = "No se actualizo")

@app.route('/eliminar_user')
def vista_eliminar_user():
    if "user_id" not in session:
        return render_template("404.html")
    return render_template('/admin/eliminar_user.html')


@app.route('/eliminar_user', methods = ['POST'])
def eliminar_user():
    con = sqlite3.connect("telefonos.db")
    cursor = con.cursor()
    if request.method == 'POST':
        id_user = request.form['id_user']
        res = cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_user,))
        con.commit()
        if res:
            return render_template('admin.html', mensaje="Se elimino el usuario")
        else:
            return render_template("admin.html", mensaje = "No se elimino el usuario")


@app.route('/logout')
def logout():
    session.pop("user_id", None) #eliminar el id de la session
    return redirect(url_for('index')) # redirigir a la pagina login o principal

















