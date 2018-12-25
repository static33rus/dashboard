from pprint import pprint
import xml.etree.ElementTree as etree
import MySQLdb
class Database:
	def __init__(self, host="172.17.0.2", user="root", passwd="12121212", db="autotest"):
		self.db = MySQLdb.connect(host, user, passwd, db)
		self.db.set_character_set('utf8')
		self.cursor = self.db.cursor()

	def parse_xml(self,xml,dumptemplate,date):
## Method parse xml and return list
## Each list consist of [dumptemplate,test_name,result,reason,duration,date], example: [CFU,CFU_1_Megafon,FAILED,Bad Dump,30.23,12.10.2018]
		self.tree = etree.parse(xml)
		self.root = self.tree.getroot()
		self.parser=list()
		for child in self.root:
			self.test_info=[dumptemplate]
			self.test_info.append(child.attrib['name'])
			if len(child)==0:
				self.test_info.append("PASSED")
				self.test_info.append("")		
			else:
				self.test_info.append(child[0].tag.upper())
				self.test_info.append("")
				# test_info.append(child[0].attrib['message'])
			self.test_info.append(child.attrib['time'])
			self.test_info.append(date)
			self.parser.append(self.test_info)
		return self.parser

	def search_last_row(self,search,table,where,cond_value):
##Method create select like "select id from test where test='3PTY'" and return last value or None(if not found)
		self.select="select {search} from {table} where {where}='{cond_value}'".format(search=search,
																						  table=table,where=where,cond_value=cond_value)
		self.cursor.execute(self.select)
		self.data=self.cursor.fetchall()
		self.search_last=self.data[-1][0] if len(self.data)>0 else None
		return self.search_last
	
	def insert_row(self,table,column,value,value_to_return="id"):
##Method insert row in table and return {value_to_return}, id by default
		self.insert="""insert into {}({}) values ('{}')""".format(table,column,value)
		self.cursor.execute(self.insert)
		self.insert_id=self.search_last_row(value_to_return,table,column,value)
		return self.insert_id

	def close(self):
		self.db.commit()
		self.db.close() 

dumptemplate="calldir"
date='17:13 15.12.2018'
megafon={
		 "provider":"Megafon",
		 "job":"Megafon_IMS_MSK",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
		 "result":"SORM_BVT_Megafon_VoLTE_COLLECTION_MASS_DEVELOP",
		 "scenario":"Megafon/Volte/BVT"
}
operators=[megafon]

autotest=Database(host="172.17.0.2", user="root", passwd="12121212", db="autotest")
list_from_xml=autotest.parse_xml("out_report.xml",dumptemplate,date)
for operator in operators:
	job_id=autotest.insert_row("job","job",operator['job']) if autotest.search_last_row("id","job","job",operator['job'])==None else autotest.search_last_row("id","job","job",operator['job'])
	print(job_id)
	for test in list_from_xml:
		dump_id=autotest.insert_row("dumptemplate","dumptemplate",test[0]) if autotest.search_last_row(
						"id","dumptemplate","dumptemplate",test[0])==None else autotest.search_last_row("id","dumptemplate","dumptemplate",test[0])

		operator_id=autotest.insert_row("operator","operator",operator['provider']) if autotest.search_last_row(
						"id","operator","operator",operator['provider'])==None else autotest.search_last_row("id","operator","operator",operator['provider'])
		test_id=autotest.insert_row("test","test",test[1]) if autotest.search_last_row(
						"id","test","test",test[1])==None else autotest.search_last_row("id","test","test",test[1])
		# total_id=
	print(dump_id,operator_id,test_id)
autotest.close()
