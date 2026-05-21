import os
import fitz  # PyMuPDF
from google import genai
from dotenv import load_dotenv

# 1. Load the environment variables
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: Could not find GEMINI_API_KEY. Your file might be named .env.txt instead of .env")
    exit()

# 2. Initialize the Gemini Client
client = genai.Client(api_key=api_key)

# 3. Define the target document
pdf_filename = "sample_order.pdf"
print(f"Reading text from {pdf_filename}...")

# 4. Extract text from the PDF
try:
    doc = fitz.open(pdf_filename)
    pdf_text = ""
    for page in doc:
        pdf_text += page.get_text()
    doc.close()
    print("Text extraction successful. Transmitting to Gemini API...")
except FileNotFoundError:
    print(f"Error: Make sure {pdf_filename} is inside your NCLT_project folder.")
    exit()

# 5. Define the Prompt
prompt = f"""
You are a highly analytical legal assistant specializing in Indian IBC and NCLT matters.
Review the following extracted text from a tribunal order.
Identify and extract every date, deadline, and compliance requirement.
Format the output as a clean, chronological bulleted list.

Document Text:
{pdf_text}
"""

# 6. Execute the API call
try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    print("\n--- DEADLINES AND COMPLIANCE DATES ---")
    print(response.text)
    print("--------------------------------------")
except Exception as e:
    print(f"An error occurred during the API call: {e}")