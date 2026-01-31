"""Uploaded file handling utilities."""

import shutil
from pathlib import Path
from typing import Any, List
import pandas as pd
from data_analysis.system.utils.paths import OUTPUT_DATA_DIR


def save_uploaded_files(uploaded_files: List[Any]) -> None:
    """Save uploaded files to current_analysis/data/.
    
    Converts Excel files to CSV format automatically.
    
    Args:
        uploaded_files: List of Streamlit UploadedFile objects.
    """
    # Clear existing data in current_analysis/data/
    if OUTPUT_DATA_DIR.exists():
        shutil.rmtree(OUTPUT_DATA_DIR)
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name

        if file_name.endswith(('.xlsx', '.xls')):
            # Convert Excel to CSV
            df = pd.read_excel(uploaded_file)
            csv_name = file_name.rsplit('.', 1)[0] + '.csv'
            csv_path = OUTPUT_DATA_DIR / csv_name
            df.to_csv(csv_path, index=False)
        else:
            # Save CSV directly
            csv_path = OUTPUT_DATA_DIR / file_name
            csv_path.write_bytes(uploaded_file.getvalue())