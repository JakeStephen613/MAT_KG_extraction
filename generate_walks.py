import random
from collections import defaultdict
import pandas as pd
from pathlib import Path


## improvements I need to add: 
## 1) it should understand that when building the random walks, to substitute CHM-CHM with a better description of the relationship. 
## 2) change the criteria for how many of each walk 
## 3) prioritize walks with higher counts? 
## 4) need to ensure no repeats
## 5) We can require: At least 2 distinct relation types No more than N CHM-CHM in a row
## 6) do not go to any neighbor whose degree is within ±1 of the previous node’s degree


# Load triples from CSV and build an adjacency list graph (subject → list of (rel, object))
def load_graph(csv_path):
    df = pd.read_csv(csv_path)
    # graph maps each subject node to all outgoing (rel, object) pairs
    graph = defaultdict(list)

    # Iterate over each row and register edges in the graph
    for _, row in df.iterrows():
        s, r, o = row["Subject"], row["Rel"], row["Object"]
        graph[s].append((r, o))
    # Return both the graph and original DataFrame for later use
    return graph, df


# Perform a simple random walk with no repeated nodes (no cycles)
def random_walk_no_cycles(graph, start_node, length):
    """Return a length-hop walk with no repeated nodes, or None if stuck."""
    # Will store the sequence of (subject, relation, object) triples
    walk = []
    # Current node position in the walk
    current = start_node
    # Track visited nodes to prevent cycles
    visited = {current}

    # Attempt to extend the walk for the desired number of hops
    for _ in range(length):
        # Get all outgoing edges from current node
        neighbors = graph.get(current, [])
        # Filter neighbors to only those whose target node hasn’t been visited yet
        candidates = [(r, nxt) for (r, nxt) in neighbors if nxt not in visited]

        # If no unvisited neighbors remain, we can’t complete the requested length
        if not candidates:
            return None  # dead end before reaching requested length

        # Randomly choose one allowed edge (relation, next_node)
        r, next_node = random.choice(candidates)
        # Append the chosen triple to the walk
        walk.append((current, r, next_node))
        # Move to the next node
        current = next_node
        # Mark the new node as visited
        visited.add(current)

    # Return the fully constructed walk
    return walk


# Repeatedly generate random walks until we have n_samples or hit a max attempt limit
def generate_n_walks(graph, df, hop_length, n_samples, max_attempts_per_walk=100):
    walks = []
    # Candidates to start walks: all unique subjects
    all_nodes = df["Subject"].unique().tolist()

    # Count how many attempts we’ve made overall
    attempts = 0
    # Global cap on attempts to avoid infinite loops if long walks are rare
    max_attempts_total = n_samples * max_attempts_per_walk

    # Keep generating walks until we have enough or we max out attempts
    while len(walks) < n_samples and attempts < max_attempts_total:
        # Randomly choose a starting node
        start = random.choice(all_nodes)
        # Try to generate a no-cycle walk from this start
        w = random_walk_no_cycles(graph, start, hop_length)
        attempts += 1
        # Only keep successful walks (i.e., correct length)
        if w:
            walks.append(w)

    # Warn if we couldn’t generate the requested number of walks
    if len(walks) < n_samples:
        print(
            f"Warning: requested {n_samples} walks of length {hop_length}, "
            f"but only generated {len(walks)} after {attempts} attempts."
        )
    # Return all successfully generated walks
    return walks


# Convert a list of walks into row-wise dictionaries for DataFrame export
def walks_to_rows(walks):
    rows = []
    # Each walk becomes one row in the output table
    for w in walks:
        row = {}
        # For each hop, assign s_i, r_i, o_i columns
        for i, (s, r, o) in enumerate(w):
            row[f"s{i+1}"] = s
            row[f"r{i+1}"] = r
            row[f"o{i+1}"] = o
        rows.append(row)
    # Return list of row dicts
    return rows


# Main script: load graph, generate walks for train/eval, and save to CSV
def main():
    # Define paths to Desktop and input/output CSVs
    desktop = Path.home() / "Desktop"
    input_csv = desktop / "matkg_extract_80k.csv"
    output_csv = desktop / "matkg_walks_no_cycles.csv"

    # Build graph and get original DataFrame
    graph, df = load_graph(input_csv)

    # Aggregate all walk rows here
    output_rows = []

    # TRAINING: generate 100 walks each with 1, 2, and 3 hops
    for hops in [1, 2, 3]:
        walks = generate_n_walks(graph, df, hop_length=hops, n_samples=100)
        output_rows += walks_to_rows(walks)

    # EVAL: generate 100 walks each with 3, 4, and 5 hops
    for hops in [3, 4, 5]:
        walks = generate_n_walks(graph, df, hop_length=hops, n_samples=100)
        output_rows += walks_to_rows(walks)

    # Save all generated walks as a flat CSV table
    pd.DataFrame(output_rows).to_csv(output_csv, index=False)
    print(f"Saved walks (no cycles) to: {output_csv}")


# Run main() only if this file is executed as a script (not imported)
if __name__ == "__main__":
    main()
