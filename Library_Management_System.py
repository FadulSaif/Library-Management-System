import sqlite3
from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# Database Connection
connector = sqlite3.connect('Library.db')
cursor = connector.cursor()

connector.execute(
    'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Function to ask for issuer card ID
def issuer_card():
    Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?')
    if not Cid:
        mb.showerror('Error', 'Issuer ID cannot be empty!')
        return None
    return Cid

# Function to display records
def display_records():
    tree.delete(*tree.get_children())
    curr = connector.execute('SELECT * FROM Library')
    data = curr.fetchall()
    for records in data:
        tree.insert('', END, values=records)

def clear_fields():
    BK_STATUS.set('Available')
    for var in [BK_NAME, BK_ID, AUTHOR_NAME, CARD_ID]:
        var.set('')
    BK_ID_entry.config(state='normal')
    try:
        tree.selection_remove(tree.selection()[0])
    except:
        pass

def clear_and_display():
    clear_fields()
    display_records()

def add_record():
    if BK_STATUS.get() == 'Issued':
        card = issuer_card()
        if card is None:
            return
        CARD_ID.set(card)
    else:
        CARD_ID.set('N/A')
    
    surety = mb.askyesno('Confirm', 'Are you sure you want to add this record?')
    if surety:
        try:
            if not all([BK_NAME.get(), BK_ID.get(), AUTHOR_NAME.get()]):
                mb.showerror('Error', 'All fields must be filled out!')
                return

            connector.execute(
                'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
                (BK_NAME.get(), BK_ID.get(), AUTHOR_NAME.get(), BK_STATUS.get(), CARD_ID.get())
            )
            connector.commit()
            clear_and_display()
            mb.showinfo('Success', 'Record added successfully')
        except sqlite3.IntegrityError:
            mb.showerror('Error', 'Book ID already exists!')

def update_record():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record to update')
        return
    
    current_item = tree.focus()
    values = tree.item(current_item)['values']
    BK_ID.set(values[1])
    
    if BK_STATUS.get() == 'Issued':
        card = issuer_card()
        if card is None:
            return
        CARD_ID.set(card)
    else:
        CARD_ID.set('N/A')
    
    cursor.execute('UPDATE Library SET BK_NAME = ?, AUTHOR_NAME = ?, BK_STATUS = ?, CARD_ID = ? WHERE BK_ID = ?',
                   (BK_NAME.get(), AUTHOR_NAME.get(), BK_STATUS.get(), CARD_ID.get(), BK_ID.get()))
    connector.commit()
    clear_and_display()
    mb.showinfo('Success', 'Record updated successfully')

def remove_record():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record to delete')
        return
    
    current_item = tree.focus()  
    values = tree.item(current_item)['values']
    cursor.execute('DELETE FROM Library WHERE BK_ID = ?', (values[1],))
    connector.commit()
    tree.delete(current_item)
    mb.showinfo('Success', 'Record deleted successfully')
    clear_and_display()

def delete_inventory():
    if mb.askyesno('Confirm', 'Are you sure you want to delete all records?'):
        cursor.execute('DELETE FROM Library')
        connector.commit()
        clear_and_display()
        mb.showinfo('Success', 'All records deleted successfully')

def change_availability():
    if not tree.selection():
        mb.showerror('Error', 'Please select a record')
        return
    
    current_item = tree.focus()
    values = tree.item(current_item)['values']
    BK_ID.set(values[1])
    
    if values[3] == 'Issued':
        if mb.askyesno('Confirm', 'Has the book been returned?'):
            cursor.execute('UPDATE Library SET BK_STATUS = ?, CARD_ID = ? WHERE BK_ID = ?', ('Available', 'N/A', BK_ID.get()))
            connector.commit()
    else:
        card = issuer_card()
        if card is None:
            return
        cursor.execute('UPDATE Library SET BK_STATUS = ?, CARD_ID = ? WHERE BK_ID = ?', ('Issued', card, BK_ID.get()))
        connector.commit()
    
    clear_and_display()

# GUI Setup
root = Tk()
root.title('Library Management System')
root.geometry('1010x530')
root.resizable(0, 0)
Label(root, text='LIBRARY MANAGEMENT SYSTEM', font=('Arial', 15, 'bold'), bg='SteelBlue', fg='White').pack(side=TOP, fill=X)

# StringVars
BK_STATUS = StringVar()
BK_NAME = StringVar()
BK_ID = StringVar()
AUTHOR_NAME = StringVar()
CARD_ID = StringVar()

# Frames
left_frame = Frame(root, bg='LightSkyBlue')
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96)
RT_frame = Frame(root, bg='DeepSkyBlue')
RT_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)
RB_frame = Frame(root)
RB_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Book Input Fields
Label(left_frame, text='Book Name', bg='LightSkyBlue').pack()
Entry(left_frame, textvariable=BK_NAME).pack()
Label(left_frame, text='Book ID', bg='LightSkyBlue').pack()
BK_ID_entry = Entry(left_frame, textvariable=BK_ID)
BK_ID_entry.pack()
Label(left_frame, text='Author Name', bg='LightSkyBlue').pack()
Entry(left_frame, textvariable=AUTHOR_NAME).pack()
Label(left_frame, text='Status', bg='LightSkyBlue').pack()
OptionMenu(left_frame, BK_STATUS, 'Available', 'Issued').pack()
Button(left_frame, text='Add Record', command=add_record).pack()

# Inventory Table
tree = ttk.Treeview(RB_frame, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Card ID'), show='headings')
tree.heading('Book Name', text='Book Name')
tree.heading('Book ID', text='Book ID')
tree.heading('Author', text='Author')
tree.heading('Status', text='Status')
tree.heading('Card ID', text='Card ID')
tree.pack(fill=BOTH, expand=True)

# Buttons
Button(RT_frame, text='Delete Record', command=remove_record).pack()
Button(RT_frame, text='Delete All', command=delete_inventory).pack()
Button(RT_frame, text='Update Record', command=update_record).pack()
Button(RT_frame, text='Change Availability', command=change_availability).pack()

clear_and_display()

# Close connection properly when closing the window
def on_closing():
    connector.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
