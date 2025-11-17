from pathlib import Path
from collections import Counter
import pandas as pd


# Load the full KG CSV and sanity check columns
def load_kg():
    desktop = Path.home() / "Desktop"
    input_path = desktop / "matkg.csv"
    print(f"Reading KG from: {input_path}")

    df = pd.read_csv(input_path)

    required_cols = {"Subject", "Object", "Rel", "Count"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    print(f"Total rows (triples, including repeats): {len(df)}")
    return df


# Basic counts: entities, relations, etc.
def basic_stats(df: pd.DataFrame):
    n_subjects = df["Subject"].nunique()
    n_objects = df["Object"].nunique()
    entities = pd.unique(df[["Subject", "Object"]].values.ravel("K"))
    n_entities = len(entities)
    n_rels = df["Rel"].nunique()

    print("\n=== BASIC STATS ===")
    print(f"Unique subjects: {n_subjects}")
    print(f"Unique objects: {n_objects}")
    print(f"Unique entities (subject ∪ object): {n_entities}")
    print(f"Unique relation types: {n_rels}")


# Distribution of relation types and domain prefixes
def relation_stats(df: pd.DataFrame, out_dir: Path):
    print("\n=== RELATION TYPE COUNTS ===")
    rel_counts = df["Rel"].value_counts()
    print(rel_counts.head(20))

    rel_counts.to_csv(out_dir / "rel_counts.csv")

    # Split Rel like "CHM-DSC" into left and right domain prefixes
    rel_split = df["Rel"].str.split("-", expand=True)
    if rel_split.shape[1] == 2:
        df["Rel_left"] = rel_split[0]
        df["Rel_right"] = rel_split[1]

        left_counts = df["Rel_left"].value_counts()
        right_counts = df["Rel_right"].value_counts()

        print("\n=== RELATION LEFT DOMAIN COUNTS (e.g. CHM / DSC / APL) ===")
        print(left_counts)

        print("\n=== RELATION RIGHT DOMAIN COUNTS ===")
        print(right_counts)

        left_counts.to_csv(out_dir / "rel_left_domain_counts.csv")
        right_counts.to_csv(out_dir / "rel_right_domain_counts.csv")
    else:
        print("\nRel column does not look like PREFIX-PREFIX, skipping domain split.")


# Find duplicate triples and their frequencies
def duplicate_triple_stats(df: pd.DataFrame, out_dir: Path):
    print("\n=== DUPLICATE TRIPLES (S, R, O) ===")
    triple_counts = (
        df.groupby(["Subject", "Rel", "Object"])
        .agg(total_rows=("Count", "size"), total_count=("Count", "sum"))
        .reset_index()
    )

    # Triples that appear more than once in the CSV
    duplicates = triple_counts[triple_counts["total_rows"] > 1]
    n_duplicates = len(duplicates)
    print(f"Triples with duplicates (same S,R,O): {n_duplicates}")

    # Save all triple frequencies to CSV
    triple_counts.sort_values("total_count", ascending=False).to_csv(
        out_dir / "triple_counts.csv", index=False
    )

    # Show top 10 strongest triples by Count
    print("\nTop 10 triples by total Count:")
    print(
        triple_counts.sort_values("total_count", ascending=False)
        .head(10)
        .to_string(index=False)
    )


# Degree stats: which nodes are hubs (high out-degree / in-degree)
def degree_stats(df: pd.DataFrame, out_dir: Path, top_n: int = 20):
    print("\n=== DEGREE STATS (HUB ENTITIES) ===")

    # Out-degree: how many times each entity appears as Subject
    out_deg = df.groupby("Subject").size().rename("out_degree")
    # In-degree: how many times each entity appears as Object
    in_deg = df.groupby("Object").size().rename("in_degree")

    degree_df = (
        pd.concat([out_deg, in_deg], axis=1)
        .fillna(0)
        .astype(int)
        .reset_index()
        .rename(columns={"index": "Entity"})
    )
    degree_df["total_degree"] = degree_df["out_degree"] + degree_df["in_degree"]

    # Save full degree table
    degree_df.sort_values("total_degree", ascending=False).to_csv(
        out_dir / "entity_degrees.csv", index=False
    )

    print(f"Top {top_n} entities by total_degree:")
    print(
        degree_df.sort_values("total_degree", ascending=False)
        .head(top_n)
        .to_string(index=False)
    )


# Topic-ish stats for a key relation type (e.g., CHM-DSC properties)
def chm_dsc_topic_stats(df: pd.DataFrame, out_dir: Path, top_n: int = 30):
    print("\n=== CHM-DSC TOPICS (CHM-DSC RELATION ONLY) ===")

    if "CHM-DSC" not in set(df["Rel"]):
        print("No CHM-DSC relations found, skipping.")
        return

    chm_dsc = df[df["Rel"] == "CHM-DSC"].copy()

    # Which chemical entities show up most often?
    top_subjects = chm_dsc["Subject"].value_counts().head(top_n)
    # Which descriptors/properties show up most often?
    top_objects = chm_dsc["Object"].value_counts().head(top_n)

    print("\nTop CHM-DSC Subjects (chemicals):")
    print(top_subjects)

    print("\nTop CHM-DSC Objects (descriptors/properties):")
    print(top_objects)

    top_subjects.to_csv(out_dir / "chm_dsc_top_subjects.csv")
    top_objects.to_csv(out_dir / "chm_dsc_top_objects.csv")


# Very rough "component" awareness: count how many entities are isolated
def connectivity_hint(df: pd.DataFrame):
    print("\n=== CONNECTIVITY HINT ===")

    # Entities seen anywhere
    entities = pd.unique(df[["Subject", "Object"]].values.ravel("K"))
    entity_set = set(entities)

    # Entities that appear at least once as both Subject and Object
    subj_set = set(df["Subject"].unique())
    obj_set = set(df["Object"].unique())
    both = subj_set & obj_set

    print(f"Entities seen only as Subject: {len(subj_set - obj_set)}")
    print(f"Entities seen only as Object: {len(obj_set - subj_set)}")
    print(f"Entities seen as BOTH Subject and Object: {len(both)}")
    print(f"Total unique entities: {len(entity_set)}")


def main():
    # Output directory: Desktop / MAT_KG_analysis_results
    desktop = Path.home() / "Desktop"
    out_dir = desktop / "MATKG_analysis_results"
    out_dir.mkdir(exist_ok=True)

    df = load_kg()

    basic_stats(df)
    relation_stats(df, out_dir)
    duplicate_triple_stats(df, out_dir)
    degree_stats(df, out_dir, top_n=30)
    chm_dsc_topic_stats(df, out_dir, top_n=30)
    connectivity_hint(df)

    print(f"\nAnalysis complete. CSV outputs written to: {out_dir}")


if __name__ == "__main__":
    main()
