from pathlib import Path
import pandas as pd
import random
from collections import defaultdict


def load_graph(csv_path):
    df = pd.read_csv(csv_path)
    graph = defaultdict(list)

    for _, row in df.iterrows():
        s, r, o = row["Subject"], row["Rel"], row["Object"]
        graph[s].append((r, o))
    return graph, df


def random_walk(graph, start_node, length):
    walk = []
    current = start_node

    for _ in range(length):
        if current not in graph or len(graph[current]) == 0:
            return None  # dead end
        r, next_node = random.choice(graph[current])
        walk.append((current, r, next_node))
        current = next_node

    return walk


def generate_n_walks(graph, df, hop_length, n_samples):
    walks = []
    all_nodes = df["Subject"].unique().tolist()

    while len(walks) < n_samples:
        start = random.choice(all_nodes)
        w = random_walk(graph, start, hop_length)
        if w:
            walks.append(w)
    return walks


def walks_to_rows(walks):
    """Flatten walks into rows with columns triple1_subject, triple1_rel, triple1_obj, ..."""
    max_len = max(len(w) for w in walks)
    rows = []

    for w in walks:
        row = {}
        for i, (s, r, o) in enumerate(w):
            row[f"s{i+1}"] = s
            row[f"r{i+1}"] = r
            row[f"o{i+1}"] = o
        rows.append(row)
    return rows


def main():
    desktop = Path.home() / "Desktop"
    input_csv = desktop / "matkg_extract_80k.csv"
    output_csv = desktop / "matkg_walks.csv"

    graph, df = load_graph(input_csv)

    output_rows = []

    # --- TRAINING WALKS ---
    for hops in [1, 2, 3]:
        walks = generate_n_walks(graph, df, hop_length=hops, n_samples=100)
        output_rows += walks_to_rows(walks)

    # --- EVALUATION WALKS ---
    for hops in [3, 4, 5]:
        walks = generate_n_walks(graph, df, hop_length=hops, n_samples=100)
        output_rows += walks_to_rows(walks)

    pd.DataFrame(output_rows).to_csv(output_csv, index=False)
    print(f"Saved all walks to: {output_csv}")


if __name__ == "__main__":
    main()
