"""Pydantic models for schema metadata and interpretation."""


from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Raw Metadata Models (extracted automatically before agent interpretation)
# ============================================================================

class ColumnMetadataModel(BaseModel):
    """Raw column metadata extracted from data source."""
    
    type: str = Field(description="Data type of the column")
    nullable: bool = Field(description="Whether the column contains null values")
    unique: bool = Field(description="Whether all values are unique")
    null_count: int = Field(description="Number of null values")
    unique_count: int = Field(description="Number of unique values")
    min: Optional[float] = Field(default=None, description="Minimum value (numeric only)")
    max: Optional[float] = Field(default=None, description="Maximum value (numeric only)")
    mean: Optional[float] = Field(default=None, description="Mean value (numeric only)")
    std: Optional[float] = Field(default=None, description="Standard deviation (numeric only)")

class TableMetadataModel(BaseModel):
    """Raw table metadata extracted from data source."""
    
    row_count: int = Field(description="Number of rows in the table")
    columns: Dict[str, ColumnMetadataModel] = Field(description="Column metadata")
    primary_key: Optional[str] = Field(default=None, description="Primary key column")
    foreign_keys: List[str] = Field(default_factory=list, description="Foreign key columns")

class RelationshipModel(BaseModel):
    """Relationship between two tables."""
    
    from_table: str = Field(description="Source table name")
    from_column: str = Field(description="Source column (foreign key)")
    to_table: str = Field(description="Target table name")
    to_column: str = Field(description="Target column (primary key)")

class RawSchemaMetadataModel(BaseModel):
    """Raw schema metadata extracted automatically from data source."""
    
    source_type: str = Field(description="Data source type (csv, sql, etc.)")
    number_of_tables: int = Field(description="Number of tables in schema")
    tables: Dict[str, TableMetadataModel] = Field(description="Table metadata")
    relationships: List[RelationshipModel] = Field(
        default_factory=list,
        description="Table relationships"
    )

# ============================================================================
# Interpreted Models (enriched by schema_interpreter agent)
# ============================================================================

class ColumnSchemaModel(BaseModel):
    """Column schema with agent interpretation."""
    
    # Raw metadata
    type: str = Field(description="Data type of the column")
    nullable: bool = Field(description="Whether the column contains null values")
    unique: bool = Field(description="Whether all values are unique")
    null_count: int = Field(description="Number of null values")
    unique_count: int = Field(description="Number of unique values")
    min: Optional[float] = Field(default=None, description="Minimum value (numeric only)")
    max: Optional[float] = Field(default=None, description="Maximum value (numeric only)")
    mean: Optional[float] = Field(default=None, description="Mean value (numeric only)")
    std: Optional[float] = Field(default=None, description="Standard deviation (numeric only)")
    # Agent interpretation
    semantic_description: str = Field(
        description="Business meaning of this column"
    )

class TableSchemaModel(BaseModel):
    """Table schema with agent interpretation."""
    
    # Raw metadata
    row_count: int = Field(description="Number of rows in the table")
    columns: Dict[str, ColumnSchemaModel] = Field(description="Column schemas")
    primary_key: Optional[str] = Field(default=None, description="Primary key column")
    foreign_keys: List[str] = Field(default_factory=list, description="Foreign key columns")
    # Agent interpretation
    role: str = Field(description="Purpose of this table in the database")
    description: str = Field(description="Detailed description of table contents")

class EnrichedMetadataModel(BaseModel):
    """Complete schema summary with agent interpretations."""
    
    # Raw metadata
    source_type: str = Field(description="Data source type")
    number_of_tables: int = Field(description="Number of tables in schema")
    tables: Dict[str, TableSchemaModel] = Field(description="Table schemas")
    relationships: List[RelationshipModel] = Field(description="Table relationships")
    # Agent interpretation
    database_domain: str = Field(
        description="Business domain (e.g., e-commerce, healthcare)"
    )
    database_description: str = Field(
        description="Comprehensive description of the database purpose"
    )
