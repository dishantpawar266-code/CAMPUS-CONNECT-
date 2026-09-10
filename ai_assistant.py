import os
import streamlit as st

def show_ai_assistant_page():
    st.title("🤖 CampusConnect AI Assistant")
    st.caption("Your intelligent academic companion powered by Ollama.")
    st.markdown("---")

    # 1. Check if 'ollama' library is installed
    try:
        import ollama
    except ImportError:
        st.error("❌ **Error:** The `ollama` package is not installed in your Python environment.")
        st.info("💡 **Solution:** Open your terminal/command prompt and run this command: \n```bash\npip install ollama\n```")
        return

    # 2. Initialize Chat History
    if "ai_messages" not in st.session_state:
        st.session_state["ai_messages"] = [
            {
                "role": "assistant",
                "content": "Hello! I am your AI academic assistant running locally via Ollama. How can I help you with your coursework, coding doubts, or technical projects today?"
            }
        ]

    # 3. Display Chat History
    for message in st.session_state["ai_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 4. Handle User Input
    if prompt := st.chat_input("Ask a question about programming, mathematics, or project concepts..."):
        st.session_state["ai_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    formatted_messages = [
                        {"role": m["role"], "content": m["content"]} for m in st.session_state["ai_messages"]
                    ]
                    
                    # Call Ollama local model with the correct name
                    response = ollama.chat(
                        model="llama3.2:3b",
                        messages=formatted_messages,
                    )
                    response_text = response['message']['content']
                except Exception as e:
                    response_text = f"❌ **Ollama Connection Error:** Make sure Ollama is running locally (`ollama serve`). Details: {e}"
                
                st.markdown(response_text)

        st.session_state["ai_messages"].append({"role": "assistant", "content": response_text})