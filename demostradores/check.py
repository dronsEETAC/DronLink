from tkinter import *
def a():
    print (leche.get())
    print (azucar.get())
root = Tk()
root.config(bd=15)

leche = IntVar()      # 1 si, 0 no
azucar = IntVar()    # 1 si, 0 no

Label(root,text="¿Cómo quieres el café?").pack()
Checkbutton(root, text="Con leche", variable=leche,
            onvalue=1, offvalue=0, command = a).pack()
Checkbutton(root, text="Con azúcar",variable=azucar,
            onvalue=1, offvalue=0, command = a).pack()

root.mainloop()