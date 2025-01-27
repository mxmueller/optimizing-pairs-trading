from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint 
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

def find_cointegrated_pairs(price_matrix, pvalue_threshold=0.05):
    n = price_matrix.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    symbols = price_matrix.columns
    pairs = []
    results = []
    
    total_pairs = sum(range(n))
    with tqdm(total=total_pairs, desc="Analyzing pairs") as pbar:
        for i in range(n):
            for j in range(i+1, n):
                S1 = price_matrix[symbols[i]]
                S2 = price_matrix[symbols[j]]
                
                result = coint(S1, S2)
                score = result[0]
                pvalue = result[1]
                
                score_matrix[i, j] = score
                pvalue_matrix[i, j] = pvalue
                
                results.append({
                    'symbol1': symbols[i],
                    'symbol2': symbols[j],
                    'p_value': pvalue,
                    'score': score
                })
                
                if pvalue <= pvalue_threshold:
                    pairs.append((symbols[i], symbols[j]))
                    
                pbar.update(1)
    
    return score_matrix, pvalue_matrix, pairs, results

def analyze_pairs(price_matrix, pvalue_threshold=0.05):
    score_matrix, pvalue_matrix, pairs, results = find_cointegrated_pairs(
        price_matrix, 
        pvalue_threshold
    )
    
    print(f"\nAnalysis complete!")
    print(f"Found {len(pairs)} cointegrated pairs")
    print(f"Total pairs analyzed: {len(results)}")
    
    summary_df = pd.DataFrame(results)
    summary_df['is_cointegrated'] = summary_df['p_value'] <= pvalue_threshold
    
    return score_matrix, pvalue_matrix, pairs, summary_df

def plot_cointegration_heatmap(pvalue_matrix, symbols, max_pvalue=0.98):
    plt.figure(figsize=(12, 8))
    mask = (pvalue_matrix >= max_pvalue)
    
    sns.heatmap(
        pvalue_matrix, 
        xticklabels=symbols, 
        yticklabels=symbols, 
        cmap='RdYlGn_r',
        mask=mask
    )
    
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    plt.title('Cointegration p-values heatmap')
    plt.tight_layout()
    plt.show()