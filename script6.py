from mymodules import *
from selenium import webdriver
from bash import bash

try:
    if os.path.exists("download"):
        bash("rm -rf ./download")
    os.mkdir("download")
    
    url1='http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/OPERATOR=Beeline,label=SORM_server/test_results_analyzer/'
    url2='http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/OPERATOR=MTS,label=SORM_server/test_results_analyzer/'
    url3='http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/OPERATOR=Megafon,label=SORM_server/test_results_analyzer/'
    url4='http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/OPERATOR=Tele2,label=SORM_server/test_results_analyzer/'
    url5='http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/OPERATOR=Sbertel,label=SORM_server/test_results_analyzer/'
    url6='http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/OPERATOR=Rostelecom,label=SORM_server/test_results_analyzer/'    
    url_list=[url1,url2,url3,url4,url5,url6]
    download_from_url(url_list, 'downloadCSV')

##Working with csv    
    fout=open("report/out.csv","w")
    # first file:
    for line in open("download/Test Results (1).csv"):
        if line.count('(root)')!=0:
            continue
        fout.write(line)
    # now the rest:    
    for num in range(2,len(url_list)+1):
        f = open("download/Test Results"+" ("+str(num)+")"+".csv")
        col_str=f.readline().strip()
        # f.readline()
        for line in f:
            if line.count('(root)')!=0:
                continue
            fout.write(line)
        f.close()
    fout.close()
    #Delete coumns from csv...............
    number_of_columns_to_delete=2
    col=''
    for symbol in col_str:
    	if symbol!='"':
    		col=col+symbol
    keep_col=col.split(',')[number_of_columns_to_delete:]
    id_progona=keep_col[1]

    f=pd.read_csv("report/out.csv")
    for i in range(0,len(f)-1):
        f["Test"][i]=f["Test"][i][14:-5]
        if f["Test"][i].count("test_run[dumpname0]")>0:
            f["Test"][i]=" " 
    df = f[keep_col]
    df = remove_rows_csv(df)
    df.to_csv("tmp.csv", index=False)

    diff=diff_table("tmp.csv")
    passed,df=countif_in_rows("PASSED","tmp.csv")
    failed,df=countif_in_rows("FAILED","tmp.csv")
    skipped,df=countif_in_rows("SKIPPED","tmp.csv")
    results=["SUMMARY:"]
    for i in range (0,len(passed)-1):
        results.append(" ")
    df.loc[len(df)]=results
    df.loc[len(df)]=passed
    df.loc[len(df)]=failed
    df.loc[len(df)]=skipped
    length=len(df)

### Download version.log to get component versions
    result_url="//10.72.1.239/Results/SORM_HYBRID_REGRESSION_COLLECTION/"+id_progona
    scenario_url="//10.72.1.239/Dumps/All_operators_main_cases/"
    allure_url="http://10.72.1.46/view/ALL_OPERATORS_IMS/job/SORM_HYBRID_REGRESSION_COLLECTION/{}/allure/".format(id_progona)
    bash("wget -P ./download/ ftp:"+ result_url+"/Beeline/result.tar.xz")
    bash("tar xf ./download/result.tar.xz -C ./download/")
    f=open("./download/versions.log","r")
    versions=f.read()
    f.close()  

    keys=[]
    values=[]
    versions_list=versions.split("\n")
    for item in versions_list[:-1]:
    	keys.append(item.split("/")[0])
    	values.append(item.split("/")[1])
    
    ver_df=pd.DataFrame(
        	{'component': keys,
        	 'version': values
        	 })  
    bash('rm -rf ./download/xmlreports/')

    keys=['Логи и конфиги','Pcap+сценарий(ini)', 'Allure-report']
    values=[result_url,scenario_url,allure_url]
    url_df=pd.DataFrame(
        	{' ': keys,
        	 'url': values
        	 })  

##Skipped sheet
    url1='wget --directory-prefix=./download/Megafon ftp://10.72.1.239/Dumps/All_operators_main_cases/Megafon/*.ini'
    url2='wget --directory-prefix=./download/Beeline ftp://10.72.1.239/Dumps/All_operators_main_cases/Beeline/*.ini'
    url3='wget --directory-prefix=./download/MTS ftp://10.72.1.239/Dumps/All_operators_main_cases/MTS/*.ini'
    url4='wget --directory-prefix=./download/Sbertel ftp://10.72.1.239/Dumps/All_operators_main_cases/Sbertel/*.ini'
    url5='wget --directory-prefix=./download/Rostelecom ftp://10.72.1.239/Dumps/All_operators_main_cases/Rostelecom/*.ini'
    url6='wget --directory-prefix=./download/Tele2 ftp://10.72.1.239/Dumps/All_operators_main_cases/Tele2/*.ini'
    url_list=[url1,url2,url3,url4,url5,url6]
    skipped_dict=skipped_dict(url_list)
    keys=list(skipped_dict.keys())
    values=list(skipped_dict.values())
    
    skipped_df=pd.DataFrame(
    	{'TEST': keys,
    	 'Reason of FAIL': values
    	 })

###Working with excel
    df_len=len(df)+1
    diff_len=len(diff)+1
    skipped_len=len(skipped_df)+1
    timestr = time.strftime("%Y.%m.%d")
    excel_writer = pd.ExcelWriter("report/"+timestr+".xlsx", engine='xlsxwriter')
    df.to_excel(excel_writer, 'summary',startrow=0 , startcol=0,index=False)
    ver_df.to_excel(excel_writer, 'summary',startrow=0 , startcol=8,index=False)
    url_df.to_excel(excel_writer, 'summary',startrow=len(ver_df)+5 , startcol=8,index=False)
    diff.to_excel(excel_writer, 'diff table',index=False)
    skipped_df.to_excel(excel_writer, 'skipped tests',index=False)

    workbook  = excel_writer.book
    worksheet1 = excel_writer.sheets['summary']
    worksheet2 = excel_writer.sheets['diff table']
    worksheet3 = excel_writer.sheets['skipped tests']
    red = workbook.add_format({'bg_color': '#FFC7CE',
                                   'font_color': '#9C0006'})
    green = workbook.add_format({'bg_color': '#81F781',
                                   'font_color': '#9C0006'})
    header_format = workbook.add_format({
    'bold': True,
    'text_wrap': True,
    'valign': 'top',
    'fg_color': '#DDD9C4',
    'border': 1})

    #Width of columns
    width = 40
    worksheet1.set_column(0, 0, width-15)
    worksheet1.set_column(8, 8, width/2)
    worksheet1.set_column(9, 9, width+50)
    worksheet2.set_column(0, 3, width)
    worksheet3.set_column(0, 0, width)
    worksheet3.set_column(1, 1, width+50)

    width = 8
    worksheet1.set_column(2, len(url_list), width)
    
    worksheet1.conditional_format('B2:F116', {'type':     'cell',
                                            'criteria': '==',
                                            'value':    '"FAILED"',
                                            'format':   red})
    
    
    worksheet1.conditional_format('B2:F116', {'type':     'cell',
                                            'criteria': '==',
                                            'value':    '"PASSED"',
                                            'format':   green})
    
    excel_writer.save()

    wb = openpyxl.load_workbook("report/"+timestr+".xlsx")
    ws1 = wb['summary']
    ws2 = wb['diff table']
    ws3 = wb['skipped tests']
    set_border(ws1, "A1:F"+str(df_len))
    set_border(ws1, "I1:J6")
    set_border(ws1, "I11:J14")
    set_border(ws2, "A1:C"+str(diff_len))
    set_border(ws3, "A1:B"+str(skipped_len))
    set_border(ws1, "A"+str(length-2)+":"+"F"+str(length+1),fill=True, color="95B3D7")
    wb.save("report/"+timestr+".xlsx")
    
#Prepare mail
    fromaddr = "jenkins@osnovalab.ru"
    toaddr = "m.pavlov@osnovalab.ru"
    subj = "Ежедневный отчет по автотестам"
    body = "Доброе утро, отчет во вложении\n"
    filename = timestr+".xlsx"
    att_path = "/home/m_pavlov/Desktop/allure-report/report/"+filename
    sendmail(fromaddr,toaddr,subj,body,filename,att_path)   

finally:
    # print("x")
    os.remove("report/out.csv")
    os.remove("tmp.csv")
    bash("rm -rf ./download")



