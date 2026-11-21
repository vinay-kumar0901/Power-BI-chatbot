# Database schema

Workbook source: `data/BI_GPT_Dashboard_Preview.xlsx`.

The application imports worksheets whose names begin with `Data_` and removes the `Data_` prefix when creating SQLite tables.

## Tables
- Customers: CustomerID, CustomerName, Gender, Age, City, State, CustomerSegment, JoinDate.
- Date: Date, Year, Quarter, MonthNumber, Month, YearMonth, WeekNumber, Day, DayName, IsWeekend.
- Employees: EmployeeID, EmployeeName, Department, JobTitle, Region, HireDate, Manager, TargetAnnual.
- OrderDetails: OrderDetailID, OrderID, ProductID, Quantity, UnitPrice, UnitCost, LineDiscount, ReturnedQuantity.
- Orders: OrderID, OrderDate, CustomerID, EmployeeID, StoreID, Channel, PaymentMethod, OrderStatus, ShippingDays, DiscountRate.
- Products: ProductID, ProductName, Category, SubCategory, Brand, UnitCost, ListPrice, Supplier, ProductRating.
- Stores: StoreID, StoreName, StoreType, City, State, Region, OpeningDate, SquareFeet.

## Relationships
- Orders.CustomerID → Customers.CustomerID
- Orders.EmployeeID → Employees.EmployeeID
- Orders.StoreID → Stores.StoreID
- Orders.OrderDate → Date.Date
- OrderDetails.OrderID → Orders.OrderID
- OrderDetails.ProductID → Products.ProductID

OrderDetails is a line-level fact table. Orders is an order-level fact/header table. Avoid summing order-level values after joining to OrderDetails without controlling for row multiplication.
