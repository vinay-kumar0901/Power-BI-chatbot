from .sql_agent import ask_ollama
from .datasets import schema_for
from .config import ROOT, OLLAMA_REQUEST_TIMEOUT


def answer(question, context, result, history, dashboard, sql_reason='', schema=''):
    system='''You are BI-GPT, a Power BI and analytics copilot. Be accurate, conversational, and concise.
Use only supplied Power BI metadata, database schema, retrieved documents, conversation history, and verified SQL results.
Never invent numeric values, tables, columns, relationships, or DAX definitions.
If the requested value is not available, say exactly what is missing.
IMPORTANT: In this supplied PBIP model, [Net Sales] = [Sales After Line Discount] - [Order Discount Amount]. [Sales After Line Discount] = [Gross Sales] - [Line Discount Amount]. [Order Discount Amount] applies Orders[DiscountRate] after the line discount. These component measures filter Orders to Completed and Shipped. Gross Sales, workbook summary Sales, Net Sales, and Gross Profit are different metrics. Never equate Net Sales with Sales minus operating expenses, cost, profit, or overheads.
For follow-up questions, resolve references using conversation history.'''
    prompt=f'''Selected dashboard: {dashboard}
Database schema:
{schema[:3500]}
Recent conversation:
{history[-2500:]}
Retrieved Power BI context:
{context[:4500] or 'No matching Power BI metadata was retrieved.'}
Verified SQL result (may be absent):
{result or 'No verified SQL result.'}
SQL reasoning:
{sql_reason or 'No SQL note.'}
User question: {question}
Answer in clear language. Use verified SQL results exactly as supplied. For this model, Net Sales is the DAX measure [Sales After Line Discount] - [Order Discount Amount]. Never substitute a workbook summary Sales value. Never claim Net Sales is Sales minus all expenses or overheads. If SQL did not execute, clearly say that a numeric answer is unavailable.'''
    return ask_ollama(prompt,system,timeout=OLLAMA_REQUEST_TIMEOUT,max_tokens=256)
