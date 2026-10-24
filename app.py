import json
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="MM Prints - Order Entry", page_icon="🖨️", layout="centered"
)

st.title("🖨️ MM Prints - New Order Booking")
st.caption("Ambur | Staff Data Entry Portal")

scopes = ["https://www.googleapis.com/auth/spreadsheets"]


@st.cache_resource
def get_gsheet_client():
  creds_dict = json.loads(st.secrets["GOOGLE_JSON_KEY"])
  creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
  return gspread.authorize(creds)


gc = get_gsheet_client()
sheet_id = st.secrets["SPREADSHEET_ID"]
sh = gc.open_by_key(sheet_id)
worksheet = sh.sheet1

st.subheader("📋 Enter Order Details")

with st.form("order_form", clear_on_submit=True):
  order_id = st.text_input("Order ID (e.g., ORD-2026-2415)", value="")
  customer_name = st.text_input("Customer Name", value="")
  phone_number = st.text_input(
      "WhatsApp / Contact Number (with country code, e.g., 919842154320)",
      value="91",
  )

  job_type = st.selectbox(
      "Job Type",
      [
          "Flex",
          "Invitation",
          "Board-13/19",
          "Board-12/18",
          "Sticker-13/19",
          "Sticker-12/18",
          "Vinyl Stickers",
          "Visiting cards",
          "Outsource",
          "Shop light board",
          "Wall posters",
          "Synthetic cards",
          "Others",
      ],
  )

  specs = st.text_area(
      "Quantity & Specifications (e.g., 10x4 ft Star Flex with eyelets)",
      value="",
  )

  designer = st.selectbox(
      "Assigned Designer",
      ["Sakkra", "Kumaran", "Surya", "Ram", "Muthukumar", "Sakthi"],
  )

  col1, col2 = st.columns(2)
  with col1:
    total_amount = st.number_input(
        "Total Amount (₹)", min_value=0, value=0, step=50
    )
  with col2:
    advance_paid = st.number_input(
        "Advance Paid (₹)", min_value=0, value=0, step=50
    )

  deadline = st.text_input(
      "Delivery Deadline (e.g., 2026-10-25 18:00)", value=""
  )

  order_status = st.selectbox(
      "Order Status",
      [
          "New Order",
          "Designing",
          "Customer Review",
          "Design Modification",
          "Customer Approved",
          "Printing",
          "Ready for Delivery",
          "Outsourced",
          "Delivered",
          "Others",
      ],
  )

  remarks = st.text_input("Follow-up Remarks / Production Notes", value="")

  submitted = st.form_submit_button("🚀 Submit Order")

if submitted:
  if not order_id or not customer_name or not phone_number:
    st.error("❌ Please fill in Order ID, Customer Name, and Phone Number!")
  else:
    balance_due = total_amount - advance_paid
    order_date = pd.Timestamp.now().strftime("%Y-%m-%d")

    wa_text = f"Hello {customer_name}! Your order {order_id} has been registered at MM Prints. Status: {order_status}. / வணக்கம் {customer_name}! உங்கள் ஆர்டர் {order_id} நிலை: {order_status}."
    encoded_msg = wa_text.replace(" ", "%20")
    wa_link = f"https://wa.me/{phone_number}?text={encoded_msg}"

    new_row = [
        order_id,
        order_date,
        customer_name,
        phone_number,
        job_type,
        specs,
        designer,
        total_amount,
        advance_paid,
        balance_due,
        deadline,
        order_status,
        remarks,
        wa_link,
    ]

    worksheet.append_row(new_row)
    st.success(f"✅ Order {order_id} for {customer_name} successfully added!")

    st.markdown(
        f'<a href="{wa_link}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">📲 Send WhatsApp Confirmation</button></a>',
        unsafe_allow_html=True,
    )
