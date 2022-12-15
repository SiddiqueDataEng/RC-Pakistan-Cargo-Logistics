-- RC Pakistan Cargo & Logistics - Star Schema Creation
-- Data Warehouse Schema for Analytics and BI

-- =====================================================
-- DIMENSION TABLES
-- =====================================================

-- DimDate - Time Dimension
CREATE TABLE DimDate (
    DateKey INT PRIMARY KEY,
    FullDate DATE NOT NULL,
    Year INT NOT NULL,
    Quarter INT NOT NULL,
    Month INT NOT NULL,
    MonthName VARCHAR(20) NOT NULL,
    Day INT NOT NULL,
    WeekDay INT NOT NULL,
    WeekDayName VARCHAR(20) NOT NULL,
    IsWeekend BIT NOT NULL
);

-- DimCustomer - Customer Dimension
CREATE TABLE DimCustomer (
    CustomerKey INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NOT NULL,
    CustomerName VARCHAR(100) NOT NULL,
    Phone VARCHAR(20),
    City VARCHAR(50),
    CreatedDate DATE,
    UNIQUE(CustomerID)
);

-- DimCity - Geographic Dimension
CREATE TABLE DimCity (
    CityKey INT IDENTITY(1,1) PRIMARY KEY,
    CityID INT NOT NULL,
    CityName VARCHAR(50) NOT NULL,
    Country VARCHAR(50) NOT NULL,
    CityType VARCHAR(20) NOT NULL, -- Origin/Destination
    UNIQUE(CityID)
);

-- DimTransportMode - Transport Mode Dimension
CREATE TABLE DimTransportMode (
    ModeKey INT IDENTITY(1,1) PRIMARY KEY,
    ModeID INT NOT NULL,
    ModeName VARCHAR(20) NOT NULL,
    Description VARCHAR(200),
    UNIQUE(ModeID)
);

-- DimStatus - Shipment Status Dimension
CREATE TABLE DimStatus (
    StatusKey INT IDENTITY(1,1) PRIMARY KEY,
    StatusID INT NOT NULL,
    StatusName VARCHAR(50) NOT NULL,
    Description VARCHAR(200),
    UNIQUE(StatusID)
);

-- =====================================================
-- FACT TABLES
-- =====================================================

-- FactShipment - Main Shipment Fact Table
CREATE TABLE FactShipment (
    ShipmentKey INT IDENTITY(1,1) PRIMARY KEY,
    ShipmentID INT NOT NULL,
    BookingID INT NOT NULL,
    CustomerKey INT NOT NULL,
    OriginCityKey INT NOT NULL,
    DestinationCityKey INT NOT NULL,
    TransportModeKey INT NOT NULL,
    StatusKey INT NOT NULL,
    BookingDateKey INT NOT NULL,
    ShipmentDateKey INT NOT NULL,
    ExpectedDeliveryDateKey INT NOT NULL,
    ActualDeliveryDateKey INT NULL,
    WeightKG DECIMAL(8,2) NOT NULL,
    TransitDays INT NOT NULL,
    
    -- Foreign Key Constraints
    FOREIGN KEY (CustomerKey) REFERENCES DimCustomer(CustomerKey),
    FOREIGN KEY (OriginCityKey) REFERENCES DimCity(CityKey),
    FOREIGN KEY (DestinationCityKey) REFERENCES DimCity(CityKey),
    FOREIGN KEY (TransportModeKey) REFERENCES DimTransportMode(ModeKey),
    FOREIGN KEY (StatusKey) REFERENCES DimStatus(StatusKey),
    FOREIGN KEY (BookingDateKey) REFERENCES DimDate(DateKey),
    FOREIGN KEY (ShipmentDateKey) REFERENCES DimDate(DateKey),
    FOREIGN KEY (ExpectedDeliveryDateKey) REFERENCES DimDate(DateKey)
);

-- FactRevenue - Revenue Fact Table
CREATE TABLE FactRevenue (
    RevenueKey INT IDENTITY(1,1) PRIMARY KEY,
    PaymentID INT NOT NULL,
    BookingID INT NOT NULL,
    CustomerKey INT NOT NULL,
    PaymentDateKey INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL,
    PaymentMethod VARCHAR(30) NOT NULL,
    WeightKG DECIMAL(8,2) NOT NULL,
    RevenuePerKG DECIMAL(10,4) NOT NULL,
    
    -- Foreign Key Constraints
    FOREIGN KEY (CustomerKey) REFERENCES DimCustomer(CustomerKey),
    FOREIGN KEY (PaymentDateKey) REFERENCES DimDate(DateKey)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Dimension Table Indexes
CREATE INDEX IX_DimDate_FullDate ON DimDate(FullDate);
CREATE INDEX IX_DimDate_Year_Month ON DimDate(Year, Month);
CREATE INDEX IX_DimCustomer_CustomerID ON DimCustomer(CustomerID);
CREATE INDEX IX_DimCity_CityName ON DimCity(CityName);
CREATE INDEX IX_DimCity_Country ON DimCity(Country);

-- Fact Table Indexes
CREATE INDEX IX_FactShipment_BookingDateKey ON FactShipment(BookingDateKey);
CREATE INDEX IX_FactShipment_CustomerKey ON FactShipment(CustomerKey);
CREATE INDEX IX_FactShipment_OriginDestination ON FactShipment(OriginCityKey, DestinationCityKey);
CREATE INDEX IX_FactShipment_TransportMode ON FactShipment(TransportModeKey);

CREATE INDEX IX_FactRevenue_PaymentDateKey ON FactRevenue(PaymentDateKey);
CREATE INDEX IX_FactRevenue_CustomerKey ON FactRevenue(CustomerKey);
CREATE INDEX IX_FactRevenue_BookingID ON FactRevenue(BookingID);

-- =====================================================
-- SAMPLE DATA POPULATION
-- =====================================================

-- Populate DimCity
INSERT INTO DimCity (CityID, CityName, Country, CityType) VALUES
(1, 'Dubai', 'UAE', 'Origin'),
(2, 'Sharjah', 'UAE', 'Origin'),
(3, 'Ajman', 'UAE', 'Origin'),
(4, 'Karachi', 'Pakistan', 'Destination'),
(5, 'Lahore', 'Pakistan', 'Destination'),
(6, 'Islamabad', 'Pakistan', 'Destination'),
(7, 'Rawalpindi', 'Pakistan', 'Destination'),
(8, 'Peshawar', 'Pakistan', 'Destination'),
(9, 'Mirpur', 'Azad Kashmir', 'Destination'),
(10, 'Muzaffarabad', 'Azad Kashmir', 'Destination');

-- Populate DimTransportMode
INSERT INTO DimTransportMode (ModeID, ModeName, Description) VALUES
(1, 'Air', 'Fast delivery, higher cost, suitable for urgent shipments'),
(2, 'Sea', 'Economical option, longer transit time, suitable for bulk cargo');

-- Populate DimStatus
INSERT INTO DimStatus (StatusID, StatusName, Description) VALUES
(1, 'Booked', 'Initial booking created, awaiting shipment'),
(2, 'In Transit', 'Shipment is in progress'),
(3, 'Arrived', 'Shipment has arrived at destination country'),
(4, 'Customs Cleared', 'Customs procedures completed'),
(5, 'Delivered', 'Successfully delivered to customer');

-- Populate DimDate (2022 full year)
DECLARE @StartDate DATE = '2022-01-01';
DECLARE @EndDate DATE = '2022-12-31';

WHILE @StartDate <= @EndDate
BEGIN
    INSERT INTO DimDate (DateKey, FullDate, Year, Quarter, Month, MonthName, Day, WeekDay, WeekDayName, IsWeekend)
    VALUES (
        CAST(FORMAT(@StartDate, 'yyyyMMdd') AS INT),
        @StartDate,
        YEAR(@StartDate),
        DATEPART(QUARTER, @StartDate),
        MONTH(@StartDate),
        DATENAME(MONTH, @StartDate),
        DAY(@StartDate),
        DATEPART(WEEKDAY, @StartDate),
        DATENAME(WEEKDAY, @StartDate),
        CASE WHEN DATEPART(WEEKDAY, @StartDate) IN (1, 7) THEN 1 ELSE 0 END
    );
    
    SET @StartDate = DATEADD(DAY, 1, @StartDate);
END;

-- =====================================================
-- VIEWS FOR COMMON ANALYTICS QUERIES
-- =====================================================

-- Monthly Shipment Summary View
CREATE VIEW vw_MonthlyShipmentSummary AS
SELECT 
    d.Year,
    d.Month,
    d.MonthName,
    COUNT(f.ShipmentKey) as TotalShipments,
    SUM(f.WeightKG) as TotalWeight,
    AVG(f.TransitDays) as AvgTransitDays,
    COUNT(CASE WHEN tm.ModeName = 'Air' THEN 1 END) as AirShipments,
    COUNT(CASE WHEN tm.ModeName = 'Sea' THEN 1 END) as SeaShipments
FROM FactShipment f
    INNER JOIN DimDate d ON f.BookingDateKey = d.DateKey
    INNER JOIN DimTransportMode tm ON f.TransportModeKey = tm.ModeKey
GROUP BY d.Year, d.Month, d.MonthName;

-- Route Performance View
CREATE VIEW vw_RoutePerformance AS
SELECT 
    oc.CityName as OriginCity,
    dc.CityName as DestinationCity,
    dc.Country as DestinationCountry,
    tm.ModeName as TransportMode,
    COUNT(f.ShipmentKey) as TotalShipments,
    SUM(f.WeightKG) as TotalWeight,
    AVG(f.TransitDays) as AvgTransitDays,
    MIN(f.TransitDays) as MinTransitDays,
    MAX(f.TransitDays) as MaxTransitDays
FROM FactShipment f
    INNER JOIN DimCity oc ON f.OriginCityKey = oc.CityKey
    INNER JOIN DimCity dc ON f.DestinationCityKey = dc.CityKey
    INNER JOIN DimTransportMode tm ON f.TransportModeKey = tm.ModeKey
GROUP BY oc.CityName, dc.CityName, dc.Country, tm.ModeName;

-- Customer Revenue Analysis View
CREATE VIEW vw_CustomerRevenueAnalysis AS
SELECT 
    c.CustomerName,
    c.City as CustomerCity,
    COUNT(DISTINCT f.BookingID) as TotalShipments,
    SUM(r.Amount) as TotalRevenue,
    AVG(r.Amount) as AvgRevenuePerShipment,
    SUM(f.WeightKG) as TotalWeight,
    AVG(f.WeightKG) as AvgWeightPerShipment,
    AVG(r.RevenuePerKG) as AvgRevenuePerKG
FROM FactShipment f
    INNER JOIN DimCustomer c ON f.CustomerKey = c.CustomerKey
    INNER JOIN FactRevenue r ON f.BookingID = r.BookingID
GROUP BY c.CustomerKey, c.CustomerName, c.City;

-- =====================================================
-- STORED PROCEDURES FOR COMMON OPERATIONS
-- =====================================================

-- Procedure to get shipment performance by date range
CREATE PROCEDURE sp_GetShipmentPerformance
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SELECT 
        d.FullDate,
        COUNT(f.ShipmentKey) as DailyShipments,
        SUM(f.WeightKG) as DailyWeight,
        AVG(f.TransitDays) as AvgTransitDays,
        SUM(r.Amount) as DailyRevenue
    FROM FactShipment f
        INNER JOIN DimDate d ON f.BookingDateKey = d.DateKey
        LEFT JOIN FactRevenue r ON f.BookingID = r.BookingID
    WHERE d.FullDate BETWEEN @StartDate AND @EndDate
    GROUP BY d.FullDate
    ORDER BY d.FullDate;
END;

-- Procedure to get top routes by volume
CREATE PROCEDURE sp_GetTopRoutes
    @TopN INT = 10
AS
BEGIN
    SELECT TOP (@TopN)
        oc.CityName + ' → ' + dc.CityName as Route,
        oc.Country as OriginCountry,
        dc.Country as DestinationCountry,
        COUNT(f.ShipmentKey) as TotalShipments,
        SUM(f.WeightKG) as TotalWeight,
        AVG(f.TransitDays) as AvgTransitDays
    FROM FactShipment f
        INNER JOIN DimCity oc ON f.OriginCityKey = oc.CityKey
        INNER JOIN DimCity dc ON f.DestinationCityKey = dc.CityKey
    GROUP BY oc.CityName, dc.CityName, oc.Country, dc.Country
    ORDER BY TotalShipments DESC;
END;

PRINT 'RC Pakistan Cargo & Logistics Star Schema created successfully!';
PRINT 'Tables created: DimDate, DimCustomer, DimCity, DimTransportMode, DimStatus, FactShipment, FactRevenue';
PRINT 'Views created: vw_MonthlyShipmentSummary, vw_RoutePerformance, vw_CustomerRevenueAnalysis';
PRINT 'Stored procedures created: sp_GetShipmentPerformance, sp_GetTopRoutes';