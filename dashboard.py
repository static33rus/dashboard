import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import dash_table
from modules.database import *
from time import time
import json

builds_in_report=2
builds_in_dropdown=7
color = ['#9ACD32', '#FF4500', '#FFFFE0', '#D0F9B1']
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
branch=["Release","Develop"]
mass=["release","develop","jenkins build"]
autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
def app_layout():
	return(html.Div([
					dcc.Tabs(
							value='Beeline',
							id='tabs',
							children=[
								  dcc.Tab(label='Beeline', value='Beeline', className='tab'),
								  dcc.Tab(label='MTS', value='MTS', className='tab'),
								  dcc.Tab(label='Megafon', value='Megafon', className='tab'),
								  dcc.Tab(label='RTK', value='RTK', className='tab'),
								  dcc.Tab(label='Sbertel', value='Sbertel', className='tab'),
								  ]
							),
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
					])
	)
app.layout=app_layout()

@app.callback(
	dash.dependencies.Output('intermediate-value', 'children'),
	[dash.dependencies.Input('tabs', 'value'),
	dash.dependencies.Input('branch_dropdown', 'value'),
	dash.dependencies.Input('slider', 'value')])
def sql_queries(tab_value,branch_value,slider_value):
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
	
	sbertel={
			 "provider":"Sbertel",
			 "job":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS",
			 "dvo":["CALLDIR","SMS","HOLD","3PTY","WAIT","CFU","CFB","CFNRY","CFNRC"],
			 "result":"SORM_BVT_SberTel_VoWiFi_COLLECTION_MASS",
			 "scenario":"SberTel/VoWiFi"
	}
	all_operators=[beeline,mts,megafon,rtk,sbertel]
	sql_data={}
	autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
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
	return json.dumps(sql_data)

@app.callback(Output('global-title', 'children'), [Input('intermediate-value', 'children')])
def global_title(json_dmp):
	data=json.loads(json_dmp)
	return "{} last {}".format(data['operator'],data['branch'])

@app.callback(Output('pie_total_graph', 'children'), [Input('intermediate-value', 'children')])
def display_pie_total_graph(json_dmp):
	data=json.loads(json_dmp)
	operator_id=data['operator_id']
	last_builds=data['last_builds']
	passed=data['passed_count_last_build']
	failed=data['failed_count_last_build']
	skipped=data['skipped_count_last_build']

	data = [
		{
			'values': [passed,failed,skipped],
			'type': 'pie',
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
	autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
	data=json.loads(json_dmp)
	if dd1=="jenkins build":
		builds=data['dropdown_builds']
	else:
		builds=autotest.select("select DISTINCT mass from version where mass REGEXP 'mass.{}' and operator={} order by id DESC limit {}".format(dd1,data['operator_id'],builds_in_dropdown))
		autotest.close()
	return [{'label': i, 'value': i} for i in builds]
@app.callback(Output('input-2-state', 'options'), [Input('intermediate-value', 'children'),Input('Dropdown-2-state', 'value')])
def get_option_for_input2_dropdown(json_dmp,dd2):
	autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
	data=json.loads(json_dmp)
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
			autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
			if dd1=="jenkins build":
				build1=[input1]				
			else:
				print("select DISTINCT build from version where mass REGEXP 'mass.{}        :{}' and operator={} order by build desc limit 1".format(dd1,input1.split(':')[1],operator_id))
				build1=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}        :{}' and operator={} order by build desc limit 1".format(dd1,input1.split(':')[1],operator_id))
			if dd2=="jenkins build":
				build2=[input2]
			else:
				print("select DISTINCT build from version where mass REGEXP 'mass.{}        :{}' and operator={} order by build desc limit 1".format(dd2,input2.split(':')[1],operator_id))
				build2=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}        :{}' and operator={} order by build desc limit 1".format(dd2,input2.split(':')[1],operator_id))
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
	operator_id=data['operator_id']
	last_builds=data['last_builds']
	result_table=pd.read_json(data['result_table'], orient='split')
	if (dd1!="release" or dd2!="release" or input1!="Latest" or input2!="Latest") and time()>data['time']+2:
		if input1=="Latest":
			input1=last_builds[0]
		if input2=="Latest":
			input2=last_builds[1]
		try:
			autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
			if dd1=="jenkins build":
				build1=[input1]				
			else:
				build1=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}        :{}' and operator={} order by build desc limit 1".format(dd1,input1.split(':')[1],operator_id))
			if dd2=="jenkins build":
				build2=[input2]
			else:
				build2=autotest.select("select DISTINCT build from version where mass REGEXP 'mass.{}        :{}' and operator={} order by build desc limit 1".format(dd2,input2.split(':')[1],operator_id))
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
	autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
	data=json.loads(json_dmp)
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
	autotest=Database(host="10.2.7.29", user="root", passwd="12121212", db="autotest")
	data=json.loads(json_dmp)
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
	tab_value=data['operator']
	last_builds=data['last_builds']
	operators=data['all_operators']
	location=[]
	for operator in operators:
		if operator['provider']==tab_value:
			location.append(html.Li(html.A("results",className='class_a', href="ftp://10.72.1.239/Results/{}/{}/".format(operator['result'],last_builds[0])),className='class_li'))
			location.append(html.Li(html.A("scenario",className='class_a', href="ftp://10.72.1.239/Dumps/{}/".format(operator['scenario'])),className='class_li'))
	return location


if __name__ == '__main__':
	# app.server.run(debug=True)
	app.server.run(host='0.0.0.0')

