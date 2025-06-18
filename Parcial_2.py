import tkinter as tk
from tkinter import messagebox, ttk
import firebase_admin
from firebase_admin import credentials, db
import re
import uuid
import os


RUTA_CRED = "C:\\Users\\Lenovo\\OneDrive\\Desktop\\parcial-245b4-firebase-adminsdk-fbsvc-7268224174.json"

if not os.path.exists(RUTA_CRED):
    raise FileNotFoundError(f"No se encontró el archivo de credenciales: {RUTA_CRED}")

try:
    credenciales = credentials.Certificate(RUTA_CRED)
    firebase_admin.initialize_app(credenciales, {
        'databaseURL': 'https://parcial-245b4-default-rtdb.firebaseio.com/' 
    })
except Exception as e:
    raise RuntimeError(f"Error al inicializar Firebase: {e}")

ref_libros = db.reference("libros")
ref_usuarios = db.reference("usuarios")

# ------------------ Definicion de Variables ------------------
class RegistroLibrosApp:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Registro de Libros en Firebase")

        self.marco_actual = None  # Contenedor de widgets actual
        self.datos_libro = {}  # Diccionario temporal con los datos del libro

        self.mostrar_pantalla_registro_usuario()  # Comenzar por registro de usuario

    def limpiar_marco(self):
        """Elimina el marco actual para mostrar una nueva pantalla"""
        if self.marco_actual:
            self.marco_actual.destroy()

    def mostrar_pantalla_registro_usuario(self):
        """Primera pantalla: registro de usuario con correo y contraseña"""
        self.limpiar_marco()
        marco = tk.Frame(self.ventana)
        marco.pack(padx=10, pady=10)
        self.marco_actual = marco

        tk.Label(marco, text="Correo electrónico:").pack()
        self.entrada_correo = tk.Entry(marco)
        self.entrada_correo.pack()

        tk.Label(marco, text="Contraseña:").pack()
        self.entrada_contraseña = tk.Entry(marco, show="*")
        self.entrada_contraseña.pack()

        tk.Button(marco, text="Registrarse", command=self.registrar_usuario).pack(pady=10)

    def registrar_usuario(self):
        """Valida y registra al usuario en la base de datos"""
        correo = self.entrada_correo.get().strip()
        contraseña = self.entrada_contraseña.get()

        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", correo):
            messagebox.showerror("Error", "Correo inválido. Debe tener formato usuario@dominio.com")
            return

        if len(contraseña) < 6:
            messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.")
            return

        id_usuario = str(uuid.uuid4())  # Crear ID único para el usuario
        try:
            ref_usuarios.child(id_usuario).set({"correo": correo, "contraseña": contraseña})
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el usuario: {e}")
            return

        messagebox.showinfo("Éxito", "Usuario registrado con éxito.")
        self.mostrar_pantalla_titulo_libro()

    def mostrar_pantalla_titulo_libro(self):
        """Segunda pantalla: ingresar el título del libro"""
        self.limpiar_marco()
        marco = tk.Frame(self.ventana)
        marco.pack(padx=10, pady=10)
        self.marco_actual = marco

        tk.Label(marco, text="Título del libro:").pack()
        self.entrada_titulo = tk.Entry(marco)
        self.entrada_titulo.pack()

        tk.Button(marco, text="Siguiente", command=self.mostrar_pantalla_genero_libro).pack(pady=10)

    def mostrar_pantalla_genero_libro(self):
        """Tercera pantalla: seleccionar el género del libro"""
        titulo = self.entrada_titulo.get().strip()
        if not titulo:
            messagebox.showerror("Error", "Debe ingresar un título.")
            return

        self.datos_libro["titulo"] = titulo

        self.limpiar_marco()
        marco = tk.Frame(self.ventana)
        marco.pack(padx=10, pady=10)
        self.marco_actual = marco

        tk.Label(marco, text="Seleccione el género del libro:").pack()
        self.selector_genero = ttk.Combobox(marco, values=["Ficción", "Ciencia", "Historia"], state="readonly")
        self.selector_genero.pack()

        tk.Button(marco, text="Registrar Libro", command=self.registrar_libro_en_firebase).pack(pady=10)

    def registrar_libro_en_firebase(self):
        """Registra el libro en Firebase con título, género y código único"""
        genero = self.selector_genero.get()
        if genero not in ["Ficción", "Ciencia", "Historia"]:
            messagebox.showerror("Error", "Seleccione un género válido.")
            return

        self.datos_libro["genero"] = genero
        codigo_unico = str(uuid.uuid4())[:8]  # Código corto (8 caracteres)
        self.datos_libro["codigo"] = codigo_unico

        try:
            ref_libros.child(codigo_unico).set(self.datos_libro)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo registrar el libro: {e}")
            return

        self.mostrar_resumen_libro()

    def mostrar_resumen_libro(self):
        """Pantalla final: muestra un resumen del libro registrado"""
        self.limpiar_marco()
        marco = tk.Frame(self.ventana)
        marco.pack(padx=10, pady=10)
        self.marco_actual = marco

        tk.Label(marco, text="Libro registrado con éxito:", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(marco, text=f"Título: {self.datos_libro['titulo']}").pack()
        tk.Label(marco, text=f"Género: {self.datos_libro['genero']}").pack()
        tk.Label(marco, text=f"Código generado: {self.datos_libro['codigo']}").pack()

        tk.Button(marco, text="Registrar otro libro", command=self.mostrar_pantalla_titulo_libro).pack(pady=10)

# ------------------ EJECUCIÓN DE LA APP ------------------
if __name__ == "__main__":
    ventana = tk.Tk()
    app = RegistroLibrosApp(ventana)
    ventana.mainloop()
    