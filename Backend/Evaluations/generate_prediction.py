import pandas as pd
import requests
import time

API_URL = "http://127.0.0.1:8000/recommend" 
INPUT_EXCEL = "Gen_AI Dataset.xlsx"
OUTPUT_CSV = "predictions.csv"

def get_recommendations(query: str):
    """Send query to the recommendation API and get a list of URLs."""
    try:
        response = requests.post(API_URL, json={"query": query})
        if response.status_code == 200:
            data = response.json()
            recs = data.get("recommended_assessments", [])
            urls = [r.get("url", "") for r in recs if r.get("url")]
            return urls
        else:
            print(f"Error {response.status_code} for query: {query}")
            return []
    except Exception as e:
        print(f"Exception for query '{query}': {e}")
        return []

def main():
    df = pd.read_excel(INPUT_EXCEL, sheet_name = 'Test-Set')
    if "Query" not in df.columns:
        raise ValueError("Excel must have a column named 'query'")

    all_results = []

    for i, row in df.iterrows():
        query = row["Query"]
        print(f"\n🔍 Query {i+1}: {query}")

        recommendations = get_recommendations(query)
        if not recommendations:
            print("No recommendations found.")
            continue

        for j, rec in enumerate(recommendations, 1):
            print(f"   Query {i+1} Recommendation {j}: {rec}")
            all_results.append({
                "Query": query,
                "URL": rec
            })

        time.sleep(0.2)

    # Save results to CSV
    output_df = pd.DataFrame(all_results)
    output_df.to_csv(OUTPUT_CSV, index=False)

    print(f"\nSaved results to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
