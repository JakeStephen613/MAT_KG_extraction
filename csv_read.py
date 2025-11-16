from pathlib import Path
import pandas as pd

def main():
    desktop = Path.home() / "Desktop"
    input_path = desktop / "matkg.csv"
    output_path = desktop / "matkg_extract_80k.csv"

    print(f"Reading input from: {input_path}")

    # Read CSV with headers: Subject, Object, Rel, Count
    df = pd.read_csv(input_path)

    # Sanity check that required columns exist
    required_cols = {"Subject", "Object", "Rel"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Filter to CHM-DSC OR CHM-CHM
    df_filters = df[(df["Rel"] == "CHM-DSC") | (df["Rel"] == "CHM-CHM")]
    print(f"Total CHM-DSC + CHM-CHM rows found: {len(df_filters)}")

    # Take first 80,000 rows
    df_extract_80k = df_filters.head(80000)
    print(f"Saving {len(df_extract_80k)} rows to: {output_path}")

    # Save selected columns
    df_extract_80k[["Subject", "Object", "Rel", "Count"]].to_csv(
        output_path, index=False
    )

    print("Done.")

if __name__ == "__main__":
    main()
