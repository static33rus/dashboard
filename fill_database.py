from modules.database import *
import sys
import time
from pprint import pprint

operator=sys.argv[1]
job=sys.argv[2].split("/")[0]
dumptemplate=sys.argv[3]
build=sys.argv[4]
date = time.strftime("%Y.%m.%d %H:%M:%S")


autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
list_from_xml=autotest.parse_xml("out_report.xml",dumptemplate,date)

list_from_versions=autotest.parse_versions("./SORM/versions.log")

job_id=autotest.insert_row(table="job",
							column="job",
							value=job,
							find_before_insert=True,
							condition="job='{}'".format(job))
for test in list_from_xml:
	dump_id=autotest.insert_row(table="dumptemplate",
								column="dumptemplate",
								value=test[0],
								find_before_insert=True,
								condition="dumptemplate='{}'".format(test[0]))
	operator_id=autotest.insert_row(table="operator",
								column="operator",
								value=operator,
								find_before_insert=True,
								condition="operator='{}'".format(operator))
	test_id=autotest.insert_row(table="test",
								column="test",
								value=test[1],
								find_before_insert=True,
								condition="test='{}'".format(test[1]))
	total_values="{}','{}','{}','{}','{}','{}','{}','{}".format(test_id,operator_id,job_id,build,dump_id,test[2],test[4],test[5])
	total_id=autotest.insert_row(table="total",
								column="test,operator,job,build,dumptemplate,result,duration,date",
								value=total_values,
								find_before_insert=True,
								condition="test={} and build={} and dumptemplate={}".format(test_id,build,dump_id))
	if len(test[3])!=0:
		errors_id=autotest.insert_row(table="errors",
								column="operator,build,test,errors",
								value="{}','{}','{}','{}".format(operator_id,build,test_id,test[3].replace("'","")),
								find_before_insert=True,
								condition="operator={} and build={} and test={}".format(operator_id,build,test_id))
for version in list_from_versions:
	version_values="{}','{}','{}','{}','{}','{}','{}".format(operator_id,build,*list_from_versions)
	version_id=autotest.insert_row(table="version",
								column="operator,build,mass,ims_s11_sh,user_registry,voltegw,libssrv",
								value=version_values,
								find_before_insert=True,
								condition="operator={} and build={}".format(operator_id,build))
autotest.close()