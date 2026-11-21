import unittest
from app.sql_agent import propose_sql
from app.main import _format_net_sales_answer

SCHEMA = """TABLE OrderDetails: OrderID INTEGER, ProductID INTEGER, Quantity INTEGER, UnitPrice REAL, LineDiscount REAL
TABLE Orders: OrderID INTEGER, OrderStatus TEXT, DiscountRate REAL
TABLE Products: ProductID INTEGER, Category TEXT"""

class NetSalesTests(unittest.TestCase):
    def test_net_sales_by_category_sql(self):
        sql, reason = propose_sql('What is the Net Sales by categories?', SCHEMA, '', '')
        self.assertIn('JOIN Products AS p', sql)
        self.assertIn('GROUP BY p.Category', sql)
        self.assertIn("IN ('Completed', 'Shipped')", sql)
        self.assertIn('(1 - COALESCE(od.LineDiscount, 0))', sql)
        self.assertIn('(1 - COALESCE(o.DiscountRate, 0))', sql)

    def test_net_sales_by_category_answer(self):
        answer = _format_net_sales_answer('Net Sales by category', {'rows':[ {'Category':'A','NetSales':125.5}, {'Category':'B','NetSales':74.5} ]}, '')
        self.assertIn('125.50', answer)
        self.assertIn('74.50', answer)
        self.assertIn('200.00', answer)

if __name__ == '__main__':
    unittest.main()
