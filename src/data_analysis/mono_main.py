"""Main entry point for the mono-agent data analysis pipeline."""

import os
import warnings
from data_analysis.crew import MonoDataAnalysis
from data_analysis.system.utils import (
    extract_and_save_schema_metadata,
    update_analysis_status,
)
from data_analysis.system.utils.paths import (
    OUTPUT_AGENT_DIR,
    OUTPUT_SCRIPT_DIR,
    OUTPUT_EXECUTE_CODE_DIR,
    OUTPUT_DATA_DIR,
    CURRENT_ANALYSIS_DIR,
)


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def clear_output_directories():
    """Clear all output directories before a new run (current analysis).
    
    Note: OUTPUT_DATA_DIR is NOT cleared as it contains the source CSV files
    that should persist throughout the analysis.
    """
    # Clear new structure directories (but NOT data directory)
    for directory in [OUTPUT_AGENT_DIR, OUTPUT_SCRIPT_DIR, OUTPUT_EXECUTE_CODE_DIR]:
        if directory.exists():
            for file in os.listdir(directory):
                path = directory / file
                if path.is_file():
                    os.remove(path)
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)
    # Also clear root-level files
    for file in [CURRENT_ANALYSIS_DIR / "analysis_status.json", CURRENT_ANALYSIS_DIR / "metadata.json", CURRENT_ANALYSIS_DIR / ".analysis_name.txt"]:
        if file.exists():
            file.unlink()

def run_mono():
    """Run the mono-agent crew for single-pass data analysis."""
    # Read analysis name from temporary file if available
    analysis_name = ""
    temp_name_file = CURRENT_ANALYSIS_DIR / ".analysis_name.txt"
    if temp_name_file.exists():
        try:
            with open(temp_name_file, "r", encoding="utf-8") as f:
                analysis_name = f.read().strip()
        except (IOError, UnicodeDecodeError):
            pass
    
    name_display = f" - {analysis_name}" if analysis_name else ""
    print("-" * 80)
    print(f"🚀 Starting analysis{name_display}")
    print("-" * 80)
    
    # Clear output directories
    clear_output_directories()
    
    # Ensure output directories exist
    OUTPUT_AGENT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_EXECUTE_CODE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Extract and save schema metadata BEFORE launching agent
    update_analysis_status("raw_schema", "in_progress")
    extract_and_save_schema_metadata()
    update_analysis_status("raw_schema", "done")
    print("✅ Metadata Extraction")
    
    # Update status: mono_agent starts
    update_analysis_status("mono_agent", "in_progress")

    # Launch the mono-agent crew (no inputs needed as all values are hardcoded in YAML)
    MonoDataAnalysis().crew().kickoff(inputs={})
    
    name_display = f" - {analysis_name}" if analysis_name else ""
    print("-" * 80)
    print(f"✅ Analysis completed{name_display}")
    print("-" * 80)

if __name__ == "__main__":
    run_mono()