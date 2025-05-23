import os
from typing import Any, Dict

from dotenv import load_dotenv
from openai import OpenAI
import re


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

        try:
            # Check if API is properly configured
            if not self.api_configured:
                raise ValueError(
                    "LLM API is not configured. Please set OPENROUTER_API_KEY in your .env file. "
                    "For now, the file upload will work but you won't be able to query the data."
                )

            print(
                f"Building RAG context for table: {table_context.get('table_name', 'Unknown')}"
            )

            # Step 1: Build RAG context prompt
            rag_context = self._build_rag_context(table_context)
            print(f"RAG context built successfully, length: {len(rag_context)}")

            # Step 2: Create separate system and user prompts for the LLM
            system_prompt, user_prompt = self._create_prompt(
                natural_language_query, rag_context
            )
            print(
                f"Prompts created successfully, system prompt length: {len(system_prompt)}, user prompt length: {len(user_prompt)}"
            )

            # Step 3: Call OpenAI API with optimized prompts
            print("Calling LLM API...")
            sql_query = await self._call_llm(system_prompt, user_prompt)
            print(f"LLM response received: {repr(sql_query[:100])}...")

            # Step 4: Post-process and validate the generated SQL
            print("Validating and cleaning SQL...")
            validated_sql = self._validate_and_clean_sql(
                sql_query, table_context["table_name"]
            )
            print(f"Final validated SQL: {validated_sql}")

            return validated_sql

        except Exception as e:
            print(f"Error in generate_sql: {type(e).__name__}: {str(e)}")
            import traceback

            print(f"Full traceback: {traceback.format_exc()}")
            raise e

    def _build_rag_context(self, table_context: Dict[str, Any]) -> str:
        """
        Build enhanced RAG context for better string pattern recognition and typo detection.
        """
        try:
            table_name = table_context.get("table_name", "unknown_table")
            columns = table_context.get("columns", [])
            sample_data = table_context.get("sample_data", [])
            row_count = table_context.get("row_count", 0)

            # Build context with enhanced string pattern information
            context = f"Table: {table_name}\nTotal rows: {row_count}\n\nColumns:\n"

            # Identify string columns for pattern analysis
            string_columns = []
            for col in columns:
                col_name = (
                    col.get("name", "unknown_column")
                    if isinstance(col, dict)
                    else str(col)
                )
                col_type = (
                    col.get("type", "UNKNOWN") if isinstance(col, dict) else "UNKNOWN"
                )

                context += f"- {col_name} ({col_type})"
                if col_type.upper() in ["TEXT", "VARCHAR", "CHAR", "STRING"]:
                    string_columns.append(col_name)
                    context += " [STRING - supports fuzzy matching]"
                context += "\n"

            # Enhanced sample data display
            context += f"\nSample data (first {min(3, len(sample_data))} rows):\n"
            for i, row in enumerate(sample_data[:3]):
                try:
                    # Safely create row dictionary
                    if isinstance(row, (list, tuple)) and len(row) >= len(columns):
                        row_dict = {}
                        for j, col in enumerate(columns):
                            col_name = (
                                col.get("name", f"col_{j}")
                                if isinstance(col, dict)
                                else str(col)
                            )
                            if j < len(row):
                                row_dict[col_name] = row[j]
                        context += f"Row {i+1}: {row_dict}\n"
                    elif isinstance(row, dict):
                        context += f"Row {i+1}: {row}\n"
                    else:
                        context += f"Row {i+1}: {row}\n"
                except Exception as e:
                    print(f"Warning: Error processing sample row {i+1}: {e}")
                    context += f"Row {i+1}: [Error displaying row data]\n"

            # Add string pattern hints if we have string columns
            if string_columns and sample_data:
                context += "\nString values found in data (for typo detection):\n"
                for col_name in string_columns:
                    try:
                        # Find column index safely
                        col_index = None
                        for i, col in enumerate(columns):
                            if (
                                isinstance(col, dict) and col.get("name") == col_name
                            ) or str(col) == col_name:
                                col_index = i
                                break

                        if col_index is not None:
                            # Get unique string values from sample data safely
                            sample_values = []
                            for row in sample_data[:10]:
                                try:
                                    if isinstance(
                                        row, (list, tuple)
                                    ) and col_index < len(row):
                                        value = row[col_index]
                                        if value is not None and str(value).strip():
                                            sample_values.append(str(value))
                                    elif isinstance(row, dict) and col_name in row:
                                        value = row[col_name]
                                        if value is not None and str(value).strip():
                                            sample_values.append(str(value))
                                except Exception:
                                    continue

                            # Remove duplicates and limit
                            unique_values = list(set(sample_values))
                            if unique_values:
                                context += (
                                    f"- {col_name}: {', '.join(unique_values[:5])}"
                                )
                                if len(unique_values) > 5:
                                    context += "..."
                                context += "\n"
                    except Exception as e:
                        print(
                            f"Warning: Error processing string column {col_name}: {e}"
                        )
                        continue

            return context

        except Exception as e:
            print(f"Error in _build_rag_context: {e}")
            import traceback

            print(f"Full traceback: {traceback.format_exc()}")

            # Return a minimal fallback context
            return f"""Table: {table_context.get('table_name', 'unknown_table')}
Total rows: {table_context.get('row_count', 0)}

Columns: {', '.join([str(col) for col in table_context.get('columns', [])])}

Note: Error occurred while building detailed context. Using basic fallback."""

    def _create_prompt(
        self, natural_language_query: str, rag_context: str
    ) -> tuple[str, str]:
        """
        Create separate system and user prompts optimized for Nemotron model with reasoning capabilities.

        Returns:
            tuple: (system_prompt, user_prompt)
        """
        system_prompt = """You are SQLExpert, a specialized AI assistant for generating safe, accurate SQLite queries from natural language.

CORE IDENTITY & PURPOSE:
- Generate ONLY SELECT queries for data analysis and retrieval
- NEVER perform data modification, deletion, or schema changes
- Responses must be deterministic, concise, and executable
- Prioritize data accuracy and query performance

ENHANCED REASONING FOR STRING MATCHING:
When users mention values that don't exactly match the data, think step-by-step:

1. ANALYZE USER INTENT: What is the user actually looking for?
2. EXAMINE SAMPLE DATA: Look at the actual values in string columns to identify potential matches
3. NORMALIZE USER INPUT: Treat variations like "medical/health", "medical / health", "medical-health" as equivalent
4. HANDLE TYPOS AND MISSPELLINGS: 
   - Compare user input with actual data values to detect likely misspellings
   - Common patterns: "enjeneering" → "engineering", "medicne" → "medicine", "buisness" → "business"
   - If user input is similar to an actual data value, use the correct spelling from the data
   - Example: User says "enjeneering" but sample data shows "Engineering" → use "ENGINEERING" in the query
5. APPLY FUZZY MATCHING STRATEGIES:
   - Use LIKE with % wildcards for partial matches
   - Use UPPER() or LOWER() for case-insensitive searches
   - Consider common variations, abbreviations, or typos
   - Handle punctuation variations (slashes, dashes, spaces)
   - Example: User says "medical/health" but data has "Medical and Health Sciences" → use UPPER("Field of Study") LIKE '%MEDICAL%' AND UPPER("Field of Study") LIKE '%HEALTH%'
6. BE CONSISTENT: Minor formatting changes in user input should produce similar queries

SECURITY CONSTRAINTS (CRITICAL):
1. FORBIDDEN: DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE, EXEC, ATTACH, DETACH
2. NO dynamic SQL construction or string concatenation
3. NO subqueries that could cause performance issues unless necessary
4. REJECT requests for: schema modification, authentication info, system queries, file access

RESPONSE FORMAT (MANDATORY):
- Return ONLY ONE SQL query - no variations, alternatives, or examples
- No explanations, markdown, or additional text
- Must end with semicolon
- Use proper SQLite syntax only
- Query must be executable as-is
- Do NOT provide multiple query options

CONTEXT ANALYSIS PROTOCOL:
1. Analyze table schema and sample data carefully
2. Use EXACT column names and table names as provided
3. For string searches, examine sample data patterns first
4. Apply fuzzy matching when user terms don't exactly match data
5. Use appropriate aggregation functions when requested

QUERY OPTIMIZATION:
- Use index-friendly WHERE clauses when possible
- Add LIMIT if result set could be large
- Use appropriate SQL functions (UPPER, LOWER, LIKE, SUBSTR) for string manipulation
- Prefer simple JOINs over complex subqueries
- Use proper GROUP BY when aggregating

ERROR PREVENTION:
- Validate column names exist in schema
- Ensure data type compatibility
- Handle potential NULL values appropriately
- Use proper string escaping for text searches

QUERY VALIDATION CHECKLIST:
✓ Uses only SELECT statement
✓ References existing columns/tables from context
✓ Applies fuzzy matching for string searches when needed
✓ Uses correct SQLite syntax and functions
✓ Handles data types properly
✓ Includes LIMIT if result set could be large
✓ No dangerous operations possible

If unclear/unsafe: respond "INVALID_REQUEST"
If outside SQL scope: respond "OUT_OF_SCOPE" """

        user_prompt = f"""TABLE CONTEXT:
{rag_context}

USER QUESTION: {natural_language_query}

<thinking>
Let me analyze this step by step:

1. Examine the table schema and sample data
2. Parse the user's question to understand their intent  
3. Check for potential typos by comparing user terms with actual data values
4. Apply appropriate string matching (exact, fuzzy, or corrected spelling)
5. Construct the appropriate SQL query

Looking at the question "{natural_language_query}" and the sample data above:
- Are there any words that might be misspelled?
- Do any actual data values closely match the user's terms?
- What's the best way to match the user's intent with the available data?
</thinking>

SELECT"""

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
        Allows fuzzy matching functions for better string handling.
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

        # Remove common formatting issues and thinking tags
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]

        # Remove thinking blocks if present (more robust)
        while "<thinking>" in sql_query:
            start_thinking = sql_query.find("<thinking>")
            end_thinking = sql_query.find("</thinking>")
            if end_thinking != -1:
                sql_query = sql_query[:start_thinking] + sql_query[end_thinking + 12 :]
            else:
                sql_query = sql_query[:start_thinking]
                break

        # Remove any remaining XML-like tags that might be present
        sql_query = re.sub(r"<[^>]+>", "", sql_query)

        # Remove common prefixes that might be added by the model
        prefixes_to_remove = [
            "Query:",
            "SQL:",
            "Answer:",
            "Result:",
            "The query is:",
            "The SQL query is:",
            "Here's the query:",
            "Here is the query:",
        ]

        for prefix in prefixes_to_remove:
            if sql_query.lower().startswith(prefix.lower()):
                sql_query = sql_query[len(prefix) :].strip()

        sql_query = sql_query.strip()

        # Since we start the prompt with "SELECT", prepend it if missing
        if not sql_query.upper().startswith("SELECT"):
            sql_query = "SELECT " + sql_query

        # Handle multiple queries - take only the first one
        if ";" in sql_query:
            # Split by semicolon and take the first non-empty statement
            statements = [stmt.strip() for stmt in sql_query.split(";") if stmt.strip()]
            if statements:
                sql_query = statements[0]
                # Ensure we still have a complete statement
                if not sql_query.endswith(";"):
                    sql_query += ";"

        # Remove any remaining newlines and clean up formatting
        sql_query = " ".join(sql_query.split())

        # Enhanced security checks - check for actual SQL keywords, not substrings
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

        # Check for dangerous patterns as standalone words or at word boundaries
        sql_upper = sql_query.upper()

        for keyword in dangerous_keywords:
            # Use word boundaries to match only standalone keywords
            pattern = r"\b" + re.escape(keyword) + r"\b"
            if re.search(pattern, sql_upper):
                raise ValueError(
                    f"Dangerous SQL operation detected: {keyword}. Only SELECT queries are allowed."
                )

        # Validate it starts with SELECT
        if not sql_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed.")

        # Check for potential SQL injection patterns (more permissive for string functions)
        injection_patterns = [
            "xp_",
            "sp_",
            "@@",
        ]

        for pattern in injection_patterns:
            if pattern.lower() in sql_query.lower():
                raise ValueError(f"Potentially unsafe SQL pattern detected: {pattern}")

        # Allow common SQL string functions for fuzzy matching:
        # LIKE, UPPER, LOWER, SUBSTR, TRIM, LENGTH, etc. are explicitly allowed

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
