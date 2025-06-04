import streamlit as st
import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY =  os.getenv("API_KEY")

if "messages" not in st.session_state:
    st.session_state.messages = []


def fetch_ai_response(base_url, api_key, model, prompt):
    try:
        response = requests.post(
            url=f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",         
            },
            json={
                "model": model,
                "messages": st.session_state.messages + [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        response.raise_for_status()
        data = response.json()

        
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            st.error("Unexpected API response format.")
            return "Sorry, I couldn't understand the response."

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return "Network error occurred. Please try again."
    except KeyError as e:
        st.error(f"Response parsing error: {e}")
        return "Failed to parse response."
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return "Something went wrong."


def main():
    st.title("🤖 AI Chat Assistant")
    st.markdown("Talk to an AI model powered by OpenRouter API")

    
    selected_model_name = st.selectbox(
        "Choose a model to chat with:",
        ("Mistral (Default)", "DeepSeek", "Gemini"),
        key="model_selector"
    )

    st.write(f"✅ You selected: **{selected_model_name}**")

    
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    
    user_prompt = st.chat_input("Type your message here...")

    if user_prompt:
        
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)

        
        if selected_model_name == "DeepSeek":
            model_id = os.getenv("DEEP_SEEK_MODEL")
        elif selected_model_name == "Gemini":
            model_id = os.getenv("GEMINI_MODEL")
        else:
            model_id = os.getenv("MISTRAL_MODEL")

        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = fetch_ai_response(BASE_URL, API_KEY, model_id, user_prompt)

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()