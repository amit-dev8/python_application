import os
import re
import csv
import qrcode
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime
from tkcalendar import DateEntry
from tkcalendar import Calendar
import textwrap
import tkinter as tk
from tkinter import ttk
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, messagebox
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from tkinter import filedialog, ttk
from ttkwidgets import CheckboxTreeview
import threading
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import mm
import requests
import json
import time
from collections import deque
from reportlab.pdfbase.ttfonts import TTFont
# Register normal and bold Arial fonts
pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))         # Regular Arial
pdfmetrics.registerFont(TTFont('Arial-Bold', 'arialbd.ttf'))  # Bold Arial
pdfmetrics.registerFont(TTFont('Arial-Black', 'ariblk.ttf'))
current_date = datetime.now().strftime('%Y-%m-%d')  # Format: YYYY-MM-DD
current_time = datetime.now().strftime('%H:%M:%S')  # Format: HH:MM:SS

class EventApp:
    def __init__(self, root):   
        self.root = root
        self.root.title("Scanner")
        root.geometry("720x550")

                # --- Initialize Badge Checkbutton Variables globally ---
        self.urn_var = tk.IntVar(value=1)
        self.name_var = tk.IntVar(value=1)
        self.desg_var = tk.IntVar(value=1)
        self.comp_var = tk.IntVar(value=1)
        self.qr_var = tk.IntVar(value=1)

          # initialize bulk_page as empty frame
        self.bulk_page = tk.Frame(self.root)
        self.bulk_page.pack_forget()
   
         # Main Title
        self.Label = tk.Label(root, text="Offline Software", font=("Times", 30, "bold"))
        self.Label.pack(pady=(10, 10))
        self.myLabel = tk.Label(root, text="Scan and Print", font=("Times", 25, "bold"),fg="royal blue")
        self.myLabel.pack(anchor="nw", pady=10)  # Align to the left
      
          # Create a navbar
        self.create_navbar()
        self.login_mode = None  # Can be 'admin' or 'database'
 
        self.frame_top = tk.Frame(root,width=590, height=880,highlightbackground='black', highlightthickness=1)
        self.frame_top.pack(anchor="nw", pady=10)      
       
        # QR Entry
        self.label = tk.Label(self.frame_top, text="Enter QR:", font=("Times", 15),anchor='w')
        self.label.pack(side=tk.LEFT,pady=15, padx=15)

        self.qr_entry = tk.Entry(self.frame_top, width=90)
        self.qr_entry.pack(side=tk.LEFT,pady=25, padx=25)
               # Ensure focus is set after initialization
        root.after(100, self.qr_entry.focus_set)   
        #  #submitting by pressing enter
        self.qr_entry.bind("<Return>", self.inpp)
  
        # Spot details
        self.frame_down = tk.Frame(root, width=600, height=880 )
        self.frame_down.pack(anchor='w')

        self.main_label = tk.Label(self.frame_down, text="Spot Registration", font=("Helvetica", 25,"bold"), fg="royal blue")
        self.main_label.grid(row=0, column=0, columnspan=1, pady=(30, 10), padx=5, sticky="w")  # Increased top padding
     
        # Dropdown for category selection
        drop_label = tk.Label(self.frame_down, text="Category:", font=("Times", 15,"bold"), anchor="w")
        drop_label.grid(row=1, column=0, padx=5, pady=10 ,sticky ="w")
            
        self.category_var = StringVar(self.frame_down)
        self.category_var.set('V')  # default value
         
        prefix_menu = OptionMenu(self.frame_down, self.category_var, 'D','EX', 'M', 'OG', 'VB' , 'SPK', 'V' , 'SP', 'VIP' , 'WS')
        prefix_menu.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="w")  # Shift to the left
        
      # Entry field for counter        
        self.counter_value = tk.StringVar()

        counter_label = tk.Label(self.frame_down, text="Counter No:", font=("times", 15, "bold"))
        counter_label.grid(row=1, column=70, padx=20, pady=10)

        counter_entry = tk.Entry(self.frame_down, textvariable=self.counter_value, width=10)
        counter_entry.grid(row=1, column=71, padx=20, pady=10)
     
        # spot Name
        self.spot_label = tk.Label(self.frame_down, text="Name:", font=("Times", 15,"bold"), anchor="w")
        self.spot_label.grid(row=3, column=0, padx=5, pady=10, sticky="w") 

        self.spot_entry = tk.Entry(self.frame_down, width=40)
        self.spot_entry.grid(row=3, column=1, pady=5)      

        # spot Designation
        self.designation_label = tk.Label(self.frame_down, text="Designation:", font=("Times", 15,"bold"))
        self.designation_label.grid(row=4, column=0, padx=5, pady=10,sticky="w")

        self.designation_entry = tk.Entry(self.frame_down, width=40)
        self.designation_entry.grid(row=4, column=1, pady=5)

        # spot Company
        self.company_label = tk.Label(self.frame_down, text="Company:", font=("Times", 15,"bold"))
        self.company_label.grid(row=5, column=0, padx=5, pady=10,sticky="w")

        self.company_entry = tk.Entry(self.frame_down, width=40)
        self.company_entry.grid(row=5, column=1, pady=5)

        # spot Contact number
        self.contact_label = tk.Label(self.frame_down, text="Contact number:", font=("Times", 15,"bold"))
        self.contact_label.grid(row=6, column=0, padx=5, pady=10 ,sticky="w")
        
        self.contact_entry = tk.Entry(self.frame_down, width=40)
        self.contact_entry.grid(row=6, column=1, pady=5)

        # spot email number
        self.email_label = tk.Label(self.frame_down, text="Email:", font=("Times", 15,"bold"))
        self.email_label.grid(row=7, column=0, padx=5, pady=10 , sticky="w")

        self.email_entry = tk.Entry(self.frame_down, width=40)
        self.email_entry.grid(row=7, column=1, pady=5)

        # Submit button
        self.spot_submit = tk.Button(self.frame_down, text="Submit", command=self.store_spot_registration, font=("Times", 15))
        self.spot_submit.grid(row=8, column=1, pady=10)  

        self.email_entry.bind('<KeyPress-Return>', lambda event=None: self.store_spot_registration())

        # self.submit_button = tk.Button(self.frame_top, text="Submit", command=self.inpp, font=("Arial", 15))
        # self.submit_button.pack(pady=25, padx=20)
       
         # Create and place the label for the count
        self.label_count = tk.Label(root, text="Counts:", font=("Arial", 14))
        self.label_count.pack(side="right", anchor="ne", pady=1)

          # Scan Frame
        self.entry_frame = tk.Frame(root, width=1100, height=980, highlightbackground='black', highlightthickness=1, relief="raised", bd=2)
        self.entry_frame.place(relx=0.5, rely=0.5, anchor="center")  # Center the frame
        self.entry_frame.pack(pady=20, anchor="n")

        # Add a heading for the scan input
        scan_heading = tk.Label(self.entry_frame, text="Entry Scan", font=("Times", 25, "bold"), fg="black")
        scan_heading.pack(pady=(10, 5))
        
          # Scan Entry
        self.scan_entry = tk.Entry(self.entry_frame, width=40)
        self.scan_entry.pack(padx=35, pady=35, anchor="center")   
           # Ensure focus is set after initialization
        root.after(100, self.scan_entry.focus_set)  

        # Submitting by pressing Enter
        self.scan_entry.bind("<KeyPress-Return>", lambda event=None: self.scan_data())
        # Clear the entry box
        self.scan_entry.delete(0, tk.END) 

        # --- Admin Frame ---
        self.admin_frame = tk.Frame(root, width=890, height=880, highlightbackground='black', highlightthickness=1)
        self.admin_frame.pack_forget()  # Hide initially

        self.admin_heading = tk.Label(self.admin_frame, text="Admin Login", font=("Times", 25, "bold"), fg="black")
        self.admin_heading.pack(pady=(10, 5))

        self.Label = tk.Label(self.admin_frame, text="Enter the username", font=('Times', 15))
        self.Label.pack()

        self.user_entry = tk.Entry(self.admin_frame, width=40)
        self.user_entry.pack(padx=25, pady=35, anchor="center")

        self.label = tk.Label(self.admin_frame, text="Enter the Password", font=('Times', 15))
        self.label.pack()

        self.pass_entry = tk.Entry(self.admin_frame, show='*', width=40)
        self.pass_entry.pack(padx=25, pady=25, anchor="center")

        self.login_button=tk.Button(self.admin_frame,text="Login",command=self.login,font=("Times",15))
        self.login_button.pack(pady=25, padx=20)  
        self.login_button.bind('<KeyPress-Return>', lambda event=None: self.login())
   
         # dashboard frame
        self.dashboard_frame = tk.Frame(root, width=590, height=880)     
        self.dashboard_frame.pack(fill="both", expand=True)

            # ================== DASHBOARD LAYOUT WRAPPER ==================
        section_wrapper = tk.Frame(self.dashboard_frame)
        section_wrapper.pack(pady=20)

        # A reusable style for section frames
        def create_section(title):
            frame = tk.LabelFrame(section_wrapper, text=title, font=("times", 12, "bold"), padx=20, pady=15)
            frame.pack(fill="x", pady=10)
            return frame


        # ================== API BUTTON ==================
        api_frame = create_section("Offline to Online")

        tk.Button(api_frame, text="POST DATA", command=self.upload_to_api,font=("times", 12, "bold"), bd=5, width=30).grid(row=0, column=0, pady=5)

        # ================== Scan-Print ==================
        scan_frame = create_section("Scan - Print Data")

        tk.Label(scan_frame, text="Start Date:", font=("times", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.scan_start = DateEntry(scan_frame, width=14, date_pattern='yyyy-mm-dd')
        self.scan_start.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(scan_frame, text="End Date:", font=("times", 12)).grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.scan_end = DateEntry(scan_frame, width=14, date_pattern='yyyy-mm-dd')
        self.scan_end.grid(row=0, column=3, padx=10, pady=5)

        tk.Button(scan_frame, text="Download Scan-Print Data",
                command=lambda: self.scanprint_excel(self.scan_start.get_date(), self.scan_end.get_date()),
                font=("times", 12, "bold"), bd=5, width=30).grid(row=0, column=4, padx=20, pady=5)


        # ================== Spot Registration ==================
        spot_frame = create_section("Spot Registration Data")

        tk.Label(spot_frame, text="Start Date:", font=("times", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.spot_start = DateEntry(spot_frame, width=14, date_pattern='yyyy-mm-dd')
        self.spot_start.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(spot_frame, text="End Date:", font=("times", 12)).grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.spot_end = DateEntry(spot_frame, width=14, date_pattern='yyyy-mm-dd')
        self.spot_end.grid(row=0, column=3, padx=10, pady=5)

        tk.Button(spot_frame, text="Download Spot Data",
                command=lambda: self.spotdata_excel(self.spot_start.get_date(), self.spot_end.get_date()),
                font=("times", 12, "bold"), bd=5, width=30).grid(row=0, column=4, padx=20, pady=5)


        # ================== Entry Scan ==================
        entry_frame = create_section("Entry Scan Data")

        tk.Label(entry_frame, text="Start Date:", font=("times", 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.entry_start = DateEntry(entry_frame, width=14, date_pattern='yyyy-mm-dd')
        self.entry_start.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(entry_frame, text="End Date:", font=("times", 12)).grid(row=0, column=2, padx=10, pady=5, sticky="e")
        self.entry_end = DateEntry(entry_frame, width=14, date_pattern='yyyy-mm-dd')
        self.entry_end.grid(row=0, column=3, padx=10, pady=5)

        tk.Button(entry_frame, text="Download Entry Scan Data",
                command=lambda: self.entrydata_excel(self.entry_start.get_date(), self.entry_end.get_date()),
                font=("times", 12, "bold"), bd=5, width=30).grid(row=0, column=4, padx=20, pady=5)

         #database frame
        self.database_frame = tk.Frame(root,width=590,height=880)     
        self.truncate_button = tk.Button(self.database_frame, text="Truncate Database",command=self.truncate_table,font=("times", 12, "bold"),bd=6,width=25,height=1)
        self.truncate_button.pack(pady=35, padx=20)

           # Frame for datawise Search on entry frame
        self.search_frame = tk.Frame(root)
        self.search_frame.pack(pady=5, anchor="w") 

        # Start Date
        tk.Label(self.search_frame, text="Start Date:", font=("Arial", 12)).pack(side="left", padx=5)
        self.start_date = DateEntry(
            self.search_frame,
            width=12,
            background='black',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.start_date.pack(side="left", padx=5)

        # End Date
        tk.Label(self.search_frame, text="End Date:", font=("Arial", 12)).pack(side="left", padx=5)
        self.end_date = DateEntry(
            self.search_frame,
            width=12,
            background='black',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.end_date.pack(side="left", padx=5)

        # Button
        self.check_btn = tk.Button(self.search_frame, text="Check Counts", command=self.show_counts_by_date)
        self.check_btn.pack(side="left", padx=10)
   
        # Clear Button
        self.clear_btn = tk.Button(self.search_frame, text="Clear", command=self.clear_result)
        self.clear_btn.pack(side="left", padx=5)

        # Result label
        self.result_label = tk.Label(root, text="", font=("Arial", 14), fg="black")
        self.result_label.pack(pady=10, anchor="w")   # Stick to left


        self.setting_frame = tk.Frame(root, width=890, height=880)
        self.setting_frame.pack_forget()  # Hide initially
        
        self.badge_frame = None 

          # Initially hide all frames
        self.entry_frame.pack_forget()
        self.admin_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        # Call the main page function to set up UI
        self.main_page()
        self.create_spot_table()
        self.create_badge_settings_table()
        self.entries = []  

          #  values
        self.urn = ""
        self.name = ""
        self.designation = ""
        self.company = ""
        self.country = ""
        self.city = ""
        self.receiptno = ""
        self.email = ""
        self.contact = ""

    def create_navbar(self):
        # Create a menu bar
        menubar = tk.Menu(self.root)
        root.config(menu=menubar)
    
        # File menu
        homemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Home", menu=homemenu)
        homemenu.add_command(label="Home Page", command=self.main_page)

          # scan menu
        scanmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Entry scan", menu=scanmenu)
        scanmenu.add_command(label="Entry scan", command=self.scandata_frame)

        # Admin menu
        adminmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Admin", menu=adminmenu)
        adminmenu.add_command(label="Admin Login", command=self.admin_login)
        adminmenu.add_command(label="Badge Setting Login", command=self.badge_login)
        adminmenu.add_command(label="Bulk Login", command=self.bulk_login)
        adminmenu.add_separator()
        adminmenu.add_command(label="Truncate Table", command=self.truncate_login) 
        root.config(menu=menubar)
  
        #   exit menu
        exitmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Exit", menu=exitmenu)
        exitmenu.add_command(label="Exit", command=self.root.destroy)
        # Set to window
        # self.root.config(menu=menubar)
    
        self.urn = ""
        self.designation = ""
        self.country = ""
        self.city = ""
        self.receiptno = ""
        self.tab = []
        self.contact="8098767876"

    def inpp(self, event=None):
        qr_data = self.qr_entry.get().upper()     
        if qr_data:
            try:             
                self.urn,self.name,self.designation,self.company,self.country,self.city,self.receiptno,self.email,self.contact = qr_data.split(":")
                self.gen()
                self.excel()
                self.insert_data()
                # check if badge settings already exist
                conn = sqlite3.connect("database.db")
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM badge_template_settings")
                badge_setting_exists = cur.fetchone()[0]
                conn.close()
                if badge_setting_exists > 0:
                    # Only call PDF generation if settings exist
                    self.generate_badge_pdf()
                    # self.upload_to_api()
                else:
                    # first time: open settings panel
                    self.save_and_generate()

            except ValueError:
                messagebox.showerror("Error","Invalid Format")
        else:
            messagebox.showerror("Error", "Please enter QR data.")

# eve_datas for qr_scan
    def insert_data(self): 
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')    
        # Connect to the database
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS scan_datas (
                urn VARCHAR  ,
                name VARCHAR(255),
                designation VARCHAR(255),
                company VARCHAR(255),
                country VARCHAR(255),
                city VARCHAR(255),
                receiptno VARCHAR(50),
                email VARCHAR(255),
                contact BIGINT,
                date DATE,
                time TIME
            )
        """)

        # Insert data u3sing parameterized query
        query = """
            INSERT INTO scan_datas (urn,name, designation, company, country, city, receiptno, email, contact, date, time)
            VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.execute(query, (
            self.urn,
            self.name,
            self.designation,
            self.company,
            self.country,
            self.city,
            self.receiptno,
            self.email,
            self.contact,
            current_date,
            current_time
        ))

        # Commit and close the connection
        conn.commit()
        conn.close()
        # Clear the entry field
        self.qr_entry.delete(0, tk.END)  # Clear the QR entry field

    # entry_datas for entry scan
    def entry_data(self):
        # Assuming `conn` is a SQLite connection object
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        # Create the table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entry_datas (
                    urn VARCHAR ,
                    name TEXT,
                    designation TEXT,
                    company TEXT,
                    country TEXT,
                    city TEXT,
                    receiptno TEXT,
                    email VARCHAR,
                    contact INTEGER,
                    date DATE,
                    time TIME
                )
        """)
        # Get the current date and time
        current_date = datetime.now().strftime("%Y-%m-%d")
        current_time = datetime.now().strftime("%H:%M:%S")

        check_query = "SELECT * FROM entry_datas WHERE urn=?"
        cur.execute(check_query, (self.urn,))                                                                                                                      

        # Check if there are any rows returned
        if len(cur.fetchall()) == 0:
            # If no rows, insert as new
            try:
                entry_query = """
                INSERT INTO entry_datas (urn, name, designation, company, country, city, receiptno, email, contact, date, time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                cur.execute(entry_query, (
                    self.urn, self.name, self.designation, self.company, self.country,
                    self.city, self.receiptno, self.email, self.contact, current_date, current_time
                ))

                # Welcome label
                if hasattr(self, 'wellabel') and self.wellabel.winfo_exists():
                    self.wellabel.config(text=f"WELCOME\n{self.name}")
                else:
                    self.wellabel = tk.Label(self.entry_frame, text=f"WELCOME\n{self.name}",
                                            font=("Times", 25), anchor='center')
                    self.wellabel.pack(padx=15, pady=15)

                # Commit insert
                conn.commit()

                # --- Update unique counts ---
                cur.execute("SELECT COUNT(DISTINCT urn) FROM entry_datas WHERE date=?", (current_date,))
                unique_count = cur.fetchone()[0]
                display_date = datetime.now().strftime("%d/%m/%Y")

                if hasattr(self, 'label_count') and self.label_count.winfo_exists():
                    self.label_count.config(text=f"Counts ({display_date}): {unique_count}")
                else:
                    self.label_count = tk.Label(self.root,
                                                text=f"Counts ({display_date}): {unique_count}",
                                                font=("Arial", 14), fg="blue")
                    self.label_count.pack(side="bottom", anchor="s", pady=5)

                cur.close()
                conn.close()
                self.scan_entry.delete(0, tk.END)

            except sqlite3.OperationalError as oe:
                messagebox.showerror("Database Error", f"Operational Error: {oe}")
            except Exception as e:
                messagebox.showerror("Database Error", f"An unexpected error occurred: {e}")

        else:
            # Duplicate URN, still insert (to track multiple scans)
            entry_query = """
                INSERT INTO entry_datas (urn, name, designation, company, country, city, receiptno, email, contact, date, time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            cur.execute(entry_query, (
                self.urn, self.name, self.designation, self.company, self.country,
                self.city, self.receiptno, self.email, self.contact, current_date, current_time
            ))

            # Welcome again label
            if hasattr(self, 'wellabel') and self.wellabel.winfo_exists():
                self.wellabel.config(text=f"WELCOME AGAIN\n{self.name}")
            else:
                self.wellabel = tk.Label(self.entry_frame, text=f"WELCOME AGAIN\n{self.name}",
                                        font=("Times", 25), anchor='center')
                self.wellabel.pack(padx=15, pady=15)

            # Commit insert
            conn.commit()

            # --- Update unique counts ---
            cur.execute("SELECT COUNT(DISTINCT urn) FROM entry_datas WHERE date=?", (current_date,))
            unique_count = cur.fetchone()[0]
            display_date = datetime.now().strftime("%d/%m/%Y")

            if hasattr(self, 'label_count') and self.label_count.winfo_exists():
                self.label_count.config(text=f"Counts ({display_date}): {unique_count}")
            else:
                self.label_count = tk.Label(self.root,
                                            text=f"Counts ({display_date}): {unique_count}",
                                            font=("Arial", 14), fg="blue")
                self.label_count.pack(side="bottom", anchor="s", pady=5)
            cur.close()
            conn.close()
            self.scan_entry.delete(0, tk.END)

    def show_counts_by_date(self):
        start_date = self.start_date.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date.get_date().strftime("%Y-%m-%d")

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        # Total scans (all rows within range)
        cur.execute("SELECT COUNT(*) FROM entry_datas WHERE date BETWEEN ? AND ?", (start_date, end_date))
        total_scans = cur.fetchone()[0]

        # Unique scans (distinct urns within range)
        cur.execute("SELECT COUNT(DISTINCT urn) FROM entry_datas WHERE date BETWEEN ? AND ?", (start_date, end_date))
        unique_scans = cur.fetchone()[0]

        conn.close()

        self.result_label.config(
            text=f"From {start_date} to {end_date}\n"
                f"Total Scans: {total_scans}\n"
                f"Unique Scans: {unique_scans}"
        )

    # Function to clear the label
    def clear_result(self):
        self.result_label.config(text="")  

    def scan_data(self):
         # Ensure focus on the entry field
            #self.scan_entry.focus_set()
            # Get the scanned QR data and process it
            scan_qr = self.scan_entry.get().upper()

            if ":" in scan_qr:
                if scan_qr:
                    try:
                        # Parse the scanned QR data
                        self.urn, self.name, self.designation, self.company, self.country, self.city, self.receiptno, self.email, self.contact = scan_qr.split(":")              
                        # Store in the entry_datas table
                        self.entry_data()                            
                        self.excel() 
                        # self.save_and_generate() 
                            # Append scanned data to CSV file
                        # self.download_excel() 
                        
                        # Clear the entry field after processing
                        self.scan_entry.delete(0, tk.END)

                    except ValueError:
                        messagebox.showerror("Error", "Invalid entry data format.")
                else:
                    messagebox.showerror("Error", "Please enter entry data.")
            elif ":" in scan_qr:
                if scan_qr:
                    try:
                        # Parse the scanned QR data
                        self.urn, self.name, self.designation, self.company, self.country, self.city, self.receiptno, self.email, self.contact = scan_qr.split(":")              
                        # Store in the entry_datas table
                        self.entry_data()                            
                        self.excel()  
                        # self.save_and_generate()
                            # Append scanned data to CSV file
                        # self.download_excel() 
                        
                        # Clear the entry field after processing
                        self.scan_entry.delete(0, tk.END)

                    except ValueError:
                        messagebox.showerror("Error", "Invalid entry data format2.")
                else:
                    messagebox.showerror("Error", "Please enter entry data.")
            else:
             pass

    def create_spot_table(self):
        conn = sqlite3.connect('database.db') 
        cur = conn.cursor()  
        try:                
            query1 = """
                CREATE TABLE IF NOT EXISTS spot_table(
                    urn TEXT ,
                    name VARCHAR(255),
                    designation VARCHAR(255),
                    company VARCHAR(255),
                    contact BIGINT(12),
                    email VARCHAR(255),
                    date DATE,
                    time TIME
                )
            """
            cur.execute(query1)
            conn.commit()       
        except Exception as e:
           print("Error in table creation:", str(e))
        finally:
            conn.close()
        
    def store_spot_registration(self, event=None):
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')

        # ---- Field Validations ----
        self.spotname = self.spot_entry.get().upper()
        self.spotdesignation = self.designation_entry.get().upper()
        self.spotcompany = self.company_entry.get().upper()
        self.spotcontact = self.contact_entry.get().strip()
        self.spotemail = self.email_entry.get().upper()

        if not self.spotname or len(self.spotname) <= 2:
            messagebox.showerror("Error", "Name must be at least 3 characters long.")
            return
        if not self.spotdesignation:
            messagebox.showerror("Error", "Designation is required.")
            return
        if not self.spotcompany:
            messagebox.showerror("Error", "Company is required.")
            return
        if not self.spotcontact:
            messagebox.showerror("Error", "Contact number is required")
            return
        if not re.match(r'^[6-9]\d{9}$', self.spotcontact):
            messagebox.showerror("Error", "Contact number must be a valid 10-digit number!")
            return

        email_pattern = r'^\s*$|^\s*[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\s*$'
        if not re.match(email_pattern, self.spotemail):
            messagebox.showerror("Error", "Invalid email address!")
            return

        input_value = self.counter_value.get().upper() if self.counter_value.get() else ""
        if not input_value:
            messagebox.showerror("Error", "Please enter the counter number")
            return

        chosen_prefix = self.category_var.get()
        if chosen_prefix not in ['D', 'EX', 'M', 'OG', 'VB', 'SPK', 'V', 'SP', 'VIP', 'WS']:
            messagebox.showerror("Error", "Please choose a valid category.")
            return

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()
        try:
            # ---- Badge Settings Check ----
            cur.execute("SELECT COUNT(*) FROM badge_template_settings")
            badge_setting_exists = cur.fetchone()[0]
            if badge_setting_exists == 0:
                self.generate_badge_pdf()

            # ---- URN generation ----
            cur.execute("SELECT urn FROM spot_table WHERE urn LIKE ? ORDER BY urn DESC LIMIT 1",
                        (f'{input_value}{chosen_prefix}%',))
            result = cur.fetchone()
            if result is None:
                next_count = 1
            else:
                last_urn = result[0]
                last_count = int(last_urn[-3:])
                next_count = last_count + 1
            urn = f'{input_value}{chosen_prefix}{next_count:03d}'

            # ---- Insert into DB ----
            cur.execute("""INSERT INTO spot_table
                (urn, name, designation, company, contact, email, date, time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (urn, self.spotname, self.spotdesignation, self.spotcompany,
                self.spotcontact, self.spotemail, current_date, current_time))
            conn.commit()

            # ---- QR Generation ----
            self.qr = f"{urn}:{self.spotname}:{self.spotdesignation}:{self.spotcompany}:{self.country}:{self.city}:{self.receiptno}:{self.spotemail}:{self.spotcontact}"
            self.img = qrcode.make(self.qr)

            folder_path = "Qr"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path, exist_ok=True)
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

            self.newqr_path = os.path.join(folder_path, f"{self.spotcontact}.png")
            self.img.save(self.newqr_path)

            # ---- Set instance vars ----
            self.clear_fields()
            self.urn = urn
            self.name = self.spotname
            self.designation = self.spotdesignation
            self.company = self.spotcompany
            self.contact = self.spotcontact
            self.email = self.spotemail

            # ---- Excel + Badge ----
            self.excel()
            self.save_and_generate()   # this calls save_badge_settings + generate_badge_pdf()

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            cur.close()
            conn.close()

    def clear_fields(self):
        # Clear entry fields after submission
        self.spot_entry.delete(0, tk.END)
        self.designation_entry.delete(0, tk.END)
        self.company_entry.delete(0, tk.END)
        self.contact_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)

  # --- Load Bulk Upload Page ---
    def load_data_page(self):
    # self._clear_frames()
        self.bulk_page = tk.Frame(self.root)
        self.bulk_page.pack(fill="both", expand=True)

        tk.Label(self.bulk_page, text="Bulk Upload", font=("Arial", 16)).pack(pady=20)

        btns = tk.Frame(self.bulk_page)
        btns.pack(pady=10)

        tk.Button(btns, text="Select All", command=self.toggle_all_bulk).pack(side="left", padx=5)
        tk.Button(btns, text="Print", command=self.start_bulk_print).pack(side="left", padx=40)  # big gap before Import

        # Keep Import File as is
        tk.Button(btns, text="Import File", command=self.import_csv).pack(side="left", padx=5)

        tk.Button(btns, text="CSV Sample", command=self.download_csv_sample).pack(side="left", padx=5)

        #  Counter label (new)
        self.print_status_label = tk.Label(self.bulk_page, text="Printing: 0/0", font=("Arial", 12))
        self.print_status_label.pack(pady=5)

        # Table area
        table_area = tk.Frame(self.bulk_page)
        table_area.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("id", "urn", "name", "designation", "company", "city", "country", "receiptno", "email", "contact")
        self.bulk_tree = CheckboxTreeview(table_area, columns=cols, show="tree headings")
        self.bulk_tree.pack(side="left", fill="both", expand=True)

        self.bulk_tree.heading("#0", text="Select")
        self.bulk_tree.column("#0", width=60)

        for col in cols:
            self.bulk_tree.heading(col, text=col.upper())
            self.bulk_tree.column(col, width=120)

        yscroll = ttk.Scrollbar(table_area, orient="vertical", command=self.bulk_tree.yview)
        self.bulk_tree.configure(yscrollcommand=yscroll.set)
        yscroll.pack(side="right", fill="y")

        # flag for select/unselect toggle
        self.bulk_all_selected = False

        # Show existing DB data
        self.show_bulk_data()
    
    def download_csv_sample(self):
        # Define headers
        headers = ["urn", "name", "designation", "company", "city", "country", "receiptno", "email", "contact"]

        # Get the user's Downloads folder path
        downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        # Create the full path for the sample file
        sample_filename = os.path.join(downloads_folder, "Bulk_Upload_Sample.csv")

        # Write CSV file
        with open(sample_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            # Optionally add a sample data row
            # writer.writerow(["URN001", "John Doe", "Manager", "TechCorp", "New York", "USA", "12345", "john@example.com", "9876543210"])
        try:
            os.startfile(sample_filename)  # Open the file in the default CSV viewer
        except Exception:
            messagebox.showinfo("Sample Created", f"Sample file saved as:\n{sample_filename}")

    # --- Import CSV Function ---
    def import_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                # expected column headers
                expected_cols = {"urn", "name", "designation", "company", "city", "country", "receiptno", "email", "contact"}
                
                # Check if headers match
                if not expected_cols.issubset(set(reader.fieldnames)):
                    messagebox.showerror("Incorrect Format", "CSV format is incorrect. Please check the column headers.")
                    return

                rows = [
                (
                    r["urn"], r["name"], r["designation"], r["company"], r["city"],
                    r["country"], r["receiptno"], r["email"], r["contact"]
                )
                for r in reader
            ]

            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute("DROP TABLE IF EXISTS bulk_data")

            # Create table if not exists with ID
            cur.execute("""
                CREATE TABLE IF NOT EXISTS bulk_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    urn TEXT,
                    name TEXT,
                    designation TEXT,
                    company TEXT,
                    city TEXT,
                    country TEXT,
                    receiptno TEXT,
                    email TEXT,
                    contact TEXT
                )
            """)
            cur.executemany("""
                    INSERT INTO bulk_data (urn, name, designation, company, city, country, receiptno, email, contact)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, rows)
            conn.commit()
            conn.close()
            # Refresh table
            self.show_bulk_data()

            
            # Success message
            messagebox.showinfo("Success", "Imported successfully!")

        except Exception as e:
            messagebox.showerror("Incorrect Format")

    # --- Show Data From DB into Treeview ---
    def show_bulk_data(self):
        for item in self.bulk_tree.get_children():
            self.bulk_tree.delete(item)

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM bulk_data")
        rows = cur.fetchall()
        conn.close()

        for row in rows:
            self.bulk_tree.insert("", "end", values=row)

    # --- Toggle Select/Unselect All ---
    def toggle_all_bulk(self):
        if not self.bulk_all_selected:
            self.bulk_tree.check_all()
            self.bulk_all_selected = True
        else:
            self.bulk_tree.uncheck_all()
            self.bulk_all_selected = False

    def print_bulk_selected(self, selected):
        # Step 2: Put in queue
        queue = deque(selected)
        # Step 3: Process one by one
        while queue:
            record = queue.popleft()
            # record includes (id, urn, name, designation, company, city, country, receiptno, email, contact)
            (_, urn, name, designation, company, city, country, receiptno, email, contact) = record
            # Assign to the same instance vars used by generate_badge_pdf()
            self.urn = urn
            self.name = name
            self.designation = designation
            self.company = company
            self.city = city
            self.country = country
            self.receiptno = receiptno
            self.email = email
            self.contact = contact

            print(f"Printing badge: {self.name}, {self.company}")
            self.gen()
            self.generate_badge_pdf()
            # self.upload_to_api()

            # Update counter
            self.printed_count += 1
            self.print_status_label.config(text=f"Printing: {self.printed_count}/{self.total_pages}")
            self.root.update_idletasks()

            time.sleep(8)  # wait before next print

        # Completed update
        self.print_status_label.config(text=f"Completed: {self.total_pages}/{self.total_pages}")
        print("\nDequeue complete.")

   # --- Start Bulk Print ---
    def start_bulk_print(self):
        selected = [self.bulk_tree.item(item, "values") for item in self.bulk_tree.get_checked()]
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one row.")
            return
        # Initialize counters
        self.total_pages = len(selected)
        self.printed_count = 0
        self.print_status_label.config(text=f"Printing: {self.printed_count}/{self.total_pages}")

        # Run in thread to avoid UI freeze  
        thread = threading.Thread(target=lambda: self.print_bulk_selected(selected), daemon=True)
        thread.start()

    def gen(self):
        # QR Code Generation
        self.stre = f"{self.urn}:{self.name}:{self.designation}:{self.company}:{self.country}:{self.city}:{self.receiptno}:{self.email}:{self.contact}"
        self.img = qrcode.make(self.stre)
        # Define the folder path for Spot QR code storage
        folder_path = "Qr"
        # Check if the folder exists, if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)

        # Remove all existing QR codes in the folder before saving the new one
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete the existing file

        # Save the Spot QR code image inside the "Qr" folder with filename as contact number
        self.newqr_path = os.path.join(folder_path, f"{self.contact}.png")
        self.img.save(self.newqr_path)
        return self.newqr_path
    
    def badge_dashboard(self):
        self.setting_frame.pack()  
        self.admin_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.entry_frame.pack_forget()
        self.database_frame.pack_forget()
        self.frame_top.pack_forget()
        self.frame_down.pack_forget()
        self.myLabel.pack_forget()
        self.label_count.pack_forget()
        #  Destroy previous badge frame if it exists
        if self.badge_frame:
            self.badge_frame.destroy()
        #  Create new badge frame and assign to self.badge_frame
        self.badge_frame = tk.Frame(self.setting_frame, padx=15, pady=15, bd=2, relief="groove")
        self.badge_frame.pack(pady=20)
        # Required Fields Title
        tk.Label(self.badge_frame, text="Select Required Fields:", font=("Arial", 12, "bold")).grid(row=0, columnspan=6, pady=5)
        self.urn_var = tk.IntVar()
        self.name_var = tk.IntVar()
        self.desg_var = tk.IntVar()
        self.comp_var = tk.IntVar()
        self.qr_var = tk.IntVar()

        self.urn_check = tk.Checkbutton(self.badge_frame, text="URN", variable=self.urn_var)
        self.name_check = tk.Checkbutton(self.badge_frame, text="Name", variable=self.name_var)
        self.desg_check = tk.Checkbutton(self.badge_frame, text="Designation", variable=self.desg_var)
        self.comp_check = tk.Checkbutton(self.badge_frame, text="Company", variable=self.comp_var)
        self.qr_check = tk.Checkbutton(self.badge_frame, text="Qrcode", variable=self.qr_var)

        self.urn_check.grid(row=1, column=0)
        self.name_check.grid(row=1, column=1)
        self.desg_check.grid(row=1, column=2)
        self.comp_check.grid(row=1, column=3)
        self.qr_check.grid(row=1, column=4)

        fields = [
            ("BADGE WIDTH MM:", "BADGE HEIGHT MM:"),
            ("NAME LEFT/RIGHT:", "NAME TOP/BOTTOM:"),
            ("DESIGNATION LEFT/RIGHT:", "DESIGNATION TOP/BOTTOM:"),
            ("COMPANY LEFT/RIGHT:", "COMPANY TOP/BOTTOM:"),
            ("URN LEFT/RIGHT:", "URN TOP/BOTTOM:"),
            ("QRCODE LEFT/RIGHT:", "QRCODE TOP/BOTTOM:")
        ]
        font_options = ["Helvetica", "Helvetica-Bold", "Courier", "Times-Roman"]
        self.entries = []

        for i, (left_label, right_label) in enumerate(fields):
            tk.Label(self.badge_frame, text=left_label).grid(row=i+2, column=0, pady=5, sticky="e")
            e1 = tk.Entry(self.badge_frame, width=10)
            e1.grid(row=i+2, column=1)

            tk.Label(self.badge_frame, text=right_label).grid(row=i+2, column=2, sticky="e")
            e2 = tk.Entry(self.badge_frame, width=10)
            e2.grid(row=i+2, column=3)

            if i != 0:
                tk.Label(self.badge_frame, text="FONT STYLE:").grid(row=i+2, column=4, sticky="e")
                font_style = ttk.Combobox(self.badge_frame, values=font_options, width=12)
                font_style.set("Helvetica")
                font_style.grid(row=i+2, column=5)

                tk.Label(self.badge_frame, text="FONT SIZE:").grid(row=i+2, column=6, sticky="e")
                font_size = tk.Entry(self.badge_frame, width=5)
                font_size.grid(row=i+2, column=7)
            else:
                font_style = None
                font_size = None

            self.entries.append((e1, e2, font_style, font_size))

        test_btn = tk.Button(self.badge_frame, text="Test Print Badge", font=("Arial", 12, "bold"), bg="orange", command=self.test_print_badge)
        test_btn.grid(row=i+6, columnspan=8, pady=10)

        self.load_badge_settings()

    def save_and_generate(self):
         # Step 1: Save current settings to DB
         self.save_badge_settings()

    # Step 2: Generate PDF with saved settings
         self.generate_badge_pdf()

    def test_print_badge(self):
        # Set test data
        self.urn = "TEST001"
        self.name = "CHINNASWAMI MUTHUSWAMI IYER"
        self.designation = "DEVELOPER"
        self.company = "INTERFACE DATA AND DESIGN LLP"
        self.country = "INDIA"
        self.city = "MUMBAI"
        self.receiptno = "08"
        self.email = "trupti@iddllp.com"
        self.contact = "7208568928"

        # Call generate PDF
        self.save_and_generate()

    def create_badge_settings_table(self):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS badge_template_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                badge_width REAL,
                badge_height REAL,
                
                name_left REAL,
                name_top REAL,
                name_font TEXT,
                name_size INTEGER,
                
                desg_left REAL,
                desg_top REAL,
                desg_font TEXT,
                desg_size INTEGER,
                
                comp_left REAL,
                comp_top REAL,
                comp_font TEXT,
                comp_size INTEGER,
                
                urn_left REAL,
                urn_top REAL,
                urn_font TEXT,
                urn_size INTEGER,
                
                qr_left REAL,
                qr_top REAL,
                qr_size INTEGER,
                
                show_urn INTEGER,
                show_name INTEGER,
                show_desg INTEGER,
                show_comp INTEGER,
                show_qr INTEGER
            )
        """)
        conn.commit()
        conn.close()

    def generate_badge_pdf(self):
        # Load last saved badge settings directly from DB
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM badge_template_settings ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Admin Setup Required", "No badge settings found. Please set badge in Admin Panel first.")
            return
        (
            _id,
            badge_width, badge_height,
            name_left, name_top, name_font, name_size,
            desg_left, desg_top, desg_font, desg_size,
            comp_left, comp_top, comp_font, comp_size,
            urn_left, urn_top, urn_font, urn_size,
            qr_left, qr_top, qr_size,
            show_urn, show_name, show_desg, show_comp, show_qr
        ) = row

        # 2. Validate: At least one field selected
        if not any([show_urn, show_name, show_desg, show_comp, show_qr]):
            messagebox.showerror("Validation Error", "Please enable at least one field (Name, URN, etc.) in Badge Settings.")
            return

        # 3. Badge dimensions
        paper_width = float(badge_width) * mm
        paper_height = float(badge_height) * mm
        qr_size = float(qr_size) * mm

        fonts = {
            "name": (name_font, float(name_size)),
            "designation": (desg_font, float(desg_size)),
            "company": (comp_font, float(comp_size)),
            "urn": (urn_font, float(urn_size))
        }
        positions = {
            "name": (float(name_left) * mm, paper_height - float(name_top) * mm),
            "designation": (float(desg_left) * mm, paper_height - float(desg_top) * mm),
            "company": (float(comp_left) * mm, paper_height - float(comp_top) * mm),
            "urn": (float(urn_left) * mm, paper_height - float(urn_top) * mm),
        }

        # 4. Collect data for badge
        qrdata = f"{self.urn}:{self.name}:{self.designation}:{self.company}:{self.country}:{self.city}:{self.receiptno}:{self.email}:{self.contact}"
        data_list = [(self.name, self.designation, self.company, qrdata, self.urn)]

        # 5. Create PDF
        pdf_filename = "Badge.pdf"
        # pdf_filename = f"{self.contact}.pdf"
        c = canvas.Canvas(pdf_filename, pagesize=(paper_width, paper_height))

        for i, (name, desg, company, qr, urn) in enumerate(data_list):
            qr_img = qrcode.make(qr)
            qr_temp_path = f"qr_temp_{i}.png"
            qr_img.save(qr_temp_path)

            def draw_movable_wrapped_text(canvas, text, font, font_size, max_width, x_offset, y):
                if not text:
                    return
                canvas.setFont(font, font_size)
                wrapped_lines = textwrap.wrap(text, width=max_width)
                total_text_height = len(wrapped_lines) * (font_size + 2)
                y_start = y + (total_text_height / 2)
                for line in wrapped_lines:
                    text_width = canvas.stringWidth(line, font, font_size)
                    x_position = ((paper_width - text_width) / 2) + x_offset
                    canvas.drawString(x_position, y_start, line)
                    y_start -= font_size + 2

            # DB checkbox values
            if show_name:
                draw_movable_wrapped_text(c, name, *fonts["name"], 19, *positions["name"])
            if show_desg:
                draw_movable_wrapped_text(c, desg, *fonts["designation"], 21, *positions["designation"])
            if show_comp:
                draw_movable_wrapped_text(c, company, *fonts["company"], 19, *positions["company"])
            if show_urn:
                draw_movable_wrapped_text(c, urn, *fonts["urn"], 25, *positions["urn"])
            if show_qr:
                qr_x = float(qr_left) * mm
                qr_y = float(qr_top) * mm
                c.drawImage(qr_temp_path, qr_x, qr_y, qr_size, qr_size)

        c.showPage()
        c.save()
        if os.name == 'nt':
             os.startfile("Badge.pdf", "print")

    def save_badge_settings(self):
        # Auto-load saved settings if missing
        if not self.entries or len(self.entries) < 6:
            conn = sqlite3.connect("database.db")
            row = conn.cursor().execute("SELECT * FROM badge_template_settings LIMIT 1").fetchone()
            conn.close()
            if row:
                self.entries = [[tk.StringVar(value=str(v)) for v in row[0:2]],   # width, height
                                [tk.StringVar(value=str(v)) for v in row[2:6]],
                                [tk.StringVar(value=str(v)) for v in row[6:10]],
                                [tk.StringVar(value=str(v)) for v in row[10:14]],
                                [tk.StringVar(value=str(v)) for v in row[14:18]],
                                [tk.StringVar(value=str(row[18])), tk.StringVar(value=str(row[19])), tk.StringVar(), tk.StringVar(value=str(row[20]))]]
                self.urn_var.set(row[21])
                self.name_var.set(row[22])
                self.desg_var.set(row[23])
                self.comp_var.set(row[24])
                self.qr_var.set(row[25])
            else:
              pass

        try:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()

            # Clear previous settings
            cur.execute("DELETE FROM badge_template_settings")

            # Insert new settings safely
            cur.execute("""
                INSERT INTO badge_template_settings (
                    badge_width, badge_height,
                    name_left, name_top, name_font, name_size,
                    desg_left, desg_top, desg_font, desg_size,
                    comp_left, comp_top, comp_font, comp_size,
                    urn_left, urn_top, urn_font, urn_size,
                    qr_left, qr_top, qr_size,
                    show_urn, show_name, show_desg, show_comp, show_qr
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                self.entries[0][0].get(), self.entries[0][1].get(),
                self.entries[1][0].get(), self.entries[1][1].get(), self.entries[1][2].get(), self.entries[1][3].get(),
                self.entries[2][0].get(), self.entries[2][1].get(), self.entries[2][2].get(), self.entries[2][3].get(),
                self.entries[3][0].get(), self.entries[3][1].get(), self.entries[3][2].get(), self.entries[3][3].get(),
                self.entries[4][0].get(), self.entries[4][1].get(), self.entries[4][2].get(), self.entries[4][3].get(),
                self.entries[5][0].get(), self.entries[5][1].get(), self.entries[5][3].get(),
                self.urn_var.get(), self.name_var.get(), self.desg_var.get(), self.comp_var.get(), self.qr_var.get()
            ))
            conn.commit()
            conn.close()
            # messagebox.showinfo("Saved", "Badge settings saved successfully.")
        except Exception as e:
            # messagebox.showerror("Error", f"Failed to save badge settings.\nDetails: {e}")
            pass

    def load_badge_settings(self):
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM badge_template_settings ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        conn.close()

        if row:
            (
                _id, badge_width, badge_height,
                name_left, name_top, name_font, name_size,
                desg_left, desg_top, desg_font, desg_size,
                comp_left, comp_top, comp_font, comp_size,
                urn_left, urn_top, urn_font, urn_size,
                qr_left, qr_top, qr_size,
                show_urn, show_name, show_desg, show_comp, show_qr
            ) = row

            # Checkbox values (these are used during PDF generation)
            self.urn_var.set(show_urn)
            self.name_var.set(show_name)
            self.desg_var.set(show_desg)
            self.comp_var.set(show_comp)
            self.qr_var.set(show_qr)
            # Optional: you can store the settings in instance variables even if UI isn't visible
            self.saved_settings = {
                "badge_width": badge_width,
                "badge_height": badge_height,
                "name_font": name_font,
                "name_size": name_size,
                "desg_font": desg_font,
                "desg_size": desg_size,
                "comp_font": comp_font,
                "comp_size": comp_size,
                "urn_font": urn_font,
                "urn_size": urn_size,
                "qr_size": qr_size,
                "name_left": name_left,
                "name_top": name_top,
                "desg_left": desg_left,
                "desg_top": desg_top,
                "comp_left": comp_left,
                "comp_top": comp_top,
                "urn_left": urn_left,
                "urn_top": urn_top,
                "qr_left": qr_left,
                "qr_top": qr_top,
            }
            if self.entries:
                self.entries[0][0].insert(0, badge_width)
                self.entries[0][1].insert(0, badge_height)

                self.entries[1][0].insert(0, name_left)
                self.entries[1][1].insert(0, name_top)
                self.entries[1][2].set(name_font)
                self.entries[1][3].insert(0, name_size)

                self.entries[2][0].insert(0, desg_left)
                self.entries[2][1].insert(0, desg_top)
                self.entries[2][2].set(desg_font)
                self.entries[2][3].insert(0, desg_size)

                self.entries[3][0].insert(0, comp_left)
                self.entries[3][1].insert(0, comp_top)
                self.entries[3][2].set(comp_font)
                self.entries[3][3].insert(0, comp_size)

                self.entries[4][0].insert(0, urn_left)
                self.entries[4][1].insert(0, urn_top)
                self.entries[4][2].set(urn_font)
                self.entries[4][3].insert(0, urn_size)

                self.entries[5][0].insert(0, qr_left)
                self.entries[5][1].insert(0, qr_top)
                self.entries[5][3].insert(0, qr_size)

    def truncate_table(self):
        popup = tk.Toplevel(self.root)
        popup.title("Truncate Table")
        popup.geometry("450x300")
        popup.resizable(False, False)

        tk.Label(popup, text="Select a table to truncate", font=("Arial", 12, "bold")).pack(pady=(15, 5))

        # Use BooleanVars for checkboxes instead of StringVar for radio
        table_vars = {
            "scan_datas": tk.BooleanVar(),
            "spot_table": tk.BooleanVar(),
            "bulk_data": tk.BooleanVar(),
            "entry_datas": tk.BooleanVar()
        }

        # Replace radio buttons with checkboxes
        for name, var in table_vars.items():
            tk.Checkbutton(popup, text=name, variable=var, font=("Arial", 10)).pack(anchor='w', padx=30)

        btn_frame = tk.Frame(popup)
        btn_frame.pack(pady=20)

        def do_truncate():
            selected = [name for name, var in table_vars.items() if var.get()]
            if not selected:
                messagebox.showwarning("No Selection", "Please select at least one table.")
                return
            if messagebox.askyesno("Confirm", f"Are you sure you want to truncate: {', '.join(selected)}?"):
                try:
                    with sqlite3.connect("database.db") as conn:
                        for name in selected:
                            conn.execute(f"DELETE FROM {name}")
                        conn.commit()
                    messagebox.showinfo("Success", f"Tables truncated: {', '.join(selected)}")
                    popup.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        tk.Button(btn_frame, text="Truncate", width=12, command=do_truncate).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="Cancel", width=12, command=popup.destroy).grid(row=0, column=1, padx=10)

    def excel(self):  
        current_date = datetime.now().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')
        # Exporting to CSV
        self.tab = [self.name, self.company, self.designation, self.email, self.contact, current_date, current_time]
        self.exce = np.asarray(self.tab)
        with open('Report.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(self.exce)

    def scanprint_excel(self, start_date, end_date):
        conn = sqlite3.connect('database.db')
        try:
            query = "SELECT * FROM scan_datas WHERE date BETWEEN ? AND ?"
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            df.to_excel('scanprint_report.xlsx', index=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.commit()
            conn.close()
        if os.name == 'nt':
            os.startfile('scanprint_report.xlsx')

    def spotdata_excel(self, start_date, end_date):
        conn = sqlite3.connect('database.db')
        try:
            query = "SELECT * FROM spot_table WHERE date BETWEEN ? AND ?"
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            df.to_excel('spot_report.xlsx', index=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.commit()
            conn.close()
        if os.name == 'nt':
            os.startfile('spot_report.xlsx')

    def entrydata_excel(self, start_date, end_date):
        conn = sqlite3.connect('database.db')
        try:
            query = "SELECT * FROM entry_datas WHERE date BETWEEN ? AND ?"
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
            df.to_excel('entry_report.xlsx', index=False)
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            conn.commit()
            conn.close()
        if os.name == 'nt':
            os.startfile('entry_report.xlsx')

    # API
    def upload_to_api(self):
        def internet_connection():
            try:
                requests.get("https://www.google.com", timeout=5)
                return True
            except requests.RequestException as e:
                print(f"Internet connection failed: {e}")
                return False

        if internet_connection():
            try:
                connection_obj = sqlite3.connect('database.db')
                cursor_obj = connection_obj.cursor()

                # Only fetch required columns
                statement = '''SELECT urn, name, designation, company, country, city, receiptno, email, contact, date, time FROM scan_datas WHERE receiptno = "0"'''
                cursor_obj.execute(statement)

                print("Selected Data:")
                for row in cursor_obj.fetchall():
                    urn, name, designation, company, country, city, receiptno, email, contact, date, time = row
                    #print(f"Name: {name}, Designation: {designation}, Company: {company}, Contact: {contact}")
                    api_key = "lkjhgfdsaasdfghjkl"

                    api_url = "https://pythonoffline.iddllp.com/offlineonline/pyapi.php"
                    headers = {
                    "Authorization": api_key,
                    "Content-Type": "application/json"
                    }

                    data_payload = [
                    {
                        "urn": urn,
                        "name": name,
                        "designation": designation,
                        "company": company,
                        "country": country,
                        "city": city,
                        "receiptno": receiptno,
                        "email": email,
                        "contact": contact,
                        "date": date,
                        "time": time
                    }

                    ]
                    try:
            
                        response = requests.post(api_url, json=data_payload, headers=headers)
                        if response.status_code == 200:
                            print("Data successfully posted to the API.")
                            print("Response:", response.json())
                            #update
                            # Variables
                            urn_value = urn          # ← change this to your target URN
                            new_receipt_number = 1        # ← change to whatever value you want

                            try:
                                # Connect to SQLite database
                                connection = sqlite3.connect("database.db")
                                cursor = connection.cursor()

                                # Update the receipt number for a specific URN
                                cursor.execute("""
                                    UPDATE scan_datas
                                    SET receiptno = ?
                                    WHERE urn = ?
                                """, (new_receipt_number, urn_value))

                                # Commit the changes
                                connection.commit()

                                if cursor.rowcount > 0:
                                    print(f"✅ Receipt number updated to {new_receipt_number} for URN: {urn_value}")
                                else:
                                    print(f"⚠️ No record found for URN: {urn_value}")

                            except sqlite3.Error as e:
                                print(f"SQLite error: {e}")

                            finally:
                                if connection:
                                    connection.close()
                            #end 
                        else:
                            print(f"Error posting data. Status code: {response.status_code}")

                            if response.status_code in (401, 403):
                                print("\n!!! Authentication or Authorization Error. Check your API Key and header name ('X-API-Key'). !!!")
                            print("Response Text:", response.text)

                    except requests.exceptions.RequestException as e:
                        print(f"An error occurred during the request: {e}")
            except sqlite3.Error as e:
                print(f"SQLite error: {e}")
            finally:
                #if connection_obj:
                connection_obj.close()
        else:
            print("The Internet is not connected.")


    def login(self):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if self.login_mode == "admin":
            if username == "admin" and password == "int@123":
                self.admin_frame.pack_forget()
                self.dashboard_page()
            else:
                messagebox.showerror("Login Failed", "Incorrect admin username or password.")
        
        elif self.login_mode == "badge_setting":
            if username == "admin" and password == "int@123":
                self.admin_frame.pack_forget()              
                self.badge_dashboard()
            else:
                messagebox.showerror("Login Failed", "Incorrect badge setting login credentials.")

        elif self.login_mode == "bulk_upload":
            if username == "admin" and password == "int@123":
                self.admin_frame.pack_forget()              
                self.load_data_page()
            else:
                messagebox.showerror("Login Failed", "Incorrect login credentials.")

        elif self.login_mode == "truncate":   
            if username == "admin" and password == "int@123":
                self.admin_frame.pack_forget()
                self.truncate_table()   
            else:
                messagebox.showerror("Login Failed", "Incorrect truncate login credentials.")

        self.user_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
 
    # --- Admin Login Function (header)---
    def admin_login(self):
        self.login_mode = "admin"
        self.admin_heading.config(text="Admin Login")
        self.show_login_frame()

    # --- Database Login Function(header) ---
    def badge_login(self):
        self.login_mode = "badge_setting"
        self.admin_heading.config(text="Badge Setting Login")
        self.show_login_frame()

    # --- Bulk Login Function(header) ---
    def bulk_login(self):
        self.login_mode = "bulk_upload"
        self.admin_heading.config(text="Bulk Login")
        self.show_login_frame()
    # --- Truncate Login Function (header) ---
    def truncate_login(self):
        self.login_mode = "truncate"
        self.admin_heading.config(text="Truncate Table Login")
        self.show_login_frame()

    # --- Shared Login Frame Display Function ---
    def show_login_frame(self):
        self.admin_frame.pack(pady=45)
        self.frame_top.pack_forget()
        self.frame_down.pack_forget()
        self.myLabel.pack_forget()
        self.dashboard_frame.pack_forget()
        self.entry_frame.pack_forget()
        self.database_frame.pack_forget()
        self.label_count.pack_forget() 
        self.setting_frame.pack_forget()
        self.bulk_page.pack_forget()
        self.search_frame.pack_forget()
        self.result_label.pack_forget()

            # --- Dashboard Page ---
    def dashboard_page(self):
        self.dashboard_frame.pack()
        self.admin_frame.pack_forget()
        self.myLabel.pack_forget()
        self.entry_frame.pack_forget()
        self.label_count.pack_forget()
        self.setting_frame.pack_forget()
        self.bulk_page.pack_forget()
        self.search_frame.pack_forget()
        self.result_label.pack_forget()

    def setting_page(self):
        self.setting_frame.pack()
        self.admin_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.entry_frame.pack_forget()
        self.database_frame.pack_forget()
        self.frame_top.pack_forget()
        self.frame_down.pack_forget()
        self.myLabel.pack_forget()
        self.label_count.pack_forget()
        self.search_frame.pack_forget()
        self.result_label.pack_forget()

    def scandata_frame(self):     
        self.search_frame.pack(pady=5, anchor="w")   
        self.result_label.pack(anchor="w" , pady=15)
        self.entry_frame.pack(pady=100, padx=100)    
        self.label_count.pack(side="bottom", pady=0, padx=1, anchor="ne")
        self.myLabel.pack_forget()
        self.frame_top.pack_forget()
        self.frame_down.pack_forget()
        self.admin_frame.pack_forget()
        self.dashboard_frame.pack_forget()
        self.setting_frame.pack_forget()
        self.bulk_page.pack_forget()

    # --- Database Frame Show Function ---
    def show_database_frame(self):
        self.database_frame.pack()
        self.admin_frame.pack_forget()
        self.myLabel.pack_forget()
        self.entry_frame.pack_forget()
        self.label_count.pack_forget()
        self.setting_frame.pack_forget()
        self.bulk_page.pack_forget()
        self.search_frame.pack_forget()
        self.result_label.pack_forget()

    def show_bulk_frame(self):
        self.bulk_page.pack()
        self.database_frame.pack_forget()
        self.admin_frame.pack_forget()
        self.myLabel.pack_forget()
        self.entry_frame.pack_forget()
        self.label_count.pack_forget()
        self.setting_frame.pack_forget()
        self.search_frame.pack_forget()
        self.result_label.pack_forget()

    def main_page(self):       
        self.entry_frame.pack_forget()  
        self.admin_frame.pack_forget() 
        self.dashboard_frame.pack_forget()  
        self.label_count.pack_forget() 
        self.bulk_page.pack_forget()
        self.myLabel.pack(anchor="nw", pady=10)
        self.frame_top.pack(anchor="nw", pady=10)
        self.frame_down.pack(anchor="w")
        self.setting_frame.pack_forget()
        self.search_frame.pack_forget()
        self.result_label.pack_forget()                                                                                                                                                      
        
root = tk.Tk()
app = EventApp(root)
root.mainloop()
