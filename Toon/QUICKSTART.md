# Quick Start Guide: Pydantic TOON Integration

## Installation

1. **Copy the module to your project:**
   ```bash
   cp pydantic_toon.py your_project/
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage (3 Methods)

### Method 1: ToonMixin (Recommended for new code)

```python
from pydantic import BaseModel
from pydantic_toon import ToonMixin

class Employee(BaseModel, ToonMixin):
    id: int
    name: str
    department: str
    salary: float

# Single object
emp = Employee(id=1, name="Alice", department="Engineering", salary=120000)
print(emp.model_dump_toon())

# Multiple objects (tabular)
employees = [
    Employee(id=1, name="Alice", department="Engineering", salary=120000),
    Employee(id=2, name="Bob", department="Marketing", salary=95000),
]
print(Employee.model_dump_toon_list(employees))
```

**Output:**
```
id: 1
name: Alice
department: Engineering
salary: 120000

[2]{id,name,department,salary}:
  1,Alice,Engineering,120000
  2,Bob,Marketing,95000
```

### Method 2: Standalone Functions (For existing models)

```python
from pydantic import BaseModel
from pydantic_toon import model_dump_toon, models_dump_toon

class Employee(BaseModel):  # No ToonMixin needed
    id: int
    name: str
    department: str
    salary: float

emp = Employee(id=1, name="Alice", department="Engineering", salary=120000)

# Single object
toon_str = model_dump_toon(emp)

# Multiple objects
employees = [emp, ...]
toon_str = models_dump_toon(employees)
```

### Method 3: Monkey Patch (Global enablement)

```python
from pydantic import BaseModel
from pydantic_toon import patch_pydantic_toon

# Call once at application startup
patch_pydantic_toon()

# Now ALL Pydantic models have .model_dump_toon()
class Employee(BaseModel):
    id: int
    name: str
    department: str
    salary: float

emp = Employee(id=1, name="Alice", department="Engineering", salary=120000)
print(emp.model_dump_toon())  # Works!
```

## Real-World Example: LLM Integration

```python
import anthropic
from pydantic_toon import ToonMixin

class Employee(BaseModel, ToonMixin):
    id: int
    name: str
    department: str
    salary: float

# Your data
employees = [Employee(...), Employee(...), ...]

# Use TOON format instead of JSON
data_toon = Employee.model_dump_toon_list(employees)

# Send to Claude (50-60% fewer tokens!)
client = anthropic.Anthropic(api_key="your-key")
message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"Analyze this employee data:\n\n{data_toon}\n\nCalculate average salary by department."
    }]
)

print(message.content)
```

## Running Examples and Tests

```bash
# Run comprehensive examples
python examples_pydantic_toon.py

# Run test suite
python test_pydantic_toon.py

# See LLM integration demo
python llm_integration_example.py
```

## Key Benefits

| Aspect | JSON | TOON | Savings |
|--------|------|------|---------|
| 10 employees | ~950 chars | ~420 chars | 55.8% |
| 20 employees | ~1,900 chars | ~840 chars | 55.8% |
| 100 employees | ~9,500 chars | ~4,200 chars | 55.8% |

**Cost Impact** (Claude Sonnet 4.5 @ $3/M input tokens):
- 1,000 queries/day: **~$280/year savings**
- 10,000 queries/day: **~$2,800/year savings**

## When to Use TOON

✅ **Use TOON when:**
- Sending structured data to LLMs
- Cost optimization is important
- Working with tabular/repetitive data
- High-frequency LLM API calls

❌ **Stick with JSON when:**
- Interoperating with non-LLM systems
- Complex nested structures dominate
- Human editing is the primary concern

## Architecture Alignment (KISS + SRP)

```
Core Serializer (Single Responsibility)
    └── ToonSerializer - handles all TOON conversion logic

Integration Layer (Separation of Concerns)
    ├── ToonMixin - optional convenience for new models
    ├── Standalone functions - for existing models
    └── Monkey patch - for global enablement

Zero Breaking Changes
    └── Existing model_dump() and model_dump_json() unchanged
```

## Next Steps

1. Copy `pydantic_toon.py` to your project
2. Choose your integration method (Mixin, Functions, or Patch)
3. Update your LLM prompts to use TOON format
4. Monitor token usage and cost savings

## Need Help?

See:
- `README.md` - Full documentation
- `examples_pydantic_toon.py` - Comprehensive examples
- `llm_integration_example.py` - LLM integration patterns
- `test_pydantic_toon.py` - Test suite with edge cases
