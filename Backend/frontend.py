import streamlit as st
import requests

st.set_page_config(page_title="Smart Course Recommender", page_icon="🎓", layout="centered")

st.title("🎓 Smart Career Course Recommender")
st.markdown("Find the perfect balance of **technical** and **interpersonal** courses for your goals.")

query = st.text_area("Describe your goal or interest:", placeholder="e.g., I want to become a Java developer and improve my communication.")

if st.button("Get Recommendations"):
    if query.strip():
        with st.spinner("Fetching recommendations..."):
            response = requests.post(
                "http://127.0.0.1:8000/recommend",
                json={"query": query}
            )
            if response.status_code == 200:
                data = response.json()
                print(data)
                st.success("Here are your personalized course recommendations:")

                for i, rec in enumerate(data.get("recommended_assessments", []), start=1):
                    st.markdown(f"### {i}. {rec['assessment_name']}")
                    st.markdown(f"**Category:** {rec.get('category', 'N/A')}")
                    st.write(rec['description'])
                    st.divider()
            else:
                st.error("Error: Could not fetch recommendations.")
    else:
        st.warning("Please enter a query first.")
