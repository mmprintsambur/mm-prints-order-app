import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Page Configuration
st.set_page_config(
    page_title="MM Prints - Order Entry",
    page_icon="🖨️",
    layout="centered"
)

def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # st.secrets-லிருந்து JSON string-ஐ எடுத்து டிக்ஷனரியாக மாற்றுதல்
    raw_key = st.secrets["GOOGLE_JSON_KEY"]
    
    if isinstance(raw_key, str):
        creds_dict = json.loads(raw_key, strict=False)
    else:
        creds_dict = dict(raw_key)
    
    # Private key-ல் உள்ள \\n-களை உண்மையான newline (\n) ஆக மாற்றுதல்
    if "private_key" in creds_dict:
        pk = creds_dict["private_key"]
        pk = pk.replace("\\\\n", "\n").replace("\\n", "\n")
        creds_dict["private_key"] = pk
        
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def main():
    st.title("🖨️ MM Prints - New Order Booking")
    st.caption("Ambur | Staff Data Entry Portal")

    # Connect to Google Sheet
    try:
        gc = get_gsheet_client()
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        sheet = gc.open_by_key(spreadsheet_id).sheet1
        st.success("Connected to Google Sheets successfully!")
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        st.stop()

    # Order Entry Form
    with st.form("order_form", clear_on_submit=True):
        st.subheader("Order Details")
        
        col1, col2 = st.columns(2)
        with col1:
            order_id = st.text_input("Order ID", value="ORD-")
            customer_name = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
        with col2:
            item_type = st.selectbox(
                "Item Type",
                ["Flex Banner", "Visiting Card", "Sign Board", "Letterhead", "Sticker / Label", "Other"]
            )
            quantity = st.number_input("Quantity", min_value=1, value=1)
            total_amount = st.number_input("Total Amount (₹)", min_value=0.0, step=10.0)

        status = st.selectbox("Status", ["Received", "Designing", "Printing", "Ready for Delivery", "Delivered"])
        notes = st.text_area("Additional Notes / Remarks")

        submitted = st.form_submit_button("🚀 Submit Order")

        if submitted:
            if not customer_name or not phone:
                st.warning("Please fill in Customer Name and Phone Number.")
            else:
                try:
                    # Append new row to Google Sheet
                    new_row = [
                        order_id,
                        customer_name,
                        phone,
                        item_type,
                        quantity,
                        total_amount,
                        status,
                        notes
                    ]
                    sheet.append_row(new_row)
                    st.balloons()
                    st.success(f"Order '{order_id}' submitted successfully!")
                except Exception as err:
                    st.error(f"Failed to save order: {err}")

if __name__ == "__main__":
    main()
