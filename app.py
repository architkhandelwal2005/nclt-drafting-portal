import os
import fitz  # PyMuPDF
from google import genai
from dotenv import load_dotenv
import streamlit as st
import json
import csv
from datetime import datetime, timedelta

# 1. Initialize Configuration
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Configuration Error: GEMINI_API_KEY not found in the .env file.")
    st.stop()

client = genai.Client(api_key=api_key)

# 2. Configure Streamlit Interface
st.set_page_config(page_title="NCLT CIRP Engine", page_icon="⚖️")
st.title("⚖️ NCLT CIRP Deadline Engine")
st.write("Extract the Order Date (T) and compute all statutory CIRP deadlines automatically.")

# 3. File Upload Mechanism
uploaded_file = st.file_uploader("Select NCLT Order (PDF format)", type="pdf")

if uploaded_file is not None:
    with st.spinner("Reading document..."):
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            pdf_text = ""
            for page in doc:
                pdf_text += page.get_text()
            doc.close()
            st.success("Document read successfully.")
        except Exception as e:
            st.error(f"Failed to read PDF: {e}")
            st.stop()

    # 4. Execution Trigger
    if st.button("Compute & Save CIRP Deadlines"):
        with st.spinner("Locating Anchor Date (T) and computing timeline..."):
            
            # Ask the AI to ONLY find Date T
            prompt = f"""
            You are a highly analytical legal assistant. Review this NCLT order.
            Identify ONLY the date the NCLT order was pronounced, uploaded, or issued. 
            This is the date of commencement of the Corporate Insolvency Resolution Process (CIRP).
            
            You MUST return the output STRICTLY as JSON.
            Format the date strictly as YYYY-MM-DD.
            Use exactly this format:
            {{"anchor_date": "YYYY-MM-DD"}}
            
            If you cannot find the date, return {{"anchor_date": null}}
            
            Document Text:
            {pdf_text}
            """

            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                # Parse the AI's response
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                extracted_data = json.loads(raw_text.strip())
                anchor_date_str = extracted_data.get("anchor_date")
                
                if not anchor_date_str:
                    st.error("Could not confidently identify the Order Date (T) in the document. Please verify the document.")
                    st.stop()
                    
                st.success(f"Anchor Date (T) located: {anchor_date_str}")
                
                # 5. THE RULES ENGINE (Computing T + X)
                date_t = datetime.strptime(anchor_date_str, "%Y-%m-%d")
                
                # We calculate all standard IBBI timeline events using Python math
                computed_deadlines = [
                    {"event": "Order Date / Commencement of CIRP (T)", "date": date_t.strftime("%Y-%m-%d")},
                    {"event": "Public announcement inviting claims (T+3)", "date": (date_t + timedelta(days=3)).strftime("%Y-%m-%d")},
                    {"event": "Submission of claims (T+14)", "date": (date_t + timedelta(days=14)).strftime("%Y-%m-%d")},
                    {"event": "Verification of claims (T+21)", "date": (date_t + timedelta(days=21)).strftime("%Y-%m-%d")},
                    {"event": "Constitution of CoC (T+23)", "date": (date_t + timedelta(days=23)).strftime("%Y-%m-%d")},
                    {"event": "First meeting of the CoC (T+30)", "date": (date_t + timedelta(days=30)).strftime("%Y-%m-%d")},
                    {"event": "Submission of Information Memorandum to CoC (T+54)", "date": (date_t + timedelta(days=54)).strftime("%Y-%m-%d")},
                    {"event": "Publish Form G - Invitation of EOI (T+75)", "date": (date_t + timedelta(days=75)).strftime("%Y-%m-%d")},
                    {"event": "Submission of EOI (T+90)", "date": (date_t + timedelta(days=90)).strftime("%Y-%m-%d")},
                    {"event": "Provisional List of Resolution Applicants (T+100)", "date": (date_t + timedelta(days=100)).strftime("%Y-%m-%d")},
                    {"event": "Final List of Resolution Applicants (T+115)", "date": (date_t + timedelta(days=115)).strftime("%Y-%m-%d")},
                    {"event": "Normal CIRP Completion Deadline (T+180)", "date": (date_t + timedelta(days=180)).strftime("%Y-%m-%d")}
                ]
                
                # 6. Save the COMPUTED data to the CSV file
                csv_file = "deadlines_database.csv"
                file_exists = os.path.isfile(csv_file)
                
                with open(csv_file, mode='a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(["Event", "Deadline Date", "Case File"]) 
                    
                    for item in computed_deadlines:
                        writer.writerow([item["event"], item["date"], uploaded_file.name])
                        
                st.success(f"Successfully computed and saved standard CIRP deadlines to database!")
                
                # Show the computed data on the screen
                st.subheader("📅 Computed Statutory Deadlines")
                st.table(computed_deadlines)
                
            except Exception as e:
                st.error(f"Error processing data: {e}")
                st.write("Raw AI Output (for debugging):", response.text)