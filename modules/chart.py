import matplotlib.pyplot as plt

class Chart:
	def __init__(self,graph_num):
		self.graph_num=graph_num
		self.fig, self.ax = plt.subplots(graph_num, 1, constrained_layout=True)
		if self.graph_num==1:
			self.fig.set_size_inches(7.5, 5, forward=True)			
		else:
			self.fig.set_size_inches(2.5*graph_num, 3.5*graph_num, forward=True)

	def add_subplot(self,plot_id,test_count,title):
		self.plot_id=plot_id
		if self.graph_num==1:
			self.ax.set_xlabel('builds')
			self.ax.set_ylabel('tests(n)')
			self.ax.set_title(title)
			self.ax.set_ylim([0,test_count+20])
		else:
			self.ax[plot_id].set_xlabel('builds')
			self.ax[plot_id].set_ylabel('tests(n)')
			self.ax[plot_id].set_title(title)
			self.ax[plot_id].set_ylim([0,test_count+20])

	def paint(self,df,color="green"):
		if self.graph_num==1:
			df.plot(style='.-',kind='line',x='builds', color=color, ax=self.ax)
		else:
			df.plot(style='.-',kind='line',x='builds', color=color, ax=self.ax[self.plot_id])

	def save(self,filename):
		plt.savefig(filename)
		plt.close()