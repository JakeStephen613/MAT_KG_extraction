import random
from collections import defaultdict
import pandas as pd
from pathlib import Path


## improvements I need to add: 
## 1) it should understand that when building the random walks, to substitute CHM-CHM with a better description of the relationship. 
## 2) change the criteria for how many of each walk 
## 3) prioritize walks with higher counts? 
## 4) need to ensure no repeats


def load_graph(csv_path):
    df = pd.read_csv(csv_path)
    graph = defaultdict(list)

    for _, row in df.iterrows():
        s, r, o = row["Subject"], row["Rel"], row["Object"]
        graph[s].append((r, o))
    return graph, df


def random_walk_no_cycles(graph, start_node, length):
    """Return a length-hop walk with no repeated nodes, or None if stuck."""
    walk = []
    current = start_node
    visited = {current}

    for _ in range(length):
        neighbors = graph.get(current, [])
        # filter to neighbors we haven't visited yet
        candidates = [(r, nxt) for (r, nxt) in neighbors if nxt not in visited]

        if not candidates:
            return None  # dead end before reaching requested length

        r, next_node = random.choice(candidates)
        walk.append((current, r, next_node))
        current = next_node
        visited.add(current)

    return walk


def generate_n_walks(graph, df, hop_length, n_samples, max_attempts_per_walk=100):
    walks = []
    all_nodes = df["Subject"].unique().tolist()

    attempts = 0
    max_attempts_total = n_samples * max_attempts_per_walk

    while len(walks) < n_samples and attempts < max_attempts_total:
        start = random.choice(all_nodes)
        w = random_walk_no_cycles(graph, start, hop_length)
        attempts += 1
        if w:
            walks.append(w)

    if len(walks) < n_samples:
        print(
            f"Warning: requested {n_samples} walks of length {hop_length}, "
            f"but only generated {len(walks)} after {attempts} attempts."
        )
    return walks


def walks_to_rows(walks):
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
    output_csv = desktop / "matkg_walks_no_cycles.csv"

    graph, df = load_graph(input_csv)

    output_rows = []

    # TRAINING: 1, 2, 3 hops
    for hops in [1, 2, 3]:
        walks = generate_n_walks(graph, df, hop_length=hops, n_samples=100)
        output_rows += walks_to_rows(walks)

    # EVAL: 3, 4, 5 hops
    for hops in [3, 4, 5]:
        walks = generate_n_walks(graph, df, hop_length=hops, n_samples=100)
        output_rows += walks_to_rows(walks)

    pd.DataFrame(output_rows).to_csv(output_csv, index=False)
    print(f"Saved walks (no cycles) to: {output_csv}")


if __name__ == "__main__":
    main()

