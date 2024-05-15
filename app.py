import streamlit as st
import os
import logging
import db_chat
import conf

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("chatbot.log"),  # Save logs to a file
        logging.StreamHandler()  # Print logs to stdout
    ]
)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="ML Playbook")
# Custom HTML for title with font customization
# Custom HTML for styled title
custom_title = """
<div style="
    font-family: Arial Black;
    font-size: 36px;
    color: white;
    background-color: #ff6347;
    padding: 10px;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
">
    ML Playbook Chatbot
</div>
"""
st.markdown(custom_title, unsafe_allow_html=True)
# Using a custom font

# Initialize chat agent using API key from conf if not already initialized
if "chat_agent" not in st.session_state:
    try:
        api_key = conf.api_key
        if api_key and ((api_key.startswith('sk-') and len(api_key) == 51) or (api_key.startswith('sk-proj-') and len(api_key) == 56)):
            st.session_state.chat_agent = db_chat.ChatAgent(api_key, conf.model)
            st.session_state.agent, st.session_state.memory = st.session_state.chat_agent.defineAgentMemory()
        else:
            chat_agent = None
            st.session_state.memory = None
            st.session_state.agent = None
    except Exception as e:
        logger.error(f"Error occurred while updating chat agent: {str(e)}")

def clear_chat_history():
    try:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
        #api_key = conf.api_key
        st.session_state.chat_agent = db_chat.ChatAgent(conf.api_key, conf.model)
        st.session_state.agent, st.session_state.memory = st.session_state.chat_agent.defineAgentMemory()
    except Exception as e:
        if """'NoneType' object has no attribute 'invoke'""" in str(e):
            st.error("Agent attribute not initialized due to missing api key. Please add it in config file and try again.")
            logger.error("Agent attribute not initialized.")

# App title

with st.sidebar:
    st.title('Chatbot')
    st.write('This chatbot is created using GPT 3.5 turbo.')
    st.write('To use your own OpenAI account, please configure your API key in the config file')
# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = db_chat.ask_query(st.session_state.agent, prompt, st.session_state.memory)
                logger.info(f"Response generated: {response}")
                placeholder = st.empty()
                full_response = ''
                for item in response["output"]:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
            except Exception as e:
                if "401" in str(e) and "Incorrect API key provided" in str(e):
                    st.error("Incorrect API key provided. Please check your API key and try again.")
                    logger.error("Incorrect API key provided.")
                    full_response = "Incorrect API key provided. Please check your API key and try again."
                elif "agent" not in st.session_state and st is not None:
                    st.error("Agent attribute not initialized due to missing api key. Please try again.")
                    logger.error("Agent attribute not initialized.")
                    full_response = "Agent attribute not initialized due to missing api key. Please try again."
                elif """'NoneType' object has no attribute 'invoke'""" in str(e):
                    st.error("Agent attribute not initialized due to missing api key. Please add it in config file and try again.")
                    logger.error("Agent attribute not initialized.")
                    full_response = "Agent attribute not initialized due to missing api key. Please add it in config file and try again."
                else:
                    st.error(f"Error occurred while generating response: {str(e)}")
                    logger.error(f"Error occurred while generating response: {str(e)}")
                    full_response = f"Error occurred: {str(e)}"
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)