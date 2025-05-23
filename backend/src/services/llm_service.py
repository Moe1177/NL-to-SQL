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

        # Check for required environment variables
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL")
        model = os.getenv("MODEL")

        if not api_key:
            print("Warning: OPENROUTER_API_KEY not found in environment variables")
            print(
                "Please create a .env file in the backend directory with your API key"
            )

        if not base_url:
            print("Warning: OPENROUTER_BASE_URL not found, using default")
            base_url = "https://openrouter.ai/api/v1"

        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.api_configured = api_key != "placeholder_key"

    async def generate_sql(
        self, natural_language_query: str, table_context: Dict[str, Any]
    ) -> str:
        print("generate_sql")
        """
        Generate SQL query from natural language using RAG context.

        Args:
            natural_language_query: User's natural language question
            table_context: Table schema and sample data for RAG context

        Returns:
            Generated SQL query string
        """

        # Check if API is properly configured
        if not self.api_configured:
            raise ValueError(
                "LLM API is not configured. Please set OPENROUTER_API_KEY in your .env file. "
                "For now, the file upload will work but you won't be able to query the data."
            )

        # Step 1: Build RAG context prompt
        rag_context = self._build_rag_context(table_context)

        # Step 2: Create separate system and user prompts for the LLM
        system_prompt, user_prompt = self._create_prompt(
            natural_language_query, rag_context
        )

        # Step 3: Call OpenAI API with optimized prompts
        sql_query = await self._call_llm(system_prompt, user_prompt)

        # Step 4: Post-process and validate the generated SQL
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
        for i, row in enumerate(sample_data[:2]):  # Show first 2 rows
            context += f"Row {i+1}: {row}\n"

        return context

    def _create_prompt(
        self, natural_language_query: str, rag_context: str
    ) -> tuple[str, str]:
        """
        Create separate system and user prompts optimized for Nemotron model with reasoning capabilities.

        Returns:
            tuple: (system_prompt, user_prompt)
        """
        system_prompt = """You are SQLExpert, an AI that generates safe SQLite SELECT queries from natural language.

CORE RULES:
- ONLY generate SELECT queries (no DROP/DELETE/UPDATE/INSERT/ALTER/CREATE/TRUNCATE/EXEC)
- Return ONLY the SQL query, no explanations
- Must end with semicolon
- Use exact table/column names from provided schema

REASONING MODE: Think step-by-step about the user's intent, especially for string matching:

1. FUZZY STRING MATCHING: When user mentions values that don't exactly match data:
   - Use LIKE with % wildcards for partial matches
   - Use UPPER() or LOWER() for case-insensitive searches  
   - Consider common variations, abbreviations, or typos
   - Example: "john" could match "John Smith" using LIKE '%john%'

2. CONTEXT ANALYSIS:
   - Examine sample data to understand value patterns
   - Infer relationships between user terms and actual column values
   - Apply domain knowledge (e.g., "USA" = "United States")

3. QUERY CONSTRUCTION:
   - Use appropriate WHERE clauses with flexible matching
   - Add LIMIT if results could be large
   - Handle NULLs appropriately
   - Optimize for performance

SECURITY: Reject requests for schema changes, authentication, system info, or file access.

ERROR RESPONSES:
- "INVALID_REQUEST" for unclear/unsafe requests
- "OUT_OF_SCOPE" for non-SQL requests"""

        user_prompt = f"""<thinking>
Let me analyze this request step by step:

1. First, I'll examine the table schema and sample data to understand the structure
2. Then I'll parse the user's natural language query to identify their intent
3. I'll look for any approximate string matches needed
4. Finally, I'll construct an appropriate SQL query

TABLE CONTEXT:
{rag_context}

USER QUESTION: {natural_language_query}

Now let me think about what the user is asking for and how to match it with the available data...
</thinking>

Based on the table context and user question above, generate the SQLite query:"""

        return system_prompt, user_prompt

    async def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """
        Call OpenAI API with the constructed prompts, optimized for Nemotron model.

        Args:
            system_prompt: The system instructions for the LLM
            user_prompt: The user query with context

        Returns:
            Generated SQL query string
        """
        try:
            response = self.client.chat.completions.create(
                model=os.getenv("MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1:free"),
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,  # Slightly higher for more creative string matching
                max_tokens=1000,  # Increased for reasoning + query
                top_p=0.95,  # Higher for better reasoning diversity
                extra_body={"thinking": True},  # Enable detailed thinking for Nemotron
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"LLM API call failed: {str(e)}")

    def _validate_and_clean_sql(self, sql_query: str, table_name: str) -> str:
        """
        Validate and clean the generated SQL query with enhanced security checks.
        """
        # Handle special responses
        sql_query = sql_query.strip()

        if sql_query == "INVALID_REQUEST":
            raise ValueError(
                "The request could not be translated to a valid SQL query. Please rephrase your question."
            )

        if sql_query == "OUT_OF_SCOPE":
            raise ValueError(
                "This request is outside the scope of SQL query generation. Please ask a question about your data."
            )

        # Remove common formatting issues
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]

        sql_query = sql_query.strip()

        # Enhanced security checks
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "UPDATE",
            "INSERT",
            "ALTER",
            "CREATE",
            "TRUNCATE",
            "EXEC",
            "EXECUTE",
            "ATTACH",
            "DETACH",
            "PRAGMA",
            "VACUUM",
        ]

        # Check for dangerous patterns
        sql_upper = sql_query.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise ValueError(
                    f"Dangerous SQL operation detected: {keyword}. Only SELECT queries are allowed."
                )

        # Validate it starts with SELECT
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed.")

        # Check for potential SQL injection patterns
        injection_patterns = [
            "--",
            "/*",
            "*/",
            "xp_",
            "sp_",
            "@@",
            "char(",
            "ascii(",
            "substring(",
        ]

        for pattern in injection_patterns:
            if pattern.lower() in sql_query.lower():
                # Allow legitimate uses of substring and other functions
                if pattern in ["substring("] and "SELECT" in sql_upper:
                    continue
                raise ValueError(f"Potentially unsafe SQL pattern detected: {pattern}")

        # Validate table name is referenced
        if table_name.lower() not in sql_query.lower():
            raise ValueError(f"Query must reference the table '{table_name}'")

        # Ensure query ends with semicolon
        if not sql_query.endswith(";"):
            sql_query += ";"

        # Basic syntax validation - check for balanced parentheses
        if sql_query.count("(") != sql_query.count(")"):
            raise ValueError("SQL query has unbalanced parentheses")

        return sql_query
