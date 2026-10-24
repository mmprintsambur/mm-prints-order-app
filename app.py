from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="MM Prints - Order Portal",
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
    st.title("🖨️ MM Prints - Order Management")
    st.caption("Ambur | Staff Portal")

    # Connect to Google Sheet
    try:
        gc = get_gsheet_client()
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        sheet = gc.open_by_key(spreadsheet_id).sheet1
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        st.stop()

    # Initialize Session State for Navigation
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # ================= HOME PAGE (Buttons View) =================
    if st.session_state.page == "home":
        st.markdown("---")
        st.subheader("Please select an action:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ New Order Entry", use_container_width=True):
                st.session_state.page = "new_order"
                st.rerun()
        with col2:
            if st.button("🔄 Update Order Status", use_container_width=True):
                st.session_state.page = "update_order"
                st.rerun()

    # ================= NEW ORDER ENTRY PAGE =================
    elif st.session_state.page == "new_order":
        if st.button("⬅️ Back to Home"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown("---")
        next_order_id = generate_order_id(sheet)
        current_date = datetime.now().strftime("%Y-%m-%d")

        with st.form("order_form", clear_on_submit=True):
            st.subheader("➕ New Order Booking")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Order ID (Auto-generated)", value=next_order_id, disabled=True)
                st.text_input("Order Date", value=current_date, disabled=True)
                customer_name = st.text_input("Customer Name")
                phone = st.text_input("Phone / Contact")
                
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
                assigned_designer = st.selectbox(
                    "Assigned Designer",
                    ["Sakkarabani", "Kumaran", "Sakthi", "Ram", "Surya"]
                )
                
                total_amount = st.number_input("Total Amount (₹)", min_value=0.0, step=10.0)
                advance_paid = st.number_input("Advance Paid (₹)", min_value=0.0, step=10.0)
                
                balance_due = max(0.0, total_amount - advance_paid)
                st.info(f"Balance Due (₹): {balance_due:.2f}")

                delivery_deadline = st.date_input("Delivery Deadline")

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
                            ""                      # N: Whatsapp Click
                        ]
                        sheet.append_row(new_row)
                        st.balloons()
                        st.success(f"Order '{next_order_id}' submitted successfully!")
                    except Exception as err:
                        st.error(f"Failed to save order: {err}")

    # ================= UPDATE ORDER STATUS PAGE =================
    elif st.session_state.page == "update_order":
        if st.button("⬅️ Back to Home"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown("---")
        st.subheader("🔄 Update Existing Order Status")
        
        try:
            all_records = sheet.get_all_records()
        except Exception:
            all_records = []

        if not all_records:
            st.info("No orders found in Google Sheet yet.")
        else:
            order_ids = [str(row.get("Order ID")) for row in all_records if row.get("Order ID")]
            
            if not order_ids:
                st.warning("No Order IDs available.")
            else:
                selected_order_id = st.selectbox("Select Order ID to Update", options=order_ids)
                
                selected_row_data = None
                row_index = -1
                for idx, row in enumerate(all_records):
                    if str(row.get("Order ID")) == selected_order_id:
                        selected_row_data = row
                        row_index = idx + 2
                        break
                
                if selected_row_data:
                    st.write(f"**Customer Name:** {selected_row_data.get('Customer Name')}")
                    st.write(f"**Job Type:** {selected_row_data.get('Job Type')}")
                    
                    current_status = selected_row_data.get('Order Status', 'New Order')
                    
                    status_options = [
                        "New Order", "Designing", "Customer Review", 
                        "Design Modification", "Customer Approved", "Printing", 
                        "Ready for Delivery", "Outsourced", "Delivered", "Others"
                    ]
                    
                    try:
                        default_idx = status_options.index(current_status)
                    except ValueError:
                        default_idx = 0

                    with st.form("update_form"):
                        new_status = st.selectbox("Update Order Status", options=status_options, index=default_idx)
                        updated_remarks = st.text_area("Update Remarks / Notes", value=str(selected_row_data.get('Follow-up Remarks / Production Notes', '')))
                        
                        update_submitted = st.form_submit_button("🔄 Update Status in Sheet")
                        
                        if update_submitted:
                            try:
                                sheet.update_cell(row_index, 12, new_status)
                                sheet.update_cell(row_index, 13, updated_remarks)
                                st.success(f"Order {selected_order_id} status updated to '{new_status}' successfully!")
                            except Exception as update_err:
                                st.error(f"Failed to update: {update_err}")

if __name__ == "__main__":
    main()
