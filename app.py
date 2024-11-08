import streamlit as st
import requests
import re
from fuzzywuzzy import fuzz, process

# OCR.Space API key
API_KEY = 'K86074082988957'

# Function to call OCR.Space API and extract text
def extract_text_from_image(image):
    url = 'https://api.ocr.space/parse/image'
    _, img_ext = image.name.rsplit('.', 1)
    files = {
        'file': (image.name, image.read(), f'image/{img_ext}')
    }
    data = {
        'apikey': API_KEY,
        'language': 'eng'
    }
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    if result['IsErroredOnProcessing']:
        return "Error processing the image"
    
    extracted_text = result['ParsedResults'][0]['ParsedText']
    return extracted_text

# Function to apply regex and extract Aadhaar info
def extract_aadhar_info(text):
    # Define regex patterns for names, Aadhaar numbers, and DOBs
    name_pattern = r'(?:Name:\s*|^)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
    dob_pattern = r'\b(?:\d{2}[-/]\d{2}[-/]\d{4}|\d{4}[-/]\d{2}[-/]\d{2})\b'
    
    # Extract names, Aadhaar numbers, and DOBs
    names = re.findall(name_pattern, text)
    aadhaar_numbers = re.findall(aadhaar_pattern, text)
    dobs = re.findall(dob_pattern, text)
    
    return {
        "Names": names,
        "Aadhaar Numbers": aadhaar_numbers,
        "Dates of Birth": dobs
    }

# Fuzzy matching function to find similar names from a reference list
def fuzzy_match_names(extracted_names, reference_names, top_n=5, threshold=80):
    all_matches = []
    for name in extracted_names:
        matches = process.extract(name, reference_names, scorer=fuzz.ratio, limit=top_n)
        filtered_matches = [match for match in matches if match[1] >= threshold]
        all_matches.extend(filtered_matches)
    
    # Sort by score and limit to top_n results
    all_matches = sorted(all_matches, key=lambda x: x[1], reverse=True)[:top_n]
    return all_matches

# Streamlit interface
st.title('OCR Text Extraction and Aadhaar Information')
st.write("Upload an image to extract text and retrieve Aadhaar details.")

uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_image is not None:
    # Display uploaded image
    st.image(uploaded_image, caption='Uploaded Image', use_column_width=True)
    
    # Extract text using OCR
    st.write("Extracting text...")
    extracted_text = extract_text_from_image(uploaded_image)
    
    # Display extracted text
    st.subheader("Extracted Text")
    st.write(extracted_text)
    
    # Process extracted text with regex to get Aadhaar info
    aadhaar_info = extract_aadhar_info(extracted_text)
    
    # Display structured Aadhaar info
    st.subheader("Extracted Aadhaar Information")
    st.write("### Names Found")
    st.write(aadhaar_info["Names"] if aadhaar_info["Names"] else "No names found")
    
    st.write("### Aadhaar Numbers Found")
    st.write(aadhaar_info["Aadhaar Numbers"] if aadhaar_info["Aadhaar Numbers"] else "No Aadhaar numbers found")
    
    st.write("### Dates of Birth Found")
    st.write(aadhaar_info["Dates of Birth"] if aadhaar_info["Dates of Birth"] else "No DOBs found")
    
    # Reference names list for fuzzy matching
    reference_names = [
        "Priya Sharma", "Aman Verma", "Rahul Kumar", "Riya Singh", "Anjali Mehta",
        "Suman Das", "Ajay Thakur", "Reema Rai", "Sunita Yadav", "Pankaj Gupta",
        "Kavita Rani", "Rohit Bhatia", "Sandeep Joshi", "Deepak Chaudhary", "Rakesh Malhotra",
        "Nisha Goel", "Rajeev Bhardwaj", "Alok Mishra", "Sneha Raj", "Vikram Chawla",
        "Meena Saxena", "Harish Yadav", "Preeti Nair", "Mohit Deshmukh", "Seema Kaushik",
        "Akash Jain", "Pooja Agrawal", "Ravi Kapoor", "Shreya Rao", "Amitabh Singh","Kiran Kumari","Kiran Kumar","Kiran Kum"
    ]
    
    # If any names are extracted, pre-fill the search box with the first name
    default_name = aadhaar_info["Names"][0] if aadhaar_info["Names"] else ''
    
    # Input search name from the user with a pre-filled extracted name
    search_name = st.text_input("Search for a name", default_name)
    

    if search_name:
        # Fuzzy match names based on the search input
        st.write(f"Searching for closest matches to: {search_name}")
        matched_names = fuzzy_match_names([search_name], reference_names, top_n=5)
        
        # Display the matched names
        st.subheader("Fuzzy Matched Names")
        if matched_names:
            for match in matched_names:
                st.write(f"Match: {match[0]} (Score: {match[1]})")
        else:
            st.write("No close matches found.")
