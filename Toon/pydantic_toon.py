"""
Pydantic v2 TOON Format Integration

This module provides TOON serialization support for Pydantic v2 models.
TOON is a token-efficient format optimized for LLM interactions.

Example:
    from pydantic import BaseModel
    from pydantic_toon import ToonMixin
    
    class Employee(BaseModel, ToonMixin):
        id: int
        name: str
        department: str
        salary: float
    
    employees = [Employee(...), Employee(...)]
    toon_output = Employee.model_dump_toon(employees)
"""

from typing import Any, List, Type, Union, get_args, get_origin
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime, date
import re


class ToonSerializer:
    """
    Converts Pydantic models to TOON format.
    
    Handles:
    - Single objects
    - Lists of objects (tabular format)
    - Nested models
    - Various Python types (int, str, float, bool, datetime, etc.)
    """
    
    @staticmethod
    def _serialize_value(value: Any, indent_level: int = 0) -> str:
        """
        Serialize a single value to TOON format.
        
        Args:
            value: The value to serialize
            indent_level: Current indentation level
            
        Returns:
            TOON-formatted string representation
        """
        indent = "  " * indent_level
        
        # Handle None
        if value is None:
            return "null"
        
        # Handle booleans
        if isinstance(value, bool):
            return "true" if value else "false"
        
        # Handle numbers
        if isinstance(value, (int, float, Decimal)):
            return str(value)
        
        # Handle datetime objects
        if isinstance(value, datetime):
            return value.isoformat()
        
        if isinstance(value, date):
            return value.isoformat()
        
        # Handle strings - escape commas and newlines
        if isinstance(value, str):
            # If string contains comma, newline, or starts/ends with whitespace, quote it
            if ',' in value or '\n' in value or value.strip() != value:
                # Escape quotes and backslashes
                escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            return value
        
        # Handle Pydantic models
        if isinstance(value, BaseModel):
            return ToonSerializer._serialize_object(value, indent_level)
        
        # Handle lists
        if isinstance(value, list):
            if not value:
                return "[]"
            
            # Check if all items are same type (Pydantic models)
            if all(isinstance(item, BaseModel) for item in value):
                # For nested lists, we want to serialize them on a new line
                tabular = ToonSerializer._serialize_list_of_models(value, indent_level)
                return "\n" + tabular
            
            # Mixed list - serialize as simple list
            items = [ToonSerializer._serialize_value(item, 0) for item in value]
            return "[" + ",".join(items) + "]"
        
        # Handle dictionaries
        if isinstance(value, dict):
            lines = []
            for key, val in value.items():
                serialized_val = ToonSerializer._serialize_value(val, indent_level + 1)
                if '\n' in serialized_val:
                    lines.append(f"{indent}  {key}:")
                    lines.append(f"{indent}    {serialized_val}")
                else:
                    lines.append(f"{indent}  {key}: {serialized_val}")
            return "\n".join(lines)
        
        # Fallback to string representation
        return str(value)
    
    @staticmethod
    def _serialize_object(obj: BaseModel, indent_level: int = 0) -> str:
        """
        Serialize a single Pydantic model to TOON format.
        
        Args:
            obj: Pydantic model instance
            indent_level: Current indentation level
            
        Returns:
            TOON-formatted string
        """
        indent = "  " * indent_level
        lines = []
        
        # Get model fields directly to preserve BaseModel instances in lists
        for field_name in obj.model_fields:
            value = getattr(obj, field_name)
            serialized_val = ToonSerializer._serialize_value(value, indent_level + 1)
            
            # Multi-line values get their own line
            if '\n' in serialized_val:
                lines.append(f"{indent}{field_name}:{serialized_val}")
            else:
                lines.append(f"{indent}{field_name}: {serialized_val}")
        
        return "\n".join(lines)
    
    @staticmethod
    def _serialize_list_of_models(models: List[BaseModel], indent_level: int = 0) -> str:
        """
        Serialize a list of Pydantic models using TOON's tabular format.
        
        Format: [count]{Field1,Field2,Field3}:
                  value1,value2,value3
                  value1,value2,value3
        
        Args:
            models: List of Pydantic model instances (all same type)
            indent_level: Current indentation level
            
        Returns:
            TOON-formatted tabular string
        """
        if not models:
            return "[]"
        
        indent = "  " * indent_level
        
        # Get field names from first model
        first_model = models[0]
        fields = list(first_model.model_dump().keys())
        
        # Build header: [count]{Field1,Field2,Field3}:
        header = f"{indent}[{len(models)}]{{{','.join(fields)}}}:"
        
        # Build rows
        rows = []
        for model in models:
            data = model.model_dump()
            values = []
            for field in fields:
                value = data.get(field)
                serialized = ToonSerializer._serialize_value(value, 0)
                values.append(serialized)
            
            row = f"{indent}  {','.join(values)}"
            rows.append(row)
        
        return "\n".join([header] + rows)
    
    @staticmethod
    def serialize(
        data: Union[BaseModel, List[BaseModel]], 
        indent_level: int = 0
    ) -> str:
        """
        Main serialization entry point.
        
        Args:
            data: Either a single Pydantic model or list of models
            indent_level: Starting indentation level
            
        Returns:
            TOON-formatted string
        """
        if isinstance(data, list):
            if all(isinstance(item, BaseModel) for item in data):
                return ToonSerializer._serialize_list_of_models(data, indent_level)
            else:
                raise ValueError("All items in list must be Pydantic models")
        
        if isinstance(data, BaseModel):
            return ToonSerializer._serialize_object(data, indent_level)
        
        raise ValueError(f"Unsupported type: {type(data)}")


class ToonMixin:
    """
    Mixin class to add TOON serialization to Pydantic models.
    
    Usage:
        class MyModel(BaseModel, ToonMixin):
            field1: str
            field2: int
        
        # Single object
        obj = MyModel(field1="test", field2=42)
        toon_str = obj.model_dump_toon()
        
        # List of objects (tabular)
        objects = [MyModel(...), MyModel(...)]
        toon_str = MyModel.model_dump_toon(objects)
    """
    
    def model_dump_toon(self) -> str:
        """
        Serialize this model instance to TOON format.
        
        Returns:
            TOON-formatted string
        """
        return ToonSerializer.serialize(self)
    
    @classmethod
    def model_dump_toon_list(cls, models: List['ToonMixin']) -> str:
        """
        Serialize a list of models to TOON tabular format.
        
        Args:
            models: List of model instances
            
        Returns:
            TOON-formatted tabular string
        """
        return ToonSerializer.serialize(models)


# Standalone functions for use without mixin
def model_dump_toon(model: BaseModel) -> str:
    """
    Serialize a Pydantic model to TOON format.
    
    Args:
        model: Pydantic model instance
        
    Returns:
        TOON-formatted string
    """
    return ToonSerializer.serialize(model)


def models_dump_toon(models: List[BaseModel]) -> str:
    """
    Serialize a list of Pydantic models to TOON tabular format.
    
    Args:
        models: List of Pydantic model instances
        
    Returns:
        TOON-formatted tabular string
    """
    return ToonSerializer.serialize(models)


# Monkey-patch approach (optional - use if you want to extend BaseModel directly)
def _patch_basemodel():
    """
    Monkey-patch Pydantic's BaseModel to add model_dump_toon method.
    Call this once at application startup if you want all models to have TOON support.
    
    Usage:
        from pydantic_toon import patch_pydantic_toon
        patch_pydantic_toon()
    """
    BaseModel.model_dump_toon = lambda self: ToonSerializer.serialize(self)
    BaseModel.model_dump_toon_list = classmethod(
        lambda cls, models: ToonSerializer.serialize(models)
    )


def patch_pydantic_toon():
    """
    Public API to enable TOON support for all Pydantic models.
    """
    _patch_basemodel()


if __name__ == "__main__":
    # Example usage
    from pydantic import Field
    
    class Employee(BaseModel, ToonMixin):
        id: int
        name: str
        department: str
        salary: float
        active: bool = True
        hire_date: date = Field(default_factory=date.today)
    
    class Department(BaseModel, ToonMixin):
        name: str
        employees: List[Employee]
        budget: float
    
    # Create sample data
    employees = [
        Employee(id=1, name="Alice", department="Engineering", salary=120000, hire_date=date(2020, 1, 15)),
        Employee(id=2, name="Bob", department="Marketing", salary=95000, hire_date=date(2021, 3, 22)),
        Employee(id=3, name="Charlie", department="Engineering", salary=110000, hire_date=date(2019, 7, 10)),
    ]
    
    print("=== Single Employee (Object Format) ===")
    print(employees[0].model_dump_toon())
    print()
    
    print("=== Multiple Employees (Tabular Format) ===")
    print(Employee.model_dump_toon_list(employees))
    print()
    
    print("=== Nested Model ===")
    dept = Department(
        name="Engineering",
        employees=employees[:2],
        budget=500000.0
    )
    print(dept.model_dump_toon())
    print()
    
    # Compare token counts (rough approximation)
    import json
    json_str = json.dumps([emp.model_dump(mode='json') for emp in employees], default=str)
    toon_str = Employee.model_dump_toon_list(employees)
    
    print("=== Token Efficiency Comparison ===")
    print(f"JSON length: {len(json_str)} chars")
    print(f"TOON length: {len(toon_str)} chars")
    print(f"Reduction: {((len(json_str) - len(toon_str)) / len(json_str) * 100):.1f}%")
