from modules.database import *
from modules.report import *
from modules.chart import *
from openpyxl import load_workbook
import sys

builds_in_report=2
SEND_MAIL=True
##Секция, описывающая параметры для diff таблицы по запросу пользователя
NEED_FOR_USER_DIFF=False
OPER="Beeline"
build_num=[348,347]
###Секция описывает отступы между таблицами
ident_from_top=1
row_ident_from_previous_table=2
col_ident_from_previous_table=1

beeline={
		 "provider":"Beeline",
		 "job":"Beeline_BVT",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
		 "result":"Beeline_BVT_NEW",
		 "scenario":"Beeline/Volte/BVT_NEW"
}
mts={
		 "provider":"MTS",
		 "job":"MTS_MSK_VOLTE",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
		 "result":"MTS_MSK_VOLTE_COLLECTION",
		 "scenario":"MTS/PSI2017/volte"
}

megafon={
		 "provider":"Megafon",
		 "job":"Megafon_IMS_MSK",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
		 "result":"Megafon_IMS_MSK",
		 "scenario":"Megafon/VoWiFi/BVT"
}

rtk={
		 "provider":"RTK",
		 "job":"SORM_BVT_RTK_NSK_IMS_COLLECTION_MASS",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","CFU","CFB","CFNRY","ACT_DVO","NEW_DVO","CLIR"],
		 "result":"SORM_BVT_RTK_NSK_IMS_COLLECTION_MASS",
		 "scenario":"Rostelecom/IMS/20180628_Novosib"
}

tele2={
		 "provider":"Tele_2",
		 "job":"SORM_BVT_Tele2_VOLTE_COLLECTION_MASS",
		 "dvo":["CALLDIR","CW","HOLD","MPTY","SRVCC","CFU","CFX"],
		 "result":"SORM_BVT_Tele2_VOLTE_COLLECTION_MASS",
		 "scenario":"Tele2/VOLTE"
}

sbertel={
		 "provider":"SberTel",
		 "job":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS",
		 "dvo":["CALLDIR","SMS","HOLD","3PTY","WAIT","CFU","CFB","CFNRY","CFNRC"],
		 "result":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS",
		 "scenario":"SberTel/VoWiFi"
}

all_operators={
		 "provider":"ALL_OPERATORS_IMS",
		 "job":"SORM_HYBRID_REGRESSION_COLLECTION",
		 "dvo":["Rostelecom","Beeline","MTS","Tele2","Sbertel","Megafon"],
		 "result":"SORM_HYBRID_REGRESSION_COLLECTION",
		 "scenario":"All_operators_main_cases"
}

builds_to_diff={
		 "provider":OPER,
		 "builds":build_num
}

tests= {"daily":[all_operators],
		"big3":[beeline,mts,megafon],
		"weekly":[beeline,mts,megafon,rtk,sbertel]
	   }
operators=tests[sys.argv[1]]
branch=sys.argv[2]

autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
report=Report()
chart=Chart(len(operators))
timestr = time.strftime("%Y.%m.%d")
excel_writer = pd.ExcelWriter(timestr+".xlsx")
for operator in operators:
### Формируем таблицы из данных, полученых из БД
	operator_id=autotest.operator_id(operator['provider'])
	last_builds=autotest.last_builds(operator_id,builds_in_report,branch)
	operator_result_table=autotest.get_autotest_result_table(operator_id,last_builds)
	version_table=autotest.get_version_table(operator_id,last_builds)
	operator_result_table = operator_result_table.sort_index(ascending=False, axis=1)
	header=list(operator_result_table.columns)
	operator_diff_table=report.create_diff_table(operator_result_table,operator['provider'], include_provider_name=True)
	operator_result_table=report.add_summary_to_df(operator_result_table,operator['provider'])
	operator_result_table=operator_result_table[~operator_result_table[str(last_builds[0])].str.contains('SKIPPED', na=False)]
	url_table=autotest.get_url_table(operator,header)
	skipped_reason_table=autotest.get_fail_reason_table(operator_id,last_builds[0],result="SKIPPED")

### Сохраним размер таблиц в словаре
	operator['operator_result_table_shape']=operator_result_table.shape
	operator['operator_diff_table_shape']=operator_diff_table.shape
	operator['version_table_shape']=version_table.shape
	operator['url_table_shape']=url_table.shape

### Создаем график
	passed_count_for_last_builds=autotest.get_result_history(operator_id,"PASSED",branch,21)
	failed_count_for_last_builds=autotest.get_result_history(operator_id,"FAILURE",branch,21)
	skipped_count_for_last_builds=autotest.get_result_history(operator_id,"SKIPPED",branch,21)
	chart.add_subplot(operators.index(operator),autotest.test_count,operator['provider'])
	chart.paint(passed_count_for_last_builds,color="green")
	chart.paint(failed_count_for_last_builds,color="red")
	chart.paint(skipped_count_for_last_builds,color="grey")


### Запишем таблицы по каждому провайдеру в эксель файл
### Примечание: у pandas.to_excel startrow начинается с 0, а в классе excel_formatting startrow начинается с 1
	builds_in_report=len(operator_result_table.columns)-1
	operator_result_table.to_excel(excel_writer, sheet_name=operator['provider'],index=False)
	operator_diff_table.to_excel(excel_writer, operator['provider'],startrow=1 , startcol=builds_in_report+2,index=False) 
	version_table.to_excel(excel_writer, operator['provider'],startrow=len(operator_diff_table)+1+ident_from_top+row_ident_from_previous_table , startcol=builds_in_report+2,index=False)
	url_table.to_excel(excel_writer, operator['provider'],startrow=len(operator_diff_table)+1+len(version_table)+1+ident_from_top+2*row_ident_from_previous_table, startcol=builds_in_report+2,index=False)	
total_df,total_previous_df,diff_table=report.get_total_tables()
issue_table=report.get_issues_from_redmine(search='[autotest]')
total_df.to_excel(excel_writer, sheet_name="SUMMARY",startrow=1,index=False)
diff_table.to_excel(excel_writer, 'SUMMARY',startrow=1 , startcol=5,index=False)
issue_table.to_excel(excel_writer, 'Список issue в redmine',index=False)
# skipped_reason_table.to_excel(excel_writer, 'Skipped tests',index=False)
chart.save('output.png')
excel_writer.save()


# if NEED_FOR_USER_DIFF==True:
#     add_user_diff_to_excel(builds_to_diff, timestr, builds_in_report)

###Форматирование получившегося excel: создание границы таблицы и подсветка шапки
wb = Excel_formatting(timestr+".xlsx")
for operator in operators:
	wb.auto_column_width(operator['provider'])
	row_end,col_end=wb.format_table(df_shape=operator['operator_result_table_shape'],start_col=1,start_row=1,fill_row="summary")
	###Оформляем дифф таблицу
	row_end,_=wb.format_table(df_shape=operator['operator_diff_table_shape'],
													start_col=col_end+col_ident_from_previous_table,
													start_row=2,
													fill_row="second",
													description='Сравнение последнего и предпоследнего прогона')
	 ###Оформляем Таблицу версий
	row_end,_=wb.format_table(df_shape=operator['version_table_shape'],
													start_col=col_end+col_ident_from_previous_table,
													start_row=row_end+row_ident_from_previous_table,
													description='Таблица версий')
	###Оформляем Таблицу url
	row_end,_=wb.format_table(df_shape=operator['url_table_shape'],
													start_col=col_end+col_ident_from_previous_table,
													start_row=row_end+row_ident_from_previous_table,
													description='Таблица с ссылками на результаты')

	###Подкрашиваем результаты тестов
	conditional_format_dict={"PASSED":"81F781",
						   "FAILURE":"FFC7CE",
						   "SKIPPED":"FFFF00"}
	wb.conditional_formatting(operator['provider'],conditional_format_dict)

ws ="SUMMARY"
wb.auto_column_width(ws)
###Форматируем total таблицу по текущему прогону
row_end,col_end=wb.format_table(df_shape=total_df.shape,
								start_col=1,start_row=2,fill_row="last",description='Cтатистика по последнему прогону')
###Форматируем total_diff таблицу
index=report.find_in_table_and_get_row_index(diff_table.reset_index(),'Перестали работать',["Megafon","RTK","Beeline","Tele2","MTS","Sbertel"])

row_end,col_end2=wb.format_table(df_shape=diff_table.shape,
				start_col=col_end+col_ident_from_previous_table,start_row=2,
				description='Таблица сравнения между последней и предпоследней сборками',fill_operator=index)

wb.insert_image(ws,col_end+col_end2,"output.png")
###Форматируем skipped sheet
# ws = "Skipped tests"
# wb.auto_column_width(ws)
# wb.format_table(df_shape=skipped_reason_table.shape)
# wb.save(timestr+".xlsx")

ws = "Список issue в redmine"
wb.auto_column_width(ws)
wb.format_table(df_shape=issue_table.shape)
wb.save(timestr+".xlsx")

if SEND_MAIL==True:
	PATH=os.getcwd()
	fromaddr = "jenkins@osnovalab.ru"
	toaddr = "m.pavlov@osnovalab.ru"
	subj = "Ежедневный отчет по автотестам"
	body = "Доброе утро, отчет во вложении\n"
	filename = timestr+".xlsx"
	att_path = PATH+"/"+filename
	report.sendmail(fromaddr,toaddr,subj,body,filename,att_path)   

