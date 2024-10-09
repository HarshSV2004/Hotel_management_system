import tkinter as tk
from tkinter import messagebox
import mysql.connector

class GuestInfoWindow(tk.Toplevel):
    def __init__(self, parent, room_number, hotel_app):
        super().__init__(parent)
        self.title("Guest Information")
        self.geometry("300x200")

        self.hotel_app = hotel_app
        self.room_number = room_number

        self.name_label = tk.Label(self, text="Name:")
        self.name_label.grid(row=0, column=0, padx=10, pady=10)
        self.name_entry = tk.Entry(self)
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)

        self.address_label = tk.Label(self, text="Address:")
        self.address_label.grid(row=1, column=0, padx=10, pady=10)
        self.address_entry = tk.Entry(self)
        self.address_entry.grid(row=1, column=1, padx=10, pady=10)

        self.aadhar_label = tk.Label(self, text="Aadhar Number:")
        self.aadhar_label.grid(row=2, column=0, padx=10, pady=10)
        self.aadhar_entry = tk.Entry(self)
        self.aadhar_entry.grid(row=2, column=1, padx=10, pady=10)

        self.phone_label = tk.Label(self, text="Phone Number:")
        self.phone_label.grid(row=3, column=0, padx=10, pady=10)
        self.phone_entry = tk.Entry(self)
        self.phone_entry.grid(row=3, column=1, padx=10, pady=10)

        self.extra_label = tk.Label(self, text="Extra Number:")
        self.extra_label.grid(row=4, column=0, padx=10, pady=10)
        self.extra_entry = tk.Entry(self)
        self.extra_entry.grid(row=4, column=1, padx=10, pady=10)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit_guest_info)
        self.submit_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    def submit_guest_info(self):
        name = self.name_entry.get()
        address = self.address_entry.get()
        aadhar_number = self.aadhar_entry.get()
        phone_number = self.phone_entry.get()
        extra_number = self.extra_entry.get()

        if name and address and aadhar_number and phone_number:
            guest_info = {
                "name": name,
                "address": address,
                "aadhar_number": aadhar_number,
                "phone_number": phone_number,
                "extra_number": extra_number
            }
            self.hotel_app.accept_guest_internal(self.room_number, guest_info)
            self.destroy()
            room_type = self.hotel_app.rooms[self.room_number]["type"]
            if room_type == "AC":
                messagebox.showinfo("Payment", "Rs.1500 for AC room.")
            else:
                messagebox.showinfo("Payment", "Rs.1200 for Non-AC room")
            self.hotel_app.ask_payment_option(self.room_number)
        else:
            messagebox.showwarning("Missing Information", "Please fill in all fields.")

class PaymentWindow(tk.Toplevel):
    def __init__(self, parent, room_number, hotel_app):
        super().__init__(parent)
        self.title("Payment")
        self.geometry("300x150")

        self.hotel_app = hotel_app
        self.room_number = room_number

        self.payment_label = tk.Label(self, text="Select Mode of Payment:")
        self.payment_label.grid(row=0, column=0, padx=10, pady=10)

        self.payment_var = tk.StringVar(self)
        self.payment_var.set("Cash")
        self.payment_options = ["Cash", "Online"]
        self.payment_menu = tk.OptionMenu(self, self.payment_var, *self.payment_options)
        self.payment_menu.grid(row=0, column=1, padx=10, pady=10)

        self.proceed_button = tk.Button(self, text="Proceed", command=self.proceed_payment)
        self.proceed_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def proceed_payment(self):
        selected_payment = self.payment_var.get()
        if selected_payment == "Cash":
            messagebox.showinfo("Payment Accepted", "Payment completed in cash. Thank you!")
            self.hotel_app.complete_payment(self.room_number, "Cash")
            self.destroy()
        elif selected_payment == "Online":
            self.upi_window = UpiWindow(self, self.room_number, self.hotel_app)

class UpiWindow(tk.Toplevel):
    def __init__(self, parent, room_number, hotel_app):
        super().__init__(parent)
        self.title("Online Payment - UPI")
        self.geometry("300x200")

        self.hotel_app = hotel_app
        self.room_number = room_number

        self.upi_label = tk.Label(self, text="Enter UPI ID:")
        self.upi_label.grid(row=0, column=0, padx=10, pady=10)
        self.upi_entry = tk.Entry(self)
        self.upi_entry.grid(row=0, column=1, padx=10, pady=10)

        self.submit_button = tk.Button(self, text="Submit", command=self.submit_upi)
        self.submit_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    def submit_upi(self):
        upi_id = self.upi_entry.get()
        if upi_id:
            messagebox.showinfo("Payment Accepted", "Payment completed online. Thank you!")
            self.hotel_app.complete_payment(self.room_number, "Online")
            self.destroy()
        else:
            messagebox.showwarning("Missing Information", "Please enter your UPI ID.")

class HotelManagementApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Hotel Management System")
        self.master.geometry("600x400")

        # Connect to the database
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hotel_management",
            port=3306
        )
        self.cursor = self.conn.cursor()
        self.create_tables()  # Create tables if they do not exist

        # Create a canvas
        self.canvas = tk.Canvas(self.master)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        self.scrollbar = tk.Scrollbar(self.master, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Create a frame inside the canvas
        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.rooms = {}
        for i in range(101, 151):
            room_type = "AC" if i % 2 != 0 else "Non-AC"
            self.rooms[str(i)] = {"status": "available", "type": room_type, "guest_info": []}

        self.create_widgets()

    def create_tables(self):
        # Create guests table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS guests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                room_number VARCHAR(10) NOT NULL,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(255) NOT NULL,
                aadhar_number VARCHAR(20) NOT NULL,
                phone_number VARCHAR(15) NOT NULL,
                extra_number VARCHAR(15),
                payment_mode VARCHAR(20) NOT NULL
            )
        """)
        self.conn.commit()

    def create_widgets(self):
        self.room_label = tk.Label(self.frame, text="Room Number:")
        self.room_label.grid(row=0, column=0, padx=10, pady=10)

        self.room_entry = tk.Entry(self.frame)
        self.room_entry.grid(row=0, column=1, padx=10, pady=10)

        self.check_button = tk.Button(self.frame, text="Check Availability", command=self.check_availability)
        self.check_button.grid(row=0, column=2, padx=10, pady=10)

        self.result_label = tk.Label(self.frame, text="")
        self.result_label.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        self.accept_button = tk.Button(self.frame, text="Accept Guest", command=self.accept_guest)
        self.accept_button.grid(row=2, column=0, padx=10, pady=10)

        self.decline_button = tk.Button(self.frame, text="Decline Guest", command=self.decline_guest)
        self.decline_button.grid(row=2, column=1, padx=10, pady=10)

        self.checkout_button = tk.Button(self.frame, text="Checkout Guest", command=self.checkout_guest)
        self.checkout_button.grid(row=9, column=0, padx=10, pady=10)

        self.ac_rooms_label = tk.Label(self.frame, text="")
        self.ac_rooms_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        self.non_ac_rooms_label = tk.Label(self.frame, text="")
        self.non_ac_rooms_label.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.update_room_labels()

    def update_room_labels(self):
        ac_rooms = [room for room in self.rooms if self.rooms[room]["type"] == "AC"]
        non_ac_rooms = [room for room in self.rooms if self.rooms[room]["type"] == "Non-AC"]

        self.ac_rooms_label.config(text="Available AC Rooms: " + ", ".join([room for room in ac_rooms if self.rooms[room]["status"] == "available"]))
        self.non_ac_rooms_label.config(text="Available Non-AC Rooms: " + ", ".join([room for room in non_ac_rooms if self.rooms[room]["status"] == "available"]))

    def check_availability(self):
        room_number = self.room_entry.get()
        if room_number in self.rooms:
            status = self.rooms[room_number]["status"]
            if status == "available":
                self.result_label.config(text=f"Room {room_number} is available.")
            else:
                self.result_label.config(text=f"Room {room_number} is not available.")
        else:
            self.result_label.config(text="Invalid room number.")

    def accept_guest(self):
        room_number = self.room_entry.get()
        if room_number in self.rooms and self.rooms[room_number]["status"] == "available":
            self.guest_window = GuestInfoWindow(self.master, room_number, self)
            self.rooms[room_number]["status"] = "occupied"
            self.update_room_labels()
        else:
            messagebox.showwarning("Room Not Available", "Selected room is not available.")

    def accept_guest_internal(self, room_number, guest_info):
        self.cursor.execute("""
            INSERT INTO guests (room_number, name, address, aadhar_number, phone_number, extra_number, payment_mode)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (room_number, guest_info['name'], guest_info['address'], guest_info['aadhar_number'], guest_info['phone_number'], guest_info['extra_number'], "Pending"))
        self.conn.commit()
        messagebox.showinfo("Guest Accepted", "Guest information has been accepted.")

    def decline_guest(self):
        room_number = self.room_entry.get()
        if room_number in self.rooms:
            self.result_label.config(text=f"Room {room_number} declined.")
        else:
            messagebox.showwarning("Invalid Room", "Please select a valid room.")

    def checkout_guest(self):
        room_number = self.room_entry.get()
        if room_number in self.rooms and self.rooms[room_number]["status"] == "occupied":
            self.rooms[room_number]["status"] = "available"
            self.update_room_labels()
            messagebox.showinfo("Checkout", f"Room {room_number} checked out.")
        else:
            messagebox.showwarning("Invalid Checkout", "Room is not occupied.")

    def ask_payment_option(self, room_number):
        self.payment_window = PaymentWindow(self.master, room_number, self)

    def complete_payment(self, room_number, payment_mode):
        self.cursor.execute("""
            UPDATE guests
            SET payment_mode = %s
            WHERE room_number = %s AND payment_mode = 'Pending'
        """, (payment_mode, room_number))
        self.conn.commit()
        messagebox.showinfo("Payment", f"Payment completed via {payment_mode}. Thank you!")

if __name__ == "__main__":
    root = tk.Tk()
    hotel_app = HotelManagementApp(root)
    root.mainloop()
