Table name: delivery_orders

delivery_id                 int        --id of delivery
order_place_time            timestamp  --time order was placed
predicted_delivery_time     timestamp  --time food is predicted to be delivered
actual_delivery_time        timestamp  --time food is actually delivered
delivery_rating             int        -- delivery rating, scale from 0 to 5
dasher_id                   int        --id of dasher / deliverer
restaurant_id               int        --id of restaurant
consumer_id                 int        --id of consumer

Table name: order_value

delivery_id             int        --id of delivery
sales                   real       --dollar contents of the order

--- Q1. A delivery is flagged as “extremely late” if its actual delivery time is 20 minutes after its predicted delivery time. What is the % of orders that were “extremely late,” grouped by month?
WITH month_data as
(
SELECT delivery_id
, DATE_TRUNC(order_place_time, MONTH) AS OrderMonth
, IF(TIMESTAMPDIFF(actual_delivery_time, predicted_delivery_time, MINUTE)>=20, 1, 0) AS LateDelivery    
)
SELECT OrderMonth
, AVG(LateDelivery) AS LateDeliveryPerc
FROM month_data
GROUP BY OrderMonth
ORDER BY OrderMonth

-----Q2: Looking at Dashers completing their first ever order: what % of Dashers’ first-ever orders have a rating of 0?
With dasher AS
(
SELECT  dasher_id
,  order_place_time
, RANK() OVER (PARTITION BY dasher_id ORDER BY order_place_time) AS OrderRank
, delivery_rating
, IF(delivery_rating = 0, 1, 0) AS ZeroRating  
FROM delivery_orders
)
SELECT AVG(ZeroRating)
FROM dasher
WHERE 1=1
AND OrderRank =1

----- other solution
With dasher AS
(
SELECT  *
, RANK() OVER (PARTITION BY dasher_id ORDER BY order_place_time) AS OrderRank
FROM delivery_orders
)
SELECT COUNT(WHEN delivery_rating =0 THEN dasher_id ELSE NULL END)/COUNT(dasher_id)
FROM dasher
WHERE 1=1
AND OrderRank = 1

--- --Q3: Use the `order_value` table and the `delivery_orders` table to answer the next question. In the year 2020, grouped by month: what % of our DoorDash’s restaurant base fulfilled more than $100 in monthly sales. Assume each restaurant had at least 1 delivery per month for simplicity. 
With res AS
(
SELECT restaurant_id
, DATE_TRUNC (order_place_time, MONTH) AS OrderMonth
, SUM(o.sales) AS MonthlySales
FROM delivery_orders AS d  
LEFT JOIN order_value AS o  
ON d.delivery_id = o.delivery_id 
WHERE 1=1
AND EXTRACT(YEAR FROM order_place_time) = 2020
GROUP BY DATE_TRUNC (order_place_time, MONTH), restaurant_id
)
SELECT OrderMonth
, AVG(IF MonthlySales >=100, 1, 0) AS More100SalesPerc
FROM res

----- Q4. Find the order growth month over month
With mon AS
(
SELECT DATE_TRUNC (order_place_time, MONTH) AS OrderMonth
, COUNT(delivery_id) AS OrderCount
FROM delivery_orders
GROUP BY OrderMonth    
)
SELECT OrderMonth
, (LAG(OrderCount) OVER (ORDER BY OrderMonth)/ OrderCount) AS Growth
FROM mon
ORDER BY OrderMonth

----- Q5. --Q4 : We want to better understand daily order value for Bob’s Burgers (restaurant_id 8) in the period between June 1, 2019 and June 30, 2019 (inclusive): 
---Can you show the aggregate order value Bob’s Burgers received every day during that time period? 
---Can you create a column that displays a rolling sum of Bob’s Burgers aggregate daily ? Example: if we did $50 in order value on June 1st and $50 in order value on June 2nd, our rolling order value to date on June 2nd would be $100. 
WITH order AS
(
SELECT delivery_id
, CAST (order_place_time AS DATE) AS OrderDate
FROM delivery_orders
WHERE 1=1
AND restaurant_id = 8
AND CAST (order_place_time AS DATE) >= "2019-06-01"
AND CAST (order_place_time AS DATE) <= "2019-30-01"     
)
SELECT OrderDate
, COUNT(delivery_id) AS OrderCount
, SUM(OrderCount) OVER (ORDER BY OrderDate ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS CumulativeOrder
FROM order
GROUP BY OrderDate
