import tkinter.ttk as ttk
from tkinter import *

class Treeview(ttk.Treeview):
    def __init__(self, parent, headers, *args, **kwargs):
        ttk.Treeview.__init__(self, parent,  columns = headers, show="headings", *args, **kwargs)

        ttk.Style().configure("Treeview",background='lightcyan', font=('Helvetica', 12), foreground='black', pady=4)

        self.vsb = ttk.Scrollbar(parent, orient="vertical", command=self.yview)
        self.hsb = ttk.Scrollbar(parent, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.pack(side='right', fill="y", anchor='w')
        self.hsb.pack(side='bottom', fill="x")

        self.parent = parent
        self.headers = headers
        self.current_selection = None
        self.bind("<<TreeviewSelect>>", self.get_selection)
        self._build_tree()

    def destroy_scrollbars(self):
        self.hsb.destroy()
        self.vsb.destroy()

    def _build_tree(self):
        for col in self.headers:
            self.heading(col, text=col, anchor='w',
                command=lambda c=col: self.sortby(self, c, 0))
            # adjust the column's width to the header string
            if col=="ItemNo":
                self.column(col, anchor='w', width=60)
            elif col=="Item" or col=="ADDRESS":
                self.column(col, anchor='w', width=200)
            else:
                self.column(col, anchor='w', width=100)

    def sortby(self, tree, col, descending):
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not descending)))

    def fill_tree(self):
        # Delete children and repopulate
        self.delete(*self.get_children())

        if self.register is not None:
            for item in self.register:
                self.insert('', 'end', values=item)  # Returns row-id
                # adjust column's width if necessary to fit each value
                try:
                    for ix, val in enumerate(item):
                        try:
                            col_w = font.Font().measure(val)
                            if self.column(self.headers[ix], width=None) < col_w:
                                self.column(self.headers[ix], width=col_w, font="Calibri 14")
                        except:
                            pass
                except TypeError:
                    raise TypeError("Tree_list must be a list of tuples")

    def get_selection(self, event=None):
        if event:
            current_selection = event.widget.focus()
            rows = self.item(current_selection)['values']
            self.current_selection = rows
            ip_no = rows[1]
            return ip_no

    def set_register(self, register):
        self.register = register
        self.update_tree()

    def update_tree(self):
        self.clear()
        self.fill_tree()

    def clear(self):
        self.delete(*self.get_children())

    def get_all(self):
        return [item for item in self.get_children()]