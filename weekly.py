from my_func import *
from openpyxl import load_workbook

number_of_progons=5
SEND_MAIL=True
##Секция, описывающая параметры для diff таблицы по запросу пользователя
NEED_FOR_USER_DIFF=False
OPER="Beeline"
build_num=[348,347]

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
         "result":"SORM_BVT_Megafon_VoLTE_COLLECTION_MASS_DEVELOP",
         "scenario":"Megafon/Volte/BVT"
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

# operators=[beeline,mts,megafon,rtk,tele2,sbertel]
operators=[all_operators]

##Get list of dictionary's with url list
dict_with_url=get_url(operators)
download_from_url(dict_with_url, number_of_progons)

total_df=pd.DataFrame(columns=[" ","PASSED","FAILED","SKIPPED"])
total_previous_df=pd.DataFrame(columns=[" ","PASSED","FAILED","SKIPPED"])
diff_table=pd.DataFrame(columns=['Стали работать','Перестали работать','Перестали запускаться'])
total_passed,total_failed,total_skipped=0,0,0
previous_passed,previous_failed,previous_skipped=0,0,0
excel_writer,timestr=merge_df_and_save_to_csv(dict_with_url, number_of_progons)
# excel_writer = pd.ExcelWriter("report/"+timestr+".xlsx", engine='xlsxwriter')
workbook  = excel_writer.book
red = workbook.add_format({'bg_color': '#FFC7CE',
                           'font_color': '#9C0006'})
green = workbook.add_format({'bg_color': '#81F781',
                               'font_color': '#9C0006'})
yellow = workbook.add_format({'bg_color': '#FFFF00',
                               'font_color': '#9C0006'})
header_format = workbook.add_format({
                             'bold': True,
                             'text_wrap': True,
                             'valign': 'top',
                             'fg_color': '#DDD9C4',
                             'border': 1})
merge_format = workbook.add_format({'align': 'center','bold':     True,'font_color': '#FF0000'})
width = 40
for operator in dict_with_url:    
    finaldf=rename_test_column("download/"+operator['provider']+".csv")
    finaldf = finaldf.sort_index(ascending=False, axis=1)
    header=list(finaldf.columns)
    real_num_of_progons=(len(list(finaldf.head(0))))-1
    diff_for_one_operator=create_diff_table(finaldf,operator['provider'], include_provider_name=True)
    diff_table=diff_table.append(diff_for_one_operator)
    finaldf,passed,failed,skipped =add_summary_to_df(finaldf)
    total_passed,total_failed,total_skipped=total_passed+passed[1],total_failed+failed[1],total_skipped+skipped[1]
    previous_passed,previous_failed,previous_skipped=previous_passed+passed[2],previous_failed+failed[2],previous_skipped+skipped[2]
    total_df=total_df.append(pd.DataFrame({
                                  ' ': operator['provider'],
                                  'PASSED': passed[1],
                                  'FAILED': failed[1],
                                  'SKIPPED': skipped[1]}, index=[0]), sort=False)
    total_previous_df=total_previous_df.append(pd.DataFrame({
                                  ' ': operator['provider'],
                                  'PASSED': passed[2],
                                  'FAILED': failed[2],
                                  'SKIPPED': skipped[2]}, index=[0]), sort=False)
    ver_df=get_version_df(operator,header)
    url_df=get_url_df(operator,header)

    finaldf.to_excel(excel_writer, sheet_name=operator['provider'],index=False)
    diff_for_one_operator.to_excel(excel_writer, operator['provider'],startrow=1 , startcol=real_num_of_progons+2,index=False) 
    ver_df.to_excel(excel_writer, operator['provider'],startrow=len(diff_for_one_operator)+3 , startcol=real_num_of_progons+2,index=False)
    url_df.to_excel(excel_writer, operator['provider'],startrow=len(diff_for_one_operator)+len(ver_df)+5 , startcol=real_num_of_progons+2,index=False)
    worksheet = excel_writer.sheets[operator['provider']]
    worksheet.set_column(0, 0, 25)
    worksheet.set_column(1, real_num_of_progons, 7)
    worksheet.set_column(real_num_of_progons+2, real_num_of_progons+2, width-15)
    worksheet.set_column(real_num_of_progons+3, real_num_of_progons+3, width+10)
    worksheet.set_column(real_num_of_progons+4, real_num_of_progons+4, width+10)
    worksheet.merge_range(num_to_letter(real_num_of_progons+3)+'1:'+num_to_letter(real_num_of_progons+5)+'1', 'Сравнение последнего и предпоследнего прогона', merge_format)
    worksheet.merge_range(num_to_letter(real_num_of_progons+3)+str(len(diff_for_one_operator)+3)+':'+num_to_letter(real_num_of_progons+5)+str(len(diff_for_one_operator)+3), 'Версии компонентов', merge_format)
    worksheet.merge_range(num_to_letter(real_num_of_progons+3)+str(len(diff_for_one_operator)+len(ver_df)+5)+':'+num_to_letter(real_num_of_progons+5)+str(len(diff_for_one_operator)+5+len(ver_df)), 'Таблица с сылками на результаты', merge_format)
    end=num_to_letter(real_num_of_progons+1)+str(len(finaldf)+1)
    worksheet.conditional_format('B2:'+end, {'type':     'cell',
                                             'criteria': '==',
                                             'value':    '"FAILED"',
                                             'format':   red})
    
    
    worksheet.conditional_format('B2:'+end, {'type':     'cell',
                                             'criteria': '==',
                                             'value':    '"PASSED"',
                                             'format':   green})

    worksheet.conditional_format('B2:'+end, {'type':     'cell',
                                             'criteria': '==',
                                             'value':    '"SKIPPED"',
                                             'format':   yellow})

    operator['finaldf_len']=len(finaldf)+1
    operator['diff_len']=len(diff_for_one_operator)+1
    operator['ver_len']=len(ver_df)+1
    operator['url_len']=len(url_df)+1

skipped_df=get_skipped_df(dict_with_url)
total_df.loc[len(total_df)]=["Всего: ",total_passed,total_failed,total_skipped]
total_previous_df.loc[len(total_df)]=["Всего: ",previous_passed,previous_failed,previous_skipped]
total_df.to_excel(excel_writer, sheet_name="SUMMARY",startrow=1,index=False)
total_previous_df.to_excel(excel_writer, sheet_name="SUMMARY",startrow=len(total_df)+4,index=False)
diff_table.to_excel(excel_writer, 'SUMMARY',startrow=1 , startcol=5,index=False)
skipped_df.to_excel(excel_writer, 'Skipped tests',startrow=0 , startcol=0,index=False)
###Форматирование summary страницы
worksheet2 = excel_writer.sheets["SUMMARY"] 
worksheet3 = excel_writer.sheets["Skipped tests"]

worksheet2.merge_range('A1:D1', 'Cтатистика по последнему прогону', merge_format)
worksheet2.merge_range('F1:H1', 'Таблица сравнения между последней и предпоследней сборками', merge_format)
worksheet2.merge_range('A'+str(len(total_df)+4)+':D'+str(len(total_df)+4), 'Cтатистика по предыдущему прогону', merge_format)
worksheet2.set_column(5, 5, width-15)
worksheet2.set_column(6, 6, width-3)
worksheet2.set_column(7, 7, width-15)
worksheet2.set_column(0, 3, 22)
worksheet3.set_column(0, 2, width*2)
excel_writer.save()

if NEED_FOR_USER_DIFF==True:
    add_user_diff_to_excel(builds_to_diff, timestr, real_num_of_progons)

###Форматирование получившегося excel: создание границы таблицы и подсветка шапки
width1=real_num_of_progons+1 #Ширина первой таблицы
width2=3 #Ширина второй табицы
empty=1  #Количество колонок между таблицами

wb = openpyxl.load_workbook("report/"+timestr+".xlsx")
for operator in dict_with_url:
    ws = wb[operator['provider']]
    if real_num_of_progons>number_of_progons:
        print("Скорее всего сейчас проходит очередной прогон или один из прогонов не завершился успешно")
    end=num_to_letter(width1)+str(operator['finaldf_len'])
    set_border(ws, "A1:"+end)
    set_border(ws, "A"+str(operator['finaldf_len']-3)+":"+end,fill=True, color="95B3D7")

    ###Оформляем дифф таблицу
    strt=num_to_letter(width1+empty+1)+"2"
    stop=num_to_letter(width1+empty+width2)+str(operator['diff_len']+1)
    fill=num_to_letter(width1+empty+1)+"3"+":"+num_to_letter(width1+empty+width2)+"3"
    set_border(ws, fill,fill=True, color="95B3D7")
    set_border(ws, strt+":"+stop)

    ###Оформляем Таблицу версий
    strt=num_to_letter(width1+empty+1)+str(operator['diff_len']+3)
    stop=num_to_letter(width1+empty+width2)+str(operator['diff_len']+2+operator['ver_len'])
    set_border(ws, strt+":"+stop)
    ###Оформляем Таблицу url
    strt=num_to_letter(width1+empty+1)+str(operator['diff_len']+4+operator['ver_len'])
    stop=num_to_letter(width1+empty+width2)+str(operator['diff_len']+3+operator['url_len']+operator['ver_len'])
    set_border(ws, fill,fill=True, color="95B3D7")
    set_border(ws, strt+":"+stop)

ws = wb["SUMMARY"]
###Форматируем total таблицу по текущему прогону
end=num_to_letter(4)+str(len(total_df)+1)
set_border(ws, "A2:"+end)
set_border(ws, "A"+str(len(total_df)+2)+":D"+str(len(total_df)+2),fill=True, color="95B3D7")
###Форматируем total таблицу по предыдущему прогону
set_border(ws, 'A'+str(len(total_df)+5)+':D'+str(len(total_df)*2+5))
set_border(ws, "A"+str(len(total_df)*2+5)+":D"+str(len(total_df)*2+5),fill=True, color="95B3D7")
###Форматируем total_diff таблицу
# set_border(ws, "F3:H3",fill=True, color="95B3D7")
diff_len=3
for item in dict_with_url:
    set_border(ws, "F"+str(diff_len)+":H"+str(diff_len),fill=True, color="95B3D7")
    diff_len=diff_len+item['diff_len']-1
set_border(ws, "F2:"+"H"+str(len(diff_table)+2))

###Форматируем skipped sheet
ws = wb["Skipped tests"]
set_border(ws, "A1:"+"B"+str(len(skipped_df)+1))
wb.save("report/"+timestr+".xlsx")


if SEND_MAIL==True:
    fromaddr = "jenkins@osnovalab.ru"
    toaddr = "m.pavlov@osnovalab.ru"
    subj = "Ежедневный отчет по автотестам"
    body = "Доброе утро, отчет во вложении\n"
    filename = timestr+".xlsx"
    att_path = PATH+"/report/"+filename
    sendmail(fromaddr,toaddr,subj,body,filename,att_path)   

