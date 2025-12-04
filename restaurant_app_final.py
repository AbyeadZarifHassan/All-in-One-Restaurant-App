import os
import streamlit as st
import pandas as pd
from datetime import datetime

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("https://images.wallpaperscraft.com/image/single/coffee_neon_text_193511_1920x1080.jpg");
background-size: cover;
background-position: center;
background-repeat: no-repeat;
background-attachment: scroll;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)
menu = {
    "Americano": 120.00,
    "Latte": 140.00,
    "Cappuccino": 160.00,
    "Espresso": 90.00,
    "Mocha": 180.00,
    "Iced Coffee": 140.00,
    "Cold Brew": 160.00,
    "Caramel Macchiato": 200.00,
    "Chai Latte": 160.00,
    "Hot Chocolate": 140.00,
    "Matcha Latte": 180.00,
    "Chai Tea": 120.00,
    "Cookies": 90.00,
    "Croissant": 120.00,
    "Muffin": 120.00,
    "Brownie": 100.00
}

class Item:
    def __init__(self, item, price, qty):
        self.item = item
        self.price = price
        self.qty = qty

class Order:
    def __init__(self, customer, date):
        self.customer = customer
        self.date = date
        self.items = []

    def item_addition(self, item):
        self.items.append(item)

    def calculator(self):
        total = 0
        for item in self.items:
            total += item.qty * item.price
        return total

    def calculate_vat(self):
        vat_rate = 0.09  # 9% VAT rate
        subtotal = self.calculator()
        vat_amount = subtotal * vat_rate
        return vat_amount

    def invoice_memory(self, amount_paid):
        invoice_dir = "invoices"
        if not os.path.exists(invoice_dir):
            os.makedirs(invoice_dir)

        formatted_date = self.date.replace("/", "_")  
        filename = f"{invoice_dir}/{self.customer}_{formatted_date}.txt"
    
        with open(filename, "w") as file:
            file.write(" Coffee Shop Invoice\n")
            file.write(f"Date: {self.date}\n")
            file.write(f"Invoice To: {self.customer}\n")
            file.write("---------------------------------------\n")
            file.write("Items\t\tQty\t\tTotal\n")
            file.write("---------------------------------------\n")
            for item in self.items:
                file.write(f"{item.item}\t\t\t\t{item.qty}\t\t\t\t{item.qty * item.price:.2f}\n")
            subtotal = self.calculator()
            vat_amount = self.calculate_vat()
            file.write("---------------------------------------\n")
            file.write(f"Sub Total\t\t\t{subtotal:.2f}\n")
            file.write(f"VAT (9%)\t\t\t{vat_amount:.2f}\n")
            file.write("---------------------------------------\n")
            file.write(f"Total Bill\t\t\t{subtotal + vat_amount:.2f}\n")
            file.write(f"Amount Paid\t\t\t{amount_paid:.2f}\n")
            file.write(f"Change\t\t\t{amount_paid - (subtotal + vat_amount):.2f}\n")
            file.write("---------------------------------------\n")


def main():
    st.title("RMEDU Coffee Shop")
    
    st.markdown("## Choose an operation:")
    option = st.radio("", ["Generate Invoice", "Show all Invoices", "Search Invoice"])

    if option == "Generate Invoice":
        st.subheader("Generate Invoice")
        customer = st.text_input("Please enter the name of the customer:", key="customer_name")
        # Automatically fetch the current date
        date = datetime.now().strftime("%d/%m/%Y")
        st.write(f"**Date:** {date}")
        order = Order(customer, date)

        n = st.number_input("Please enter the number of items:", min_value=1, step=1)

        selected_items = []  

        for i in range(int(n)):
            st.write(f"### Item {i + 1}")
            item_name = st.selectbox("Select Item:", list(menu.keys()), key=f"item_name_{i}")
            qty = st.number_input("Quantity:", min_value=1, step=1, key=f"item_qty_{i}")
            price = menu[item_name]

            item = Item(item_name, price, qty)
            order.item_addition(item)
            selected_items.append((item_name, qty))  

        st.subheader("Invoice Summary")
        st.write(f"**Customer Name:** {order.customer}")
        st.write("---------------------------------------")
        st.write("### Items")
        df = pd.DataFrame([(item.item, item.qty, item.qty * item.price) for item in order.items],
                          columns=["Item", "Qty", "Total"])
        st.dataframe(df, width=500, height=150)  
        st.write("---------------------------------------")

        total = order.calculator()
        vat_amount = order.calculate_vat()
        subtotal_with_vat = total + vat_amount

        st.write(f"**Sub Total:**\t\t\t{total:.2f}")
        st.write(f"**VAT (9%):**\t\t\t{vat_amount:.2f}")
        st.write(f"**Total with VAT:**\t\t{subtotal_with_vat:.2f}")
        st.write("---------------------------------------")

        amount_paid = st.number_input("Amount Paid:", min_value=0.01, step=0.01)
        change = amount_paid - subtotal_with_vat
        st.write(f"**Amount Paid:**\t\t\t{amount_paid:.2f}")
        st.write(f"**Change:**\t\t\t{change:.2f}")
        st.write("---------------------------------------")

        save_invoice = st.button("Save Invoice")
        if save_invoice:
            order.invoice_memory(amount_paid)
            st.success("Invoice saved successfully!")

    elif option == "Show all Invoices":
        st.subheader("All Invoices")
        invoice_dir = "invoices"
        for filename in os.listdir(invoice_dir):
            if filename.endswith(".txt"):
                with open(os.path.join(invoice_dir, filename), "r") as file:
                    st.code(file.read(), language="txt")

    elif option == "Search Invoice":
        st.subheader("Search Invoice")
        name = st.text_input("Enter the name of the customer:", key="search_customer_name")
        date = st.text_input("Enter the date (DD/MM/YYYY):", key="search_invoice_date")
        formatted_date = date.replace("/", "_")
        invoice_dir = "invoices"
        found = False
        for filename in os.listdir(invoice_dir):
            if filename.startswith(name) and formatted_date in filename:
                with open(os.path.join(invoice_dir, filename), "r") as file:
                    st.subheader("Invoice Details")
                    st.code(file.read(), language="txt")
                found = True
                break

        if not found:
            st.error(f"Sorry, the invoice for {name} on {date} does not exist.")


if __name__ == "__main__":
    main()
