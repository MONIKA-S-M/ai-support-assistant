import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000"


st.set_page_config(
    page_title="AI Support Ticket Assistant",
    page_icon="🎫",
    layout="wide",
)

st.title("AI Support Ticket Assistant")
st.write("Ask questions about support tickets using natural language.")


question = st.text_input(
    "Enter your question",
    placeholder="Example: How many tickets are currently open?",
)


if st.button("Ask"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        try:
            response = requests.get(
                f"{API_URL}/ask",
                params={"question": question},
                timeout=120,
            )

            if response.status_code == 200:
                result = response.json()

                st.subheader("Answer")
                st.write(result["answer"])
            else:
                st.error(f"API error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to API: {e}")

st.divider()

st.subheader("Detected Anomalies")

if st.button("Check Anomalies"):
    try:
        response = requests.get(
            f"{API_URL}/anomalies",
            timeout=120,
        )

        if response.status_code == 200:
            data = response.json()

            st.write(f"**Total anomalies detected: {data['count']}**")

            if data["anomalies"]:
                for anomaly in data["anomalies"]:
                    st.warning(
                        f"**{anomaly['ticket_id']} — {anomaly['type']}**\n\n"
                        f"{anomaly['details']}"
                    )
            else:
                st.success("No anomalies detected.")
        else:
            st.error(f"API error: {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to API: {e}")