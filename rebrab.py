import streamlit as st
import requests
import json
from docx import Document
import io

# Hardcoded API key
API_KEY = "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"

# Page config
st.set_page_config(page_title="Content Rebranding AI", page_icon="✨", layout="wide")

# Title
st.title("✨ Content Rebranding AI Tool")
st.markdown("Upload a Word document and transform it into your brand voice")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("Brand Voice Options")
    brand_voice = st.selectbox(
        "Choose target brand voice:",
        ["Casual & Friendly", "Professional & Corporate", "Fun & Playful", 
         "Technical & Expert", "Warm & Empowering", "Direct & Sales-Focused"]
    )

# Main content area
col1, col2 = st.columns(2)

with col1:
    st.header("📤 Upload Document")
    uploaded_file = st.file_uploader("Choose a Word document", type=['docx'])
    
    if uploaded_file:
        st.success(f"✅ Uploaded: {uploaded_file.name}")
        
        # Read the Word document
        try:
            doc = Document(uploaded_file)
            original_text = "\n\n".join([para.text for para in doc.paragraphs if para.text.strip()])
            
            # Calculate character count
            char_count = len(original_text)
            gemini_limit = 750000  # Gemini 2.0 Flash can handle ~750k characters
            
            # Display stats
            st.subheader("📊 Document Stats")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Total Characters", f"{char_count:,}")
            with col_b:
                st.metric("Gemini Limit", f"{gemini_limit:,}")
            with col_c:
                percentage = (char_count / gemini_limit) * 100
                st.metric("Usage", f"{percentage:.1f}%")
            
            # Check if processable
            if char_count > gemini_limit:
                st.error(f"⚠️ Document is too large! ({char_count:,} chars) Reduce to under {gemini_limit:,} characters.")
                st.info("💡 Tip: Split your document into smaller sections or remove some content.")
            else:
                st.success(f"✅ Document size is good! Can process all {char_count:,} characters.")
            
            st.subheader("📄 Original Content Preview")
            st.text_area("Preview (first 1000 chars):", original_text[:1000], height=300)
            
            # Store in session state
            st.session_state['original_text'] = original_text
            st.session_state['char_count'] = char_count
            
        except Exception as e:
            st.error(f"Error reading document: {e}")

with col2:
    st.header("✨ Transformed Content")
    
    if 'original_text' in st.session_state:
        # Check if document is too large
        if st.session_state.get('char_count', 0) > 750000:
            st.error("⚠️ Document is too large to process. Please upload a smaller document.")
        else:
            if st.button("🚀 Transform Content", type="primary"):
                with st.spinner("🤖 AI is transforming your content..."):
                    # Call OpenRouter API
                    try:
                        prompt = f"""Transform this content into a {brand_voice} brand voice. 
                        
Keep the same information and structure, but rewrite it to match the tone.

Original Content:
{st.session_state['original_text']}

Provide the transformed version:"""

                        response = requests.post(
                            url="https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {API_KEY}",
                                "Content-Type": "application/json",
                            },
                            data=json.dumps({
                                "model": "google/gemini-2.5-flash-lite-preview-09-2025",
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": prompt
                                    }
                                ]
                            }),
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            transformed_text = result['choices'][0]['message']['content']
                            
                            st.success("✅ Transformation complete!")
                            st.text_area("Transformed Content:", transformed_text, height=300)
                            
                            # Store transformed text
                            st.session_state['transformed_text'] = transformed_text
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Transformed Content",
                                data=transformed_text,
                                file_name=f"transformed_{uploaded_file.name.replace('.docx', '.txt')}",
                                mime="text/plain"
                            )
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                            
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("👈 Upload a document to get started")

# Footer
st.markdown("---")
st.markdown("**How to use:**")
st.markdown("1. Choose your target brand voice")
st.markdown("2. Upload a Word document")
st.markdown("3. Click 'Transform Content' to see the magic!")