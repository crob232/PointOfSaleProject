import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

# Connect to a database (or create one if it doesn't exist)
conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Create a table for the products
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
''')

conn.commit()
conn.close()

def update_product_price(product_code, new_price):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = ? WHERE code = ?", (new_price, product_code))
        conn.commit()

def update_product_name(product_code, new_name):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET name = ? WHERE code = ?", (new_name, product_code))
        conn.commit()

def update_product_stock(product_code, new_stock):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = ? WHERE code = ?", (new_stock, product_code))
        conn.commit()

def fetch_all_products():
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        return cursor.fetchall()

def display_product_buttons():
    products = fetch_all_products()

    for product in products:
        code, name, _, _ = product
        product_button = tk.Button(root, text=name, command=lambda c=code: add_to_cart(c))
        product_button.pack(pady=5)

def open_new_product_dialog():
    def save_product():
        code = code_entry.get()
        name = name_entry.get()
        price = float(price_entry.get())
        stock = int(stock_entry.get())
        add_product(code, name, price, stock)
        new_product_window.destroy()

    new_product_window = tk.Toplevel(root)
    new_product_window.title("Add New Product")
    
    tk.Label(new_product_window, text="Product Code").grid(row=0, column=0, padx=10, pady=10)
    code_entry = tk.Entry(new_product_window)
    code_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(new_product_window, text="Product Name").grid(row=1, column=0, padx=10, pady=10)
    name_entry = tk.Entry(new_product_window)
    name_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(new_product_window, text="Product Price").grid(row=2, column=0, padx=10, pady=10)
    price_entry = tk.Entry(new_product_window)
    price_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(new_product_window, text="Product Stock").grid(row=3, column=0, padx=10, pady=10)
    stock_entry = tk.Entry(new_product_window)
    stock_entry.grid(row=3, column=1, padx=10, pady=10)

    save_button = tk.Button(new_product_window, text="Save Product", command=save_product)
    save_button.grid(row=4, columnspan=2, pady=20)


def add_product(code, name, price, stock):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO products (code, name, price, stock) VALUES (?, ?, ?, ?)", (code, name, price, stock))
        conn.commit()

def get_product(code):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE code=?", (code,))
        return cursor.fetchone()

def update_stock(code, stock_change):
    with sqlite3.connect('inventory.db') as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET stock = stock + ? WHERE code=?", (stock_change, code))
        conn.commit()

def open_database_viewer():
    # Create a new window
    view_window = tk.Toplevel(root)
    view_window.title("View Products")
    view_window.geometry("600x400")  # Adjust the size as needed

    # Create a Treeview widget
    tree = ttk.Treeview(view_window, columns=('Product Code', 'Product Name', 'Product Price', 'Product Stock'), show='headings')

    # Set up column headings and their widths
    tree.heading('Product Code', text='Product Code')
    tree.heading('Product Name', text='Product Name')
    tree.heading('Product Price', text='Product Price')
    tree.heading('Product Stock', text='Product Stock')

    tree.column('Product Code', width=100)
    tree.column('Product Name', width=200)
    tree.column('Product Price', width=100)
    tree.column('Product Stock', width=100)

    # Insert products into the Treeview
    products = fetch_all_products()
    for product in products:
        tree.insert('', tk.END, values=product)

    # Pack the Treeview to the window
    tree.pack(fill=tk.BOTH, expand=True)

    # Add a scrollbar (useful if you have many products)
    scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    def on_item_double_click(event):
        # Remove any existing in-place editor
        if hasattr(tree, 'editor'):
            tree.editor.destroy()

        # Get selected item
        item = tree.selection()[0]
        column = tree.identify_column(event.x)

        # Create in-place editor
        x, y, width, height = tree.bbox(item, column)
        tree.editor = ttk.Entry(tree)
        tree.editor.place(x=x, y=y, width=width, height=height)

        # Load the current value into the editor
        tree.editor.insert(0, tree.item(item, 'values')[tree.heading(column)['id']])
        
        # Focus on the editor and bind it to save or cancel actions
        tree.editor.focus_set()
        tree.editor.bind('<Return>', lambda e: finish_editing(item, column))
        tree.editor.bind('<Escape>', lambda e: tree.editor.destroy())

    def finish_editing(item, column):
        # Get new value from the editor
        new_value = tree.editor.get()

        # Update the treeview
        values = list(tree.item(item, 'values'))
        values[tree.heading(column)['id']] = new_value
        tree.item(item, values=values)

        # Destroy the editor
        tree.editor.destroy()

        # Update the database (assuming your database update function is called 'update_product')
        product_code = values[0]
        if column == "#1":  # Product Code
            # If product code is changed, handle it accordingly
            pass
        elif column == "#2":  # Product Name
            update_product_name(product_code, new_value)
        elif column == "#3":  # Product Price
            update_product_price(product_code, float(new_value))
        elif column == "#4":  # Product Stock
            update_product_stock(product_code, int(new_value))

    tree.bind("<Double-1>", on_item_double_click)



# Sample inventory
inventory = {
    "001": {"name": "Hotdog", "price": 4.00, "stock": 100},
    "002": {"name": "German", "price": 5.00, "stock": 50},
}

current_transaction = []

def add_to_cart(product_code):
    product = get_product(product_code)
    
    if not product:
        messagebox.showerror("Error", "Product not found!")
        return
    
    _, _, _, stock = product

    if stock <= 0:
        messagebox.showerror("Error", "Out of stock!")
        return
    
    current_transaction.append(product_code)
    update_display()

#def add_to_cart(product_code):
#    if product_code not in inventory:
#        messagebox.showerror("Error", "Product not found!")
#        return
    
#    if inventory[product_code]['stock'] <= 0:
#        messagebox.showerror("Error", "Out of stock!")
#        return
    
#    current_transaction.append(product_code)
#    update_display()

def update_display():
    total = sum(inventory[code]['price'] for code in current_transaction)
    display_var.set(f"Items: {len(current_transaction)}, Total: ${total:.2f}")

def display_product_buttons():
    products = fetch_all_products()

    for product in products:
        code, name, _, _ = product
        product_button = tk.Button(root, text=name, command=lambda c=code: add_to_cart(c))
        product_button.pack(pady=5)

#def finalize_transaction():
##    for code in current_transaction:
#        inventory[code]['stock'] -= 1
#    current_transaction.clear()
#    update_display()
#    messagebox.showinfo("Success", "Transaction finalized!")

def finalize_transaction():
    for code in current_transaction:
        update_stock(code, -1)
    current_transaction.clear()
    update_display()
    messagebox.showinfo("Success", "Transaction finalized!")


root = tk.Tk()
root.title("POS System")
root.geometry("800x600")

product_entry = tk.Entry(root)
product_entry.pack(pady=20)

add_button = tk.Button(root, text="Add to Cart", command=lambda: add_to_cart(product_entry.get()))
add_button.pack()

display_var = tk.StringVar()
display_label = tk.Label(root, textvariable=display_var)
display_label.pack(pady=20)

finalize_button = tk.Button(root, text="Finalize Transaction", command=finalize_transaction)
finalize_button.pack(pady=20)

add_product_button = tk.Button(root, text="Add New Product", command=open_new_product_dialog)
add_product_button.pack(pady=20)

view_products_button = tk.Button(root, text="View Products", command=open_database_viewer)
view_products_button.pack(pady=20)

display_product_buttons()

update_display()

root.mainloop()
