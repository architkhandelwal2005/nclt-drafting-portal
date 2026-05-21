import streamlit as st

# --- SECURITY GATE ---
def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == st.secrets["app_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Please enter the portal password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Please enter the portal password", type="password", on_change=password_entered, key="password")
        st.error("Incorrect password.")
        return False
    return True

if not check_password():
    st.stop()  # Do not execute the rest of the app if password is wrong
# ---------------------

# Your normal app code continues below here...
import streamlit as st
import pandas as pd
import json
import os
from document_engine import generate_master_document

# --- 1. Page Configuration ---
st.set_page_config(page_title="NCLT Phase 4: Drafting Portal", layout="wide")
st.title("NCLT AI Automation: Automated Drafting Portal")

# --- 2. Initialize Centralized Case State ---
if 'case_state' not in st.session_state:
    st.session_state['case_state'] = {
        "cd_name": "", "cin": "", "nclt_bench": "", "cp_ib_number": "", "md_name": "", "cd_address": "",
        "ip_name": "", "ibbi_reg_no": "", "afa_validity": "", "ip_reg_address": "", "ip_email": "", "process_email": "",
        "cirp_order_date": "", "order_upload_date": "", "pa_date": "", "pa_newspapers": "", "claim_cutoff_date": "", "loc_date": "", "loc_filing_date": "", "loc_ia_number": "",
        "meeting_number": "", "meeting_date": "", "meeting_time": "", "meeting_mode": "", "meeting_venue": "", "notice_date": "",
        "evoting_start": "", "evoting_end": "", "evoting_link": "",
        "process_bank": "", "initial_funding": "", "ip_fee": "", "ip_ope": "", "nclt_fee": "", "valuer_fee_cap": "",
        "df_creditors": None, "df_suspended_mgmt": None, "df_expenses": None
    }

def update_state(key, widget_key):
    st.session_state['case_state'][key] = st.session_state[widget_key]

def load_profile(uploaded_file):
    if uploaded_file is not None:
        try:
            loaded_data = json.load(uploaded_file)
            for k, v in loaded_data.items():
                st.session_state['case_state'][k] = v
            st.success("Case profile loaded successfully. The fields have been updated in the background.")
        except Exception as e:
            st.error(f"Error loading profile: {e}")

# --- 3. Sidebar: Global Case & IP Details ---
with st.sidebar:
    st.header("Case Management")
    
    # Save & Load Feature
    with st.expander("💾 Save / Load Case Profile", expanded=False):
        uploaded_profile = st.file_uploader("Upload Profile (.json)", type=["json"])
        if uploaded_profile:
            load_profile(uploaded_profile)
            
        # Filter out DataFrames for JSON serialization
        serializable_state = {k: v for k, v in st.session_state['case_state'].items() if not isinstance(v, pd.DataFrame) and v is not None}
        json_string = json.dumps(serializable_state, indent=4)
        
        cd_name_clean = st.session_state['case_state'].get('cd_name', 'Case').replace("/", "_").replace(" ", "_")
        if not cd_name_clean: cd_name_clean = "New_Case"
        
        st.download_button(
            label="Download Current Profile",
            data=json_string,
            file_name=f"{cd_name_clean}_profile.json",
            mime="application/json"
        )
        
    st.divider()
    st.header("Global Variables")
    
    with st.expander("1. Corporate Debtor Details", expanded=True):
        st.text_input("CD Name", value=st.session_state['case_state']['cd_name'], key="cd_name_input", on_change=lambda: update_state("cd_name", "cd_name_input"))
        st.text_input("CIN", value=st.session_state['case_state']['cin'], key="cin_input", on_change=lambda: update_state("cin", "cin_input"))
        st.text_input("NCLT Bench", value=st.session_state['case_state']['nclt_bench'], key="nclt_bench_input", on_change=lambda: update_state("nclt_bench", "nclt_bench_input"))
        st.text_input("CP(IB) Number", value=st.session_state['case_state']['cp_ib_number'], key="cp_ib_input", on_change=lambda: update_state("cp_ib_number", "cp_ib_input"))
        st.text_input("MD Name", value=st.session_state['case_state']['md_name'], key="md_name_input", on_change=lambda: update_state("md_name", "md_name_input"))
        st.text_area("CD Address", value=st.session_state['case_state']['cd_address'], key="cd_address_input", on_change=lambda: update_state("cd_address", "cd_address_input"))

    with st.expander("2. Professional Details"):
        st.text_input("IP Name", value=st.session_state['case_state']['ip_name'], key="ip_name_input", on_change=lambda: update_state("ip_name", "ip_name_input"))
        st.text_input("IBBI Reg No", value=st.session_state['case_state']['ibbi_reg_no'], key="ibbi_input", on_change=lambda: update_state("ibbi_reg_no", "ibbi_input"))
        st.text_input("AFA Validity Date", value=st.session_state['case_state']['afa_validity'], key="afa_input", on_change=lambda: update_state("afa_validity", "afa_input"))
        st.text_area("Registered Address", value=st.session_state['case_state']['ip_reg_address'], key="ip_address_input", on_change=lambda: update_state("ip_reg_address", "ip_address_input"))
        st.text_input("IP Email", value=st.session_state['case_state']['ip_email'], key="ip_email_input", on_change=lambda: update_state("ip_email", "ip_email_input"))
        st.text_input("Process Email", value=st.session_state['case_state']['process_email'], key="process_email_input", on_change=lambda: update_state("process_email", "process_email_input"))

    with st.expander("3. CIRP Timeline"):
        st.text_input("CIRP Order Date", value=st.session_state['case_state']['cirp_order_date'], key="cirp_date_input", on_change=lambda: update_state("cirp_order_date", "cirp_date_input"))
        st.text_input("Claim Cut-off Date", value=st.session_state['case_state']['claim_cutoff_date'], key="claim_cutoff_input", on_change=lambda: update_state("claim_cutoff_date", "claim_cutoff_input"))
        st.text_input("LOC / CoC Date", value=st.session_state['case_state']['loc_date'], key="loc_date_input", on_change=lambda: update_state("loc_date", "loc_date_input"))

    st.divider()
    
    # Cheat Sheet Integrated into Sidebar
    with st.expander("📋 Staff Cheat Sheet (Data Requirements)", expanded=False):
        st.markdown("""
        **Global Variables (Required for ALL)**
        *Entered once above. Applies everywhere.*
        * **CD Details:** Name, CIN, NCLT Bench, CP(IB) No, Address
        * **IP Details:** Name, IBBI No, AFA Date, Address, Emails
        * **CIRP Dates:** Order, Upload, PA, Claim Cut-off, LOC Date

        ---
        **1. Voting Agenda**
        * **Meeting Tabs:** Number, Date, Time.
        * **Financials Tab:** IP Fee, IP OPE, Valuer Fee Cap, Bank.
        * **CSV Uploads:** Creditors List, Expenses.

        **2. Constitution of CoC**
        * **CSV Uploads:** Creditors List.

        **3. Notice of 1st CoC**
        * **Meeting Tabs:** Date, Time, Mode, Notice Date, E-Voting Parameters.
        * **Financials Tab:** IP Fee, Bank.
        * **CSV Uploads:** Creditors List, Suspended Mgmt.

        **4. Notice of 2nd CoC**
        * **Meeting Tabs:** Date, Time, Mode, Venue, Notice Date, E-Voting.
        * **CSV Uploads:** Creditors List, Suspended Mgmt.

        **5. LOC Filing & CoC Report**
        * **Required Fields (Add to forms):** LOC Filing Date, IA Number, NCLT Fee, PA Newspapers.
        """)

# --- 4. Main Interface: Document Generation Engine ---
tab1, tab2, tab3 = st.tabs(["Meeting Setup & Filing", "Financials & Tables", "Generate Documents"])

with tab1:
    st.subheader("Current Meeting Dynamics")
    col1, col2 = st.columns(2)
    col1.text_input("Notice Date", value=st.session_state['case_state']['notice_date'], key="notice_date_input", on_change=lambda: update_state("notice_date", "notice_date_input"))
    col2.text_input("Meeting Number (e.g., 01st)", value=st.session_state['case_state']['meeting_number'], key="meeting_number_input", on_change=lambda: update_state("meeting_number", "meeting_number_input"))
    col1.text_input("Meeting Date (e.g., 01st October 2025)", value=st.session_state['case_state']['meeting_date'], key="meeting_date_input", on_change=lambda: update_state("meeting_date", "meeting_date_input"))
    col2.text_input("Meeting Time (e.g., 11:00 AM)", value=st.session_state['case_state']['meeting_time'], key="meeting_time_input", on_change=lambda: update_state("meeting_time", "meeting_time_input"))
    col1.text_input("Meeting Mode", value=st.session_state['case_state']['meeting_mode'], key="meeting_mode_input", on_change=lambda: update_state("meeting_mode", "meeting_mode_input"))
    col2.text_input("Meeting Venue", value=st.session_state['case_state']['meeting_venue'], key="meeting_venue_input", on_change=lambda: update_state("meeting_venue", "meeting_venue_input"))
    
    st.markdown("**E-Voting Parameters**")
    col3, col4 = st.columns(2)
    col3.text_input("Start (e.g., 02nd Oct at 10 AM)", value=st.session_state['case_state']['evoting_start'], key="evoting_start_input", on_change=lambda: update_state("evoting_start", "evoting_start_input"))
    col4.text_input("End (e.g., 03rd Oct at 10 AM)", value=st.session_state['case_state']['evoting_end'], key="evoting_end_input", on_change=lambda: update_state("evoting_end", "evoting_end_input"))
    st.text_input("E-Voting Link", value=st.session_state['case_state']['evoting_link'], key="evoting_link_input", on_change=lambda: update_state("evoting_link", "evoting_link_input"))

    st.divider()
    st.subheader("Filing Specifics (For LOC Document)")
    col5, col6 = st.columns(2)
    col5.text_input("LOC Filing Date", value=st.session_state['case_state']['loc_filing_date'], key="loc_filing_date_input", on_change=lambda: update_state("loc_filing_date", "loc_filing_date_input"))
    col6.text_input("IA Number", value=st.session_state['case_state']['loc_ia_number'], key="loc_ia_input", on_change=lambda: update_state("loc_ia_number", "loc_ia_input"))
    st.text_input("PA Newspapers (e.g., Economic Times, Chautha Sansar)", value=st.session_state['case_state']['pa_newspapers'], key="pa_news_input", on_change=lambda: update_state("pa_newspapers", "pa_news_input"))

with tab2:
    st.subheader("Financial Parameters")
    col1, col2 = st.columns(2)
    col1.text_input("Process Bank (Name & Branch)", value=st.session_state['case_state']['process_bank'], key="bank_input", on_change=lambda: update_state("process_bank", "bank_input"))
    col2.text_input("IP Fee Amount", value=st.session_state['case_state']['ip_fee'], key="ip_fee_input", on_change=lambda: update_state("ip_fee", "ip_fee_input"))
    col1.text_input("IP OPE Amount", value=st.session_state['case_state']['ip_ope'], key="ip_ope_input", on_change=lambda: update_state("ip_ope", "ip_ope_input"))
    col2.text_input("Valuer Fee Cap", value=st.session_state['case_state']['valuer_fee_cap'], key="valuer_fee_input", on_change=lambda: update_state("valuer_fee_cap", "valuer_fee_input"))
    col1.text_input("NCLT Filing Fee Paid", value=st.session_state['case_state']['nclt_fee'], key="nclt_fee_input", on_change=lambda: update_state("nclt_fee", "nclt_fee_input"))
    
    st.subheader("Tabular Data Uploads")
    st.markdown("Upload CSV files containing the data matrices.")
    
    creditors_file = st.file_uploader("Upload Creditors List (CSV)", type=["csv"])
    if creditors_file: st.session_state['case_state']["df_creditors"] = pd.read_csv(creditors_file)
        
    mgmt_file = st.file_uploader("Upload Suspended Management List (CSV)", type=["csv"])
    if mgmt_file: st.session_state['case_state']["df_suspended_mgmt"] = pd.read_csv(mgmt_file)
        
    expenses_file = st.file_uploader("Upload CIRP Expenses (CSV)", type=["csv"])
    if expenses_file: st.session_state['case_state']["df_expenses"] = pd.read_csv(expenses_file)

with tab3:
    st.subheader("Document Generation Engine")
    st.write("Ensure required variables are filled in the Sidebar and Tabs 1 & 2 before generating.")
    
    docs_to_generate = {
        "Voting Agenda": "Voting_Agenda_Template.docx",
        "Constitution of CoC": "Constitution_of_CoC_Template.docx",
        "Notice of 1st CoC": "Notice_1st_CoC_Template.docx",
        "Notice of 2nd CoC": "Notice_2nd_CoC_Template.docx",
        "LOC Filing": "LOC_Filing_Template.docx"
    }

    selected_doc = st.selectbox("Select Document to Draft", list(docs_to_generate.keys()))
    
    if st.button("Generate Document"):
        template_filename = docs_to_generate[selected_doc]
        template_path = os.path.join("templates", template_filename)
        
        if not os.path.exists(template_path):
            st.error(f"Template not found at {template_path}. Ensure the file is saved correctly in the templates/ folder.")
        else:
            try:
                generated_file_bytes = generate_master_document(template_path, st.session_state['case_state'])
                
                cd_name_clean = st.session_state['case_state'].get('cd_name', 'Case').replace("/", "_").replace(" ", "_")
                if not cd_name_clean: cd_name_clean = "New_Case"
                
                output_filename = f"{cd_name_clean}_{selected_doc.replace(' ', '_')}.docx"
                
                st.success(f"Successfully compiled {selected_doc}!")
                st.download_button(
                    label=f"Download {output_filename}",
                    data=generated_file_bytes,
                    file_name=output_filename,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"An error occurred during generation: {e}")