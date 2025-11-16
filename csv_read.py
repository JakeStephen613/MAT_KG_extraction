from pathlib import Path
import pandas as pd

def main():
    desktop = Path.home() / "Desktop/RESEARCH"
    input_path = desktop / "matkg.csv"
    output_path = desktop / "matkg_chm_dsc_80k.csv"

    print(f"Reading input from: {input_path}")

    # Read CSV with headers: Subject, Object, Rel, Count
    df = pd.read_csv(input_path)

    # Sanity check that required columns exist
    required_cols = {"Subject", "Object", "Rel"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    # Filter to CHM-DSC relations
    df_chm_dsc = df[df["Rel"] == "CHM-DSC"]
    print(f"Total CHM-DSC rows found: {len(df_chm_dsc)}")

    # Take first 80,000
    df_chm_dsc_80k = df_chm_dsc.head(80000)
    print(f"Saving {len(df_chm_dsc_80k)} rows to: {output_path}")

    # Keep just the core columns
    df_chm_dsc_80k[["Subject", "Object", "Rel", "Count"]].to_csv(
        output_path, index=False
    )

    print("Done.")

if __name__ == "__main__":
    main()
