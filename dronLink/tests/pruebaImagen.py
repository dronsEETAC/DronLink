import tkinter as tk
from PIL import Image, ImageTk

# Crear ventana principal
root = tk.Tk()
root.title("Mostrar imagen 300x300")

# Cargar la imagen original con PIL
imagen = Image.open("imagen.png")

# Redimensionar la imagen a 300x300 píxeles
imagen = imagen.resize((300, 300), Image.LANCZOS)

# Convertir la imagen para usarla en Tkinter
imagen_tk = ImageTk.PhotoImage(imagen)

# Crear el Label y asignarle la imagen
label = tk.Label(root, image=imagen_tk)
label.pack(padx=10, pady=10)

# Mantener una referencia (evita que la imagen sea recolectada por el GC)
label.image = imagen_tk

# Ejecutar el bucle principal de Tkinter
root.mainloop()
