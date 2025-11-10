import pandas as pd
import ast
import numpy as np

def recall_at_k(recommended, relevant, k):
    """Compute Recall@K for a single query."""
    recommended_top_k = recommended[:k]
    if not relevant:
        return 0.0
    hits = len(set(recommended_top_k) & set(relevant))
    return hits / len(relevant)

def mean_recall_at_k(ground_truth_df, predictions_df, k=5):
    """Compute Mean Recall@K across all queries."""
    recalls = []
    
    for _, row in ground_truth_df.iterrows():
        query = row['query']
        relevant = row['relevant_assessments']

        # find corresponding predictions
        pred_row = predictions_df[predictions_df['query'] == query]
        if pred_row.empty:
            recalls.append(0.0)
            continue
        
        recommended = pred_row.iloc[0]['predictions']
        recalls.append(recall_at_k(recommended, relevant, k))
    
    mean_recall = np.mean(recalls)
    return mean_recall, recalls

if __name__ == "__main__":
    # === INPUT FILES ===
    ground_truth_file = "Gen_AI Dataset.xlsx"  
    predictions_file = "predictions.csv" 

    # === LOAD FILES ===
    ground_truth_df =pd.read_excel( ground_truth_file, sheet_name="Train-Set")
    predictions_df = pd.read_csv(predictions_file)

    # parse stringified lists if necessary
    for df in [ground_truth_df, predictions_df]:
        for col in ['relevant_assessments', 'predictions']:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    for k in [1, 3, 5, 10]:
        mean_recall, recalls = mean_recall_at_k(ground_truth_df, predictions_df, k)
        print(f"Mean Recall@{k}: {mean_recall:.4f}")

