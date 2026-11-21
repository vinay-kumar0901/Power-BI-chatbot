# BI-GPT Retail Business Glossary

- Sales: dashboard display label used by the summary worksheets. For transaction-level Net Sales, use the semantic model's DAX measure: line sales after LineDiscount and Orders[DiscountRate], restricted to Completed and Shipped orders.
- Cost: sum of quantity × unit cost for order lines.
- Net Sales: [Sales After Line Discount] - [Order Discount Amount], matching the PBIP DAX measure. It is not gross Sales and does not mean revenue after subtracting operating expenses.
- Profit: Net Sales minus Total Cost.
- Profit margin: profit divided by sales.
- Order: one unique OrderID in the Orders table.
- Units sold: quantity from OrderDetails, net of returned quantity where stated by a metric.
- Customer: unique CustomerID.
- Product: unique ProductID.
- Store: unique StoreID.
- Channel: order acquisition/sales channel, such as Retail, Online, Wholesale or Marketplace.
- Order status: lifecycle status such as Completed, Shipped, Cancelled or Returned.
- Region: store sales region from Stores.
