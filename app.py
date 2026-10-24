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
    """
    இன்றைய தேதிக்கு (YYYYMMDD) தகுந்தவாறு அடுத்த 3 இலக்க சீரிஸ் நம்பரை உருவாக்குகிறது.
    உதாரணம்: MMP20261024001
    """
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"MMP{today_str}"
    
    try:
        # ஷீட்டில் உள்ள எல்லா Order ID-க்களையும் எடுக்கிறோம் (Column 1)
        records = sheet.col_values(1)
        
        # இன்றைய தேதிக்கான ஏற்கனவே உள்ள ஆர்டர்களை வடிகட்டுகிறோம்
        today_orders = [rec for rec in records if rec and rec.startswith(prefix)]
        
        if today_orders:
            # கடைசியாக உள்ள ஆர்டரின் சீரிஸ் எண்ணை எடுத்து +1 செய்கிறோம்
            last_order = today_orders[-1]
            try:
                seq_num = int(last_order[-3:]) + 1
            except ValueError:
                seq_num = 1
        else:
            # இன்றைய தேதியில் முதல் ஆர்டர் என்றால் 001 இலிருந்து தொடங்கும்
            seq_num = 1
            
        return f"{prefix}{seq_num:03d}"
    except Exception:
        # ஏதேனும் பிழை ஏற்பட்டால் ஃபால்பாக்பாக முதல் எண்ணைத் தரும்
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

    # ஆட்டோமேட்டிக்காக அடுத்த Order ID-யை உருவாக்குதல்
    next_order_id = generate_order_id(sheet)

    # Order Entry Form
    with st.form("order_form", clear_on_submit=True):
        st.subheader("Order Details")
        
        col1, col2 = st.columns(2)
        with col1:
            # ஆட்டோமேட்டிக் ஜெனரேட் ஆன ID-யை இங்கு செட் செய்கிறோம் (ஸ்டாஃப் மாற்ற முடியாது)
            order_id = st.text_input("Order ID (Auto-generated)", value=next_order_id, disabled=True)
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
                    # ஷீட்டில் சேமிக்கும்போது ஆட்டோமேட்டிக் ஜெனரேட் ஆன ID-யைப் பயன்படுத்துகிறோம்
                    new_row = [
                        next_order_id,
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
                    st.success(f"Order '{next_order_id}' submitted successfully!")
                    # ஃபார்ம் சப்மிட் ஆனதும் பேஜை ரெப்ரெஷ் செய்து அடுத்த ID-க்கு மாற்றலாம்
                    st.rerun()
                except Exception as err:
                    st.error(f"Failed to save order: {err}")

if __name__ == "__main__":
    main()
