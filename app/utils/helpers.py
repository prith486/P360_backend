"""
Utility helper functions for the P360 backend.
"""

def normalize_branch(val: str) -> str:
    """Normalize branch names for consistent comparison."""
    if not val:
        return ""
    # Remove common abbreviations and standardize format
    val = str(val).lower().strip()
    val = val.replace("computer science", "computer_science").replace("cse", "computer_science").replace("cs", "computer_science")
    val = val.replace("information technology", "information_technology").replace("it", "information_technology")
    val = val.replace("electronics", "electronics").replace("ece", "electronics").replace("entc", "electronics")
    val = val.replace("mechanical", "mechanical").replace("mech", "mechanical")
    val = val.replace("ai/ml", "ai_ml").replace("ai", "ai_ml")
    val = val.replace(" ", "_").replace("/", "_").replace("-", "_")
    return val

def normalize_year(val: str) -> str:
    """Normalize academic year/batch labels."""
    if not val:
        return ""
    val = str(val).lower().strip()
    # Normalize year labels
    val = val.replace("first year", "first").replace("1st year", "first").replace("1st", "first")
    val = val.replace("second year", "second").replace("2nd year", "second").replace("2nd", "second")
    val = val.replace("third year", "third").replace("3rd year", "third").replace("3rd", "third")
    val = val.replace("fourth year", "fourth").replace("final year", "fourth").replace("4th year", "fourth").replace("4th", "fourth")
    val = val.replace(" ", "_")
    return val
