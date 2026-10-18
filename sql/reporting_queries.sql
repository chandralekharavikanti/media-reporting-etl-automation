-- Daily traffic
SELECT date, SUM(sessions) AS sessions, SUM(pageviews) AS pageviews FROM traffic GROUP BY date ORDER BY date;
-- Monthly booked advertising revenue
SELECT substr(date,1,7) AS month, product, SUM(booked_revenue) AS booked_revenue FROM bookings GROUP BY month, product ORDER BY month, product;
-- Print circulation
SELECT substr(issue_date,1,7) AS month, publication, SUM(circulation) AS copies FROM circulation GROUP BY month,publication;
