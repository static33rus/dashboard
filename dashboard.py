import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table
from modules.database import *
from time import time
import json

builds_in_report=2 ### Кол-во столбцов в таблице с результатами тестов
builds_in_dropdown=7 ###Кол-во значений в выпадающих меню
color = ['#9ACD32', '#FF4500', '#FFFFE0', '#D0F9B1']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
branch=["Release","Develop"]
mass=["release","develop","jenkins build"]
autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions'] = True
'''
Layout - это структура html страницы (размер div, позиционирование и тд).
app.layout - основной layout, который отображается всегда. В данном случае это tab'ы 
first_layout - это то, что отобразится при нажатии на tab'ы для функциональных тестов
second_layout - то, что отобразится при нажатии на dpdk tab
'''
app.layout=html.Div([
					dcc.Tabs(
							value='Beeline',
							id='tabs',
							children=[
								  dcc.Tab(label='Beeline', value='Beeline', className='tab'),
								  dcc.Tab(label='MTS', value='MTS', className='tab'),
								  dcc.Tab(label='Megafon', value='Megafon', className='tab'),
								  dcc.Tab(label='RTK', value='RTK', className='tab'),
								  dcc.Tab(label='Sbertel', value='Sbertel', className='tab'),
								  dcc.Tab(label='Командные 645', value='libSSRV_645', className='tab'),
								  dcc.Tab(label='Командные 645 с сумматором', value='libSSRV_645_with_SUMMATOR', className='tab'),
								  dcc.Tab(label='DPDK', value='DPDK', className='tab'),
								  ]
							),
					html.Div(id='tab-output')
					])

first_layout =[
					html.Div([html.H3(id='global-title',className='class_h1')],style={'width': '100%'}),
					html.Div([
						html.Div( [
							dcc.Dropdown(id="branch_dropdown",options=[{'label': i,'value': i} for i in branch],value='Release'),
							],style={'width': '20%','display': 'inline-block'}),
						html.Div([dcc.Slider(id='slider',min=10,max=30, marks={10:'10',15:'15',20:'20',25:'25',30:'30'},value=15)],style={'width': '30%','display': 'inline-block','float':'right','margin-right':80}),
					]),
					html.Div(id='intermediate-value', style={'display': 'none'}),
					html.Div([
						html.Div(id='pie_total_graph')
						],style={'width': '40%','margin-top':40,'display': 'inline-block','vertical-align': 'top'}),
					
					html.Div([
						dcc.Graph(id='history-graph'),
						],style={'width': '58%','display': 'inline-block'}),
					html.Div([html.H3('Difference between builds',className='class_h3')],style={'width': '100%'}),
					html.Div([
						html.Div([
							html.Div([
							dcc.RadioItems(
								  id='Dropdown-1-state',
								  options=[{'label': i, 'value': i} for i in mass],
								  value='release',
								  labelStyle={'display': 'inline-block'}
							  ),
							dcc.Dropdown(id="input-1-state",value='Latest',style={'width': '100%','height':35, 'float': 'right', 'display': 'inline-block'})
						  ],
						  style={'width': '48%', 'display': 'inline-block'}),

							html.Div([
							  dcc.RadioItems(
								  id='Dropdown-2-state',
								  options=[{'label': i, 'value': i} for i in mass],
								  value='release',
								  labelStyle={'display': 'inline-block'}
							  ),
							dcc.Dropdown(id='input-2-state', value='Latest',style={'width': '100%', 'height':35,'float': 'right', 'display': 'inline-block'}),
							],style={'width': '48%', 'float': 'right', 'display': 'inline-block'}),
					],style={'width': '80%', 'display': 'inline-block'}),
					html.Button(id='submit-button', n_clicks=0, children='get diff',style={'width': '20%','height':35, 'float': 'right','display': 'inline-block','margin-top':24})
				],style={'width': '45%','margin-top':'30'}),

				html.Div(dash_table.DataTable(id='result-table',
						style_cell={'textAlign': 'center'},
						style_header={'backgroundColor': '#cadef7','fontWeight': 'bold'},
						style_data_conditional=[{
										'if': {
											'column_id': str(i),
											'filter': '{} eq "PASSED"'.format(str(i))
										},
										'backgroundColor': '#3D9970',
										'color': 'white',} for i in range (0,1000)],
						sorting=True,
						sorting_type="multi"),
					style={'width': '45%','display': 'inline-block'}),
			
				html.Div(dash_table.DataTable(id='version-table',
						style_cell={'textAlign': 'center'},
						style_header={'backgroundColor': '#cadef7','fontWeight': 'bold'},
						sorting=True,
						sorting_type="multi"),
					style={'width': '45%','margin-top':'17','margin-left':'50','display': 'inline-block','vertical-align': 'top'}),
				html.Div([
						html.Div([
							html.Ul(id="download",className='class_ul')])
						])
				]


second_layout = [
  html.Div( [dcc.Dropdown(id="dpdk_dropdown",value='Latest'),
			],style={'width': '20%','display': 'inline-block'}),
  html.Div([html.H3('DPDK PERFOMANCE TEST',className='class_h1')],style={'width': '100%'}),
  html.Div([
		html.Div(id='left-side',style={'width': '49%','display': 'inline-block'}),
		html.Div(id='right-side',style={'width': '49%','display': 'inline-block'}),
  ]),
  html.Div(id='intermediate-value', style={'display': 'none'}),
]

'''
Callback - это декоратор, который передает функции input значения и указывает какому элементу объекта layout вернуть ouput значения.
Простыми словами: callback позволяет динамически изменять страницу при определенных действиях: нажатии на кнопку и тд 
'''
@app.callback(
	dash.dependencies.Output('intermediate-value', 'children'),
	[dash.dependencies.Input('tabs', 'value'),
	dash.dependencies.Input('branch_dropdown', 'value'),
	dash.dependencies.Input('slider', 'value')])
def sql_queries(tab_value,branch_value,slider_value):
'''
Данный callback принимает значения нажатой вкладки, выпадающего меню и слайдера. Затем подключается к базе и считывает все нужные данные, после их хранит
в sql_dump'e
'''
	sql_data={}
	if tab_value!='DPDK':
		beeline={
			 "provider":"Beeline",
			 "result":"Beeline_BVT_NEW",
			 "scenario":"Beeline/Volte/BVT_NEW"
		}
		mts={
				 "provider":"MTS",
				 "result":"MTS_MSK_VOLTE_COLLECTION",
				 "scenario":"MTS/PSI2017/volte"
		}
		
		megafon={
				 "provider":"Megafon",
				 "result":"Megafon_IMS_MSK",
				 "scenario":"Megafon/VoWiFi/BVT"
		}
		
		rtk={
				 "provider":"RTK",
				 "result":"SORM_BVT_RTK_NSK_IMS_COLLECTION_MASS",
				 "scenario":"Rostelecom/IMS/20180628_Novosib"
		}
		
		sbertel={
				 "provider":"Sbertel",
				 "result":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS",
				 "scenario":"SberTel/VoWiFi"
		}
	
		libSSRV_645={
				 "provider":"libSSRV_645",
				 "result":"libSSRV_645",
		}
	
		libSSRV_645_with_SUMMATOR={
				 "provider":"libSSRV_645_with_SUMMATOR",
				 "result":"libSSRV_645_with_SUMMATOR",
		}
		all_operators=[beeline,mts,megafon,rtk,sbertel,libSSRV_645,libSSRV_645_with_SUMMATOR]
		autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
		operator_id=autotest.operator_id(tab_value)
		last_builds=autotest.last_builds(operator_id,builds_in_report,branch_value)
		dropdown_builds=autotest.last_builds(operator_id,builds_in_dropdown,branch_value)
		passed=autotest.select("select count(id) from total where operator={} and build={} and result='PASSED'".format(operator_id,last_builds[0]))[0]
		failed=autotest.select("select count(id) from total where operator={} and build={} and result='FAILURE'".format(operator_id,last_builds[0]))[0]
		skipped=autotest.select("select count(id) from total where operator={} and build={} and result='SKIPPED'".format(operator_id,last_builds[0]))[0]
		passed_history=autotest.get_result_history(operator_id,"PASSED",branch_value,slider_value)
		failed_history=autotest.get_result_history(operator_id,"FAILURE",branch_value,slider_value)
		skipped_history=autotest.get_result_history(operator_id,"SKIPPED",branch_value,slider_value)
		result_table=autotest.get_autotest_result_table(operator_id,last_builds)
		autotest.close()
		sql_data['operator']=tab_value
		sql_data['branch']=branch_value
		sql_data['operator_id']=operator_id
		sql_data['all_operators']=all_operators
		sql_data['last_builds']=last_builds
		sql_data['dropdown_builds']=dropdown_builds
		sql_data['passed_count_last_build']=passed
		sql_data['failed_count_last_build']=failed
		sql_data['skipped_count_last_build']=skipped
		sql_data['passed_history']=passed_history.to_json(orient='split', date_format='iso')
		sql_data['failed_history']=failed_history.to_json(orient='split', date_format='iso')
		sql_data['skipped_history']=skipped_history.to_json(orient='split', date_format='iso')
		sql_data['result_table']=result_table.to_json(orient='split', date_format='iso')
		sql_data['time']=time()
	else:
		sql_data['operator']=tab_value
		autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest_perf")
		sql_data['last_builds']=autotest.select("select DISTINCT build from dpdk_drops order by build DESC limit {}".format(builds_in_dropdown))
		autotest.close()
	return json.dumps(sql_data)

@app.callback(
  Output('tab-output', 'children'),
  [Input('tabs', 'value')])
def show_content(value):
'''
Данный callback возвращает нужный layout в зависимости от нажатой кнопки
'''
	if value != 'DPDK':
		return first_layout
	else:
		return second_layout

@app.callback(Output('global-title', 'children'), [Input('intermediate-value', 'children')])
def global_title(json_dmp):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		return "{} last {}".format(data['operator'],data['branch'])

@app.callback(Output('pie_total_graph', 'children'), [Input('intermediate-value', 'children')])
def display_pie_total_graph(json_dmp):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		operator_id=data['operator_id']
		last_builds=data['last_builds']
		passed=data['passed_count_last_build']
		failed=data['failed_count_last_build']
		skipped=data['skipped_count_last_build']
		data = [
			{
				'values': [passed,failed,skipped],
				'type': 'pie',
				'hoverinfo': 'label+percent',
				'textfont': dict(size=18,family='Courier New, monospace'),
				'textinfo': 'value',
				'labels': ['PASSED', 'FAILED', 'SKIPPED'],
				'marker': dict(colors=color, line=dict(color='#000000', width=1))
			},
		]
	
		return html.Div([
			dcc.Graph(
				id='graph',
				figure={
					'data': data,
					'layout': {
						'height': 400,
						'margin': {
							'l': 0,
							'r': 0,
							'b': 0,
							't': 0
						},
						'legend': {'x': 0, 'y': 1}
					}
				}
			)
		])


@app.callback(Output('history-graph', 'figure'), [Input('intermediate-value', 'children')])
def display_history_line_graph(json_dmp):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		operator_id=data['operator_id']
		last_builds=data['last_builds']
		passed=pd.read_json(data['passed_history'], orient='split')
		failed=pd.read_json(data['failed_history'], orient='split')
		skipped=pd.read_json(data['skipped_history'], orient='split')
		return { 'data': [ 
				{'x': passed['builds'], 'y': passed['PASSED'], 'type': 'line', 'line' : {'color' : '#9ACD32','width' : 3},'name':'PASSED','text':'click to view version'}, 
				{'x': failed['builds'], 'y': failed['FAILURE'], 'type': 'line', 'line' : {'color' : 'red','width' : 3},'name':'FAILED'},
				{'x': skipped['builds'], 'y': skipped['SKIPPED'], 'type': 'line', 'line' : {'color' : 'grey','width' : 3},'name':'SKIPPED'}
				],
			'layout': go.Layout(
				title = 'History graph',
				titlefont=dict(family='Courier New, monospace',size=20),
				xaxis=dict(
							showline=True,
							title='builds',
							titlefont=dict(family='Courier New, monospace',size=14),
							showgrid=False,
							showticklabels=True,
							linecolor='rgb(204, 204, 204)',
							linewidth=2,
							ticks='outside',
							tickcolor='rgb(204, 204, 204)',
							tickwidth=2,
							ticklen=5,
							tickfont=dict(
							family='Arial',
							size=12,
							color='rgb(82, 82, 82)')),
				yaxis=dict(showgrid=False,zeroline=False,showline=False,showticklabels=False),
				# yaxis={'title': 'Test count', 'range': [0, 200],'titlefont': {'family':'Courier New, monospace','size':16,'color':'#7f7f7f'}},
				showlegend=False,
				hovermode='x',
			)
		 }

@app.callback(Output('input-1-state', 'options'), [Input('intermediate-value', 'children'),Input('Dropdown-1-state', 'value')])
def get_option_for_input1_dropdown(json_dmp,dd1):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
		if dd1=="jenkins build":
			builds=data['dropdown_builds']
		else:
			builds=autotest.select("select DISTINCT mass from version where mass REGEXP 'mass.{}' and operator={} order by id DESC limit {}".format(dd1,data['operator_id'],builds_in_dropdown))
			autotest.close()
		return [{'label': i, 'value': i} for i in builds]
@app.callback(Output('input-2-state', 'options'), [Input('intermediate-value', 'children'),Input('Dropdown-2-state', 'value')])
def get_option_for_input2_dropdown(json_dmp,dd2):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
		if dd2=="jenkins build":
			builds=data['dropdown_builds']
		else:
			builds=autotest.select("select DISTINCT mass from version where mass REGEXP 'mass.{}' and operator={} order by id DESC limit {}".format(dd2,data['operator_id'],builds_in_dropdown))
		autotest.close()
		return [{'label': i, 'value': i} for i in builds]


@app.callback(Output('result-table', 'data'), [Input('intermediate-value', 'children'),Input('submit-button', 'n_clicks')],
			[State('Dropdown-1-state', 'value'),
			State('Dropdown-2-state', 'value'),
			State('input-1-state', 'value'),
			State('input-2-state', 'value')])
def return_rows_for_autotest_result_table(json_dmp,n_clicks,dd1,dd2, input1, input2):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		operator_id=data['operator_id']
		last_builds=data['last_builds']
		result_table=pd.read_json(data['result_table'], orient='split')
		result_table=result_table[result_table[str(last_builds[0])] != result_table[str(last_builds[1])]]
		if (dd1!="release" or dd2!="release" or input1!="Latest" or input2!="Latest") and time()>data['time']+2:
			if input1=="Latest":
				input1=last_builds[0]
			if input2=="Latest":
				input2=last_builds[1]
			try:
				autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
				if dd1=="jenkins build":
					build1=[input1]				
				else:
					print("select DISTINCT build from version where mass REGEXP 'mass.{}\\\s*:\\\s*{}' and operator={} order by build desc limit 1".format(dd1,input1.split(':')[1],operator_id))
					build1=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}\\\s*:\\\s*{}' and operator={} order by build desc limit 1".format(dd1,input1.split(':')[1],operator_id))
				if dd2=="jenkins build":
					build2=[input2]
				else:
					print("select DISTINCT build from version where mass REGEXP 'mass.{}\\\s*:\\\s*{}' and operator={} order by build desc limit 1".format(dd2,input2.split(':')[1],operator_id))
					build2=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}\\\s*:\\\s*{}' and operator={} order by build desc limit 1".format(dd2,input2.split(':')[1],operator_id))
				result_table=autotest.get_autotest_result_table(operator_id,build1+build2)
				result_table=result_table[result_table[str(build1[0])] != result_table[str(build2[0])]]
				if result_table.empty:
					return None
				# result_table.columns=["test","{} {} (build {})".format(dd1,input1,build1),"{} {} (build {})".format(dd2,input2,build2) ]
			except IndexError:
				print("No in database")
				return None
			finally:
				autotest.close()
		return result_table.to_dict("rows")
@app.callback(Output('result-table', 'columns'), [Input('intermediate-value', 'children'),Input('submit-button', 'n_clicks')],
			[State('Dropdown-1-state', 'value'),
			State('Dropdown-2-state', 'value'),
			State('input-1-state', 'value'),
			State('input-2-state', 'value')])
def return_header_for_autotest_result_table(json_dmp,n_clicks,dd1,dd2, input1, input2):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		operator_id=data['operator_id']
		last_builds=data['last_builds']
		result_table=pd.read_json(data['result_table'], orient='split')
		if (dd1!="release" or dd2!="release" or input1!="Latest" or input2!="Latest") and time()>data['time']+2:
			if input1=="Latest":
				input1=last_builds[0]
			if input2=="Latest":
				input2=last_builds[1]
			try:
				autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
				if dd1=="jenkins build":
					build1=[input1]				
				else:
					build1=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}\\\s*:\\\s*{}' and operator={} order by build desc limit 1".format(dd1,input1.split(':')[1],operator_id))
				if dd2=="jenkins build":
					build2=[input2]
				else:
					build2=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}\\\s*:\\\s*{}' and operator={} order by build desc limit 1".format(dd2,input2.split(':')[1],operator_id))
				result_table=autotest.get_autotest_result_table(operator_id,build1+build2)
				if result_table.empty:
					return None
				# result_table.columns=["test","{} {} (build {})".format(dd1,input1,build1[0]),"{} {} (build {})".format(dd2,input2,build2[0]) ]
			except IndexError:
				print("No in database")
				return None
			finally:
				autotest.close()
		return [{"name": i, "id": i} for i in result_table.columns]

@app.callback(Output('version-table', 'columns'),[Input('history-graph', 'clickData'),Input('intermediate-value', 'children')])
def return_header_for_version_table(clickData,json_dmp):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
		operator_id=data['operator_id']
		last_builds=data['last_builds']
		if clickData is not None and time()>data['time']+2:
			current_build=list()
			current_build.append(clickData['points'][0]['x'])
		else:
			current_build=last_builds
		version_table=autotest.get_version_table(operator_id,current_build)
		autotest.close()
		return [{"name": i, "id": i} for i in version_table.columns]
@app.callback(Output('version-table', 'data'),[Input('history-graph', 'clickData'),Input('intermediate-value', 'children')])
def return_rows_for_version_table(clickData,json_dmp):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		autotest=Database(host="10.72.1.17", user="dash", passwd="12121212", db="autotest")
		operator_id=data['operator_id']
		last_builds=data['last_builds']
		if clickData is not None and time()>data['time']+2:
			current_build=list()
			current_build.append(clickData['points'][0]['x'])
		else:
			current_build=last_builds
		version_table=autotest.get_version_table(operator_id,current_build)
		autotest.close()
		return version_table.to_dict("rows")

@app.callback(Output('download', 'children'), [Input('intermediate-value', 'children')])
def return_link_for_download_result(json_dmp):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab != 'DPDK':
		tab_value=data['operator']
		last_builds=data['last_builds']
		operators=data['all_operators']
		location=[]
		for operator in operators:
			if operator['provider']==tab_value:
				if "result" in operator:
					location.append(html.Li(html.A("results",className='class_a', href="ftp://10.72.1.239/Results/{}/{}/".format(operator['result'],last_builds[0])),className='class_li'))
				if "scenario" in operator:
					location.append(html.Li(html.A("scenario",className='class_a', href="ftp://10.72.1.239/Dumps/{}/".format(operator['scenario'])),className='class_li'))
		return location



###Performance tab
@app.callback(Output('dpdk_dropdown', 'options'), [Input('intermediate-value', 'children'),Input('tabs', 'value')])
def get_option_for_dpdk_dropdown(json_dmp,tab_value):
	data=json.loads(json_dmp)
	tab=data['operator']
	if tab == 'DPDK':
		builds=data['last_builds']
		return [{'label': 'Jenkins build {}'.format(i), 'value': i} for i in builds]

@app.callback(Output('left-side', 'children'), [Input('intermediate-value', 'children'),Input('dpdk_dropdown', 'value')])
def display_drops_per_test(json_dmp,dropdown_value):
	data=json.loads(json_dmp)
	tab=data['operator']
	builds=data['last_builds']
	list_with_graphs=[]
	if tab == 'DPDK':
		if dropdown_value=='Latest':
			dropdown_value=builds[0]
		autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest_perf")
		drops = pd.read_sql('select * from dpdk_drops where build={}'.format(dropdown_value), con=autotest.db)
		tests=list(drops.test.unique())
		for test in tests:
			test_name=autotest.select("select test from test where id={}".format(test))[0]
			df=drops[drops.test == test]
			steps=list(df['step'])
			traffic_rate=list(df['Traffic_rate'])
			traffic_rate = [element*1000 for element in traffic_rate]
			rx_drops=list(df['rx_drops'])
			rx_drops = [element/1024/1024/1024 for element in rx_drops]
			drops_per_sec=list(df['rx_dropsPerSec'])
			list_with_graphs.append(dcc.Graph(
        					id='{} drops'.format(test_name),
        					figure={
        					  'data': [ 
        					{'x': steps, 'y': traffic_rate, 'type': 'line', 'line' : {'color' : '#9ACD32','width' : 3},'name':'rate','text':'Mb/sec'}, 
        					{'x': steps, 'y': drops_per_sec, 'type': 'line', 'line' : {'color' : 'orange','width' : 3},'name':'drops/sec','text':'pkts/sec'},
        					{'x': steps, 'y': rx_drops, 'type': 'line', 'line' : {'color' : 'red','width' : 3},'name':'drops','text':'Gb'},
        					],
        					  'layout': go.Layout(
        					      title = 'DPDK drops in test: {}'.format(test_name),
        					      titlefont=dict(family='Courier New, monospace',size=20),
        						  xaxis=dict(
        					      		showline=False,
        					      		title='test step',
        					      		titlefont=dict(family='Courier New, monospace',size=14),
        					      		showgrid=False,
        					      		showticklabels=True,
        					      		linecolor='rgb(204, 204, 204)',
        					      		linewidth=2,
        					      		tickvals=steps,
        					      		tickcolor='rgb(204, 204, 204)',
        					      		tickwidth=2,
        					      		ticklen=5,
        					      		tickfont=dict(
        					      		family='Arial',
        					      		size=12,
        					      		color='rgb(82, 82, 82)')),
        					      yaxis=dict(
        					      		showline=False),
        					showlegend=False,
        					hovermode='x',
      						)},
							))
		print(list_with_graphs)
		autotest.close()
		return list_with_graphs


@app.callback(Output('right-side', 'children'), [Input('intermediate-value', 'children'),Input('dpdk_dropdown', 'value')])
def display_system_load_per_test(json_dmp,dropdown_value):
	data=json.loads(json_dmp)
	tab=data['operator']
	builds=data['last_builds']
	list_with_graphs=[]
	if tab == 'DPDK':
		if dropdown_value=='Latest':
			dropdown_value=builds[0]
		autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest_perf")
		stats = pd.read_sql('select * from system_load where build={}'.format(dropdown_value), con=autotest.db)
		tests=list(stats.test.unique())		
		for test in tests:
			test_name=autotest.select("select test from test where id={}".format(test))[0]
			memory=autotest.select_list_of_rows("select at_start,at_end,max from system_load where build={} and resource='mem' and test={}".format(dropdown_value,test))[0]
			cpu=autotest.select_list_of_rows("select at_start,at_end,max from system_load where build={} and resource='cpu' and test={}".format(dropdown_value,test))[0]
			print("sdsdsdsdsd",memory,cpu)
			list_with_graphs.append(dcc.Graph(
        					id='{} usage'.format(test_name),
        					figure={
        					  'data': [ 
        					{'x': ['start value','end value','maximum'], 'y': memory, 'type': 'bar','name':'memory usage','text':'mb'}, 
        					{'x': ['start value','end value','maximum'], 'y': cpu, 'type': 'bar','name':'cpu usage','text':'%'},
        					],
        					  'layout': go.Layout(
        					title = 'Resource usage in test: {}'.format(test_name),
        					titlefont=dict(family='Courier New, monospace',size=20),
        					xaxis=dict(
        					      showline=True,
        					      titlefont=dict(family='Courier New, monospace',size=14),
        					      showgrid=False,
        					      showticklabels=True,
        					      linecolor='rgb(204, 204, 204)',
        					      linewidth=2,
        					      ticks='outside',
        					      tickcolor='rgb(204, 204, 204)',
        					      tickwidth=2,
        					      ticklen=5,
        					      tickfont=dict(
        					      family='Arial',
        					      size=12,
        					      color='rgb(82, 82, 82)')),
        					yaxis=dict(
        					      showline=False),
        					showlegend=False,
        					hovermode='x',
      						)},
							))
		autotest.close()
		return list_with_graphs

if __name__ == '__main__':
	app.server.run(debug=True)
	# app.server.run(host='0.0.0.0')

