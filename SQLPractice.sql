Table name: delivery_orders

delivery_id                 int        --id of delivery
order_place_time            timestamp  --time order was placed
predicted_delivery_time     timestamp  --time food is predicted to be delivered
actual_delivery_time        timestamp  --time food is actually delivered
delivery_rating             int        -- delivery rating, scale from 0 to 5
dasher_id                   int        --id of dasher / deliverer
restaurant_id               int        --id of restaurant
consumer_id                 int        --id of consumer

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