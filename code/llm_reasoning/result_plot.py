import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Data for LLM table
data_llm = {
    'Model Name': ['Gemini 1.5 Flash', 'Meta Llama 3 8B', 'Mixtral-8x7B Instruct', 'GPT-4o', 'Claude 3.5 Sonnet'],
    'Prompt 1': ['1/5', '1/5', '5/5', '2/5', '5/5'],
    'Prompt 2': ['4/5', '5/5', '5/5', '5/5', '5/5'],
    'Prompt 3': ['2/5', '2/5', '2/5', '5/5', '5/5'],
    'Prompt 4a': ['2/5', '0/5', '4/5', '4/5', '5/5'],
    'Prompt 4b': ['4/5', '4/5', '4/5', '5/5', '5/5'],
    'Prompt 4c': ['5/5', '3/5', '5/5', '5/5', '5/5'],
    'Prompt 5': ['2/5', '2/5', '2/5', '3/5', '5/5']
}

# Data for LLM+Ontology table
data_llm_ontology = {
    'Model Name': ['Gemini 1.5 Flash', 'Meta Llama 3 8B', 'Mixtral-8x7B Instruct', 'GPT-4o', 'Claude 3.5 Sonnet'],
    'Prompt 1': ['0/5', '0/5', '4/5', '1/5', '5/5'],
    'Prompt 2': ['5/5', '4/5', '5/5', '5/5', '5/5'],
    'Prompt 3': ['4/5', '4/5', '4/5', '5/5', '5/5'],
    'Prompt 4a': ['5/5', '3/5', '4/5', '4/5', '5/5'],
    'Prompt 4b': ['5/5', '5/5', '5/5', '5/5', '5/5'],
    'Prompt 4c': ['5/5', '5/5', '5/5', '5/5', '5/5'],
    'Prompt 5': ['1/5', '1/5', '1/5', '1/5', '5/5']
}

# Data for LLM table and LLM+Ontology table remain the same

def create_heatmap(data, title):
    df = pd.DataFrame(data)
    df.set_index('Model Name', inplace=True)

    # Convert fractions to floats for coloring
    df_float = df.applymap(lambda x: eval(x) if isinstance(x, str) else x)

    plt.figure(figsize=(12, 6))
    cmap = plt.cm.PuBu
    ax = sns.heatmap(df_float, cmap=cmap, cbar=False, linewidths=0.5, linecolor='white')

    plt.title(title, fontsize=16, pad=20)
    plt.ylabel('')
    plt.xlabel('')

    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')

    # Add text annotations for all cells
    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            if df.iloc[i, j] in ['0/5', '1/5', '2/5', '3/5', '4/5', '5/5']:
                cell_value = df_float.iloc[i, j]
                color = cmap(cell_value)
                text_color = 'white' if np.mean(color[:3]) < 0.5 else 'black'

                text = ax.text(j + 0.5, i + 0.5, df.iloc[i, j],
                               ha="center", va="center", color=text_color,
                               fontweight='bold')

    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f"{title.replace(' ', '_')}.png", dpi=300, bbox_inches='tight')
    plt.close()


# Create heatmaps
create_heatmap(data_llm, "plots/Final Scores for the LLM type prompt")
create_heatmap(data_llm_ontology, "plots/Final Scores for the LLM+Ontology type prompt")
