import os
import time
from selenium import webdriver
import pandas as pd
import xlsxwriter
import time
import openpyxl
from pprint import pprint
from openpyxl.styles import Font, Border, Side, Style, Color, PatternFill, Alignment
from openpyxl.utils import coordinate_from_string

PATH=os.getcwd()

def get_url(operators):    
    for operator in operators:
        download_url=[]
        provider=operator['provider']
        dvo_list=operator['dvo']
        job=operator['job']
        for dvo in dvo_list:
            if operator['provider']=="ALL_OPERATORS_IMS":
                download_url.append("http://10.72.1.46/view/{provider}/job/{job}/OPERATOR={dvo},label=SORM_server/test_results_analyzer/".format(provider=provider,job=job, dvo=dvo))
            else:
                download_url.append("http://10.72.1.46/view/{provider}/job/{job}/dumptemplate={dvo},label=SORM_server/test_results_analyzer/".format(provider=provider,job=job, dvo=dvo))
        operator['url']=download_url
    return operators

def download_from_url(url_list,num,sleep=3):
    options = webdriver.ChromeOptions()
    options.headless = False
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(PATH+'/chromedriver',chrome_options=options)  # Optional argument, if not specified will search path.
    driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': PATH+"/download/"}}
    command_result = driver.execute("send_command", params)
    for operator in url_list:
        n=len(operator['url'])
        for url in operator['url']:
            newname="download/{}{}.csv".format(operator['provider'],str(n))
            driver.get(url);
            if num!=5:
                search_box = driver.find_element_by_id("settingsmenubutton").click()
                driver.find_element_by_id("noofbuilds").clear()
                driver.find_element_by_id("noofbuilds").send_keys(str(num))
                time.sleep(sleep)
            search_box = driver.find_element_by_id('downloadCSV').click()
            time.sleep(1)
            os.rename('download/Test Results.csv', newname)
            n-=1
    time.sleep(2)
    return True

def remove_rows_csv(df,num,word_list=["Esli eto slovo est v stroke, to stroka udalit'sya"]):
    #if row will contain word, row will be deleted
    x=[]
    for index, row in df.iterrows():
        n=0
        for item in row:
            if type(item)==float:
                n+=1
            if type(item)==str:
                for word in word_list:
                    if item.count(word)>0:
                        x.append(index)
                        continue
                if item.count("\\")>2:
                    x.append(index)
                    continue
        if n==num:
            x.append(index)
    df1=df.drop(x, axis=0)
    return df1

def colnum_string(n):
    ###Example of this function: input=6, output=F
    string = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        string = chr(65 + remainder) + string
    return string

def rename_test_column(path):
    df = pd.read_csv(path)
    for i in range(0,len(df)):
        df["Test"][i]=df["Test"][i][14:-5]
    ###Merge rows with NA values
    df=df.fillna('').groupby('Test',as_index=False).agg('sum')
    df.to_csv(path,index=False)
    return(df)

def merge_df_and_save_to_excel(dict_with_url, number_of_progons):
    total_df=pd.DataFrame(columns=[" ","PASSED","FAILED","SKIPPED"])
    total_previous_df=pd.DataFrame(columns=[" ","PASSED","FAILED","SKIPPED"])
    diff_table=pd.DataFrame(columns=['Стали работать','Перестали работать','Перестали запускаться'])
    total_passed,total_failed,total_skipped=0,0,0
    previous_passed,previous_failed,previous_skipped=0,0,0
    length_dfs=[]
    diff_tables_len=[]
    cols=list(range(2,number_of_progons+3))
    timestr = time.strftime("%Y.%m.%d")
    excel_writer = pd.ExcelWriter("report/"+timestr+".xlsx", engine='xlsxwriter')
    for operator in dict_with_url:
        for i in range (1,len(operator['url'])+1):
            df = pd.read_csv("download/{}{}.csv".format(operator['provider'],i),usecols=cols)
            df = remove_rows_csv(df,number_of_progons,["SORM.test","start_sorm","test_stop"])
            if i==1:
                header=list(df.columns)
                finaldf=pd.DataFrame(columns=header)
            finaldf=finaldf.append(df,sort=False)

        ####Создадим дифф таблицу
        finaldf.to_csv("download/"+operator['provider']+".csv", index=False)
        finaldf=rename_test_column("download/"+operator['provider']+".csv")
        finaldf = finaldf.sort_index(ascending=False, axis=1)
        real_num_of_progons=(len(list(finaldf.head(0))))-1
        diff_for_one_operator=create_diff_table(finaldf,operator['provider'], include_provider_name=True)
        diff_for_one_operator.to_excel(excel_writer, operator['provider'],startrow=1 , startcol=real_num_of_progons+2,index=False)
        diff_table=diff_table.append(diff_for_one_operator)
        diff_tables_len.append(len(diff_table))

        ###Считаем сколько passed,failed,skipped тестов и создаем отдельную таблицу        
        passed=countif_in_rows("PASSED",finaldf)
        failed=countif_in_rows("FAILED",finaldf)
        skipped=countif_in_rows("SKIPPED",finaldf)
        results=["SUMMARY:"]
        for i in range (0,len(passed)-1):
            results.append(" ")
        finaldf.loc[len(finaldf)+30]=results
        finaldf.loc[len(finaldf)+30]=passed
        finaldf.loc[len(finaldf)+30]=failed
        finaldf.loc[len(finaldf)+30]=skipped      
        length_dfs.append(len(finaldf)+1)
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
        ###### Save df to excel
        finaldf.to_excel(excel_writer, sheet_name=operator['provider'],index=False)
        workbook  = excel_writer.book
        worksheet = excel_writer.sheets[operator['provider']]
        
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
        worksheet.set_column(0, 0, 25)
        worksheet.set_column(1, real_num_of_progons, 7)
        worksheet.set_column(real_num_of_progons+2, real_num_of_progons+2, width-15)
        worksheet.set_column(real_num_of_progons+3, real_num_of_progons+3, width-3)
        worksheet.set_column(real_num_of_progons+4, real_num_of_progons+4, width-15)
        worksheet.merge_range(colnum_string(real_num_of_progons+3)+'1:'+colnum_string(real_num_of_progons+5)+'1', 'Сравнение последнего и предпоследнего прогона', merge_format)

        end=colnum_string(real_num_of_progons+1)+str(len(finaldf)+1)
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
   

    total_df.loc[len(total_df)]=["Всего: ",total_passed,total_failed,total_skipped]
    total_previous_df.loc[len(total_df)]=["Всего: ",previous_passed,previous_failed,previous_skipped]
    total_df.to_excel(excel_writer, sheet_name="SUMMARY",startrow=1,index=False)
    total_previous_df.to_excel(excel_writer, sheet_name="SUMMARY",startrow=len(total_df)+4,index=False)
    diff_table.to_excel(excel_writer, 'SUMMARY',startrow=1 , startcol=5,index=False)
    ###Форматирование summary страницы
    worksheet2 = excel_writer.sheets["SUMMARY"]   
    worksheet2.merge_range('A1:D1', 'Cтатистика по последнему прогону', merge_format)
    worksheet2.merge_range('F1:H1', 'Таблица сравнения между последней и предпоследней сборками', merge_format)
    worksheet2.merge_range('A'+str(len(total_df)+4)+':D'+str(len(total_df)+4), 'Cтатистика по предыдущему прогону', merge_format)
    worksheet2.set_column(5, 5, width-15)
    worksheet2.set_column(6, 6, width-3)
    worksheet2.set_column(7, 7, width-15)
    worksheet2.set_column(0, 3, 22)
    excel_writer.save()
    return timestr, length_dfs, len(total_df)+1, diff_tables_len, real_num_of_progons

def set_border(ws, cell_range, fill=False, color="DDD9C4"):
    border = Border(left=Side(border_style='thin', color='000000'),
                right=Side(border_style='thin', color='000000'),
                top=Side(border_style='thin', color='000000'),
                bottom=Side(border_style='thin', color='000000'))
    if fill==False:
        tmp=cell_range.split(":")
        a=tmp[0][1:]
        b=tmp[1][0]+a
        header=tmp[0]+":"+b
    
        rows = ws[cell_range]
        for row in rows:
            for cell in row:
                cell.border = border
    
        head=ws[header]
        for row in head:
            for cell in row:
                cell.style=Style(fill=PatternFill(patternType='solid',
                                        fill_type='solid', 
                                        fgColor=Color(color)))
                cell.border = border
    if fill==True:
        rows = ws[cell_range]
        for row in rows:
            for cell in row:
                cell.style=Style(fill=PatternFill(patternType='solid',
                                        fill_type='solid', 
                                        fgColor=Color(color)))
                cell.border = border

def countif_in_rows(word,df):
##count in each columns by word, return list of counts
    x=['TOTAL '+word]
    n=0
    for column in df.columns[1:]:
        for cell in df[column]:
            if cell==word:
                n=n+1
        x.append(n)
        n=0
    return(x)

def create_diff_table(df,provider,builds_to_diff="default",include_provider_name=False):
    if builds_to_diff=="default":
        build1=1
        build2=2
    else:
        try:
            build1=list(df.columns).index(str(builds_to_diff[0]))
            build2=list(df.columns).index(str(builds_to_diff[1]))
        except ValueError:
        	print("В отчете нет информации по сборкам, которые хотите сравнить")
        	empty_df=pd.DataFrame({'A' : []})
        	return empty_df

    # df=pd.read_csv(csv)
    test=df[df.columns[0]]
    today=df[df.columns[build1]]
    yesterday=df[df.columns[build2]]
    
    if include_provider_name:
        passed=[" "]
        failed=[provider]
        norun=[" "]
    else:
        passed=[]
        failed=[]
        norun=[]    	
    for i in range(0,len(test)-1):
        if str(today[i])==str(yesterday[i]):
            continue
        if str(today[i])=='PASSED' and str(yesterday)!="PASSED":
            passed.append(test[i])
        if str(today[i])=='FAILED' and (str(yesterday)!='FAILED' or str(yesterday)=='SKIPPED'):
            failed.append(test[i])
        if str(today[i])=='' and str(yesterday)!='':
            norun.append(test[i])
    
    s1=pd.Series(passed,name='Стали работать')
    s2=pd.Series(failed,name='Перестали работать')
    s3=pd.Series(norun,name='Перестали запускаться')
    
    
    df1=pd.concat([s1,s2,s3], axis=1)
    return df1

def get_maximum_row(ws, column):
    try:
        return max(coordinate_from_string(cell)[-1]
            for cell in ws._cells if cell.startswith(column))
    except ValueError:
        return 1

def append_df_to_excel(filename, df, startcol, sheet_name='Sheet1', descr=None,
	                   startrow=None,
                       truncate_sheet=False, 
                       **to_excel_kwargs):
    """
    Append a DataFrame [df] to existing Excel file [filename]
    into [sheet_name] Sheet.
    If [filename] doesn't exist, then this function will create it.

    Parameters:
      filename : File path or existing ExcelWriter
                 (Example: '/path/to/file.xlsx')
      df : dataframe to save to workbook
      sheet_name : Name of sheet which will contain DataFrame.
                   (default: 'Sheet1')
      startrow : upper left cell row to dump data frame.
                 Per default (startrow=None) calculate the last row
                 in the existing DF and write to the next row...
      truncate_sheet : truncate (remove and recreate) [sheet_name]
                       before writing DataFrame to Excel file
      to_excel_kwargs : arguments which will be passed to `DataFrame.to_excel()`
                        [can be dictionary]

    Returns: None
    """
    from openpyxl import load_workbook

    # ignore [engine] parameter if it was passed
    if 'engine' in to_excel_kwargs:
        to_excel_kwargs.pop('engine')

    writer = pd.ExcelWriter(filename, engine='openpyxl')

    try:
        # try to open an existing workbook


        writer.book = load_workbook(filename)

        # get the last row in the existing Excel sheet
        # if it was not specified explicitly
        # if startrow is None and sheet_name in writer.book.sheetnames:
        #     startrow = writer.book[sheet_name].max_row

        startrow=max(get_maximum_row(writer.book[sheet_name],colnum_string(startcol+1)),
                     get_maximum_row(writer.book[sheet_name],colnum_string(startcol+2)),
                     get_maximum_row(writer.book[sheet_name],colnum_string(startcol+3)))

        # truncate sheet
        if truncate_sheet and sheet_name in writer.book.sheetnames:
            # index of [sheet_name] sheet
            idx = writer.book.sheetnames.index(sheet_name)
            # remove [sheet_name]
            writer.book.remove(writer.book.worksheets[idx])
            # create an empty sheet [sheet_name] using old index
            writer.book.create_sheet(sheet_name, idx)

        # copy existing sheets
        writer.sheets = {ws.title:ws for ws in writer.book.worksheets}
    except FileNotFoundError:
        # file does not exist yet, we will create it
        pass

    if startrow is None:
        startrow = 0

    # write out the new sheet
    df.to_excel(writer, sheet_name, startrow=startrow+2, startcol=startcol, **to_excel_kwargs)
    if descr!=None:
        writer.book[sheet_name].merge_cells(colnum_string(startcol+1)+str(startrow+2)+":"+colnum_string(startcol+3)+str(startrow+2))
        writer.book[sheet_name][colnum_string(startcol+1)+str(startrow+2)]=descr
        writer.book[sheet_name].cell(colnum_string(startcol+1)+str(startrow+2)).alignment = Alignment(horizontal='center')
        writer.book[sheet_name].cell(colnum_string(startcol+1)+str(startrow+2)).font = Font(color="FF0000", bold=True)
    set_border(writer.book[sheet_name], colnum_string(startcol+1)+str(startrow+3)+":"+colnum_string(startcol+3)+str(startrow+3+len(df)))
    # save the workbook
    writer.save()