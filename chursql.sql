-- Удаляем таблицу если она есть (чтобы пересоздать)
DROP TABLE IF EXISTS customers;

-- Создаем таблицу с правильными названиями колонок (как в CSV)
CREATE TABLE customers (
    customerID VARCHAR(50),
    gender VARCHAR(10),
    SeniorCitizen INT,
    Partner VARCHAR(10),
    Dependents VARCHAR(10),
    tenure INT,
    PhoneService VARCHAR(10),
    MultipleLines VARCHAR(20),
    InternetService VARCHAR(20),
    OnlineSecurity VARCHAR(20),
    OnlineBackup VARCHAR(20),
    DeviceProtection VARCHAR(20),
    TechSupport VARCHAR(20),
    StreamingTV VARCHAR(20),
    StreamingMovies VARCHAR(20),
    Contract VARCHAR(20),
    PaperlessBilling VARCHAR(10),
    PaymentMethod VARCHAR(50),
    MonthlyCharges NUMERIC(10,2),
    TotalCharges VARCHAR(20), -- Сначала как текст, потом преобразуем
    Churn VARCHAR(10)
);

-- Простые запросы для анализа (с правильными названиями колонок)
COPY customers 
FROM '/Users/admin/Downloads/WA_Fn-UseC_-Telco-Customer-Churn.csv' 
DELIMITER ',' 
CSV HEADER;
-- 1. Сколько всего клиентов?
SELECT COUNT(*) as total_customers FROM customers;

-- 2. Сколько клиентов ушло?
SELECT 
    COUNT(*) as total_customers,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) as churned_customers,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as churn_rate
FROM customers;

-- 3. Отток по типам контракта (используем колонку Contract)
SELECT 
    Contract,
    COUNT(*) as total,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) as churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as churn_rate
FROM customers
GROUP BY Contract
ORDER BY churn_rate DESC;

-- 4. Отток по типу интернета
SELECT 
    InternetService,
    COUNT(*) as total,
    SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) as churned,
    ROUND(100.0 * SUM(CASE WHEN Churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) as churn_rate
FROM customers
GROUP BY InternetService
ORDER BY churn_rate DESC;

-- 5. Средние показатели по ушедшим и оставшимся
SELECT 
    Churn,
    ROUND(AVG(tenure), 1) as avg_tenure,
    ROUND(AVG(MonthlyCharges), 2) as avg_monthly_payment
FROM customers
GROUP BY Churn;