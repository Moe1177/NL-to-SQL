import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI


class LLMService:
    """
    Service for generating SQL queries from natural language using LLM with RAG.
    This is where you'll implement your LLM integration and RAG logic.
    """

    def __init__(self):
        load_dotenv()
        self.client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        pass

    async def generate_sql(
        self, natural_language_query: str, table_context: Dict[str, Any]
    ) -> str:
        """
        Generate SQL query from natural language using RAG context.

        Args:
            natural_language_query: User's natural language question
            table_context: Table schema and sample data for RAG context

        Returns:
            Generated SQL query string

        TODO: Implement your LLM logic here:
        """

        # TODO: 1. Build RAG context prompt
        rag_context = self._build_rag_context(table_context)

        # TODO: 2. Create the full prompt for the LLM
        full_prompt = self._create_prompt(natural_language_query, rag_context)

        # TODO: 3. Call your LLM API
        sql_query = await self._call_llm(full_prompt)

        # TODO: 4. Post-process and validate the generated SQL
        validated_sql = self._validate_and_clean_sql(
            sql_query, table_context["table_name"]
        )

        return validated_sql

    def _build_rag_context(self, table_context: Dict[str, Any]) -> str:
        """
        Build RAG context string from table information.

        TODO: Customize this method to create the best context for your LLM:
        - Include column names and types
        - Add sample data rows
        - Include column statistics if available
        - Add business context or column descriptions
        """
        table_name = table_context["table_name"]
        columns = table_context["columns"]
        sample_data = table_context["sample_data"]
        row_count = table_context["row_count"]

        # Basic context building (expand this based on your needs)
        context = f"""
                    Table: {table_name}
                    Total rows: {row_count}

                Columns:
                """
        for col in columns:
            context += f"- {col['name']} ({col['type']})\n"

        context += "\nSample data:\n"
        for i, row in enumerate(sample_data[:3]):  # Show first 3 rows
            context += f"Row {i+1}: {row}\n"

        return context

    def _create_prompt(self, natural_language_query: str, rag_context: str) -> str:
        """
        Create the full prompt for the LLM.

        TODO: Design your prompt template here:
        - Include clear instructions for SQL generation
        - Specify the SQL dialect (SQLite in this case)
        - Include examples of good queries
        - Add constraints and safety instructions
        """
        prompt = f"""
You are a SQL expert. Generate a SQLite query based on the user's natural language question.

CONTEXT INFORMATION:
{rag_context}

RULES:
1. Only generate SELECT queries (no INSERT, UPDATE, DELETE, DROP, etc.)
2. Use proper SQLite syntax
3. Use the exact table and column names provided in the context
4. Return only the SQL query without explanations
5. Ensure the query is safe and doesn't contain any malicious code

USER QUESTION: {natural_language_query}

SQL QUERY:
"""
        return prompt

    async def _call_llm(self, prompt: str) -> str:
        """
        Call your LLM API with the constructed prompt.

        TODO: Implement your LLM API call here:
        """

        # PLACEHOLDER - Replace with your actual LLM API call
        # Examples:

        # OpenAI API call:
        # response = await openai.ChatCompletion.acreate(
        #     model="gpt-4",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content

        # Anthropic API call:
        # response = await anthropic.messages.create(
        #     model="claude-3-sonnet-20240229",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.content[0].text

        # Local model (Ollama) example:
        # response = requests.post(
        #     "http://localhost:11434/api/generate",
        #     json={"model": "your-model", "prompt": prompt}
        # )
        # return response.json()["response"]

        # FOR TESTING PURPOSES - Remove this and implement your LLM call
        return f"SELECT * FROM {prompt.split('Table: ')[1].split()[0]} LIMIT 10;"

    def _validate_and_clean_sql(self, sql_query: str, table_name: str) -> str:
        """
        Validate and clean the generated SQL query.

        TODO: Add comprehensive SQL validation:
        - Check for dangerous SQL operations
        - Validate table names and column names
        - Ensure proper SQL syntax
        - Add query performance checks
        """

        # Basic cleaning
        sql_query = sql_query.strip()

        # Remove common formatting issues
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]

        sql_query = sql_query.strip()

        # Basic safety checks
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "CREATE",
            "TRUNCATE",
        ]
        sql_upper = sql_query.upper()

        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(f"Dangerous SQL operation detected: {keyword}")

        # Ensure query ends with semicolon
        if not sql_query.endswith(";"):
            sql_query += ";"

        return sql_query
