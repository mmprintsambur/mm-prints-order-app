from datetime import datetime
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Page Configuration
st.set_page_config(
    page_title="MM Prints - Management Portal",
    page_icon="🖨️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional Corporate Branding & Layout
st.markdown("""
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .corporate-header {
        background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        margin-bottom: 25px;
        border-bottom: 4px solid #ffd700;
    }
    .logo-img {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #ffd700;
        margin-bottom: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .corporate-header h1 {
        color: #ffffff !important;
        font-size: 26px;
        margin: 5px 0;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .tagline {
        color: #ffd700;
        font-size: 13px;
        font-style: italic;
        margin-bottom: 8px;
    }
    .address-box {
        color: #e0e0e0;
        font-size: 12px;
        line-height: 1.4;
        background: rgba(255, 255, 255, 0.08);
        padding: 8px 12px;
        border-radius: 8px;
        display: inline-block;
        margin-top: 5px;
    }
    .footer-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #2c5364;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        margin-top: 30px;
        font-size: 12px;
        color: #6c757d;
        text-align: center;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        height: 3.2em;
        width: 100%;
        background-color: #2c5364;
        color: white;
    }
    .stButton>button:hover {
        background-color: #203a43;
        border-color: #ffd700;
        color: #ffd700;
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

def main():
    # Corporate Header with Official Logo & GST Address
    st.markdown("""
        <div class="corporate-header">
            <img src="https://i.ibb.co/3ykS5s4/mm-prints-logo.jpg" class="logo-img" alt="MM Prints Logo">
            <h1>MM PRINTS</h1>
            <div class="tagline">"YOUR IMAGINATION — OUR CREATION"</div>
            <div class="address-box">
                📍 <b>Ground Floor, No.80/1A, S.K. Road, Krishnapuram, Ambur, Tirupathur, Tamil Nadu - 635802</b><br>
                🔖 <b>GSTIN:</b> 33BFXPL1178K1ZV | 🖨️ Commercial Printing & Signage Solutions
            </div>
        </div>
    """, unsafe_allow_html=True)

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

    # ================= HOME PAGE =================
    if st.session_state.page == "home":
        st.markdown("<h3 style='text-align: center; color: #2c5364; margin-bottom: 20px;'>Select Operation Mode</h3>", unsafe_allow_html=True)
        
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
                    st.info(f"**Customer Name:** {selected_row_data.get('Customer Name')} | **Job Type:** {selected_row_data.get('Job Type')}")
                    
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

    # Corporate Footer
    st.markdown("""
        <div class="footer-box">
            <b>MM Prints Internal Operations & Management Portal</b> &copy; 2026 | Prop: Lawrance Madhankumar | Ambur, TN
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
