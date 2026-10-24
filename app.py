from datetime import datetime
import urllib.parse
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(
    page_title="MM Prints - Management Portal",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS with PWA manifest link and Full Page Box Border Effect
st.markdown("""
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#1e3a8a">
    <style>
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }
    .main {
        background-color: #f8fafc;
    }
    .corporate-header {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 20px;
        border-top: 4px solid #1e3a8a;
    }
    .footer-box {
        background-color: #f8fafc;
        padding: 15px;
        border-radius: 8px;
        border-bottom: 4px solid #1e3a8a;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        margin-top: 30px;
        font-size: 11px;
        color: #475569;
        text-align: center;
        line-height: 1.5;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
        height: 3em;
        width: 100%;
        background-color: #1e3a8a;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

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

def format_phone_number(phone):
    cleaned = ''.join(filter(str.isdigit, str(phone)))
    if len(cleaned) == 10:
        return f"91{cleaned}"
    return cleaned

def main():
    # Header Section
    st.markdown('<div class="corporate-header">', unsafe_allow_html=True)
    
    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        try:
            st.image("logo.png", use_column_width=True)
        except Exception:
            st.markdown("<h3 style='color:#1e3a8a; text-align:center;'>MM PRINTS</h3>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Connect to Google Sheet
    try:
        gc = get_gsheet_client()
        spreadsheet_id = st.secrets["SPREADSHEET_ID"]
        sheet = gc.open_by_key(spreadsheet_id).sheet1
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {e}")
        st.stop()

    if "page" not in st.session_state:
        st.session_state.page = "home"

    # ================= HOME PAGE =================
    if st.session_state.page == "home":
        st.markdown("<h4 style='text-align: center; color: #1e3a8a; margin-bottom: 15px;'>Select Operation Mode</h4>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="medium")
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
        if st.button("⬅️ Back to Home Menu"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown("---")
        next_order_id = generate_order_id(sheet)
        current_date = datetime.now().strftime("%Y-%m-%d")

        with st.form("order_form", clear_on_submit=True):
            st.subheader("📝 New Order Booking Form")
            
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("Order ID (Auto-generated)", value=next_order_id, disabled=True)
                st.text_input("Order Date", value=current_date, disabled=True)
                customer_name = st.text_input("Customer Name *")
                phone = st.text_input("Phone / Contact Number *")
                
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

            submitted = st.form_submit_button("🚀 Submit Order & Save")

            if submitted:
                if not customer_name or not phone:
                    st.warning("Please fill in Customer Name and Phone Number.")
                else:
                    try:
                        new_row = [
                            next_order_id,          
                            current_date,           
                            customer_name,          
                            phone,                  
                            job_type,               
                            quantity_specs,         
                            assigned_designer,      
                            total_amount,           
                            advance_paid,           
                            balance_due,            
                            str(delivery_deadline), 
                            order_status,           
                            remarks,                
                            ""                      
                        ]
                        sheet.append_row(new_row)
                        st.balloons()
                        st.success(f"Order '{next_order_id}' submitted successfully to Google Sheets!")
                    except Exception as err:
                        st.error(f"Failed to save order: {err}")

    # ================= UPDATE ORDER STATUS PAGE =================
    elif st.session_state.page == "update_order":
        if st.button("⬅️ Back to Home Menu"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown("---")
        st.subheader("🔄 Update Existing Order Status")
        
        try:
            all_rows = sheet.get_all_values()
        except Exception:
            all_rows = []

        if len(all_rows) <= 1:
            st.info("No orders found in Google Sheet yet.")
        else:
            header = all_rows[0]
            data_rows = all_rows[1:]
            
            order_ids = [row[0] for row in data_rows if len(row) > 0 and row[0]]
            
            if not order_ids:
                st.warning("No Order IDs available.")
            else:
                selected_order_id = st.selectbox("Select Order ID to Update", options=order_ids)
                
                selected_row_values = None
                row_index = -1
                for idx, row in enumerate(data_rows):
                    if len(row) > 0 and row[0] == selected_order_id:
                        selected_row_values = row
                        row_index = idx + 2
                        break
                
                if selected_row_values:
                    cust_name = selected_row_values[2] if len(selected_row_values) > 2 else ""
                    job_t = selected_row_values[4] if len(selected_row_values) > 4 else ""
                    
                    try:
                        tot_amt = float(selected_row_values[7]) if len(selected_row_values) > 7 and selected_row_values[7] else 0.0
                    except ValueError:
                        tot_amt = 0.0
                        
                    try:
                        adv_paid = float(selected_row_values[8]) if len(selected_row_values) > 8 and selected_row_values[8] else 0.0
                    except ValueError:
                        adv_paid = 0.0
                        
                    bal_due = max(0.0, tot_amt - adv_paid)
                    
                    st.info(f"**Customer:** {cust_name} | **Job:** {job_t} | **Balance Due:** ₹{bal_due:.2f}")
                    
                    current_status = selected_row_values[11] if len(selected_row_values) > 11 and selected_row_values[11] else "New Order"
                    current_remarks = selected_row_values[12] if len(selected_row_values) > 12 else ""
                    
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
                        updated_remarks = st.text_area("Update Remarks / Notes", value=str(current_remarks))
                        
                        update_submitted = st.form_submit_button("🔄 Update Status in Sheet")
                        
                        if update_submitted:
                            try:
                                sheet.update_cell(row_index, 12, new_status)
                                sheet.update_cell(row_index, 13, updated_remarks)
                                
                                st.session_state.update_success = True
                                st.session_state.updated_order_id = selected_order_id
                                st.session_state.cust_name = cust_name
                                st.session_state.cust_phone = selected_row_values[3] if len(selected_row_values) > 3 else ""
                                st.session_state.new_status = new_status
                                st.session_state.bal_due = bal_due
                                st.rerun()
                            except Exception as update_err:
                                st.error(f"Failed to update: {update_err}")

        # Show WhatsApp Button if status was just successfully updated
        if st.session_state.get("update_success"):
            st.success(f"Order {st.session_state.updated_order_id} status updated to '{st.session_state.new_status}' successfully!")
            
            wa_phone = format_phone_number(st.session_state.cust_phone)
            wa_message = (
                f"Hello {st.session_state.cust_name},\n\n"
                f"Your order (ID: {st.session_state.updated_order_id}) with MM PRINTS status has been updated to: {st.session_state.new_status}.\n"
            )
            if float(st.session_state.bal_due or 0) > 0:
                wa_message += f"Balance Due: ₹{st.session_state.bal_due:.2f}\n\n"
            wa_message += "Thank you for choosing MM Prints - Ambur! 🖨️"
            
            encoded_msg = urllib.parse.quote(wa_message)
            wa_link = f"https://wa.me/{wa_phone}?text={encoded_msg}"
            
            st.markdown(f"""
                <div style="text-align: center; margin-top: 15px; margin-bottom: 15px;">
                    <a href="{wa_link}" target="_blank">
                        <button style="background-color: #25d366; color: white; padding: 12px 24px; border: none; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            💬 Send WhatsApp Update to Customer
                        </button>
                    </a>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("❌ Close / Clear"):
                st.session_state.update_success = False
                st.rerun()

    # Footer with Bottom Blue Border
    st.markdown("""
        <div class="footer-box">
            📍 <b>MM PRINTS</b> | Ground Floor, No.80/1A, S.K. Road, Krishnapuram, Ambur, Tirupathur, Tamil Nadu - 635802<br>
            🔖 <b>GSTIN:</b> 33BFXPL1178K1ZV | 📞 <b>Contact:</b> +91 9933360360 | +91 7010660360 | +91 9025660360<br>
            <hr style="margin: 8px 0; border-top: 1px solid #cbd5e1;">
            Internal Management Portal &copy; 2026 | Prop: Lawrance Madhankumar
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
