from tkinter import *
from TkinterNEW import new

root = Tk()
root.geometry('500x400')


new.TranparentWindow(root)
new.BlurWorkAround(root,new.GetHWNDNew(root))
new.NewPanel()

l = new.NewLabel(text='New Widgets')
l.place(relx=.4,y=1)

#NewEntry
e = new.NewEntry(width=9)
e[1].insert(0,'Entry')
e[0].place(relx=.4,y=50)


#NewButton
b = new.NewButton(text='Button')
b[0].place(relx=.4,y=100)


#NewDropDown
choosed = StringVar() 
choosed.set('1')
objs = ['1','2','3'] #list 
b = new.NewDropDown(objs=objs,variable=choosed)
b[0].place(relx=.4,y=150)


root.mainloop()