from tkinter import *
import tkinter.ttk as ttk
from tkinter.messagebox import showerror
import mysql.connector as mysql
from collections import OrderedDict
import time, os
from datetime import datetime, date, timedelta
import threading
from PIL.ImageTk import Image, PhotoImage

from my_widgets import compute_age_from_dates
from my_widgets.widgets import DateField, MyText, BP,createToolTip, Treeview
from my_widgets.widgets import ComboBox
from patient import Patient
from models import Db

try:
    db = Db()
except mysql.connection.errors.Error:
    Tk().withdraw()
    showerror("Connection Error!","Unable to connect to MySQL Server!\nMake sure that the server is running and try again")
    sys.exit()

fields = ["ID", "NAME","DOB", "AGE", "SEX", "ADDRESS", "DATE", "TIME","MOBILE","BP","HR","RR",
        "SPO2","TEMP","CATEGORY","REASON", "COMPLAINTS"]

tooltip_text=[
"Enter Patient ID. This must be unique", "Enter Patient Name","Date of birth(dd-mm-yyyy)",
"Only Patients age if date of birth is unknown\nMust be of format; 2yr 3m 15d\n(y=years, m=months, d=days)",
"Choose the sex from dropdown","Patient's Full Address","Date of Admission",
"Time of admission(H:M PM/AM)","Mobile Number/Telephone", "Enter Systolic BP & Diastolic BP","Enter Pulse Rate",
"Enter Respiratory Rate","Enter Oxygen saturation","Enter Temperature",
"Choose the Triage Category","Reason for attendance", "Summary of patient complaints"
]

entries=OrderedDict()

root = Tk()
root.title("Demographics")
root.geometry("{}x{}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
root.overrideredirect(False)
root.iconbitmap(os.path.abspath("icon.ico"))
root.option_add("*Label*font", "Consolas 13")
root.option_add("*Entry*font", "Consolas 13")
root.option_add("*Button*font", "Consolas 13")
root.option_add("*TCombobox*Listbox.font", "Consolas 13")
root.option_add("*TCombobox*Listbox.background", "powderblue")

# theme_names =('winnative', 'clam', 'alt', 'default', 'classic', 'vista', 'xpnative')
style= ttk.Style()
style.theme_use("clam")
status_message= StringVar()

bp=BP(root)
now = StringVar() # Time variable

clock_frame= Frame(root)
clock_frame.pack(anchor='e', padx=50)

searchframe = Frame(root)
searchframe.place(x= root.winfo_screenwidth()/2, y=10)

lab=Label(clock_frame, textvariable=now, font="Consolas 18", foreground='red')
lab.pack()

class Triage:
    def __init__(self,parent=None):
        self.parent=parent
        logo = PhotoImage(file=os.path.abspath('triage.png'))

        HEADING =Label(self.parent, image=logo,font="Consolas 24 bold",
                        fg='blue')
        HEADING.pack(anchor='nw',pady=4,padx=10)
        HEADING.image = logo

        f= Frame(self.parent)
        f.pack(side=LEFT, padx=10,pady=2, expand=1, fill=BOTH)

        self.create_widgets(f)
        self.clock_thread()

    def clock_thread(self):
        t= threading.Thread(target=self.run_clock)
        t.start()

    def run_clock(self):
        now.set(datetime.now().time().strftime("%I:%M :%S %p"))
        self.sync_clock()

    def sync_clock(self):
        self.parent.after(1000, self.run_clock)

    def close(self):
        self.parent.quit()

    def analyse_vitals(self):
        try:
            HR=int(entries["HR"].get())
            try:
                assert 60<=HR<=90, "HR is abnormal"
            except AssertionError:
                entries["HR"].config(foreground="red")
            else:
                entries["HR"].config(foreground="green")
        except ValueError:pass

        try:
            RR=int(entries["RR"].get())
            try:
                assert 12<=RR<=18, "RR is abnormal"
            except AssertionError:
                entries["RR"].config(foreground="red")
            else:
                entries["RR"].config(foreground="green")

        except ValueError:pass

        try:
            SPO2=int(entries["SPO2"].get())
            try:
                assert SPO2>=90, "SPO2 is abnormal"
            except AssertionError:
                entries["SPO2"].config(foreground="red")
            else:
                entries["SPO2"].config(foreground="green")
        except ValueError:
            if "%" in entries["SPO2"].get():
                try:
                    SPO2= int(entries["SPO2"].get().replace("%",""))
                    try:
                        assert SPO2>=90, "SPO2 is abnormal"
                    except AssertionError:
                        entries["SPO2"].config(foreground="red")
                    else:
                        entries["SPO2"].config(foreground="green")
                except ValueError:pass

        try:
            TEMP = float(entries["TEMP"].get())
            try:
                assert 36.1<TEMP<37.2, "TEMP is abnormal"
            except AssertionError:
                entries["TEMP"].config(foreground="red")
            else:
                entries["TEMP"].config(foreground="green")
        except ValueError:pass

    @staticmethod
    def current_time():
        now =datetime.now().time().strftime("%I:%M %p")
        entries["TIME"].delete(0,END)
        entries["TIME"].insert(0, now)

    @staticmethod
    def set_age():
        today = date.today()
        dob= entries["DOB"].get()
        if dob.strip()=="":
            return

        if "-" in dob:
            d,m,y = dob.split("-")
        elif "/" in dob:
            d,m,y = dob.split("/")

        age= compute_age_from_dates("{}-{}-{}".format(y,m,d), deceased=False, dod=None)
        # Insert true date
        entries["AGE"].delete(0,END)
        entries["AGE"].insert(0, age)

    @staticmethod
    def reset_status():
        status_message.set("")

    @staticmethod
    def get_id():
        try:
            pk = int(entries["ID"].get())
        except ValueError:
            return None
        else:
            return pk

    def update(self):
        self.set_age()
        ID = self.get_id()
        if ID:
            new_patient = Patient()

            for field, entry in entries.items():
                try:
                    value = entry.get()
                except TypeError:
                    value = entry.get("1.0", "end").strip()

                setattr(new_patient, field, value)

            update_msg = db.update(new_patient)
            if update_msg is True:
                self.update_register(self.tree)
                self.analyse_vitals()
                status_message.set("Updated succesfully!")
            else:
                status_message.set(str(update_msg))

            self.parent.after(2000, self.reset_status)

    def save(self):
        patient=Patient()
        for field, entry in entries.items():
            try:
                value = entry.get()
            except TypeError:
                value = entry.get("1.0", "end").strip()
            if value !="":
                setattr(patient, field, value)

        inserted=db.insert(patient)
        if inserted is True:
            self.update_register(self.tree)
            self.analyse_vitals()
            self.set_age()
            status_message.set("Saved succesfully!")
        else:
            status_message.set(str(inserted))
        self.parent.after(2000, self.reset_status)

    def find(self, pk=None,event=None):
        pk = self.get_id()
        if pk:
            value_list= db.lookup(pk)
            fields = db.fields
            if value_list is not None:
                self.clear()
                for i in range(len(fields)):
                    field = entries.get(fields[i][0])
                    try:
                        field.insert(0, value_list[0][i])
                    except:
                        field.insert("1.0", value_list[0][i])
            else:
                self.clear()
            self.set_age()
            self.show_alarm()

    @staticmethod
    def clear():
        # Insert true date
        for entry in entries.values():
            try:
                entry.delete(0,"end")
            except:
                entry.delete("1.0", "end")
        entries['ID'].focus()

    def delete(self):
        pk = self.get_id()
        if pk:
            deleted=db.remove(pk)
            if deleted is True:
                status_message.set("Deleted succesfully")
                self.clear()
                self.update_register(self.tree)
            else:
                status_message.set(deleted)

            self.parent.after(2000, self.reset_status)

    @staticmethod
    def saved_patients():
        return db.get_all()

    def update_register(self, tree):
        register = self.saved_patients()
        self.tree.set_register(register)

    def get_selected(self,event):
        current_selection = event.widget.focus()
        rows = event.widget.item(current_selection)['values']
        ip_no = rows[0]
        entries['ID'].delete(0, 'end')
        entries['ID'].insert(0, ip_no)
        self.find()

    def show_alarm(self, event=None):
        val = entries["CATEGORY"].get()

        if val =="EMERGENCY":
            entries["CATEGORY"].config(foreground="red")
        elif val =="PRIORITY":
            entries["CATEGORY"].config(foreground="brown")
        elif val=="URGENT":
            entries["CATEGORY"].config(foreground="orange")
        elif val =="NON URGENT":
            entries["CATEGORY"].config(foreground="green")
        else:
            entries["CATEGORY"].config(foreground="white")

        # ANalyse vitals
        self.analyse_vitals()

    def search_by_name(self, ip_no):
        entries["ID"].delete(0,END)
        entries["ID"].insert(0, ip_no)
        self.find()

    def create_widgets(self, f):
        # SEARCH ENTRY IN self.demoframe3
        for index, field in enumerate(fields):
            if field is not "BP":
                Label(f, text=field.upper().replace("_", " ")).grid(row=index, column=0)

            if field=="DOB" or field =="DATE":
                entry = DateField(f)

            elif field=="BP":
                entry = BP(f)

            elif field=='CATEGORY' or field=="REASON" or field=="SEX":
                if field=="CATEGORY":
                    entry = ComboBox(f, width=21, values=["NON URGENT","URGENT","PRIORITY","EMERGENCY"])
                elif field=="SEX":
                    entry = ComboBox(f, width=21, values=["Male","Female"])
                else:
                    entry = ComboBox(f, width=21, values=["CONSULTATION","LAB ONLY","RADIOLOGY ONLY"])

                entry.configure(font="Consolas 14 bold")

            elif field=="COMPLAINTS":
                entry = MyText(f, width=25, height=4, font="Consolas 14", wrap=WORD)
            elif field=="TIME":
                entry = ttk.Entry(f, width=25,font="Arial 12")
                Button(f, text="Current Time", bg="powderblue", command=self.current_time,
                    font="Calibri 10 bold").grid(row=index, column=4, columnspan=2)
            else:
                entry = ttk.Entry(f, width=25, font="Arial 12")

            if field is not "BP":
                entry.grid(row=index, column=1, columnspan=6, pady=2, sticky='w')
            else:
                entry.grid(row=index, column=0, columnspan=6, pady=5)
            entries[field]=entry

            createToolTip(widget=entry, text= tooltip_text[index])

        entries['ID'].focus()
        entries['ID'].bind("<Return>", self.find)
        entries['CATEGORY'].bind("<<ComboboxSelected>>", self.show_alarm)
        btnfont=  font="Consolas 10 bold"

        style.configure("TButton", font=btnfont, width=6, background='powderblue')
        bsave = ttk.Button(f, text="SAVE", command=self.save)
        bsave.grid(row = len(fields) +2, column=0,pady=8)

        bupdate = ttk.Button(f, text="UPDATE", command=self.update)
        bupdate.grid(row = len(fields) +2, column=1,padx=2)

        bclear = ttk.Button(f, text="CLEAR", command=self.clear)
        bclear.grid(row = len(fields) +2, column=2,padx=2)
        bclear = ttk.Button(f, text="CLOSE", command=self.close)
        bclear.grid(row = len(fields) +2, column=3,padx=2)

        status_bar=Label(f, textvariable=status_message, relief='ridge', font='Calibri 10', fg='red')
        status_bar.grid(row= len(fields) + 3, columnspan=6, sticky='ew', pady=4)

        f2= Frame(self.parent, relief='raised', bd=4)
        f2.pack(expand=1, fill=Y,side=BOTTOM, padx=10,pady=10)

        search = AutocompleteEntry(searchframe, command=self.search_by_name)
        search.ent.configure(width=35)

        self.rowresult = StringVar()
        resetfrm= Frame(self.parent)

        Qresult = Label(resetfrm, textvariable=self.rowresult, fg='green', font='Arial 14 bold')
        Qresult.pack(side=LEFT, anchor='w',padx=10,pady=2)
        self.reset=ttk.Button(resetfrm, text="RESET", state=DISABLED,
            command=self.reset_filters, width=15)
        self.reset.pack(side=RIGHT, anchor='e', padx=10)

        resetfrm.pack(side=TOP, expand=0, fill=X)

        btnshow=ttk.Button(resetfrm, text="Show Filters", width=15)
        btnshow.pack(side=RIGHT, anchor='e', padx=10)
        btnshow.bind("<Button-1>", self.show_filters)
        resetfrm.pack(side=TOP, expand=0, fill=X)
        resetfrm.lower()

        # show filters
        tree_header=Label(f2, text="PATIENT REGISTER", font="Consolas 20 bold")
        tree_header.pack(expand=0)

        self.tree= Treeview(f2, headers=[field.upper() for field in fields[0:8]])
        self.tree.pack(expand=1, fill=BOTH,padx=5, pady=5)
        f2.lower()
        self.tree.bind("<<TreeviewSelect>>", self.get_selected)
        ttk.Style().configure("Treeview", background='lightcyan',
            font=('Consolas', 12), foreground='black', pady=5)

        # update register
        self.update_register(self.tree)

    def show_filters(self, event):
        if event.widget['text']=="Show Filters":
            event.widget['text']="Hide Filters"
            self.filterframe= Frame(self.parent)
            self.filterframe.pack(padx=10,pady=2, expand=0, fill=X)
            self.filterframe.lower()
            self.reset.configure(state=NORMAL)
        else:
            self.reset_filters()
            self.filterframe.destroy()
            event.widget['text']="Show Filters"
            self.filterframe=None
            self.reset.configure(state=DISABLED)
            return

        Label(self.filterframe, text="Filter:").pack(side=LEFT)
        self.field_name=ComboBox(self.filterframe, values= fields)
        self.field_name.pack(side=LEFT)
        self.field_name.bind("<<ComboboxSelected>>", self.update_field_values_cbo1)

        self.field_values=ComboBox(self.filterframe)
        self.field_values.pack(side=LEFT)
        self.field_values.bind("<<ComboboxSelected>>", self.update_by_filter)

        # 2nd Layer of filters
        Label(self.filterframe, text="&").pack(side=LEFT)
        self.field_name2=ComboBox(self.filterframe, values= fields)
        self.field_name2.pack(side=LEFT)
        self.field_name2.bind("<<ComboboxSelected>>", self.update_field_values_cbo2)

        self.field_values2=ComboBox(self.filterframe)
        self.field_values2.pack(side=LEFT)
        self.field_values2.bind("<<ComboboxSelected>>", self.update_by_filter)

        # 3rd Layer of filters
        Label(self.filterframe, text="&").pack(side=LEFT)
        self.field_name3=ComboBox(self.filterframe, values= fields)
        self.field_name3.pack(side=LEFT)
        self.field_name3.bind("<<ComboboxSelected>>", self.update_field_values_cbo3)

        self.field_values3=ComboBox(self.filterframe)
        self.field_values3.pack(side=LEFT)
        self.field_values3.bind("<<ComboboxSelected>>", self.update_by_filter)

    def reset_filters(self):
        if self.filterframe is not None:
            self.field_name.delete(0,'end')
            self.field_name2.delete(0,'end')
            self.field_name3.delete(0,'end')

            self.field_values.delete(0,'end')
            self.field_values2.delete(0,'end')
            self.field_values3.delete(0,'end')
            self.update_register(self.tree)
            self.rowresult.set("")

    def update_field_values_cbo1(self, event):
        field_name=event.widget.get()
        sql = "SELECT {} FROM triage".format(field_name)

        vals = db.execute(sql)
        cbovals=[]

        if vals:
            for val in vals:
                cbovals.append(val[0])
            self.field_values['values']= list(set(cbovals))

    def update_field_values_cbo2(self, event):
        field_name=event.widget.get()
        sql = "SELECT {} FROM triage".format(field_name)

        vals = db.execute(sql)
        cbovals=[]

        if vals:
            for val in vals:
                cbovals.append(val[0])
            self.field_values2['values']= list(set(cbovals))

    def update_field_values_cbo3(self, event):
        field_name=event.widget.get()
        sql = "SELECT {} FROM triage".format(field_name)

        vals = db.execute(sql)
        cbovals=[]

        if vals:
            for val in vals:
                cbovals.append(val[0])
            self.field_values3['values']= list(set(cbovals))

    def update_by_filter(self, event):
        field_name1 = self.field_name.get()
        field_value1 = self.field_values.get()

        field_name2 = self.field_name2.get()
        field_value2 = self.field_values2.get()

        field_name3 = self.field_name3.get()
        field_value3 = self.field_values3.get()

        sql="SELECT * FROM triage WHERE "
        # sql2="SELECT ID, NAME, AGE, DOA, REASON, ADDRESS FROM triage WHERE "

        if field_name1 and field_name2 and field_name3:
            sql +="{}='{}' AND {}='{}' AND {}='{}' ".format(
                field_name1, field_value1,field_name2, field_value2,
                field_name3, field_value3)

        elif field_name1 and field_name2:
            sql +=" {}='{}' AND {}='{}' ".format(field_name1, field_value1,field_name2, field_value2)

        elif field_name1 and field_name3:
            sql +=" {}='{}' AND {}='{}' ".format(field_name1, field_value1,field_name3, field_value3)

        elif field_name2 and field_name3:
            sql +=" {}='{}' AND {}='{}' ".format(field_name2, field_value2,field_name3, field_value3)

        elif field_name1:
            sql +="{} = '{}'".format(field_name1, field_value1)

        elif field_name2:
            sql +="{} = '{}'".format(field_name2, field_value2)

        elif field_name3:
            sql +="{} = '{}'".format(field_name3, field_value3)

        else:
            sql = None

        if sql:
            results = db.execute(sql)
            if results:
                self.current_register= results
                self.tree.set_register(results)
                self.rowresult.set("Query returned {} result(s)".format(len(results)))
            else:
                self.current_register=[]
                self.tree.set_register([])
                self.rowresult.set("Query returned no (Zero) results!")

    def create_register(self):
        from word_docx import MyDocument
        import os

        doc = MyDocument()
        doc.add_title("Register")
        values=[]
        for value in self.current_register:
            values.append(value[0:8])

        table = doc.add_table("Table " +
                            str(datetime.today().date().__format__("%d-%m-%Y")) + " at " +
                            str(datetime.today().time().__format__("%I:%M:%S %p")),
                            fields[0:8],values)

        table.style = 'Medium Shading 1 Accent 5'

        doc.save("register.docx")
        os.startfile("register.docx")

# AUTO-SEARCH BOX
class AutocompleteEntry(Frame):
    def __init__(self, frame, command):
        Frame.__init__(self)
        var = StringVar()

        self.frame = frame
        self.command = command
        self.SearchQuery()
        self.ent = Entry(self.frame, textvariable=var, width=40)
        self.ent.configure(font="Calibri 16 bold", fg="green")
        createToolTip(widget=self.ent, text="Search Patient")

        self.ent.focus()
        self.ent.pack(side='top', fill=Y, pady=2)
        self.var = var
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)

        self.lb_up = False

    def SearchQuery(self):
        # Keep patinet list inside search query to dynamicall update the list
        self.PATIENTLIST = []
        results=db.get_all()

        for result in results:
            self.PATIENTLIST.append(str(result[0]) + "   :   " + result[1])

    def changed(self, name, index, mode):
        # Keep track of the updates by calling Search function every keypress
        self.SearchQuery()
        if self.var.get() == '':
            try:
                self.lb.destroy()
                self.sbar.destroy()
                self.lb_up = False
            except:
                pass
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.sbar = Scrollbar(self.frame)
                    self.lb = Listbox(self.frame, relief=RIDGE, bd=4)
                    self.sbar.config(command=self.lb.yview)  # xlink sbar and list
                    self.lb.config(yscrollcommand=self.sbar.set)  # move one moves other
                    self.sbar.pack(side=RIGHT, fill=Y, padx=1, pady=2)  # pack first=clip last
                    self.lb.pack(side=LEFT, expand=YES, fill=BOTH)  # list clipped first
                    self.lb.config(font=('arial', 12, 'bold'), fg='navy', height=8)
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Return>", self.selection)
                    self.lb_up = True

                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.sbar.destroy()
                    self.lb_up = False

    def selection(self, event):
        if self.lb_up:
            self.var.set(self.lb.get(ACTIVE))
            self.lb.destroy()
            self.sbar.destroy()
            self.lb_up = False

            item = self.ent.get().split("   :   ")
            self.command(item[0])

            try:
                self.ent.delete(0, 'end')
            except TclError:
                pass  # Deleting the lab search entry when demogframe is dstroyed.

    def up(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':
                self.lb.selection_clear(first=index)
                index = str(int(index) - 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):
        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != END:
                self.lb.selection_clear(first=index)
                index = str(int(index) + 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def comparison(self):
        try:
            pattern = re.compile('.*' + self.var.get() + '.*', re.I | re.M)
            return [w for w in self.PATIENTLIST if re.match(pattern, w)]
        except:
            pass

if __name__ == '__main__':
    application = Triage(root)
    mainloop()

