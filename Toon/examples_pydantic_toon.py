"""
Comprehensive Examples: Pydantic TOON Serialization

This file demonstrates various real-world use cases for TOON serialization
with Pydantic v2 models.
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic_toon import ToonMixin, patch_pydantic_toon
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal
import json


# ============================================================================
# Example 1: Basic Employee Database (from article)
# ============================================================================

class Employee(BaseModel, ToonMixin):
    """Employee model matching the article's example."""
    id: int
    name: str
    department: str
    salary: float


def example_basic_employees():
    """Replicate the article's employee example."""
    print("=" * 70)
    print("Example 1: Basic Employee Database (Article Example)")
    print("=" * 70)
    
    employees = [
        Employee(id=1, name="Alice", department="Engineering", salary=120000),
        Employee(id=2, name="Bob", department="Marketing", salary=95000),
        Employee(id=3, name="Charlie", department="Engineering", salary=110000),
    ]
    
    print("\nJSON Format:")
    print("-" * 70)
    json_str = json.dumps([emp.model_dump() for emp in employees], indent=2)
    print(json_str)
    
    print("\nTOON Format:")
    print("-" * 70)
    toon_str = Employee.model_dump_toon_list(employees)
    print(toon_str)
    
    print("\nSize Comparison:")
    print(f"  JSON: {len(json_str)} characters")
    print(f"  TOON: {len(toon_str)} characters")
    print(f"  Reduction: {((len(json_str) - len(toon_str)) / len(json_str) * 100):.1f}%")
    print()


# ============================================================================
# Example 2: E-commerce Order System
# ============================================================================

class OrderItem(BaseModel, ToonMixin):
    """Individual item in an order."""
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    discount: float = 0.0


class Order(BaseModel, ToonMixin):
    """Customer order with multiple items."""
    order_id: int
    customer_name: str
    order_date: date
    items: List[OrderItem]
    total_amount: Decimal
    status: str = "pending"


def example_ecommerce_orders():
    """Demonstrate TOON with e-commerce data."""
    print("=" * 70)
    print("Example 2: E-commerce Order System")
    print("=" * 70)
    
    orders = [
        Order(
            order_id=1001,
            customer_name="John Doe",
            order_date=date(2024, 11, 15),
            items=[
                OrderItem(product_id=101, product_name="Laptop", quantity=1, 
                         unit_price=Decimal("1299.99"), discount=0.1),
                OrderItem(product_id=102, product_name="Mouse", quantity=2, 
                         unit_price=Decimal("29.99"), discount=0.0),
            ],
            total_amount=Decimal("1229.97"),
            status="shipped"
        ),
        Order(
            order_id=1002,
            customer_name="Jane Smith",
            order_date=date(2024, 11, 16),
            items=[
                OrderItem(product_id=103, product_name="Keyboard", quantity=1, 
                         unit_price=Decimal("89.99"), discount=0.0),
            ],
            total_amount=Decimal("89.99"),
            status="pending"
        ),
    ]
    
    print("\nSingle Order (Nested Structure):")
    print("-" * 70)
    print(orders[0].model_dump_toon())
    
    print("\nMultiple Orders (Tabular):")
    print("-" * 70)
    # For tabular format of orders (simplified view)
    simple_orders = [
        {"order_id": o.order_id, "customer": o.customer_name, 
         "date": o.order_date, "total": o.total_amount, "status": o.status}
        for o in orders
    ]
    
    class SimpleOrder(BaseModel, ToonMixin):
        order_id: int
        customer: str
        date: date
        total: Decimal
        status: str
    
    simple_order_models = [SimpleOrder(**o) for o in simple_orders]
    print(SimpleOrder.model_dump_toon_list(simple_order_models))
    print()


# ============================================================================
# Example 3: User Analytics Dashboard
# ============================================================================

class UserMetrics(BaseModel, ToonMixin):
    """User engagement metrics."""
    user_id: int
    username: str
    sessions: int
    page_views: int
    avg_session_duration: float  # minutes
    conversion_rate: float  # percentage
    last_login: datetime
    is_premium: bool


def example_analytics_dashboard():
    """Demonstrate TOON for analytics data."""
    print("=" * 70)
    print("Example 3: User Analytics Dashboard")
    print("=" * 70)
    
    users = [
        UserMetrics(
            user_id=1, username="user123", sessions=45, page_views=320,
            avg_session_duration=12.5, conversion_rate=3.2,
            last_login=datetime(2024, 11, 17, 14, 30),
            is_premium=True
        ),
        UserMetrics(
            user_id=2, username="user456", sessions=23, page_views=180,
            avg_session_duration=8.7, conversion_rate=1.8,
            last_login=datetime(2024, 11, 17, 9, 15),
            is_premium=False
        ),
        UserMetrics(
            user_id=3, username="user789", sessions=67, page_views=520,
            avg_session_duration=15.3, conversion_rate=4.5,
            last_login=datetime(2024, 11, 17, 16, 45),
            is_premium=True
        ),
    ]
    
    print("\nUser Metrics (TOON Tabular Format):")
    print("-" * 70)
    toon = UserMetrics.model_dump_toon_list(users)
    print(toon)
    
    print("\nJSON Format (for comparison):")
    print("-" * 70)
    json_str = json.dumps([u.model_dump(mode='json') for u in users], indent=2, default=str)
    print(json_str[:500] + "..." if len(json_str) > 500 else json_str)
    
    print(f"\nJSON size: {len(json_str)} chars")
    print(f"TOON size: {len(toon)} chars")
    print(f"Reduction: {((len(json_str) - len(toon)) / len(json_str) * 100):.1f}%")
    print()


# ============================================================================
# Example 4: Database Query Results
# ============================================================================

class QueryResult(BaseModel, ToonMixin):
    """Result from a database query."""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    table_name: str
    row_count: int
    columns: List[str]
    query_time_ms: float
    timestamp: datetime


def example_database_queries():
    """Demonstrate TOON for database query results."""
    print("=" * 70)
    print("Example 4: Database Query Results")
    print("=" * 70)
    
    queries = [
        QueryResult(
            table_name="employees",
            row_count=1250,
            columns=["id", "name", "department", "salary", "hire_date"],
            query_time_ms=45.3,
            timestamp=datetime.now()
        ),
        QueryResult(
            table_name="orders",
            row_count=8934,
            columns=["order_id", "customer_id", "order_date", "total"],
            query_time_ms=123.7,
            timestamp=datetime.now()
        ),
        QueryResult(
            table_name="products",
            row_count=456,
            columns=["product_id", "name", "price", "stock"],
            query_time_ms=12.1,
            timestamp=datetime.now()
        ),
    ]
    
    print("\nQuery Results (TOON Format):")
    print("-" * 70)
    print(QueryResult.model_dump_toon_list(queries))
    print()


# ============================================================================
# Example 5: Using Monkey Patch (No Mixin Required)
# ============================================================================

def example_monkey_patch():
    """Demonstrate using patch_pydantic_toon() for all models."""
    print("=" * 70)
    print("Example 5: Monkey Patching (No Mixin Required)")
    print("=" * 70)
    
    # Models defined WITHOUT ToonMixin
    class Product(BaseModel):
        id: int
        name: str
        price: Decimal
        in_stock: bool
    
    class Category(BaseModel):
        id: int
        name: str
        products: List[Product]
    
    # Enable TOON for ALL Pydantic models
    patch_pydantic_toon()
    
    products = [
        Product(id=1, name="Laptop", price=Decimal("1299.99"), in_stock=True),
        Product(id=2, name="Mouse", price=Decimal("29.99"), in_stock=True),
        Product(id=3, name="Keyboard", price=Decimal("89.99"), in_stock=False),
    ]
    
    category = Category(id=1, name="Electronics", products=products)
    
    print("\nCategory with Nested Products:")
    print("-" * 70)
    print(category.model_dump_toon())
    
    print("\nProducts List (Tabular):")
    print("-" * 70)
    print(Product.model_dump_toon_list(products))
    print()


# ============================================================================
# Example 6: LLM Prompt Optimization
# ============================================================================

def example_llm_prompt():
    """Demonstrate token efficiency for LLM prompts."""
    print("=" * 70)
    print("Example 6: LLM Prompt Optimization")
    print("=" * 70)
    
    # Create a larger dataset
    employees = [
        Employee(
            id=i,
            name=f"Employee_{i:03d}",
            department=["Engineering", "Marketing", "Sales", "HR"][i % 4],
            salary=80000 + (i * 5000)
        )
        for i in range(1, 21)  # 20 employees
    ]
    
    # JSON version
    json_data = json.dumps([emp.model_dump() for emp in employees])
    
    # TOON version
    toon_data = Employee.model_dump_toon_list(employees)
    
    print(f"\n20 Employees - Format Comparison:")
    print("-" * 70)
    print(f"JSON characters: {len(json_data)}")
    print(f"TOON characters: {len(toon_data)}")
    print(f"Reduction: {((len(json_data) - len(toon_data)) / len(json_data) * 100):.1f}%")
    
    # Rough token estimation (1 token ≈ 4 chars for English text)
    json_tokens = len(json_data) / 4
    toon_tokens = len(toon_data) / 4
    
    print(f"\nEstimated Tokens:")
    print(f"JSON: ~{json_tokens:.0f} tokens")
    print(f"TOON: ~{toon_tokens:.0f} tokens")
    print(f"Token savings: ~{json_tokens - toon_tokens:.0f} tokens")
    
    # Cost estimation (example: $0.003 per 1K tokens)
    cost_per_1k = 0.003
    json_cost = (json_tokens / 1000) * cost_per_1k
    toon_cost = (toon_tokens / 1000) * cost_per_1k
    
    print(f"\nEstimated Cost (@ ${cost_per_1k} per 1K tokens):")
    print(f"JSON: ${json_cost:.6f}")
    print(f"TOON: ${toon_cost:.6f}")
    print(f"Savings: ${json_cost - toon_cost:.6f} ({((json_cost - toon_cost) / json_cost * 100):.1f}%)")
    
    print("\nTOON Preview (first 500 chars):")
    print("-" * 70)
    print(toon_data[:500])
    print()


# ============================================================================
# Main Execution
# ============================================================================

def main():
    """Run all examples."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "Pydantic TOON Serialization Examples" + " " * 15 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    example_basic_employees()
    example_ecommerce_orders()
    example_analytics_dashboard()
    example_database_queries()
    example_monkey_patch()
    example_llm_prompt()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
