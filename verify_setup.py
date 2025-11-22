try:
    import streamlit
    import langchain
    import langchain_openai
    import pypdf
    import faiss
    print("All dependencies installed successfully!")
except ImportError as e:
    print(f"Import Error: {e}")
