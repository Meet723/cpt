import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# App title and configuration
st.set_page_config(page_title="CPT Code Description & Guidelines Finder", layout="wide")

# Authentication setup
def show_login_page():
    st.title("Login to CPT Code Description & Guidelines Finder")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Log in")
    
    correct_username = "Meet"
    correct_password = "Meet123"
    
    if login_button:
        if username == correct_username and password == correct_password:
            st.session_state["authenticated"] = True
        else:
            st.error("Invalid username or password.")

# Function to load data
@st.cache_data
def load_data(file_path):
    try:
        data = pd.read_excel(file_path, header=None)
        data = data[[0, 6]]  # Column A (index 0) and Column G (index 6)
        data.columns = ["CPT Code", "Description"]
        return data.dropna()
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return None

# Function to safely search for guidelines
def get_guidelines(cpt_code):
    try:
        # List of medical coding resource websites
        resource_urls = [
            f"https://www.aapc.com/codes/cpt-codes/{cpt_code}",
            f"https://www.findacode.com/code.php?set=CPT&c={cpt_code}",
            f"https://www.medicalcodingbuff.com/cpt-code-{cpt_code}"
        ]
        
        guidelines = []
        
        for url in resource_urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    guidelines.append(url)
            except:
                continue
            time.sleep(1)  # Polite delay between requests
        
        return guidelines
    except Exception as e:
        st.error(f"Error searching for guidelines: {e}")
        return []

# Main app logic
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    show_login_page()
else:
    st.title("CPT Code Description & Guidelines Finder")
    
    # Load the Excel file
    file_path = "/Users/apple/Desktop/surgery-service-codes-spreadsheet-5-1-24.xlsx"
    data = load_data(file_path)
    
    if data is not None:
        # Create two columns for layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Enter CPT Code")
            cpt_code_input = st.text_input("CPT Code:", placeholder="e.g., 36556")
        
        if cpt_code_input:
            # Filter for matching CPT code
            description = data.loc[data['CPT Code'].astype(str) == cpt_code_input, 'Description'].values
            
            with col2:
                if len(description) > 0:
                    st.subheader("Description:")
                    st.write(description[0])
                    
                    # Search for guidelines
                    st.subheader("CPT Code Guidelines Resources:")
                    with st.spinner("Searching for guidelines..."):
                        guideline_links = get_guidelines(cpt_code_input)
                        
                    if guideline_links:
                        st.success(f"Found {len(guideline_links)} resource(s) for CPT {cpt_code_input}")
                        for i, link in enumerate(guideline_links, 1):
                            st.markdown(f"{i}. [Access Guidelines Resource {i}]({link})")
                    else:
                        st.warning("No specific guidelines found. Try searching on:")
                        st.markdown("- [AAPC](https://www.aapc.com)")
                        st.markdown("- [Find-A-Code](https://www.findacode.com)")
                        st.markdown("- [CPT Professional Edition](https://www.ama-assn.org)")
                else:
                    st.warning(f"No description found for CPT Code {cpt_code_input}")
    else:
        st.info("Please ensure the Excel file is available and correctly formatted.")