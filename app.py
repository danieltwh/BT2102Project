from datetime import *
from tkinter import *
from tkinter import ttk
import tkinter.font as tkFont
from tkinter.ttk import Label, Style
from tkinter.messagebox import askyesno, askquestion
from typing import Match
from PIL import ImageTk, Image
import sqlite3
import pandas as pd

# For SQL query
from sqlalchemy import create_engine
from pymysql.constants import CLIENT
import pandas as pd

from config import USERNAME, MYSQL_PASSWORD
db = create_engine(f"mysql+pymysql://{USERNAME}:{MYSQL_PASSWORD}@127.0.0.1:3306/ECOMMERCE", 
        connect_args = {"client_flag": CLIENT.MULTI_STATEMENTS}
    )



##### IMPORT PAGES #####
from login import Admin_Login_Page, Admin_Signup_Page, Login_Page, Signup_Page
from request_page import Request_Page
from admin_request import Admin_Request_Page
from cus_request_details import Request_Details
from customerItem import Customer_Shopping_Catalogue_Page
from past_purchases import Past_Purchase_Page
from request_table_page import Request_Table_Page
from adminItem import Admin_Shopping_Catalogue_Page
from ResetDB import RESET_DB

PAGES = {
    "login": Login_Page, 
    "customer_shopping_catalogue": Customer_Shopping_Catalogue_Page,
    "customer_past_purchases": Past_Purchase_Page,
    "admin_request": Admin_Request_Page,
    "admin_items": Admin_Shopping_Catalogue_Page,
    "request_table":Request_Table_Page,
}

##########################

class SideBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, width=400, height=800)
        self.master = master

        catalogue_btn = Button(self, text="Shop", padx=10, highlightbackground="#ffffff", 
            font = self.master.font14, 
            command=lambda: self.master.switch_frame(PAGES.get("customer_shopping_catalogue")))
        catalogue_btn.grid(row=1, column=0, padx=(5, 10), sticky="EW", pady=(10, 5))

        past_purchases_btn = Button(self, text="Past Purchases / Make Request", wraplength=130,
            font = self.master.font14,
            command=lambda: self.master.switch_frame(PAGES.get("customer_past_purchases")))
        past_purchases_btn.grid(row=2, column=0, padx=(5, 10), sticky="EW", pady=(5, 5))

        request_table_btn = Button(self, text="Past Requests", wraplength=130,
            font = self.master.font14,
            command=lambda: self.master.switch_frame(PAGES.get("request_table")))
        request_table_btn.grid(row=3, column=0, padx=(5, 10), sticky="EW", pady=(5, 5))

        # ttk.Style().configure("red/black.TButton", foreground="black", background="red")

        logout_btn = Button(self, text="Logout", padx=10,  
            font = self.master.font14,
            command=lambda: self.master.logout())
        logout_btn.grid(row=4, column=0, padx=(5, 10), sticky="EW", pady=(5, 5))

class AdminSideBar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, width=400, height=800)
        self.master = master

        catalogue_btn = Button(self, text="Items", padx=10, highlightbackground="#ffffff", 
            font = self.master.font14,
            command=lambda: self.master.switch_frame(PAGES.get("admin_items")))
        catalogue_btn.grid(row=1, column=0, padx=(5, 10), sticky="EW", pady=(10, 5))

        past_purchases_btn = Button(self, text="Manage Request", wraplength=130,
            font = self.master.font14, padx=10,
            command=lambda: self.master.switch_frame(PAGES.get("admin_request")))
        past_purchases_btn.grid(row=2, column=0, padx=(5, 10), sticky="EW", pady=(5, 5))

        # ttk.Style().configure("red/black.TButton", foreground="black", background="red")

        logout_btn = Button(self, text="Logout", padx=10,  
            font = self.master.font14,
            command=lambda: self.master.logout())
        logout_btn.grid(row=3, column=0, padx=(5, 10), sticky="EW", pady=(5, 5))

        DB_reset_btn = Button(self, text = "Reset DB", padx=10,
            font = self.master.font14, 
            bg = "#fe5f55", bd=2.5,
            highlightthickness=4, highlightbackground="#fe5f55", highlightcolor="#fe5f55",
            command=lambda: self.resetDB())
        # DB_reset_btn.grid(row=4, column=0, padx=(5, 10), sticky="EW",pady=(660, 5))
        DB_reset_btn.grid(row=4, column=0, padx=(5, 10), sticky="EW",pady=(5, 5))

    
    def resetDB(self):
        answer = askyesno(title = 'ResetDB Confirmation', message = 'Are you sure?')
        if answer:
            RESET_DB()
            # self.master.switch_frame(PAGES.get("customer_shopping_catalogue"))
            self.master.logout()
        
        


class App(Tk):
    def __init__(self):
        Tk.__init__(self)
        self._frame = None
        self._sideBar= None
        
        self.customerId = ""
        self.adminId = "NULL"
        
        # self.mount_sidebar()
        # self.switch_frame(Request_Details)

        self.configure(background="#e0fbfc")
        self.font12 = tkFont.Font(self, size=12)
        self.font14 = tkFont.Font(self, size=14)
        self.font16 = tkFont.Font(self, size=16)
        self.font18 = tkFont.Font(self, size=18)
        self.font20 = tkFont.Font(size=20)
        self.font24 = tkFont.Font(size=24)
        # self.option_add('*Font', '12')

        self.title("Handy Hardware")

        # self.style = Style(self)

        # self.style.configure("TLabel", font=('Helvetica', 20))
        # self.style.configure("TButton", font=('Helvetica', 20))
        # self.style.configure("TFrame", font=('Helvetica', 20))
        # self.style.configure("TLabelFrame", font=('Helvetica', 20))

        self.load_login_page();

        

    def switch_frame(self, frame_class):
        print(self.customerId if self.customerId else self.adminId)
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame

        if frame_class in [Login_Page, Signup_Page, Admin_Login_Page, Admin_Signup_Page]:
            # self._frame.pack(fill="both", expand=True, padx=0, pady=225, anchor ="center")
            self._frame.pack(expand=True)
        else:
            self._frame.pack(side="right", fill="both", expand=True, anchor = "nw", padx=(10, 0))
            # self._frame.grid(row=0, column=1, )

    ## Switch frame that passes an id
    def id_switch_frame(self, id, frame_class):
        new_frame = frame_class(id,self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(side="top", fill="both", expand=True)

    ### FOR CUSTOMERS ###
    def mount_sidebar(self):
        self._sideBar = SideBar(self)
        self._sideBar.config(bg="#495867")
        self._sideBar.pack(side="left", fill="y")

    def unmount_sidebar(self):
        self._sideBar.destroy()
    
    def load_login_page(self):
        new_frame = PAGES.get("login")(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        # self._frame.pack(fill="both", expand=True, padx=0, pady=225)
        self._frame.pack(expand=True)
    
    def logout(self):
        self.customerId = ""
        self.adminId = ""
        self.unmount_sidebar()
        self.load_login_page()

    def login(self, customerId):
        self.customerId = customerId
        self.auto_cancel_request()
        self.mount_sidebar()
        self.switch_frame(PAGES.get("customer_shopping_catalogue"))


    ### FOR ADMINS ###   
    def mount_admin_sidebar(self):
        self._sideBar = AdminSideBar(self)
        self._sideBar.config(bg="#495867")
        self._sideBar.pack(side="left", fill="y")

    def admin_login(self, adminId):
        self.adminId = adminId
        self.mount_admin_sidebar()
        self.switch_frame(PAGES.get("admin_request"))
    

    def auto_cancel_request(self):
        df_check = pd.read_sql_query(f"""
                SELECT r.requestID, r.requestStatus, f.creationDate, TIMESTAMPDIFF(DAY, f.creationDate, CURRENT_DATE())
                FROM Requests r 
                LEFT JOIN ServiceFees f ON f.requestID = r.requestID
                WHERE r.requestStatus in ('Submitted and Waiting for payment') AND 
                TIMESTAMPDIFF(DAY, f.creationDate, CURRENT_DATE()) > 10;
                """, db)

        for request in df_check.itertuples():
            requestId = int(request.requestID)
            requestStatus = request.requestStatus
            creationDate = request.creationDate

            # Auto-cancel Request not paid after 10 days
            time_diff = date.today() - creationDate

            if time_diff.days > 10 and requestStatus == 'Submitted and Waiting for payment':  
                
                requestStatus = "Cancelled"

                print("Auto-cancel", requestId)
                
                with db.begin() as conn2:
                    try:
                        savepoint = conn2.begin_nested()
                        conn2.execute(f"""
                        UPDATE Requests
                        SET requestStatus = "Cancelled"
                        WHERE requestID = {requestId}
                        ;
                        """)

                        conn2.execute(f"""
                        UPDATE Services
                        SET serviceStatus = "Completed"
                        where requestID = {requestId}
                        ;
                        """)

                        savepoint.commit()
                    except:
                        savepoint.rollback()
                        print("Failed to auto-cancel request")



def main():
    # root = Tk()
    # root.title("OSHE")
    # # root.iconbitmap('coffee.ico')
    # root.geometry("800x800")
    # # app = Signup_Page(root)
    # # app = Login_Page(root)
    # root.mainloop()

    app = App()
    
    # app.option_add("*Label.Font", '30')
    app.geometry("1400x800")
    # style = Style(app)
    # style.configure("TLabel", font=('Helvetica', 20))
    app.mainloop()

if __name__ == "__main__":
    main()