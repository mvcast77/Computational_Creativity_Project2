# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the test server (to be replaced by a Large Language Model)

    ```
    $ python api.py
    ```

3. In another window, run the app

   ```
   $ streamlit run streamlit_app.py
   ```

----------------

To test if user input can be presented into the output on the page, all you need to do is comment out in streamlit_app.py:

1) All of Section 3: Function: Call LLM

2) lines 108 - 109:

#with st.spinner("Generating outline..."):
        #     result = call_llm(prompt)

3) And change line 112 from    st.markdown(result) --->    st.markdown(combined_text)

