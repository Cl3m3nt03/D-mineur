from tkinter import * 
from tkinter.messagebox import *    

root = Tk()

root.title("Calculatrice ISN")
root.minsize(500,500)

def alert():
    showinfo("alerte", "Bravo!")

def rules():
    showinfo("Les Règles","Les règles du jeu son simple , le but du jeu est de découvrir toutes les cases libres sans faire exploser les mines, c'est-à-dire sans cliquer sur les cases qui les dissimulent")

def editer():
    height = Spinbox(root, from_=0, to=0)
    height.pack()
    withl = Spinbox(root, from_=0, to=0)
    withl.pack()

def map():
    
    
    for ligne in range(5):
        for colonne in range(5):
            Button(root, text='L%s-C%s' % (ligne, colonne), borderwidth=1).grid(row=ligne, column=colonne)
        
menubar = Menu(root)

menu1 = Menu(menubar, tearoff=0)
menu1.add_command(label="Sauvegarder", command=alert)
menu1.add_command(label="Rejouer", command=alert)
menu1.add_separator()
menu1.add_command(label="Quitter", command=root.quit)
menubar.add_cascade(label="Fichier", menu=menu1)

menu2 = Menu(menubar, tearoff=0)
menu2.add_command(label="Easy", command=alert)
menu2.add_command(label="Medium", command=alert)
menu2.add_command(label="hard", command=alert)
menubar.add_cascade(label="Niveau", menu=menu2)

menu3 = Menu(menubar, tearoff=0)
menu3.add_command(label="A propos", command=rules)
menubar.add_cascade(label="Aide", menu=menu3)

menu4 = Menu(menubar,tearoff=0)
menubar.add_cascade(label="Personalisation",command=editer)

root.config(menu=menubar)

p = PanedWindow(root, orient=HORIZONTAL)
p.pack(side=TOP, expand=Y, fill=BOTH, pady=0, padx=0)
p.add(Label(p, text='Configuration', background='white', anchor=CENTER,) )
p.add(Label(p, text='Map', background='red', anchor=CENTER) )
p.pack()

root.mainloop()
