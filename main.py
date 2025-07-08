
import streamlit as st
from src.agent import graph  # Import your compiled LangGraph graph
import uuid
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage # Keep SystemMessage for general use if needed, but not strictly for summary

def main():
    st.set_page_config(page_title="LangGraph Chatbot", layout="centered")
    st.title("LangGraph Chatbot Demo")

    # Initialize session state for messages and thread_id
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "thread_id" not in st.session_state:
        st.session_state["thread_id"] = str(uuid.uuid4())

    # Display chat history
    for msg in st.session_state["messages"]:
        # Using 'st.chat_message' automatically handles the role styling
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Handle new user input
    if user_input := st.chat_input("Type your message here...", key="chat_input"):
        # 1. Add user message to session_state
        st.session_state["messages"].append({"role": "user", "content": user_input})

        # 2. Display the newly submitted user message immediately
        with st.chat_message("user"):
            st.write(user_input)

        # 3. Prepare for assistant's response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()  # Placeholder for streaming
            full_response = ""

            # Convert session state dictionaries to LangChain message objects
            langgraph_messages = []
            for msg_dict in st.session_state["messages"]:
                if msg_dict["role"] == "user":
                    langgraph_messages.append(HumanMessage(content=msg_dict["content"]))
                elif msg_dict["role"] == "assistant":
                    langgraph_messages.append(AIMessage(content=msg_dict["content"]))

            try:
                chat_config = {"configurable": {"thread_id": st.session_state["thread_id"]}}

                # Call the graph with the current conversation history
                for event in graph.stream({"messages": langgraph_messages}, config=chat_config, stream_mode="values"):
                    if "messages" in event and event["messages"]:
                        latest_msg_obj = event["messages"][-1] # Get the latest message object

                        # Only process AIMessage for display to the user
                        if isinstance(latest_msg_obj, AIMessage):
                            chunk = latest_msg_obj.content
                            full_response += chunk
                            message_placeholder.write(full_response + "▌") # Blinking cursor
                
                # 4. After streaming, write the final response and add to session state
                message_placeholder.write(full_response)
                st.session_state["messages"].append({"role": "assistant", "content": full_response})

            except Exception as e:
                st.error(f"An error occurred: {e}")
                message_placeholder.write(f"An error occurred: {e}") # Display error in placeholder

        # 5. Rerun the app to update chat history and clear input
        st.rerun()

if __name__ == "__main__":
    main()
