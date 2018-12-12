from my_func import *
from openpyxl import load_workbook

number_of_progons=5
wait=3
NEED_FOR_USER_DIFF=True

beeline={
         "provider":"Beeline",
		 "job":"Beeline_BVT",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
		 "result":"Beeline_BVT_NEW"
}
mts={
         "provider":"MTS",
		 "job":"MTS_MSK_VOLTE",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
         "result":"MTS_MSK_VOLTE_COLLECTION"
}

megafon={
         "provider":"Megafon",
		 "job":"Megafon_IMS_MSK",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"],
         "result":"SORM_BVT_Megafon_VoLTE_COLLECTION_MASS_DEVELOP"
}

rtk={
         "provider":"RTK",
         "job":"SORM_BVT_RTK_NSK_IMS_COLLECTION_MASS",
         "dvo":["CALLDIR","WAIT","HOLD","3PTY","CFU","CFB","CFNRY","ACT_DVO","NEW_DVO","CLIR"],
         "result":"SORM_BVT_RTK_NSK_IMS_COLLECTION_MAS"
}

tele2={
         "provider":"Tele_2",
         "job":"SORM_BVT_Tele2_VOLTE_COLLECTION_MASS",
         "dvo":["CALLDIR","CW","HOLD","MPTY","SRVCC","CFU","CFX"],
         "result":"SORM_BVT_Tele2_VOLTE_COLLECTION_MASS"
}

sbertel={
         "provider":"SberTel",
         "job":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS",
         "dvo":["CALLDIR","SMS","HOLD","3PTY","WAIT","CFU","CFB","CFNRY","CFNRC"],
         "result":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS"
}

all_operators={
         "provider":"ALL_OPERATORS_IMS",
         "job":"SORM_HYBRID_REGRESSION_COLLECTION",
         "dvo":["Rostelecom","Beeline","MTS","Tele2","Sbertel","Megafon"],
         "result":"SORM_HYBRID_REGRESSION_COLLECTION"
}

builds_to_diff={
	     "provider":"Beeline",
	     "builds":[347,344]
}

operators=[beeline,mts,megafon,rtk,tele2,sbertel]
# operators=[all_operators]

##Get list of dictionary's with url list
dict_with_url=get_url(operators)

try:
    # if os.path.exists("download"):
    #     bash("rm -rf ./download")
    # if not os.path.exists("report"):
    #     os.mkdir("report")
    # os.mkdir("download")
    # download_from_url(dict_with_url, number_of_progons,wait)
    timestr, length_dfs, total_df_len, diff_df_len, real_num_of_progons=merge_df_and_save_to_excel(dict_with_url, number_of_progons)
    if NEED_FOR_USER_DIFF==True:
        add_user_diff_to_excel(builds_to_diff, timestr, real_num_of_progons)
finally:
    print("GOTOVO")

wb = openpyxl.load_workbook("report/"+timestr+".xlsx")    
n=0
previous=0
for operator in dict_with_url:
    current=diff_df_len[n]-previous
    ws = wb[operator['provider']]
    if real_num_of_progons>number_of_progons:
        print("Скорее всего сейчас проходит очередной прогон или один из прогонов не завершился успешно")
    # end=colnum_string(number_of_progons+1)+str(length_dfs[n])
    end=colnum_string(real_num_of_progons+1)+str(length_dfs[n])
    set_border(ws, "A1:"+end)
    set_border(ws, "A"+str(length_dfs[n]-3)+":"+end,fill=True, color="95B3D7")
    strt=colnum_string(real_num_of_progons+3)+"2"
    stop=colnum_string(real_num_of_progons+5)+str(current+2)
    fill=colnum_string(real_num_of_progons+3)+"3"+":"+colnum_string(real_num_of_progons+5)+"3"
    set_border(ws, fill,fill=True, color="95B3D7")
    set_border(ws, strt+":"+stop)
    previous=diff_df_len[n]
    n+=1
    fill=colnum_string(real_num_of_progons+3)+str(current+5)+":"+colnum_string(real_num_of_progons+5)+str(current+5)
    strt=colnum_string(real_num_of_progons+3)+str(current+4)
    stop=colnum_string(real_num_of_progons+5)+str(current+9)
    set_border(ws, fill,fill=True, color="95B3D7")
    set_border(ws, strt+":"+stop)

ws = wb["SUMMARY"]
###Форматируем total таблицу по текущему прогону
end=colnum_string(4)+str(total_df_len)
set_border(ws, "A2:"+end)
set_border(ws, "A"+str(total_df_len+1)+":D"+str(total_df_len+1),fill=True, color="95B3D7")
###Форматируем total таблицу по предыдущему прогону
set_border(ws, 'A'+str(total_df_len+4)+':D'+str(total_df_len*2+3))
set_border(ws, "A"+str(total_df_len*2+3)+":D"+str(total_df_len*2+3),fill=True, color="95B3D7")
###Форматируем total_diff таблицу
set_border(ws, "F3:H3",fill=True, color="95B3D7")
for item in diff_df_len[:-1]:
    set_border(ws, "F"+str(3+item)+":H"+str(3+item),fill=True, color="95B3D7")
set_border(ws, "F2:"+"H"+str(diff_df_len[-1]+2))
wb.save("report/"+timestr+".xlsx")

