# !/usr/bin/env python3

from tkinter import *
from PIL import Image
from tkinter import messagebox, filedialog
from tkinter.filedialog import askdirectory
import socket
import requests
import json


class AppObject:
    def __init__(self, root):
        self.root = root
        self.initUserInterface()
        self.center_window(500, 400)
        self.root.resizable(width=False, height=False)
        self.lbl1 = Label(root, text="URL")
        self.lbl1.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.url = Entry(width=35)
        self.url.place(relx=0.5, rely=0.4, anchor=CENTER)
        self.v0 = IntVar()
        self.v0.set(2)
        self.r1 = Radiobutton(root, text="service", variable=self.v0, value=1)
        self.r2 = Radiobutton(root, text="manual", variable=self.v0, value=2)
        self.r1.place(relx=0.8, rely=0.1)
        self.r2.place(relx=0.8, rely=0.2)
        self.button_internet_connection = Button(self.root, text="Check internet connection", command=self.internet_connection, bg='brown', fg='white', font=('helvetica', 9, 'bold'))
        self.button_internet_connection.place(relx=1.0, rely=1.0, anchor=SE)
        self.button_download = Button(self.root, text='Download', command=self.download, bg='brown', fg='white',font=('helvetica', 9, 'bold'))
        self.button_download.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.root.bind('<Button-3>', self.click)
        self.root.bind('<Control-a>', self.callback)

    def initUserInterface(self):
        self.root.title("Picture downloader")
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.clear)
        filemenu.add_command(label="Open", command=self.open_img)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_separator()
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Stop service", command=self.stop_api)
        menubar.add_cascade(label="Service", menu=filemenu)


    def stop_api(self):
        r = requests.post("http://localhost:5000/shutdown", json={})
        if r.status_code == 200:
            messagebox.showinfo('Service', "Service is DOWN!")
        else:
            messagebox.showinfo('Service', "Service is already down or something is not right!")

    def callback(self,event):
        event.widget.select_range(0, 'end')
        event.widget.icursor('end')
        return

    def click(self,e):
        try:
            def Copy(e):
                e.widget.event_generate('<Control-c>')
            def Cut(e):
                e.widget.event_generate('<Control-x>')
            def Paste(e):
                e.widget.event_generate('<Control-v>')
            e.widget.focus()

            lst = [(' Cut'  , lambda e=e: Cut(e)),
                   (' Copy' , lambda e=e: Copy(e)),
                   (' Paste', lambda e=e: Paste(e))]

            local_menu = Menu(None, tearoff=0, takefocus=0)
            for desc, command in lst:
                local_menu.add_command(label=desc, command=command)

            local_menu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")
        except:
            messagebox.showinfo('Error', ' Something is wrong!')
            pass
        return

    def openfn(self):
        filename = filedialog.askopenfilename(title='open')
        if filename:
            return filename
        else:
            return False

    def open_img(self):
        x = str(self.openfn())
        img = Image.open(x)
        img.show()

    def center_window(self, width=300, height=200):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def clear(self):
        MsgBox = messagebox.askquestion('Exit from current state', 'Are you sure ?',
                                        icon='warning')
        if MsgBox == 'yes':
            self.root.destroy()
            root = Tk()
            AppObject(root)
            root.mainloop()
        else:
            messagebox.showinfo('Return', 'You will now return to the application screen!')

    def save(self):
        directory = filedialog.asksaveasfilename(initialdir="/", title="Select file",
                                                 filetypes=(("Jpeg files", "*.jpg"),
                                                            ("Png files", "*.png"),
                                                            ("All files", "*.*")), defaultextension='.jpg')
        return directory

    def download(self):
        if self.v0.get() == 2:

            if not self.internet_connection(noty=False):
                return

            try:
                f = open(self.save(), 'wb')
            except:
                return

            self.button_download['state'] = 'disabled'
            temp = requests.get(self.url.get()).content
            f.write(temp)
            f.close()
            self.url.delete(0, 'end')
            self.button_download['state'] = 'normal'

        elif self.v0.get() == 1:  # different procedure than above

            if not self.internet_connection(host = '0.0.0.0', port = 5000, info="Web service is down!", noty=False):
                return

            try:
                folder = askdirectory()
            except:
                return

            self.button_download['state'] = 'disabled'
            r = requests.post("http://localhost:5000/", json={"url":self.url.get()})
            data_json = json.loads(r.content)
            keys = list(data_json.keys())

            for key in keys:
                url = data_json[key]['url']
                try:
                    f = open(folder + "/" + key, 'wb')
                    temp = requests.get(url).content
                    f.write(temp)
                    f.close()
                except:
                    pass

        self.button_download['state'] = 'normal'
        messagebox.showinfo('Downloaded', 'The picture/s has/have been downloaded!')
        MsgBox = messagebox.askquestion('Open', 'Would you like to open the picture?', icon='warning')

        if MsgBox == 'yes':
            self.open_img()
        else:
            self.root.destroy()
            root = Tk()
            AppObject(root)
            root.mainloop()

    def internet_connection(self, host="8.8.8.8", port=53, info = 'Not Connected!', noty = True):
        try:
            socket.setdefaulttimeout(1)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            if noty:
                messagebox.showinfo('Internet connection', "Connected!")
            return True
        except Exception as ex:
            messagebox.showinfo('Internet connection', info + "\n" + str(ex))
            return False

def main():
    root = Tk()
    AppObject(root)
    root.mainloop()

if __name__ == '__main__':
    main()
