# cleaning IPUMS-CPS data for visual exploration of rise of female labor force, stagnation of male/household wages

# key vars:
# HHINCOME: total household income, one yearly back to 1968
# EMPSTAT: establishes rise of labor participation - show female only alongside total, available monthly to 76, then yearly to 62
# SEX: as EMPSTAT, available monthly to 76, then yearly to 62
# INCTOT: personal income - yearly to 62
# FTOTVAL: total family income - could be a replacement for HHINCOME, buys you 5 years - yearly to 64
# CLASSWKR: 29 is 'unpaid family worker' so you could track with this - it goes back to 62

from __future__ import division
import pandas as pd
import csv

dollars_2016={1964:7.64,1965:7.52,1966:7.3,1967:7.1,1968:6.81,1969:6.46,1970:6.1,1971:5.85,1972:5.67,1973:5.33,1974:4.81,1975:4.4,1976:4.16,1977:3.91,1978:3.63,1979:3.27,1980:2.88,1981:2.61,1982:2.46,1983:2.38,1984:2.28,1985:2.2,1986:2.16,1987:2.09,1988:2,1989:1.91,1990:1.81,1991:1.74,1992:1.69,1993:1.64,1994:1.6,1995:1.56,1996:1.51,1997:1.48,1998:1.45,1999:1.42,2000:1.38,2001:1.34,2002:1.32,2003:1.29,2004:1.25,2005:1.21,2006:1.18,2007:1.14,2008:1.1,2009:1.1,2010:1.09,2011:1.05,2012:1.03,2013:1.02,2014:1,2015:1}

def load_data():
	ipumsfile='/Users/austinclemens/Desktop/findingtimedata.dat'
	with open(ipumsfile,'rU') as file:
		data=[row for row in file]

	# data is:
	# year: 0-4
	# asecflag: 19
	# wtsupp: 25-35
	# perwt04: 35-42
	# earnwt: 43-53
	# age: 53-55
	# sex: 55
	# empstat: 56-58
	# labforce: 58
	# ftotval: 59-69
	# inctot: 69-77
	# serial: 4:9
	# hwtsupp: 9:19

	lines=[]
	for line in data:
		year=int(line[0:4])
		wtsupp=int(line[25:35])/10000
		age=int(line[53:55])
		sex=int(line[55])
		empstat=int(line[56:58])
		labforce=int(line[58])
		inctot=int(line[69:77])
		hwtsupp=int(line[9:19])/10000

		try:
			ftotval=int(line[59:69])
		except:
			ftotval=-9999

		lines.append([year,line[19],wtsupp,age,sex,empstat,labforce,ftotval,inctot,line[4:9],hwtsupp])

	data=pd.DataFrame(lines,columns=['year','asecflag','wtsupp','age','sex','empstat','labforce','ftotval','inctot','serial','hwtsupp'])
	data=data[data['year']>=1964]
	return data

def summarize_data(data):
	# now need by year rows that summarize:
	# inctot by gender by year (ie how much did females/males earn in 1993 etc.) - these should be medians REMOVE TOPCODES - 9999999etc.
	# ftotval by year (again median and remove topcodes... argggggh 1968-1975 the topcode is a massive $50k. Screw you CPS. Could I paper over this with HHINCOME? Oh wait, I'm taking medians! Yay medians!)
	# labor force participation by gender by year (so for labforce, 1=not in force, 2=in LF. %age for each gender by year)
	# RESTRICT ALL TO PRIME AGE: 25-54

	# data=data[(data['age']>=25) & (data['age']<=54)]
	final_data=[]

	for year in range(1964,2016,1):
		temp=data[data['year']==year]
		temp_m=temp[temp['sex']==1]
		temp_f=temp[temp['sex']==2]

		# thanks to http://stackoverflow.com/a/35349142/3001940 for a weighted median algorithm
		temp_f=temp_f[temp_f['inctot']<99999998].sort_values('inctot')
		cumsum=temp_f.wtsupp.cumsum()
		cutoff=temp_f.wtsupp.sum()/2
		median_female_income=temp_f.inctot[cumsum>=cutoff].iloc[0]*dollars_2016[year]

		temp_m=temp_m[temp_m['inctot']<99999998].sort_values('inctot')
		cumsum=temp_m.wtsupp.cumsum()
		cutoff=temp_m.wtsupp.sum()/2
		median_male_income=temp_m.inctot[cumsum>=cutoff].iloc[0]*dollars_2016[year]

		# remove duplicate households here! Also use hwtsupp.
		temp2=temp.drop_duplicates(subset=['serial','year'])
		temp2=temp2.sort_values('ftotval')
		cumsum=temp2.hwtsupp.cumsum()
		cutoff=temp2.hwtsupp.sum()/2
		median_hh_income=temp2.ftotval[cumsum>=cutoff].iloc[0]*dollars_2016[year]

		lf_male=sum(temp_m[temp_m['labforce']==2]['wtsupp'])/sum(temp_m[temp_m['labforce']>0]['wtsupp'])
		lf_female=sum(temp_f[temp_f['labforce']==2]['wtsupp'])/sum(temp_f[temp_f['labforce']>0]['wtsupp'])

		row=[year,median_female_income,median_male_income,median_hh_income,lf_male,lf_female]
		final_data.append(row)

	final_json={}
	for row in final_data:
		final_json[row[0]]={'mf_income':row[1],'mm_income':row[2],'mhh_income':row[3],'lf_male':row[4],'lf_female':row[5]}

	for row in final_data:
		print row[0],row[1],row[2],row[3],row[4],row[5]

	return final_json



















