"""Code execution and validation utilities."""


from typing import Any, Dict
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from data_analysis.system.utils.paths import OUTPUT_DATA_DIR


def create_execution_env() -> Dict[str, Any]:
    """Create a shared execution environment with data analysis libraries.
    
    Loads pandas, matplotlib, seaborn, and all CSV files from current_analysis/data/.
    
    Returns:
        Dictionary with libraries, dataframes, and builtins for code execution.
    """
    env: Dict[str, Any] = {
        'pd': pd,
        'plt': plt,
        'sns': sns,
        'matplotlib': __import__('matplotlib'),
        'seaborn': __import__('seaborn'),
        '__builtins__': __builtins__,
    }

    # Load all CSV files from current_analysis/data/
    for csv_file in sorted(OUTPUT_DATA_DIR.glob("*.csv")):
        df = pd.read_csv(csv_file)
        table_name = csv_file.stem
        env[table_name] = df

        # Add singular alias for plural table names
        if table_name.endswith('s') and len(table_name) > 1:
            singular = table_name[:-1]
            env[singular] = df

    return env


def validate_python_syntax(code: str, exec_globals: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and execute Python code.
    
    Args:
        code: Python code string to execute.
        exec_globals: Execution environment dictionary.
    
    Returns:
        Dictionary with:
        - success: Whether execution succeeded
        - error: Error message if failed, None otherwise
        - exec_globals: Updated execution environment
    """
    try:
        exec(code, exec_globals)
        return {
            'success': True,
            'error': None,
            'exec_globals': exec_globals
        }
    except KeyError as e:
        # KeyError usually means a column name doesn't exist in DataFrame
        missing_key = str(e.args[0]) if e.args else str(e)
        return {
            'success': False,
            'error': f"Column '{missing_key}' not found. Check column name spelling and ensure it exists in the DataFrame.",
            'exec_globals': exec_globals
        }
    except NameError as e:
        # NameError means a variable/table name doesn't exist
        error_msg = str(e)
        if "name" in error_msg and "is not defined" in error_msg:
            # Extract the variable name from the error message
            return {
                'success': False,
                'error': f"Variable or table name not found: {error_msg}. Check spelling and ensure tables are loaded.",
                'exec_globals': exec_globals
            }
        return {
            'success': False,
            'error': error_msg,
            'exec_globals': exec_globals
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'exec_globals': exec_globals
        }

