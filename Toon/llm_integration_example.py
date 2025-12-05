"""
Real-World Example: Using TOON with LLM APIs

This demonstrates how to use TOON serialization to reduce costs and improve
performance when sending data to LLMs like Claude, GPT-4, or other models.
"""

from pydantic import BaseModel, Field
from pydantic_toon import ToonMixin
from typing import List
from datetime import date
import json


# ============================================================================
# Scenario: Analyzing Employee Data with an LLM
# ============================================================================

class Employee(BaseModel, ToonMixin):
    """Employee record."""
    id: int
    name: str
    department: str
    salary: float
    hire_date: date
    performance_score: float = Field(ge=0, le=100)
    years_experience: int


# Sample dataset
employees = [
    Employee(
        id=1, name="Alice Johnson", department="Engineering",
        salary=125000, hire_date=date(2020, 3, 15),
        performance_score=92, years_experience=8
    ),
    Employee(
        id=2, name="Bob Smith", department="Engineering",
        salary=110000, hire_date=date(2021, 6, 20),
        performance_score=88, years_experience=5
    ),
    Employee(
        id=3, name="Charlie Davis", department="Marketing",
        salary=95000, hire_date=date(2019, 1, 10),
        performance_score=85, years_experience=10
    ),
    Employee(
        id=4, name="Diana Chen", department="Marketing",
        salary=98000, hire_date=date(2021, 9, 5),
        performance_score=91, years_experience=6
    ),
    Employee(
        id=5, name="Edward Wilson", department="Sales",
        salary=105000, hire_date=date(2020, 11, 12),
        performance_score=89, years_experience=7
    ),
    Employee(
        id=6, name="Fiona Martinez", department="Sales",
        salary=112000, hire_date=date(2018, 4, 8),
        performance_score=94, years_experience=12
    ),
    Employee(
        id=7, name="George Lee", department="Engineering",
        salary=130000, hire_date=date(2019, 7, 22),
        performance_score=96, years_experience=9
    ),
    Employee(
        id=8, name="Hannah Brown", department="HR",
        salary=88000, hire_date=date(2022, 2, 14),
        performance_score=87, years_experience=4
    ),
]


def create_prompt_json(employees: List[Employee], question: str) -> str:
    """Create a prompt using JSON format (traditional approach)."""
    data_json = json.dumps([emp.model_dump(mode='json') for emp in employees], default=str, indent=2)
    
    prompt = f"""Analyze the following employee data and answer the question.

Employee Data (JSON):
{data_json}

Question: {question}

Please provide a detailed analysis."""
    
    return prompt


def create_prompt_toon(employees: List[Employee], question: str) -> str:
    """Create a prompt using TOON format (optimized approach)."""
    data_toon = Employee.model_dump_toon_list(employees)
    
    prompt = f"""Analyze the following employee data and answer the question.

Employee Data (TOON format):
{data_toon}

Question: {question}

Please provide a detailed analysis."""
    
    return prompt


def compare_approaches():
    """Compare JSON vs TOON for LLM prompts."""
    question = "What is the average salary by department, and which department has the highest average performance score?"
    
    # Create both versions
    prompt_json = create_prompt_json(employees, question)
    prompt_toon = create_prompt_toon(employees, question)
    
    print("=" * 80)
    print("LLM Prompt Comparison: JSON vs TOON")
    print("=" * 80)
    print()
    
    print("Question:", question)
    print()
    
    # JSON version
    print("-" * 80)
    print("JSON Prompt (first 800 chars):")
    print("-" * 80)
    print(prompt_json[:800])
    if len(prompt_json) > 800:
        print("...")
    print()
    
    # TOON version
    print("-" * 80)
    print("TOON Prompt (complete):")
    print("-" * 80)
    print(prompt_toon)
    print()
    
    # Statistics
    print("=" * 80)
    print("Comparison Statistics")
    print("=" * 80)
    
    json_chars = len(prompt_json)
    toon_chars = len(prompt_toon)
    reduction = ((json_chars - toon_chars) / json_chars) * 100
    
    # Rough token estimation (1 token ≈ 4 chars for English)
    json_tokens = json_chars / 4
    toon_tokens = toon_chars / 4
    token_savings = json_tokens - toon_tokens
    
    print(f"JSON Prompt:")
    print(f"  - Characters: {json_chars:,}")
    print(f"  - Est. Tokens: ~{json_tokens:,.0f}")
    print()
    print(f"TOON Prompt:")
    print(f"  - Characters: {toon_chars:,}")
    print(f"  - Est. Tokens: ~{toon_tokens:,.0f}")
    print()
    print(f"Savings:")
    print(f"  - Character reduction: {reduction:.1f}%")
    print(f"  - Est. token savings: ~{token_savings:,.0f} tokens")
    print()
    
    # Cost estimation (using Claude Sonnet 4.5 pricing as example)
    # Input: $3 per million tokens
    cost_per_million = 3.00
    json_cost = (json_tokens / 1_000_000) * cost_per_million
    toon_cost = (toon_tokens / 1_000_000) * cost_per_million
    cost_savings = json_cost - toon_cost
    
    print(f"Cost Estimation (@ ${cost_per_million} per 1M input tokens):")
    print(f"  - JSON cost: ${json_cost:.6f}")
    print(f"  - TOON cost: ${toon_cost:.6f}")
    print(f"  - Savings per query: ${cost_savings:.6f}")
    print()
    
    # Scale it up
    queries_per_day = 1000
    daily_savings = cost_savings * queries_per_day
    monthly_savings = daily_savings * 30
    yearly_savings = daily_savings * 365
    
    print(f"Scaled Savings (at {queries_per_day:,} queries/day):")
    print(f"  - Daily: ${daily_savings:.2f}")
    print(f"  - Monthly: ${monthly_savings:.2f}")
    print(f"  - Yearly: ${yearly_savings:.2f}")
    print()
    
    print("=" * 80)


def pseudo_llm_call_example():
    """
    Pseudo-code showing how to use TOON with actual LLM APIs.
    
    This is not executable - just demonstrates the pattern.
    """
    print("\n" + "=" * 80)
    print("Example: Integration with LLM APIs (Pseudo-code)")
    print("=" * 80)
    print()
    
    example_code = '''
# Example 1: With Anthropic's Claude API
import anthropic

client = anthropic.Anthropic(api_key="your-api-key")

# Use TOON format for data
data_toon = Employee.model_dump_toon_list(employees)

message = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": f"""Analyze this employee data:

{data_toon}

Calculate the average salary by department."""
    }]
)

print(message.content)


# Example 2: With OpenAI's GPT API
from openai import OpenAI

client = OpenAI(api_key="your-api-key")

data_toon = Employee.model_dump_toon_list(employees)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{
        "role": "user",
        "content": f"""Analyze this employee data:

{data_toon}

Calculate the average salary by department."""
    }]
)

print(response.choices[0].message.content)


# Example 3: With any LLM via LangChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

# Define prompt template with TOON data
template = """Analyze the following employee data in TOON format:

{data_toon}

{question}

Provide a detailed analysis with specific numbers."""

prompt = PromptTemplate(
    input_variables=["data_toon", "question"],
    template=template
)

llm = OpenAI(model_name="gpt-4")

# Use TOON format
data_toon = Employee.model_dump_toon_list(employees)

result = llm(prompt.format(
    data_toon=data_toon,
    question="What is the correlation between years of experience and performance score?"
))

print(result)
'''
    
    print(example_code)
    print()


def main():
    """Run the demonstration."""
    print()
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "TOON + LLM Integration Example" + " " * 27 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    compare_approaches()
    pseudo_llm_call_example()
    
    print("=" * 80)
    print("Key Takeaways")
    print("=" * 80)
    print()
    print("✅ TOON reduces prompt size by 50-60%")
    print("✅ Lower costs for every API call")
    print("✅ Faster inference due to fewer tokens")
    print("✅ Easy to integrate with existing Pydantic models")
    print("✅ Works with Claude, GPT-4, and other LLMs")
    print()
    print("💡 Best for: Structured data, tabular datasets, frequent LLM calls")
    print("💡 Savings scale with usage - higher volume = greater impact")
    print()


if __name__ == "__main__":
    main()
