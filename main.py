import streamlit as st
import requests
import json


BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = "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"  


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
                    {
                        "role": "user", 
                        "content": prompt
                     
                     }
                ]
            }
        )

        response.raise_for_status()
        data = response.json()

        
        if 'choices' in data and len(data['choices']) > 0:
            return data['choices'][0]['message']['content']
        else:
            st.error("Unexpected API response format.")
            return "⚠️ Sorry, I couldn't understand the response."

    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return "⚠️ Network error occurred. Please try again."
    except KeyError as e:
        st.error(f"Response parsing error: {e}")
        return "⚠️ Failed to parse response."
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return "⚠️ Something went wrong."


def main():
    st.title("🤖 AI Chat Assistant")
    st.markdown("Talk to an AI model powered by OpenRouter API")

    
    selected_model_name = st.selectbox(
        "Choose a model to chat with:",
        ("Mistral (Default)", "DeepSeek", "Gemini"),
        key="model_selector"
    )

    st.write(f"✅ Model: **{selected_model_name}**")

    
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
            model_id = "deepseek/deepseek-r1-0528-qwen3-8b:free"
        elif selected_model_name == "Gemini":
            model_id = "google/gemini-2.0-flash-exp:free"
        else:
            model_id = "mistralai/mistral-small-24b-instruct-2501:free"

        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = fetch_ai_response(BASE_URL, API_KEY, model_id, user_prompt)

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
