from datetime import date
from tkinter import *
import tkinter as tk
from typing import Match
from PIL import ImageTk, Image
import sqlite3
import pymongo
from tkinter.messagebox import askyesno, askquestion
import tkinter.font as tkFont

# For SQL query
from sqlalchemy import create_engine
from pymysql.constants import CLIENT
import pandas as pd

from config import USERNAME, MYSQL_PASSWORD
db = create_engine(f"mysql+pymysql://{USERNAME}:{MYSQL_PASSWORD}@127.0.0.1:3306/ECOMMERCE", 
        connect_args = {"client_flag": CLIENT.MULTI_STATEMENTS}
    )
# For mongodb query
from pymongo import MongoClient

#get data from mongodb
client = MongoClient()
mydb = client.Assignment
products = mydb.products
items = mydb.items
data = products.find({})


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self.switch_frame(Customer_Shopping_Catalogue_Page)

    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(side="top", fill="both", expand=True)


def main():
    app = App()
    app.geometry("1200x800")
    app.mainloop()

class Catalogue_Table(tk.LabelFrame):
    def __init__(self, data, *args, **kwargs):
        tk.LabelFrame.__init__(self, width=800, height=800, *args, **kwargs)

        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text="Category", anchor="w").grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(self, text="Model", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        tk.Label(self, text="Price ($)", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)
        tk.Label(self, text="Warranty (months)", anchor="w").grid(row=0, column=3, sticky="ew", padx=10)
        tk.Label(self, text="Number of Items Available", anchor="w").grid(row=0, column=4, sticky="ew", padx=10)
        items = mydb.items

        bg = ["#ffffff", "#d9e1f2"]
        row = 1
        for dic in data:
            categories_label = tk.Label(self, text=str(dic["Category"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])
            model_label = tk.Label(self, text=str(dic["Model"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])
            price_label = tk.Label(self, text=str(dic["Price ($)"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])
            warranty_label = tk.Label(self, text=str(dic["Warranty (months)"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])            
            numberOfItemsAvailable_label = tk.Label(self, text=str(items.count_documents({"Category": dic["Category"], "PurchaseStatus": "Unsold", "Model": dic["Model"]})), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])


            categories_label.grid(row=row, column=0, sticky="ew")
            model_label.grid(row=row, column=1, sticky="ew")
            price_label.grid(row=row, column=2, sticky="ew", )
            warranty_label.grid(row=row, column=3, sticky="ew")
            warranty_label.grid_columnconfigure(0, weight=5)
            numberOfItemsAvailable_label.grid(row=row, column=4, sticky="ew")
            numberOfItemsAvailable_label.grid_columnconfigure(0, weight=5)

            itemdata = list(items.find({}))
            store = ""
            for i in itemdata:
                if i['Category'] == dic['Category'] and i['PurchaseStatus'] == "Unsold" and i['Model'] == dic['Model']:
                    store = i
                    break

            if store != "":
                if items.count_documents({"Category": dic["Category"], "PurchaseStatus": "Unsold", "Model": dic["Model"]}) != 0:
                    action_button = tk.Button(self, text="Purchase", command=lambda store = store, dic = dic: self.purchase(store['ItemID'], self.master.master.customerId, int(dic['Price ($)'])))
                    action_button.grid(row=row, column=5, sticky="ew")

            row += 1

    def purchase(self, itemID, customerID, amount):
        answer = askyesno(title = 'Confirmation', message = 'Are you sure you want to purchase the item?')
        if answer:
            with db.begin() as conn:
                try:
                    savepoint = conn.begin_nested()
                    query = """
                    SELECT COUNT(*) INTO @p_count FROM Payments;
                    INSERT INTO Payments(paymentID, itemID, purchaseDate, customerID, amount) VALUES 
                    (@p_count + 1,%s,'%s','%s',%s)""" % (itemID, date.today().strftime("%Y-%m-%d"), customerID, amount)


                    conn.execute(query)

                    query2 = """UPDATE Items SET purchaseStatus = 'Sold' WHERE itemID = %s""" 
                    val = (itemID)
                    conn.execute(query2, val)
                    

                    items.update_one(
                        {"ItemID" : itemID},
                        { "$set": {"PurchaseStatus" : "Sold"} }
                    )

                    savepoint.commit()
                    print("yes")

                except:
                    savepoint.rollback()
                    print("No")

        self.master.filter_status1(self.master.clicked1)

class Advance_Table(tk.LabelFrame):
    def __init__(self, data, *args, **kwargs):
        tk.LabelFrame.__init__(self, width=800, height=800, *args, **kwargs)

        self.grid_columnconfigure(1, weight=1)
        tk.Label(self, text="Category", anchor="w").grid(row=0, column=0, sticky="ew", padx=10)
        tk.Label(self, text="Model", anchor="w").grid(row=0, column=1, sticky="ew", padx=10)
        tk.Label(self, text="Price ($)", anchor="w").grid(row=0, column=2, sticky="ew", padx=10)
        tk.Label(self, text="Warranty (months)", anchor="w").grid(row=0, column=3, sticky="ew", padx=10)
        tk.Label(self, text="Number of Items Available", anchor="w").grid(row=0, column=4, sticky="ew", padx=10)
        items_data = data
        products_data = products.find({})

        bg = ["#ffffff", "#d9e1f2"]
        row = 1
        for dic in products_data:
            if self.master.clicked3.get() != "Filter 1: All Price":
                if int(dic["Price ($)"]) != int(self.master.clicked3.get()[1:]):
                    continue
            
            if self.master.clicked1.get() == "Category: Lights":
                if dic["Category"] != "Lights":
                    continue

            if self.master.clicked1.get() == "Category: Locks":
                if dic["Category"] != "Locks":
                    continue  

            if self.master.clicked1.get() == "Model: Light1":
                if dic["Model"] != "Light1":
                    continue  

            if self.master.clicked1.get() == "Model: Light2":
                if dic["Model"] != "Light2":
                    continue  
            
            if self.master.clicked1.get() == "Model: Safe1":
                if dic["Model"] != "Safe1":
                    continue  

            if self.master.clicked1.get() == "Model: Safe2":
                if dic["Model"] != "Safe2":
                    continue  
            
            if self.master.clicked1.get() == "Model: Safe3":
                if dic["Model"] != "Safe3":
                    continue  

            if self.master.clicked1.get() == "Model: SmartHome1":
                if dic["Model"] != "SmartHome1":
                    continue  

            categories_label = tk.Label(self, text=str(dic["Category"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])
            model_label = tk.Label(self, text=str(dic["Model"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])
            price_label = tk.Label(self, text=str(dic["Price ($)"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])
            warranty_label = tk.Label(self, text=str(dic["Warranty (months)"]), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])  
            
            count = 0
            for idic in items_data:
                if idic['PurchaseStatus'] == 'Unsold':
                    if dic['Category'] == idic['Category']:
                        if dic['Model'] == idic['Model']:
                            count += 1

            numberOfItemsAvailable_label = tk.Label(self, text=str(count), anchor="w", borderwidth=2, relief="groove", padx=10, bg=bg[row%2])


            categories_label.grid(row=row, column=0, sticky="ew")
            model_label.grid(row=row, column=1, sticky="ew")
            price_label.grid(row=row, column=2, sticky="ew", )
            warranty_label.grid(row=row, column=3, sticky="ew")
            warranty_label.grid_columnconfigure(0, weight=5)
            numberOfItemsAvailable_label.grid(row=row, column=4, sticky="ew")
            numberOfItemsAvailable_label.grid_columnconfigure(0, weight=5)
        
            if count != 0:
                iid = items_data[0]["ItemID"]
                for idic in items_data:
                    if idic['PurchaseStatus'] == 'Unsold':
                        if dic['Category'] == idic['Category']:
                            if dic['Model'] == idic['Model']:
                                iid = idic['ItemID']

                action_button = tk.Button(self, text="Purchase", command=lambda dic = dic, iid = iid: self.purchase(iid, self.master.master.customerId, dic['Price ($)']))
                action_button.grid(row=row, column=5, sticky="ew")

            row += 1

    def purchase(self, itemID, customerID, amount):
        answer = askyesno(title = 'Confirmation', message = 'Are you sure you want to purchase the item?')
        if answer:
            with db.begin() as conn:
                try:
                    savepoint = conn.begin_nested()
                    query = """
                    SELECT COUNT(*) INTO @p_count FROM Payments;
                    INSERT INTO Payments(paymentID, itemID, purchaseDate, customerID, amount) VALUES 
                    (@p_count + 1,%s,'%s','%s',%s)""" % (itemID, date.today().strftime("%Y-%m-%d"), customerID, amount)


                    conn.execute(query)

                    query2 = """UPDATE Items SET purchaseStatus = 'Sold' WHERE itemID = %s""" 
                    val = (itemID)
                    conn.execute(query2, val)

                    items.update_one(
                        {"ItemID" : itemID},
                        { "$set": {"PurchaseStatus" : "Sold"} }
                    )

                    savepoint.commit()
                    print("yes")

                except:
                    savepoint.rollback()
                    print("No")

        self.master.filter_status2(self.master.clicked3, self.master.clicked4, self.master.clicked5, self.master.clicked6)


class Customer_Shopping_Catalogue_Page_Header(tk.LabelFrame):
    def __init__(self, master, *args, **kwargs):
        tk.LabelFrame.__init__(self, master, *args, **kwargs)
        self.master = master

        title = tk.Label(self, text="Shopping Catalogue Page", font=tkFont.Font(size=20), width = 20)
        title.grid(row=0, column=0, padx=(10, 5))

        tab1 = tk.Button(self, text="Refresh Shopping Catalogue", command= lambda: master.refresh("All"))
        tab1.grid(row=1, column=0, sticky = "ew", padx = 5)

        self.master.clicked1.set("All Categories & Models")
        self.master.clicked3.set("Filter 1: All Price")
        self.master.clicked4.set("Filter 2: All Color")
        self.master.clicked5.set("Filter 3: All Factory")
        self.master.clicked6.set("Filter 4: All Production Year")

        # dropdown filter
        tab2 = OptionMenu(self, self.master.clicked1, "All Models", "Category: Lights", "Category: Locks", "Model: Light1", "Model: Light2", "Model: SmartHome1", "Model: Safe1", "Model: Safe2", "Model: Safe3").grid(row=1, column=1, sticky="ew", padx=5)

        tab8 = tk.Button(self, text="Simple Search", command=lambda clicked1 = self.master.clicked1: master.filter_status1(self.master.clicked1)).grid(row=1, column=2, sticky="ew", padx=5)
        
        #tk.Label(self, text="Price Filter", anchor="w").grid(row=0, column=2, sticky="ew", padx=5)
        tab4 = OptionMenu(self, self.master.clicked3, "Filter 1: All Price", "$50", "$60", "$70", "$100", "$120", "$125", "$200").grid(row=2, column=0, sticky="ew", padx=5)

        #tk.Label(self, text="Color Filter", anchor="w").grid(row=0, column=3, sticky="ew", padx=5)
        tab5 = OptionMenu(self, self.master.clicked4, "Filter 2: All Color", "White", "Blue", "Yellow", "Green", "Black").grid(row=2, column=1, sticky="ew", padx=5)

        #tk.Label(self, text="Factory Filter", anchor="w").grid(row=0, column=4, sticky="ew", padx=5)
        tab6 = OptionMenu(self, self.master.clicked5, "Filter 3: All Factory", "Malaysia", "China", "Philippines").grid(row=2, column=2, sticky="ew", padx=5)
    
        #tk.Label(self, text="Production Year Filter", anchor="w").grid(row=0, column=5, sticky="ew", padx=5)
        tab7 = OptionMenu(self, self.master.clicked6, "Filter 4: All Production Year", "2014", "2015", "2016", "2017", "2018", "2019", "2020").grid(row=2, column=3, sticky="ew", padx=5)
        
        tab8 = tk.Button(self, text="Advanced Search", command= lambda: master.filter_status2(self.master.clicked3, self.master.clicked4, self.master.clicked5, self.master.clicked6)).grid(row=2, column=4, sticky="ew", padx=5)


        # tab3 = OptionMenu(self, clicked2, "All Models", "Light1", "Light2", "SmartHome1", "Safe1", "Safe2", "Safe3",
        # command=lambda clicked2 = clicked2: master.filter_status2(clicked2)).grid(row=0, column=2, sticky="ew", padx=5)
class Customer_Shopping_Catalogue_Page(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.master = master
        curr_data = products.find({})
        self.clicked1 = tk.StringVar()
        self.clicked2 = tk.StringVar()
        self.clicked3 = tk.StringVar()
        self.clicked4 = tk.StringVar()
        self.clicked5 = tk.StringVar()
        self.clicked6 = tk.StringVar()        

        self.header = Customer_Shopping_Catalogue_Page_Header(self, borderwidth=0, highlightthickness = 0, pady=10)
        self.header.pack(side="top", fill="x", expand=False)
        self.Catalogue_Table = Catalogue_Table(curr_data, self)
        self.Catalogue_Table.pack(side="top", fill="both", expand=True)

    
    def refresh(self, curr_view):

        self.Catalogue_Table.destroy()
        self.header.destroy()

        curr_data = products.find({})
        #curr_data = filter(self.filter.get(curr_view), curr_data)

        self.header = Customer_Shopping_Catalogue_Page_Header(self, borderwidth=0, highlightthickness = 0, pady=10)
        self.header.pack(side="top", fill="x", expand=False)
        self.Catalogue_Table = Catalogue_Table(curr_data, self)
        self.Catalogue_Table.pack(side="top", fill="both", expand=True)

    def filter_status1(self, curr_view):
        self.clicked3.set("Filter 1: All Price")
        self.clicked4.set("Filter 2: All Color")
        self.clicked5.set("Filter 3: All Factory")
        self.clicked6.set("Filter 4: All Production Year")

        self.Catalogue_Table.destroy()
        curr_data = products.find({})
        
        if self.clicked1.get() == 'Category: Lights':
            curr_data = products.find({"Category": "Lights"})    
        elif self.clicked1.get() == 'Category: Locks':
            curr_data = products.find({"Category": "Locks"})
        elif self.clicked1.get() == 'Model: Light1':
            curr_data = products.find({"Model": "Light1"})    
        elif self.clicked1.get() == 'Model: Light2':
            curr_data = products.find({"Model": "Light2"})    
        elif self.clicked1.get() == 'Model: Safe1':
            curr_data = products.find({"Model": "Safe1"})
        elif self.clicked1.get() == 'Model: Safe2':
            curr_data = products.find({"Model": "Safe2"})
        elif self.clicked1.get() == 'Model: Safe3':
            curr_data = products.find({"Model": "Safe3"})
        elif self.clicked1.get() == 'Model: SmartHome1':
            curr_data = products.find({"Model": "SmartHome1"})

        self.Catalogue_Table = Catalogue_Table(curr_data, self)
        self.Catalogue_Table.pack(side="top", fill="both", expand=True)
    
    def filter_status2(self, c3, c4, c5, c6):
        
        self.Catalogue_Table.destroy()
        items_data = list(items.find({}))
        price_list = ["$50", "$60", "$100", "$120", "$125"]
        model_list = ["Light1", "Light2", "Safe1", "Safe2", "Safe3"]

        for dic in items_data.copy():
            if c4.get() != "Filter 2: All Color":
                if dic["Color"] != c4.get():
                    if dic in items_data:
                        items_data.remove(dic)
            if c5.get() != "Filter 3: All Factory":
                if dic['Factory'] != c5.get():
                    if dic in items_data:
                        items_data.remove(dic)
            if c6.get() != "Filter 4: All Production Year":
                if dic['ProductionYear'] != c6.get():
                    if dic in items_data:
                        items_data.remove(dic)

            if c3.get() == "$70":
                if dic['Category'] != 'Lights':
                    if dic in items_data:
                        items_data.remove(dic)
                else:
                    if dic['Model'] != 'SmartHome1':
                        if dic in items_data:
                            items_data.remove(dic)

            if c3.get() == "$200":
                if dic['Category'] != 'Locks':
                    if dic in items_data:
                        items_data.remove(dic)
                else:
                    if dic['Model'] != 'SmartHome1':
                        if dic in items_data:
                            items_data.remove(dic)   

            if self.clicked1.get() == 'Category: Lights':
                if dic['Category'] != 'Lights':
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Category: Locks':
                if dic['Category'] != "Locks":
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Model: Light1':
                if dic['Model'] != "Light1":
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Model: Light2':
                if dic['Model'] != "Light2":
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Model: Safe1':
                if dic['Model'] != "Safe1":
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Model: Safe2':
                if dic['Model'] != "Safe2":
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Model: Safe3':
                if dic['Model'] != "Safe3":
                    if dic in items_data:
                        items_data.remove(dic)
            elif self.clicked1.get() == 'Model: SmartHome1':
                if dic['Model'] != "SmartHome1":
                    if dic in items_data:
                        items_data.remove(dic)

            for i in range(len(price_list)):
                if c3.get() == price_list[i]:
                    if dic['Model'] != model_list[i]:
                        if dic in items_data:
                            items_data.remove(dic)
                            break

        self.Catalogue_Table = Advance_Table(items_data, self)
        self.Catalogue_Table.pack(side="top", fill="both", expand=True)


    def switch_frame(self, frame_class):
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(side="top", fill="both", expand=True)


if __name__ == "__main__":
    main()  