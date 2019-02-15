from pprint import pprint
import xml.etree.ElementTree as etree
import pandas as pd
import MySQLdb
class Database:
	def __init__(self, host="10.2.7.29", user="root", passwd="12121212", db="autotest"):
		self.db = MySQLdb.connect(host, user, passwd, db)
		self.db.set_character_set('utf8')
		self.cursor = self.db.cursor()
		self.total_skipped_df=pd.DataFrame(columns=['Test','Reason of Fail'])

	def select(self,string):
		total=list()
		self.cursor.execute(string)
		for item in self.cursor.fetchall():	
			total.append(item[0])
		return total

	def parse_xml(self,xml,dumptemplate,date):
## Method parse xml and return list
## Each list consist of [dumptemplate,test_name,result,reason,duration,date], example: [CFU,CFU_1_Megafon,FAILED,"Reason of fail/skipped",30.23,12.10.2018]
		self.tree = etree.parse(xml)
		self.root = self.tree.getroot()
		self.parser=list()
		for child in self.root:
			self.test_info=[dumptemplate]
			self.test_info.append(child.attrib['name'][14:-5])
			if len(child)==0:
				self.test_info.append("PASSED")
				self.test_info.append("")       
			else:
				self.test_info.append(child[0].tag.upper())
				self.test_info.append("error code: ...") if (child[0].tag=="failure" or child[0].tag=="error")  else self.test_info.append(child[0].text.strip()[:199])
			self.test_info.append(child.attrib['time'])
			self.test_info.append(date)
			self.parser.append(self.test_info)
		return self.parser

	def parse_versions(self,path):
		self.f=open(path,"r")
		self.versions=self.f.read()
		self.f.close()
		self.version_list=[item.split("/")[1] for item in self.versions.split("\n")[:-1]]
		return self.version_list

	def search_row(self,search,table,where):
##Method create select like "select id from test where test='3PTY'" and return last value or None(if not found)
		self.select="select {search} from {table} where {where}".format(search=search,table=table,where=where)
		self.cursor.execute(self.select)
		self.data=self.cursor.fetchall()
		self.search_last=self.data[-1][0] if len(self.data)>0 else None
		return self.search_last
	
	def insert_row(self,table="table",column="columns",value="values",value_to_return="id",find_before_insert=False,condition="condition"):
##Method insert row in table and return {value_to_return}, id by default        
		self.insert="""insert into {}({}) values ('{}')""".format(table,column,value)
		if find_before_insert==True:
			self.cursor.execute(self.insert) if self.search_row(value_to_return,table,condition)==None else None
			self.insert_id=self.cursor.lastrowid if self.search_row(value_to_return,table,condition)==None else self.search_row(value_to_return,table,condition)
		else:
			self.cursor.execute(self.insert)
			self.insert_id=self.cursor.lastrowid
		return self.insert_id

	def operator_id(self,operator):
		operator_id="select id from operator where operator='{}'".format(operator)
		self.cursor.execute(operator_id)
		operator_id=[item[0] for item in self.cursor.fetchall()][0]
		return operator_id

	def last_builds(self,operator_id,num,branch):
		top_N_builds="select DISTINCT  build  from version where mass REGEXP 'mass.{}' and operator={} order by build desc limit {}".format(branch,operator_id,num)
		self.cursor.execute(top_N_builds)
		builds=[item[0] for item in self.cursor.fetchall()]
		if len(builds)==0:
			print("Нет информации в базе по заданным параметрам. operator_id:{}".format(operator_id))
			raise Exception("No last builds on current branch")
		return builds

	def get_result_history(self,operator_id,word,branch,num):
		builds=Database.last_builds(self,operator_id,num,branch)
		total=list()
		for build in builds:
			select='select count(result) from (select test.test,result from total left join test on total.test=test.id where build={} and operator={}) T1 where result="{}"'.format(build,operator_id,word)
			self.cursor.execute(select)
			for item in self.cursor.fetchall():	
				total.append(item[0])

		s1=pd.Series(builds,name='builds')
		s2=pd.Series(total,name='{}'.format(word)) 
		df=pd.concat([s1,s2], axis=1)
		return df

	def get_autotest_result_table(self,operator_id,builds):
		select="select T1.test, T1.result as `{build}` from (select test.test,result from total left join test on total.test=test.id where build={build} and operator={id}) T1".format(build=builds[0],id=operator_id)
		df = pd.read_sql_query(select,self.db)
		for build in builds[1:]:
			select="select T1.test, T1.result as `{build}` from (select test.test,result from total left join test on total.test=test.id where build={build} and operator={id}) T1".format(build=build,id=operator_id)
			build_df = pd.read_sql_query(select,self.db)
			if len(df)>len(build_df):
				df=df.merge(build_df,how='left', left_on='test', right_on='test')
			else:
				df=df.merge(build_df,how='right', left_on='test', right_on='test')

### Посчитаем кол-во тестов в последнем прогоне
		test_count='select count(id) from total where operator={} and build={}'.format(operator_id,builds[0])
		self.cursor.execute(test_count)
		self.test_count=self.cursor.fetchone()[0]
		return df

	def get_version_table(self,operator_id,builds):
		versions="select mass,ims_s11_sh,user_registry,voltegw,libssrv from version where operator={id} and build={build}".format(
																															id=operator_id, build=builds[0])
		try:
			previous_versions="select mass,ims_s11_sh,user_registry,voltegw,libssrv from version where operator={id} and build={build}".format(
																															id=operator_id, build=builds[1])
		except IndexError:
			previous_versions=None

		df = pd.read_sql_query(versions,self.db).T
		df.reset_index(inplace=True)
		df.columns = ['component',builds[0]]
		
		if previous_versions is not None:
			previous_df = pd.read_sql_query(previous_versions,self.db).T
			previous_df.reset_index(inplace=True)
			previous_df.columns = ['component',builds[1]]
			df=pd.merge(df, previous_df, how='left', on=['component'])
		return df

	def get_url_table(self,operator,header):
		scenario_url="//10.72.1.239/Dumps/{}/".format(operator['scenario'])
		result_url="//10.72.1.239/Results/{job}/{id}".format(job=operator['result'],id=header[1])
		allure_url="http://10.72.1.46/view/{operator}/job/{job}/{id}/allure/".format(operator=operator['provider'],job=operator['job'],id=header[1])
	
		keys=['Логи и конфиги','Pcap+сценарий(ini)', 'Allure-report']
		values=[result_url,scenario_url,allure_url]
	
		df=pd.DataFrame(
					{' ': keys,
					 'url': values
						 })
		return df

	def get_fail_reason_table(self,operator_id,build,result="SKIPPED"):
		select='''
		select test.test, errors.errors from 
		(select * from total where result="{result}" and operator={operator_id} and build={build}) T1 
		left join errors 
		on 
		T1.build=errors.build and T1.test=errors.test and T1.operator=errors.operator
		left join test
		on
		T1.test=test.id;
		'''.format(result=result,operator_id=operator_id,build=build)
		df = pd.read_sql_query(select,self.db)
		df.columns = ['Test','Reason of Fail']
		df = df[~df['Reason of Fail'].str.contains('http')]
		self.total_skipped_df=self.total_skipped_df.append(df)
		return self.total_skipped_df

	def close(self):
		self.db.commit()
		self.db.close() 


