from my_func import *
from bash import bash
from pprint import pprint

number_of_progons=5
wait=3

beeline={
         "provider":"Beeline",
		 "job":"Beeline_BVT",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"]
}
mts={
         "provider":"MTS",
		 "job":"MTS_MSK_VOLTE",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"]
}

megafon={
         "provider":"Megafon",
		 "job":"Megafon_IMS_MSK",
		 "dvo":["CALLDIR","WAIT","HOLD","3PTY","SRVCC","CFU","CFX"]
}

operators=[beeline,mts,megafon]
# operators=[megafon]

##Get list of dictionary's with url list
dict_with_url=get_url(operators)

try:
    # if os.path.exists("download"):
    #     bash("rm -rf ./download")
    # if not os.path.exists("report"):
    #     os.mkdir("report")
    # os.mkdir("download")
    # download_from_url(dict_with_url, number_of_progons,wait)
    timestr, length_dfs=merge_df_and_save_to_excel(dict_with_url, number_of_progons)
finally:
    print("GOTOVO")

n=0
for operator in dict_with_url:
    wb = openpyxl.load_workbook("report/"+timestr+".xlsx")
    ws = wb[operator['provider']]
    end=colnum_string(number_of_progons+1)+str(length_dfs[n])
    set_border(ws, "A1:"+end)
    n+=1
    # set_border(ws1, "I1:J6")
    # set_border(ws1, "I11:J14")
    # set_border(ws2, "A1:C"+str(diff_len))
    # set_border(ws3, "A1:B"+str(skipped_len))
    # set_border(ws, "A"+str(length_dfs[0]-2)+":"+"F"+str(length_dfs[0]+1),fill=True, color="95B3D7")
    wb.save("report/"+timestr+".xlsx")
