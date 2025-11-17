from pathlib import Path
import pandas as pd


## points to improve: 
## 1) figure out the most relevant topics and relatinoships for KG extraction
## 2) ....

# Main entry point: extract a filtered subset of triples from matkg.csv
def main():
    # Build paths to Desktop and input/output CSVs
    desktop = Path.home() / "Desktop"
    input_path = desktop / "full_kg.csv"
    output_path = desktop / "matkg_extract_80k.csv"

    # Log which file we're reading
    print(f"Reading input from: {input_path}")

    # Read CSV with headers: Subject, Object, Rel, Count
    df = pd.read_csv(input_path)

    # Define which columns we expect to see
    required_cols = {"Subject", "Object", "Rel"}
    # Compute any missing required columns
    missing = required_cols - set(df.columns)
    # Fail fast if columns aren’t present
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Filter rows to keep only CHM-DSC OR CHM-CHM relations
    df_filters = df[(df["Rel"] == "CHM-DSC") | (df["Rel"] == "CHM-CHM")]
    # Log how many rows matched the filter
    print(f"Total CHM-DSC + CHM-CHM rows found: {len(df_filters)}")

    # Take the first 80,000 filtered rows
    df_extract_80k = df_filters.head(80000)
    # Log how many rows we’re about to save
    print(f"Saving {len(df_extract_80k)} rows to: {output_path}")

    # Save only the core triple columns (plus Count) to a new CSV
    df_extract_80k[["Subject", "Object", "Rel", "Count"]].to_csv(
        output_path, index=False
    )

    # Indicate completion
    print("Done.")

# Run main() only if this file is executed as a script (not imported)
if __name__ == "__main__":
    main()
