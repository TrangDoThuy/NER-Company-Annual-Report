DROP TABLE IF EXISTS companies
CREATE TABLE IF NOT EXISTS companies(
                                	id integer PRIMARY KEY AUTOINCREMENT,
                                	CIK text NOT NULL,
                                	ticker text NOT NULL,
                                	company_name text NOT NULL,
                                	exchange text
                                	);
INSERT INTO company(CIK, ticker,company_name,id) 
SELECT DISTINCT CIK, ticker,company_name FROM reports
SELECT DISTINCT id FROM exchange WHERE exchange.exchange_name = report.exchange


DROP TABLE IF EXISTS exchange
CREATE TABLE IF NOT EXISTS exchange(
	id integer PRIMARY KEY AUTOINCREMENT,
	exchange_name text NOT NULL
)
INSERT INTO exchange(exchange_name) SELECT DISTINCT exchange FROM companies

CREATE TABLE company(
    id integer PRIMARY KEY AUTOINCREMENT,
    CIK text NOT NULL,
    ticker text NOT NULL,
    company_name text NOT NULL,
	exchangeId INTEGER NOT NULL,
  FOREIGN KEY(exchangeId) REFERENCES exchange(id)
);


INSERT INTO company(CIK, ticker,company_name,exchangeId) 
SELECT CIK, ticker,company_name, exchange.id
FROM companies
INNER JOIN exchange ON exchange.exchange_name = companies.exchange

CREATE TABLE IF NOT EXISTS report(
	id integer PRIMARY KEY AUTOINCREMENT,
	report_period text,
	filing_date text,
	source_url text,
	file_directory text,
	companyId INTEGER NOT NULL,
	FOREIGN KEY(companyId) REFERENCES company(id)
	);

INSERT INTO report(report_period,filing_date,source_url,file_directory,companyId)
SELECT report_period,filing_date,source_url,file_directory,company.id
FROM reports
INNER JOIN company ON reports.CIK = company.CIK