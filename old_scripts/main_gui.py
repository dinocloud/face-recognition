from Tkinter import *
import subprocess as sub
p = sub.Popen('./main_objects_2.py',stdout=sub.PIPE,stderr=sub.PIPE)
output, errors = p.communicate()

root = Tk()
text = Text(root)
text.pack()
text.insert(END, output)
root.mainloop()
