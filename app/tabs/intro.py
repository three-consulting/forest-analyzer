import streamlit as st

def tab():
    st.header("SQL queries with Natural Language Processing")

    st.markdown("Thank you for joining us today! We are Three Point Consulting and we have prepaired a little game for you to play today. We'll tell you more about it shortly, but let's kick things off with a short introduction to Natural Language Processing or NLP in short.")

    st.subheader("A short introduction to NLP")
    st.markdown("NLP is a branch of artificial intelligence that focuses on enabling computers to understand, interpret, and generate human language. Many of you may have experienced this technology with OpenAI's ChatGPT. In fact, this game is powered by the same language model as the ChatGPT+, which is GPT-4. NLP's applications include topics, such as chatbots, semantic search, machine translation, document- and sentiment analysis. We don't want to bother you with the mathematical or technical details of language models or NLP in general, but we are more than happy to discuss these topics if you are interested so don't be afraid to ask!")
    
    st.subheader("SQL and Geospatial data")
    st.markdown("You might also be pretty well acquinted with SQL. If you are not, SQL is a declarative language which allows user to search (or query) data from databases. Today we are going to introduce you to quering data using only natural language, so no more annoying joins, subqueries, etc!")
    
    st.subheader("Your task")
    st.markdown("We are running a Supabase instance locally where different geospatial forest data is stored. We are running a Supabase instance locally where different geospatial forest data from Finland Proper (Varsinais-Suomi) is stored. Your task is to query the database using natural language (english). You are supposed search (or prompt) the largest forest polygon from our database using only natural language. The SQL query which is created from the prompt is displayed on the exercise page.")