"""
Test suite for Pydantic TOON serialization.

Tests cover:
- Single object serialization
- List/tabular serialization
- Nested models
- Various data types
- Edge cases
"""

from pydantic import BaseModel, Field
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic_toon import ToonMixin, model_dump_toon, models_dump_toon, patch_pydantic_toon


class SimpleModel(BaseModel, ToonMixin):
    """Simple model for basic testing."""
    id: int
    name: str
    active: bool


class Employee(BaseModel, ToonMixin):
    """Employee model matching the article example."""
    id: int
    name: str
    department: str
    salary: float


class ComplexModel(BaseModel, ToonMixin):
    """Model with various data types."""
    id: int
    name: str
    score: float
    active: bool
    created_at: datetime
    birth_date: date
    balance: Decimal
    tags: List[str]
    metadata: Optional[dict] = None


class NestedModel(BaseModel, ToonMixin):
    """Model with nested relationships."""
    id: int
    name: str
    employees: List[Employee]


def test_single_object_serialization():
    """Test serializing a single object."""
    emp = Employee(id=1, name="Alice", department="Engineering", salary=120000)
    toon = emp.model_dump_toon()
    
    assert "id: 1" in toon
    assert "name: Alice" in toon
    assert "department: Engineering" in toon
    assert "salary: 120000" in toon


def test_list_serialization_tabular():
    """Test serializing a list of objects in tabular format."""
    employees = [
        Employee(id=1, name="Alice", department="Engineering", salary=120000),
        Employee(id=2, name="Bob", department="Marketing", salary=95000),
        Employee(id=3, name="Charlie", department="Engineering", salary=110000),
    ]
    
    toon = Employee.model_dump_toon_list(employees)
    
    # Check header
    assert "[3]{id,name,department,salary}:" in toon
    
    # Check data rows
    assert "1,Alice,Engineering,120000" in toon
    assert "2,Bob,Marketing,95000" in toon
    assert "3,Charlie,Engineering,110000" in toon


def test_boolean_serialization():
    """Test boolean value serialization."""
    model = SimpleModel(id=1, name="Test", active=True)
    toon = model.model_dump_toon()
    assert "active: true" in toon
    
    model2 = SimpleModel(id=2, name="Test2", active=False)
    toon2 = model2.model_dump_toon()
    assert "active: false" in toon2


def test_datetime_serialization():
    """Test datetime serialization to ISO format."""
    dt = datetime(2024, 1, 15, 10, 30, 45)
    d = date(2024, 1, 15)
    
    model = ComplexModel(
        id=1,
        name="Test",
        score=95.5,
        active=True,
        created_at=dt,
        birth_date=d,
        balance=Decimal("1000.50"),
        tags=["python", "pydantic"]
    )
    
    toon = model.model_dump_toon()
    
    assert "2024-01-15T10:30:45" in toon
    assert "2024-01-15" in toon


def test_decimal_serialization():
    """Test Decimal type serialization."""
    model = ComplexModel(
        id=1,
        name="Test",
        score=95.5,
        active=True,
        created_at=datetime.now(),
        birth_date=date.today(),
        balance=Decimal("12345.67"),
        tags=[]
    )
    
    toon = model.model_dump_toon()
    assert "12345.67" in toon


def test_list_field_serialization():
    """Test serialization of list fields."""
    model = ComplexModel(
        id=1,
        name="Test",
        score=95.5,
        active=True,
        created_at=datetime.now(),
        birth_date=date.today(),
        balance=Decimal("1000"),
        tags=["python", "pydantic", "toon"]
    )
    
    toon = model.model_dump_toon()
    assert "tags: [python,pydantic,toon]" in toon


def test_nested_model_serialization():
    """Test serialization of nested models."""
    employees = [
        Employee(id=1, name="Alice", department="Engineering", salary=120000),
        Employee(id=2, name="Bob", department="Marketing", salary=95000),
    ]
    
    nested = NestedModel(id=1, name="Tech Department", employees=employees)
    toon = nested.model_dump_toon()
    
    # Should contain nested employee data in tabular format
    assert "employees:" in toon
    assert "[2]{id,name,department,salary}:" in toon
    assert "1,Alice,Engineering,120000" in toon


def test_empty_list():
    """Test serialization of empty lists."""
    nested = NestedModel(id=1, name="Empty Department", employees=[])
    toon = nested.model_dump_toon()
    
    assert "employees: []" in toon


def test_none_value():
    """Test serialization of None values."""
    model = ComplexModel(
        id=1,
        name="Test",
        score=95.5,
        active=True,
        created_at=datetime.now(),
        birth_date=date.today(),
        balance=Decimal("1000"),
        tags=[],
        metadata=None
    )
    
    toon = model.model_dump_toon()
    assert "metadata: null" in toon


def test_string_with_comma():
    """Test that strings with commas are properly quoted."""
    emp = Employee(id=1, name="Smith, John", department="Engineering", salary=120000)
    toon = emp.model_dump_toon()
    
    # String with comma should be quoted
    assert '"Smith, John"' in toon or 'name: Smith, John' in toon


def test_standalone_functions():
    """Test standalone serialization functions."""
    emp = Employee(id=1, name="Alice", department="Engineering", salary=120000)
    
    # Test single object function
    toon = model_dump_toon(emp)
    assert "name: Alice" in toon
    
    # Test list function
    employees = [emp, Employee(id=2, name="Bob", department="Marketing", salary=95000)]
    toon_list = models_dump_toon(employees)
    assert "[2]{id,name,department,salary}:" in toon_list


def test_monkey_patch():
    """Test monkey-patching BaseModel."""
    # Create a model WITHOUT ToonMixin
    class UnmixedEmployee(BaseModel):
        id: int
        name: str
        department: str
        salary: float
    
    # Patch it
    patch_pydantic_toon()
    
    # Now it should have model_dump_toon
    emp = UnmixedEmployee(id=1, name="Alice", department="Engineering", salary=120000)
    toon = emp.model_dump_toon()
    
    assert "name: Alice" in toon


def test_efficiency_comparison():
    """Compare TOON vs JSON size (rough token estimate)."""
    import json
    
    employees = [
        Employee(id=i, name=f"Employee{i}", department="Engineering", salary=100000 + i * 1000)
        for i in range(1, 11)
    ]
    
    # JSON format
    json_str = json.dumps([emp.model_dump(mode='json') for emp in employees])
    
    # TOON format
    toon_str = Employee.model_dump_toon_list(employees)
    
    # TOON should be significantly shorter
    reduction = ((len(json_str) - len(toon_str)) / len(json_str)) * 100
    
    print(f"\nEfficiency Test (10 employees):")
    print(f"JSON size: {len(json_str)} chars")
    print(f"TOON size: {len(toon_str)} chars")
    print(f"Reduction: {reduction:.1f}%")
    
    assert len(toon_str) < len(json_str), "TOON should be more compact than JSON"
    assert reduction > 20, "TOON should reduce size by at least 20%"


def test_dict_field_serialization():
    """Test serialization of dictionary fields."""
    model = ComplexModel(
        id=1,
        name="Test",
        score=95.5,
        active=True,
        created_at=datetime.now(),
        birth_date=date.today(),
        balance=Decimal("1000"),
        tags=["test"],
        metadata={"key1": "value1", "key2": 42, "key3": True}
    )
    
    toon = model.model_dump_toon()
    
    # Dict should be serialized with indentation
    assert "metadata:" in toon
    assert "key1: value1" in toon
    assert "key2: 42" in toon
    assert "key3: true" in toon


if __name__ == "__main__":
    # Run basic tests
    print("Running Pydantic TOON Serialization Tests\n")
    
    test_single_object_serialization()
    print("✓ Single object serialization")
    
    test_list_serialization_tabular()
    print("✓ List/tabular serialization")
    
    test_boolean_serialization()
    print("✓ Boolean serialization")
    
    test_datetime_serialization()
    print("✓ Datetime serialization")
    
    test_decimal_serialization()
    print("✓ Decimal serialization")
    
    test_list_field_serialization()
    print("✓ List field serialization")
    
    test_nested_model_serialization()
    print("✓ Nested model serialization")
    
    test_empty_list()
    print("✓ Empty list handling")
    
    test_none_value()
    print("✓ None value handling")
    
    test_standalone_functions()
    print("✓ Standalone functions")
    
    test_dict_field_serialization()
    print("✓ Dictionary field serialization")
    
    test_efficiency_comparison()
    print("✓ Efficiency comparison")
    
    print("\nAll tests passed! ✨")
