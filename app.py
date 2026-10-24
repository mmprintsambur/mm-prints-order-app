from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

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
    creds_dict = dict(st.secrets["gcp_service_account"])
    if "private_key" in creds_dict:
        pk = str(creds_dict["private_key"])
        pk = pk.replace("\\n", "\n")
        creds_dict["private_key"] = pk

    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
    return gspread.authorize(creds)

def generate_order_id(sheet):
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"MMP{today_str}"
    
    try:
        records = sheet.col_values(1)
        today_orders = [rec for rec in records if rec and rec.startswith(prefix)]
        
        if today_orders:
            last_order = today_orders[-1]
            try:
                seq_num = int(last_order[-3:]) + 1
            except ValueError:
                seq_num = 1
        else:
            seq_num = 1
            
        return f"{prefix}{seq_num:03d}"
    except Exception:
        return f"{prefix}001"

def main():
    st.title("🖨️ MM Prints - New Order Booking")
    st.caption("Ambur | Staff Data Entry Portal")

    # Connect to Google Sheet
    try:
        gc = get_gsheet_client()
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        sheet = gc.open_by_key(spreadsheet_id).sheet1
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        st.stop()

    next_order_id = generate_order_id(sheet)
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Order Entry Form
    with st.form("order_form", clear_on_submit=True):
        st.subheader("Order Details")
        
        col1, col2 = st.columns(2)
        with col1:
            order_id = st.text_input("Order ID (Auto-generated)", value=next_order_id, disabled=True)
            order_date = st.text_input("Order Date", value=current_date, disabled=True)
            customer_name = st.text_input("Customer Name")
            phone = st.text_input("Phone / Contact")
            
            # 👉 Google Sheet-ல் உள்ள அதே Job Type Dropdown ஆப்ஷன்கள்
            job_type = st.selectbox(
                "Job Type",
                [
                    "Flex", "Invitation", "Board-13/19", "Board-12/18", 
                    "Sticker-13/19", "Sticker-12/18", "Vinyl Stickers", 
                    "Visiting cards", "Outsource", "Shop light board", 
                    "Wall posters", "Synthetic cards", "Others"
                ]
            )
            quantity_specs = st.text_input("Quantity & Specifications (e.g., 1, 10x10)")

        with col2:
            # 👉 Google Sheet-ல் உள்ள அதே Assigned Designer ஆப்ஷன்கள்
            assigned_designer = st.selectbox(
                "Assigned Designer",
                ["Sakkarabani", "Kumaran", "Sakthi", "Ram", "Surya"]
            )
            
            total_amount = st.number_input("Total Amount (₹)", min_value=0.0, step=10.0)
            advance_paid = st.number_input("Advance Paid (₹)", min_value=0.0, step=10.0)
            
            # Balance Due ஆட்டோமேட்டிக்காக கணக்கிடப்படுகிறது
            balance_due = max(0.0, total_amount - advance_paid)
            st.info(f"Balance Due (₹): {balance_due:.2f}")

            delivery_deadline = st.date_input("Delivery Deadline")

        # 👉 Google Sheet-ல் உள்ள அதே Order Status ஆப்ஷன்கள்
        order_status = st.selectbox(
            "Order Status",
            [
                "New Order", "Designing", "Customer Review", 
                "Design Modification", "Customer Approved", "Printing", 
                "Ready for Delivery", "Outsourced", "Delivered", "Others"
            ]
        )
        
        remarks = st.text_area("Follow-up Remarks / Production Notes")

        submitted = st.form_submit_button("🚀 Submit Order")

        if submitted:
            if not customer_name or not phone:
                st.warning("Please fill in Customer Name and Phone Number.")
            else:
                try:
                    # Google Sheet-ல் உள்ள 14 Columns வரிசைப்படி டேட்டாவை அனுப்புகிறோம்
                    new_row = [
                        next_order_id,          # A: Order ID
                        current_date,           # B: Order Date
                        customer_name,          # C: Customer Name
                        phone,                  # D: Phone / Contact
                        job_type,               # E: Job Type
                        quantity_specs,         # F: Quantity & Specifications
                        assigned_designer,      # G: Assigned Designer
                        total_amount,           # H: Total Amount
                        advance_paid,           # I: Advance Paid
                        balance_due,            # J: Balance Due
                        str(delivery_deadline), # K: Delivery Deadline
                        order_status,           # L: Order Status
                        remarks,                # M: Follow-up Remarks
                        ""                      # N: Whatsapp Click (Blank)
                    ]
                    sheet.append_row(new_row)
                    st.balloons()
                    st.success(f"Order '{next_order_id}' submitted successfully!")
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to save order: {err}")

if __name__ == "__main__":
    main()
