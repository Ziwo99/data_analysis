"""Saved analyses management utilities."""


import io
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from data_analysis.system.utils.paths import (
    CURRENT_ANALYSIS_DIR,
    SAVED_ANALYSES_DIR,
    TEST_DATA_DIR,
)


def get_saved_analyses() -> List[Dict]:
    """Get list of all saved analyses with metadata.
    
    Returns:
        List of dicts with name, date, dataset, and source, sorted by date (most recent first).
    """
    if not SAVED_ANALYSES_DIR.exists():
        return []

    analyses = []
    for folder in SAVED_ANALYSES_DIR.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            # Check for metadata.json at root of saved analysis
            metadata_file = folder / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    analyses.append({
                        "name": folder.name,
                        "date": metadata.get("date", "Unknown"),
                        "dataset": metadata.get("dataset", "Unknown"),
                        "source": metadata.get("source", "Unknown"),
                    })
                except (json.JSONDecodeError, IOError):
                    # If metadata can't be read, use folder modification time as fallback
                    folder_mtime = folder.stat().st_mtime
                    analyses.append({
                        "name": folder.name,
                        "date": datetime.fromtimestamp(folder_mtime).isoformat(),
                        "dataset": "Unknown",
                        "source": "Unknown",
                    })
            else:
                # If no metadata, use folder modification time
                folder_mtime = folder.stat().st_mtime
                analyses.append({
                    "name": folder.name,
                    "date": datetime.fromtimestamp(folder_mtime).isoformat(),
                    "dataset": "Unknown",
                    "source": "Unknown",
                })

    # Sort by date (most recent first)
    def get_sort_key(analysis: Dict) -> float:
        """Get sort key from date string or folder modification time."""
        date_str = analysis.get("date", "")
        if date_str == "Unknown":
            return 0.0
        try:
            # Try to parse ISO format date
            return datetime.fromisoformat(date_str).timestamp()
        except (ValueError, TypeError):
            # Fallback to 0 if date can't be parsed
            return 0.0
    
    analyses.sort(key=get_sort_key, reverse=True)
    
    return analyses

def get_saved_analysis_names() -> List[str]:
    """Get list of saved analysis names.
    
    Returns:
        List of analysis names.
    """
    return [a["name"] for a in get_saved_analyses()]

def validate_analysis_name(name: str) -> Dict[str, any]:
    """Validate analysis name for uniqueness and format.
    
    Args:
        name: Proposed analysis name.
    
    Returns:
        Dict with 'valid' boolean and 'error' message.
    """
    if not name or not name.strip():
        return {"valid": False, "error": "Analysis name is required"}

    name = name.strip()

    if len(name) < 2:
        return {"valid": False, "error": "Name must be at least 2 characters"}

    if len(name) > 50:
        return {"valid": False, "error": "Name cannot exceed 50 characters"}

    if not re.match(r'^[\w\s\-]+$', name, re.UNICODE):
        return {"valid": False, "error": "Name can only contain letters, numbers, spaces, hyphens and underscores"}

    existing_names = [n.lower() for n in get_saved_analysis_names()]
    if name.lower() in existing_names:
        return {"valid": False, "error": "An analysis with this name already exists"}

    return {"valid": True, "error": None}

def sanitize_folder_name(name: str) -> str:
    """Sanitize analysis name for use as folder name.
    
    Args:
        name: Analysis name.
    
    Returns:
        Sanitized folder name.
    """
    sanitized = re.sub(r'[^\w\-]', '_', name.strip())
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')

def save_analysis(name: str, dataset: str, source: str, pipeline_mode: str = "multi", openai_model: str = "gpt-4o") -> bool:
    """Save current analysis to saved_analyses folder.
    
    Args:
        name: Analysis name.
        dataset: Dataset folder name.
        source: Data source type ('uploaded' or 'existing').
        pipeline_mode: Pipeline mode ('mono' or 'multi').
        openai_model: OpenAI model used for the analysis.
    
    Returns:
        True if saved successfully.
    """
    folder_name = sanitize_folder_name(name)
    analysis_dir = SAVED_ANALYSES_DIR / folder_name

    try:
        SAVED_ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
        analysis_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata at root of analysis directory
        metadata = {
            "name": name,
            "folder_name": folder_name,
            "date": datetime.now().isoformat(),
            "dataset": dataset,
            "source": source,
            "pipeline_mode": pipeline_mode,
            "openai_model": openai_model,
        }
        metadata_path = analysis_dir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        # Copy entire current_analysis directory to saved_analyses
        if CURRENT_ANALYSIS_DIR.exists():
            # Copy all contents of current_analysis to the saved analysis directory
            for item in CURRENT_ANALYSIS_DIR.iterdir():
                dest_item = analysis_dir / item.name
                if item.is_dir():
                    if dest_item.exists():
                        shutil.rmtree(dest_item)
                    shutil.copytree(item, dest_item)
                else:
                    if dest_item.exists():
                        dest_item.unlink()
                    shutil.copy2(item, dest_item)

        return True

    except Exception as e:
        print(f"Error saving analysis: {e}")
        if analysis_dir.exists():
            shutil.rmtree(analysis_dir, ignore_errors=True)
        return False

def load_analysis(name: str) -> Tuple[bool, str]:
    """Load a saved analysis into current_analysis directory.
    
    Args:
        name: Analysis folder name.
    
    Returns:
        Tuple of (success, pipeline_mode). pipeline_mode is 'mono' or 'multi'.
    """
    analysis_dir = SAVED_ANALYSES_DIR / name

    if not analysis_dir.exists():
        return (False, "multi")

    try:
        CURRENT_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

        # Get pipeline_mode from metadata
        metadata_file = analysis_dir / "metadata.json"
        pipeline_mode = "multi"  # Default
        
        if metadata_file.exists():
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                    pipeline_mode = metadata.get("pipeline_mode", "multi")
            except (json.JSONDecodeError, IOError):
                pass

        # Copy entire saved analysis directory to current_analysis
        CURRENT_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Copy all contents from saved analysis to current_analysis
        for item in analysis_dir.iterdir():
            # Skip metadata.json as it's only for saved analyses
            if item.name == "metadata.json":
                continue
            dest_item = CURRENT_ANALYSIS_DIR / item.name
            if item.is_dir():
                if dest_item.exists():
                    shutil.rmtree(dest_item)
                shutil.copytree(item, dest_item)
            else:
                if dest_item.exists():
                    dest_item.unlink()
                shutil.copy2(item, dest_item)

        return (True, pipeline_mode)

    except Exception as e:
        print(f"Error loading analysis: {e}")
        return (False, "multi")

def delete_analysis(name: str) -> bool:
    """Delete a saved analysis.
    
    Args:
        name: Analysis folder name.
    
    Returns:
        True if deleted successfully.
    """
    analysis_dir = SAVED_ANALYSES_DIR / name

    if not analysis_dir.exists():
        return False

    try:
        shutil.rmtree(analysis_dir)
        return True
    except Exception as e:
        print(f"Error deleting analysis: {e}")
        return False

def get_analysis_metadata(name: str) -> Optional[Dict]:
    """Get metadata for a saved analysis.
    
    Args:
        name: Analysis folder name.
    
    Returns:
        Metadata dictionary or None.
    """
    metadata_file = SAVED_ANALYSES_DIR / name / "metadata.json"

    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def update_existing_analyses_with_model(default_model: str = "gpt-4o") -> int:
    """Update all existing saved analyses to include openai_model field.
    
    Args:
        default_model: Default model to use for analyses that don't have one.
    
    Returns:
        Number of analyses updated.
    """
    if not SAVED_ANALYSES_DIR.exists():
        return 0
    
    updated_count = 0
    for folder in SAVED_ANALYSES_DIR.iterdir():
        if folder.is_dir() and not folder.name.startswith('.'):
            metadata_file = folder / "metadata.json"
            if metadata_file.exists():
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                    
                    # Only update if openai_model is missing
                    if "openai_model" not in metadata:
                        metadata["openai_model"] = default_model
                        
                        with open(metadata_file, "w", encoding="utf-8") as f:
                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                        
                        updated_count += 1
                except (json.JSONDecodeError, IOError):
                    # Skip if metadata can't be read
                    continue
    
    return updated_count

def get_source_data_files(analysis_name: str) -> List[Path]:
    """Get source data files from a saved analysis.
    
    Args:
        analysis_name: Analysis folder name.
    
    Returns:
        List of file paths.
    """
    data_dir = SAVED_ANALYSES_DIR / analysis_name / "data"

    if not data_dir.exists():
        return []

    files = []
    # Only look for CSV files (Excel files are converted to CSV)
    files.extend(data_dir.glob("*.csv"))

    return sorted(files)

def get_current_source_data_files(dataset: str) -> List[Path]:
    """Get source data files from current dataset.
    
    Args:
        dataset: Dataset folder name.
    
    Returns:
        List of file paths.
    """
    data_dir = TEST_DATA_DIR / dataset

    if not data_dir.exists():
        return []

    files = []
    # Only look for CSV files (Excel files are converted to CSV)
    files.extend(data_dir.glob("*.csv"))

    return sorted(files)

def create_source_data_zip(analysis_name: str = None, dataset: str = None) -> Optional[bytes]:
    """Create a zip file of source data files.
    
    Args:
        analysis_name: If provided, get files from saved analysis.
        dataset: If provided, get files from current dataset.
    
    Returns:
        Zip file bytes or None.
    """
    if analysis_name:
        files = get_source_data_files(analysis_name)
    elif dataset:
        files = get_current_source_data_files(dataset)
    else:
        return None

    if not files:
        return None

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in files:
            zip_file.write(file_path, file_path.name)

    zip_buffer.seek(0)
    return zip_buffer.getvalue()