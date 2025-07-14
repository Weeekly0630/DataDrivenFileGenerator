"""Handler factory for creating and validating data and template handlers"""

from typing import Dict, Any
from . import (
    DataHandler,
    TemplateHandler,
    validate_data_handler,
    validate_template_handler,
    GeneratorError,
    GeneratorErrorType
)
from ..jinja.jinja_handler import JinjaTemplateHandler
from ..yaml.yaml_handler import YamlDataTreeHandler
from .types import DataHandlerType, TemplateHandlerType

class HandlerFactory:
    """Factory class for creating and validating handlers"""
    
    # Handler type mapping
    _data_handler_map = {
        DataHandlerType.YAML_HANDLER: YamlDataTreeHandler,
    }
    
    _template_handler_map = {
        TemplateHandlerType.JINJA_HANDLER: JinjaTemplateHandler,
    }
    
    @staticmethod
    def create_data_handler(handler_type: DataHandlerType, config: Dict[str, Any]) -> DataHandler:
        """Create and validate a data handler
        
        Args:
            handler_type: Type of data handler to create
            config: Configuration for the handler
            
        Returns:
            Initialized and validated data handler
            
        Raises:
            GeneratorError: If handler creation or validation fails
        """
        handler_class = HandlerFactory._data_handler_map.get(handler_type)
        if not handler_class:
            raise GeneratorError(
                GeneratorErrorType.DATA_INIT_ERROR,
                f"Unsupported data handler type: {handler_type}"
            )
            
        try:
            handler = handler_class(config)
            validate_data_handler(handler)
            return handler
        except Exception as e:
            raise GeneratorError(
                GeneratorErrorType.DATA_INIT_ERROR,
                f"Failed to initialize {handler_type.value}: {str(e)}"
            )

    @staticmethod
    def create_template_handler(handler_type: TemplateHandlerType, config: Dict[str, Any]) -> TemplateHandler:
        """Create and validate a template handler
        
        Args:
            handler_type: Type of template handler to create
            config: Configuration for the handler
            
        Returns:
            Initialized and validated template handler
            
        Raises:
            GeneratorError: If handler creation or validation fails
        """
        handler_class = HandlerFactory._template_handler_map.get(handler_type)
        if not handler_class:
            raise GeneratorError(
                GeneratorErrorType.TEMPLATE_INIT_ERROR,
                f"Unsupported template handler type: {handler_type}"
            )
            
        try:
            handler = handler_class(config)
            validate_template_handler(handler)
            return handler
        except Exception as e:
            raise GeneratorError(
                GeneratorErrorType.TEMPLATE_INIT_ERROR,
                f"Failed to initialize {handler_type.value}: {str(e)}"
            )
