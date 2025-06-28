import streamlit as st
from docx import Document
import openai

# Configure OpenAI API key
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_docx_text(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def evaluate_prompt(contract_text, prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a legal analyst evaluating contract clauses."},
            {"role": "user", "content": f"Contract:\n{contract_text}\n\nCheck this:\n{prompt}"}
        ],
        temperature=0,
    )
    return response["choices"][0]["message"]["content"]

st.title("📄 Contract Checker Agent")
st.write("Upload a prompt file and a contract document to run automated checks.")

with st.form("file_form"):
    prompts_doc = st.file_uploader("1️⃣ Upload the Prompt Document (.docx)", type="docx")
    contract_doc = st.file_uploader("2️⃣ Upload the Contract Document (.docx or .txt)", type=["docx", "txt"])
    submitted = st.form_submit_button("✅ Run Checks")

if submitted:
    if not prompts_doc or not contract_doc:
        st.error("Please upload both the prompt and contract documents.")
    else:
        with st.spinner("Reading documents..."):
            prompt_texts = extract_docx_text(prompts_doc).splitlines()
            prompt_texts = [p.strip() for p in prompt_texts if p.strip()]
            contract_text = (
                extract_docx_text(contract_doc)
                if contract_doc.name.endswith(".docx")
                else contract_doc.read().decode("utf-8")
            )

        st.info(f"Running {len(prompt_texts)} checks on the contract. This might take a moment...")

        results = []
        for i, prompt in enumerate(prompt_texts, start=1):
            with st.spinner(f"Processing prompt {i}/{len(prompt_texts)}: {prompt}"):
                result = evaluate_prompt(contract_text, prompt)
                results.append((prompt, result))

        st.success("✅ All prompts processed!")

        for prompt, answer in results:
            st.markdown(f"**🔹 Prompt:** {prompt}")
            st.markdown(f"**📘 Result:** {answer}")
            st.markdown("---")