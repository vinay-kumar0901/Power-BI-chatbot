# Metric definitions

The code's default sales metrics are based on OrderDetails:
- Net Sales = [Gross Sales] - [Line Discount Amount] - [Order Discount Amount]. For each eligible order line this is Quantity × UnitPrice × (1 − LineDiscount) × (1 − Orders[DiscountRate]). The supplied PBIP measure filters Orders to OrderStatus Completed or Shipped.
- Cost = SUM(Quantity * UnitCost).
- Profit = Net Sales - Cost.
- Profit Margin = Profit / Net Sales.
- Units Sold = SUM(Quantity - ReturnedQuantity).
- Orders = COUNT(DISTINCT Orders.OrderID).
- Customers = COUNT(DISTINCT Orders.CustomerID).
- Average Order Value = Net Sales / distinct order count.

These definitions are sample-project choices. The exact Net Sales DAX measure is defined in the PBIP semantic model's Measure table.tmdl; use that measure rather than substituting the workbook's pre-aggregated Sales columns. Confirm whether cancelled/returned orders should be excluded before using the figures in a business setting. The starter code includes all order statuses unless a query explicitly filters them.
