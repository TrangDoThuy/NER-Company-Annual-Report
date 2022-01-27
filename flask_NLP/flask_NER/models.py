from flask_NER import db
class Exchange(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    exchange_name = db.Column(db.String(20),unique=True, nullable=False)
    companies = db.relationship('Company',backref='exchange',lazy=True)


class Company(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    CIK = db.Column(db.String(20),unique=True, nullable=False)
    ticker = db.Column(db.String(20),unique=True, nullable=False)
    company_name = db.Column(db.String(120),unique=True, nullable=False)
    exchangeId = db.Column(db.Integer,db.ForeignKey('exchange.id'), nullable=False)
    reports = db.relationship('Report',backref='company_source',lazy=True)

class Report(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    report_period = db.Column(db.Text,nullable=False)
    filing_date = db.Column(db.Text,nullable=False)
    source_url = db.Column(db.Text,nullable=False)
    file_directory = db.Column(db.Text,nullable=False)
    companyId = db.Column(db.Integer,db.ForeignKey('company.id'), nullable=False)
    JSON_files = db.relationship('JSON_file',backref='report',lazy=False)

class JSON_type(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    type_name = db.Column(db.Text,nullable=False)
    JSON_files = db.relationship('JSON_file',backref='JSON_type',lazy=True)

class JSON_file(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    original_fileID = db.Column(db.Integer,db.ForeignKey('report.id'), nullable=False)
    file_directory = db.Column(db.Text,nullable=False)
    category = db.Column(db.Integer,db.ForeignKey('JSON_type.id'), nullable=False)

class table_type(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    type_name = db.Column(db.Text,unique=True,nullable=False)
    table_files = db.relationship('table_file',backref='table_type',lazy=True)

class table_file(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    report_id = db.Column(db.Integer,db.ForeignKey('report.id'), nullable=False)
    file_directory = db.Column(db.Text,nullable=False)
    category = db.Column(db.Integer,db.ForeignKey('table_type.id'), nullable=False)
    file_type = db.Column(db.String(20))
