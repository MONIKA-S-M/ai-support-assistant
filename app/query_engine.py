from app.anomaly_detector import detect_weekly_resolution_anomalies
from app.data_loader import load_data


def get_ticket_count():
    df = load_data()
    return len(df)


def get_open_ticket_count():
    df = load_data()
    return int((df["status"].str.lower() == "open").sum())


def get_average_rating():
    df = load_data()
    return round(df["customer_rating"].mean(), 2)


def get_average_resolution_time():
    df = load_data()
    return round(df["resolution_time_hrs"].mean(), 2)


def get_tickets_by_category():
    df = load_data()
    return df["category"].value_counts().to_dict()

def get_average_rating_by_category(category):
    df = load_data()

    category_df = df[
        df["category"].str.lower() == category.lower()
    ]

    if category_df["customer_rating"].dropna().empty:
        return None

    return round(category_df["customer_rating"].mean(), 2)

def get_category_count(category):
    df = load_data()
    return int(
        (df["category"].str.lower() == category.lower()).sum()
    )


def get_tickets_by_priority():
    df = load_data()
    return df["priority"].value_counts().to_dict()

def get_priority_count(priority):
    df = load_data()
    return int(
        (df["priority"].str.lower() == priority.lower()).sum()
    )


def get_tickets_by_status():
    df = load_data()
    return df["status"].value_counts().to_dict()

def get_status_count(status):
    df = load_data()
    return int(
        (df["status"].str.lower() == status.lower()).sum()
    )

def get_critical_not_resolved_within(hours=12):
    df = load_data()

    critical = df[
        df["priority"].str.lower() == "critical"
    ]

    result = critical[
        (critical["status"].str.lower() != "resolved")
        | (critical["resolution_time_hrs"] > hours)
    ]

    return result[
        ["ticket_id", "status", "resolution_time_hrs"]
    ].to_dict(orient="records")

def get_top_agent_this_month():
    df = load_data()

    latest_date = df["created_at"].max()
    latest_month = latest_date.month
    latest_year = latest_date.year

    monthly = df[
        (df["created_at"].dt.month == latest_month)
        & (df["created_at"].dt.year == latest_year)
        & (df["status"].str.lower() == "resolved")
    ]

    if monthly.empty:
        return None

    return monthly["agent_id"].value_counts().idxmax()

def get_top_agent():
    df = load_data()
    resolved = df[df["status"].str.lower() == "resolved"]

    if resolved.empty:
        return None

    return resolved["agent_id"].value_counts().idxmax()

import ollama


def ask_llm(question):
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an AI support ticket assistant. "
                    "Understand the user's question about support tickets "
                    "and respond concisely. "
                    "Do not invent ticket statistics or business information. "
                    "Only use information provided in the question or available ticket data. "
                    "If the requested information is not available, say so clearly."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],
    )

    return response["message"]["content"]

def answer_question(question):
    question_lower = question.lower()

    # Handle clearly recognizable status queries deterministically
    if "resolved" in question_lower and any(
        phrase in question_lower
        for phrase in ["how many", "number of", "count"]
    ):
        return f"There are {get_status_count('resolved')} resolved tickets."

    if "open" in question_lower and any(
        phrase in question_lower
        for phrase in ["how many", "number of", "count"]
    ):
        return f"There are {get_status_count('open')} open tickets."

    if "escalated" in question_lower and any(
        phrase in question_lower
        for phrase in ["how many", "number of", "count"]
    ):
        return f"There are {get_status_count('escalated')} escalated tickets."

    if "this month" in question_lower and (
        "resolved the most" in question_lower
        or "top agent" in question_lower
        or "most tickets" in question_lower
    ):
        return f"The top resolving agent this month is {get_top_agent_this_month()}."

    if (
        "critical" in question_lower
        and "not resolved" in question_lower
        and "within 12 hours" in question_lower
    ):
        tickets = get_critical_not_resolved_within(12)

        return (
            f"Found {len(tickets)} Critical tickets not resolved within 12 hours: "
            + ", ".join(ticket["ticket_id"] for ticket in tickets)
        )

    if "average" in question_lower and "rating" in question_lower:
        for category in ["technical", "billing", "general"]:
            if category in question_lower:
                rating = get_average_rating_by_category(category)
                return (
                    f"The average customer rating for {category.title()} "
                    f"category tickets is {rating}."
                )

    if "anomal" in question_lower and "resolution time" in question_lower:
        anomalies = detect_weekly_resolution_anomalies()

        if anomalies:
            return (
                f"Found {len(anomalies)} resolution-time anomalies this week: "
                + ", ".join(
                    f"{item['ticket_id']} ({item['resolution_time_hrs']} hrs)"
                    for item in anomalies
                )
            )
    

        return "No resolution-time anomalies were detected this week."

    prompt = f"""
Classify the user's support-ticket question into exactly ONE of these intents.

INTENTS:
- open_tickets = asks specifically about tickets whose status is Open
- total_tickets = asks for the total/all/overall number of tickets
- average_rating = asks for average customer rating
- average_resolution = asks for average resolution time
- by_category = asks for ticket counts by category
- by_priority = asks for ticket counts by priority
- by_status = asks for ticket counts by status
- top_agent = asks which agent resolved the most tickets
- general = questions that do not clearly ask for one of the specific statistics or breakdowns above
Examples:
"How many tickets are currently open?" -> open_tickets
"How many open tickets do we have?" -> open_tickets
"How many tickets are there in total?" -> total_tickets
"Can you tell me the total number of support tickets?" -> total_tickets
"What is the overall ticket count?" -> total_tickets
"What is the average customer rating?" -> average_rating
"What is the average resolution time?" -> average_resolution
"How many tickets are in each category?" -> by_category
"Show tickets by priority" -> by_priority
"How many tickets are resolved?" -> by_status
"Which agent resolved the most tickets?" -> top_agent
"Can you help me understand the support tickets?" -> general
"Tell me about the support ticket system" -> general
"What can you tell me about these tickets?" -> general

IMPORTANT:
Return ONLY one intent name from the list above.
Do not explain your answer.

Question: {question}
"""
    if "critical" in question_lower and any(
        phrase in question_lower
        for phrase in ["how many", "number of", "count"]
    ):
        return f"There are {get_priority_count('Critical')} Critical tickets."


    if any(
        priority in question_lower
        for priority in ["critical", "high", "medium", "low"]
    ) and any(
        phrase in question_lower
        for phrase in ["how many", "number of", "count"]
    ):
        if "critical" in question_lower:
            return f"There are {get_priority_count('Critical')} Critical tickets."

        if "high" in question_lower:
            return f"There are {get_priority_count('High')} High priority tickets."

        if "medium" in question_lower:
            return f"There are {get_priority_count('Medium')} Medium priority tickets."

        if "low" in question_lower:
            return f"There are {get_priority_count('Low')} Low priority tickets."

    response = ask_llm(prompt).strip().lower()

    if "open_tickets" in response:
        return f"There are {get_open_ticket_count()} open tickets."

    if "total_tickets" in response:
        return f"There are {get_ticket_count()} tickets in total."

    if "average_rating" in response:
        return f"The average customer rating is {get_average_rating()}."

    if "average_resolution" in response:
        return (
            f"The average resolution time is "
            f"{get_average_resolution_time()} hours."
        )

    if "by_category" in response:
        if any(
            word in question_lower
            for word in ["technical", "billing", "general"]
        ):
            if "technical" in question_lower:
                return f"There are {get_category_count('Technical')} Technical tickets."

            if "billing" in question_lower:
                return f"There are {get_category_count('Billing')} Billing tickets."

            if "general" in question_lower:
                return f"There are {get_category_count('General')} General tickets."

        return f"Tickets by category: {get_tickets_by_category()}"

    if "by_priority" in response:
        if any(
            word in question_lower
            for word in ["critical", "high", "medium", "low"]
        ):
            if "critical" in question_lower:
                return f"There are {get_priority_count('Critical')} Critical tickets."

        if "high" in question_lower:
            return f"There are {get_priority_count('High')} High priority tickets."

        if "medium" in question_lower:
            return f"There are {get_priority_count('Medium')} Medium priority tickets."

        if "low" in question_lower:
            return f"There are {get_priority_count('Low')} Low priority tickets."

        return f"Tickets by priority: {get_tickets_by_priority()}"

    if "by_status" in response:
        if any(
            word in question_lower
            for word in ["status", "resolved", "open", "escalated"]
        ):
            if "resolved" in question_lower:
                return f"There are {get_status_count('resolved')} resolved tickets."

            if "open" in question_lower:
                return f"There are {get_status_count('open')} open tickets."

            if "escalated" in question_lower:
                return f"There are {get_status_count('escalated')} escalated tickets."

            return f"Tickets by status: {get_tickets_by_status()}"

    return ask_llm(question)
    return f"Tickets by status: {get_tickets_by_status()}"

    if "top_agent" in response and "this month" in question_lower:
        return f"The top resolving agent this month is {get_top_agent_this_month()}."

    if "top_agent" in response:
        return f"The top resolving agent is {get_top_agent()}"

    return ask_llm(question)