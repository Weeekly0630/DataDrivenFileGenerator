from enum import Enum, auto
from typing import Optional

class YamlErrorType(Enum):
    """Enumeration of possible YAML handling error types"""
    MISSING_REQUIRED_FIELD = auto()  # Missing required configuration field
    INVALID_ROOT_PATH = auto()       # Root path does not exist
    FILE_NOT_FOUND = auto()          # YAML file not found
    LOAD_ERROR = auto()              # Error loading YAML file
    MISSING_KEY = auto()             # Required key missing in YAML data
    CIRCULAR_REFERENCE = auto()      # Circular reference detected in YAML tree
    MAX_DEPTH_EXCEEDED = auto()      # Maximum recursion depth exceeded
    INVALID_CHILDREN = auto()        # Invalid children path specification
    PARENT_NOT_FOUND = auto()        # Parent node not found
    PATTERN_ERROR = auto()           # Error in file pattern matching

class YamlError(Exception):
    """Base class for YAML handling errors"""
    def __init__(self, error_type: YamlErrorType, message: str, path: Optional[str] = None):
        self.error_type = error_type
        self.path = path
        super().__init__(message)

    def __str__(self) -> str:
        if self.path:
            return f"{self.error_type.name}: {self.args[0]} (path: {self.path})"
        return f"{self.error_type.name}: {self.args[0]}"

class YamlConfigError(YamlError):
    """Error in YAML configuration"""
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(YamlErrorType.MISSING_REQUIRED_FIELD, message, path)

class YamlPathError(YamlError):
    """Error with YAML file paths"""
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(YamlErrorType.INVALID_ROOT_PATH, message, path)

class YamlLoadError(YamlError):
    """Error loading YAML file"""
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(YamlErrorType.LOAD_ERROR, message, path)

class YamlStructureError(YamlError):
    """Error in YAML file structure"""
    def __init__(self, error_type: YamlErrorType, message: str, path: Optional[str] = None):
        super().__init__(error_type, message, path)

    @classmethod
    def missing_key(cls, key: str, path: Optional[str] = None) -> "YamlStructureError":
        """Create error for missing required key"""
        return cls(YamlErrorType.MISSING_KEY, f"Missing required key '{key}'", path)

    @classmethod
    def circular_reference(cls, path: str) -> "YamlStructureError":
        """Create error for circular reference detection"""
        return cls(YamlErrorType.CIRCULAR_REFERENCE, f"Circular reference detected", path)

    @classmethod
    def max_depth_exceeded(cls, depth: int, path: str) -> "YamlStructureError":
        """Create error for maximum recursion depth exceeded"""
        return cls(YamlErrorType.MAX_DEPTH_EXCEEDED, 
                  f"Maximum recursion depth ({depth}) exceeded", path)

    @classmethod
    def invalid_children(cls, details: str, path: Optional[str] = None) -> "YamlStructureError":
        """Create error for invalid children specification"""
        return cls(YamlErrorType.INVALID_CHILDREN, 
                  f"Invalid children path specification: {details}", path)
