# Check file_history.log for last data update 

# SELECT covid etl pipeline schema 
USE covid_etl_pipeline;

# Create Table for Total Cases Per Country
DROP TABLE IF EXISTS Total_Cases_Per_Continent ;
CREATE TABLE Total_Cases_Per_Continent 
(date date,
 location varchar(255),
 cumulative_cases numeric);
 
INSERT INTO Total_Cases_Per_Continent
SELECT date, 
	   location,
       SUM(new_cases) OVER w AS cumulative_cases
FROM covid_19_data
WHERE location IN ('Europe', 'South America', 'North America', 'European Union', 'Africa', 'Oceania', 'Asia')
#GROUP BY date, location
WINDOW w AS (PARTITION BY location ORDER BY date);