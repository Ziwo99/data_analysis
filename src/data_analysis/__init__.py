"""Data Analysis package using CrewAI for automated data analysis workflows."""


# Lazy imports to avoid circular dependencies and unnecessary module loading
def __getattr__(name):
    """Lazy import for main functions and crew classes."""
    if name == "run":
        from .main import run
        return run
    elif name == "run_mono":
        from .mono_main import run_mono
        return run_mono
    elif name == "DataAnalysis":
        from .crew import DataAnalysis
        return DataAnalysis
    elif name == "MonoDataAnalysis":
        from .crew import MonoDataAnalysis
        return MonoDataAnalysis
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "__version__",
    "run",
    "run_mono",
    "DataAnalysis",
    "MonoDataAnalysis",
]