import streamlit as st
from docx import Document
from openai import OpenAI
import time
from openai import RateLimitError

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def extract_docx_text(uploaded_file):
    doc = Document(uploaded_file)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def evaluate_prompt(contract_text, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are a legal analyst evaluating contract clauses."},
                {"role": "user", "content": f"Contract:\n{contract_text}\n\nCheck this:\n{prompt}"}
            ],
            temperature=0,
        )
        return response.choices[0].message.content
    except RateLimitError:
        time.sleep(5)
        return "❗ Rate limit reached. Please wait and try again later."

def evaluate_all_prompts(contract_text, prompt_list):
    joined_prompts = "\\n".join([f"- {p}" for p in prompt_list])
    message = f"""You will now receive a contract. Then check the following items:
{joined_prompts}

Here is the contract:
{contract_text}
"""

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
                time.sleep(1.2)  # delay between API calls

        st.success("✅ All prompts processed!")

        for prompt, answer in results:
            st.markdown(f"**🔹 Prompt:** {prompt}")
            st.markdown(f"**📘 Result:** {answer}")
            st.markdown("---")
