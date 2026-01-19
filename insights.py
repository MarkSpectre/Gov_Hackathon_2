def generate_insights(df):
    return {
        "top_state": df.groupby("state")["total_activity"].sum().idxmax(),
        "total_activity": int(df["total_activity"].sum())
    }
