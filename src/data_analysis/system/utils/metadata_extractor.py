"""Metadata extraction utilities."""


import json
from pathlib import Path
from typing import Any, Dict
import pandas as pd
from data_analysis.crew.models.metadata_models import (
    ColumnMetadataModel,
    RawSchemaMetadataModel,
    RelationshipModel,
    TableMetadataModel,
)
from data_analysis.system.utils.paths import (
    OUTPUT_SCRIPT_DIR,
    RAW_SCHEMA_METADATA_FILE,
    OUTPUT_DATA_DIR,
)


def extract_csv_schema_metadata(csv_folder: Path = None) -> RawSchemaMetadataModel:
    """Extract raw schema metadata from CSV files.
    
    Reads all CSV files and extracts technical metadata including
    types, statistics, primary keys, foreign keys, and relationships.
    
    Args:
        csv_folder: Path to CSV folder. Uses global config if None.
    
    Returns:
        RawSchemaMetadataModel with all extracted metadata.
    """
    if csv_folder is None:
        csv_folder = OUTPUT_DATA_DIR

    csv_files = sorted(csv_folder.glob("*.csv"))
    tables: Dict[str, TableMetadataModel] = {}

    for csv_file in csv_files:
        table_name = csv_file.stem

        try:
            df = pd.read_csv(csv_file)
        except Exception:
            tables[table_name] = TableMetadataModel(
                row_count=0,
                columns={},
                primary_key=None,
                foreign_keys=[],
            )
            continue

        columns_metadata: Dict[str, ColumnMetadataModel] = {}
        primary_key = None
        row_count = len(df)

        for column in df.columns:
            series = df[column]
            unique_count = int(series.nunique(dropna=True))
            null_count = int(series.isnull().sum())
            is_unique = unique_count == row_count
            is_not_null = null_count == 0

            column_data: Dict[str, Any] = {
                "type": str(series.dtype),
                "nullable": not is_not_null,
                "unique": is_unique,
                "null_count": null_count,
                "unique_count": unique_count,
            }

            # Add numeric statistics
            if pd.api.types.is_numeric_dtype(series):
                column_data.update({
                    "min": float(series.min()) if pd.notna(series.min()) else None,
                    "max": float(series.max()) if pd.notna(series.max()) else None,
                    "mean": float(series.mean()) if pd.notna(series.mean()) else None,
                    "std": float(series.std()) if pd.notna(series.std()) else None,
                })

            columns_metadata[column] = ColumnMetadataModel(**column_data)

            # Detect primary key (unique, not null, contains "id")
            if primary_key is None and is_unique and is_not_null and "id" in column.lower():
                primary_key = column

        tables[table_name] = TableMetadataModel(
            row_count=row_count,
            columns=columns_metadata,
            primary_key=primary_key,
            foreign_keys=[],
        )

    # Detect relationships based on column naming
    relationships: list[RelationshipModel] = []
    table_names = list(tables.keys())

    for table_name, table_data in tables.items():
        for column_name in table_data.columns.keys():
            if "." not in column_name:
                continue

            referenced_table = column_name.split(".")[0]

            if referenced_table not in table_names or referenced_table == table_name:
                continue

            referenced_pk = tables[referenced_table].primary_key
            if not referenced_pk:
                continue

            if column_name not in table_data.foreign_keys:
                table_data.foreign_keys.append(column_name)

            relationships.append(RelationshipModel(
                from_table=table_name,
                from_column=column_name,
                to_table=referenced_table,
                to_column=referenced_pk,
            ))

    return RawSchemaMetadataModel(
        source_type="csv",
        number_of_tables=len(tables),
        tables=tables,
        relationships=relationships,
    )

def extract_and_save_schema_metadata(csv_folder: Path = None) -> Path:
    """Extract schema metadata and save to JSON.
    
    Should be called before launching CrewAI agents.
    
    Args:
        csv_folder: Path to CSV folder.
    
    Returns:
        Path to saved JSON file.
    """
    metadata = extract_csv_schema_metadata(csv_folder)

    OUTPUT_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

    with open(RAW_SCHEMA_METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata.model_dump(), f, ensure_ascii=False, indent=2)

    return RAW_SCHEMA_METADATA_FILE

def load_raw_schema_metadata() -> RawSchemaMetadataModel:
    """Load raw schema metadata from JSON file.
    
    Returns:
        RawSchemaMetadataModel with previously extracted metadata.
    
    Raises:
        FileNotFoundError: If metadata file does not exist.
    """
    if not RAW_SCHEMA_METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Raw schema metadata file not found: {RAW_SCHEMA_METADATA_FILE}. "
            "Run extract_and_save_schema_metadata() first."
        )

    with open(RAW_SCHEMA_METADATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return RawSchemaMetadataModel(**data)

def get_raw_schema_metadata_json() -> str:
    """Get raw schema metadata as JSON string.
    
    Used by metadata extractor tool to provide metadata to agents.
    
    Returns:
        JSON string of raw schema metadata.
    """
    metadata = load_raw_schema_metadata()
    return json.dumps(metadata.model_dump(), ensure_ascii=False, indent=2)

