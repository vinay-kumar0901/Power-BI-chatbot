POWER BI SALES PRACTICE DATASET

Files:
1. Customers.csv      - 1,200 rows
2. Products.csv       - 1,200 rows
3. Employees.csv      - 1,000 rows
4. Stores.csv         - 1,000 rows
5. Orders.csv         - 5,000 rows
6. OrderDetails.csv   - 10,000 rows
7. Date.csv           - 1,826 rows

Recommended model:
Date[Date] 1 -> * Orders[OrderDate]
Customers[CustomerID] 1 -> * Orders[CustomerID]
Employees[EmployeeID] 1 -> * Orders[EmployeeID]
Stores[StoreID] 1 -> * Orders[StoreID]
Orders[OrderID] 1 -> * OrderDetails[OrderID]
Products[ProductID] 1 -> * OrderDetails[ProductID]

Main measures to practice:
Sales = SUMX(OrderDetails, OrderDetails[Quantity] * OrderDetails[UnitPrice] * (1 - OrderDetails[LineDiscount]))
Cost = SUMX(OrderDetails, OrderDetails[Quantity] * OrderDetails[UnitCost])
Profit = [Sales] - [Cost]
Profit % = DIVIDE([Profit], [Sales])
Orders = DISTINCTCOUNT(Orders[OrderID])
Units Sold = SUM(OrderDetails[Quantity])
Returned Units = SUM(OrderDetails[ReturnedQuantity])
Average Order Value = DIVIDE([Sales], [Orders])

Suggested Power BI topics:
Bookmarks, navigation buttons, tooltip pages, slicers, sync slicers,
conditional formatting, drillthrough, dynamic titles, field parameters,
Power Query transformations, basic DAX, time intelligence,
RLS, Performance Analyzer, Calculation Groups + Tabular Editor,
and an end-to-end executive sales dashboard.
