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

# dollars_2016={1964:7.64,1965:7.52,1966:7.3,1967:7.1,1968:6.81,1969:6.46,1970:6.1,1971:5.85,1972:5.67,1973:5.33,1974:4.81,1975:4.4,1976:4.16,1977:3.91,1978:3.63,1979:3.27,1980:2.88,1981:2.61,1982:2.46,1983:2.38,1984:2.28,1985:2.2,1986:2.16,1987:2.09,1988:2,1989:1.91,1990:1.81,1991:1.74,1992:1.69,1993:1.64,1994:1.6,1995:1.56,1996:1.51,1997:1.48,1998:1.45,1999:1.42,2000:1.38,2001:1.34,2002:1.32,2003:1.29,2004:1.25,2005:1.21,2006:1.18,2007:1.14,2008:1.1,2009:1.1,2010:1.09,2011:1.05,2012:1.03,2013:1.02,2014:1,2015:1}
# CPI-U-RS
dollars_2016={1964:6.57,1965:6.47,1966:6.29,1967:6.1,1968:5.87,1969:5.62,1970:5.36,1971:5.13,1972:4.98,1973:4.69,1974:4.26,1975:3.94,1976:3.73,1977:3.5,1978:3.28,1979:2.99,1980:2.69,1981:2.46,1982:2.32,1983:2.22,1984:2.14,1985:2.07,1986:2.03,1987:1.96,1988:1.89,1989:1.82,1990:1.73,1991:1.67,1992:1.63,1993:1.59,1994:1.56,1995:1.52,1996:1.48,1997:1.45,1998:1.43,1999:1.40,2000:1.35,2001:1.32,2002:1.30,2003:1.27,2004:1.23,2005:1.19,2006:1.16,2007:1.12,2008:1.08,2009:1.09,2010:1.07,2011:1.04,2012:1.02,2013:1.00,2014:1.00,2015:1}

def load_data():
	ipumsfile='/Users/austinclemens/Desktop/findingtimedata.dat'
	with open(ipumsfile,'rU') as file:
		data=[row for row in file]

	# data is:
	# year: 0:4
	# serial: 4:9
	# hwtsupp: 9:19
	# asecflag: 19
	# hhincome: 21:29
	# wtsupp: 33:43
	# perwt04: 43:51
	# earnwt: 51:61
	# famunit: 61:63
	# age: 63:65
	# sex: 65
	# empstat: 66:68
	# labforce: 68
	# ftotval: 69:79
	# inctot: 79:87
	# ftype: 87

	lines=[]
	for line in data:
		year=int(line[0:4])
		wtsupp=int(line[33:43])/10000
		age=int(line[63:65])
		sex=int(line[65])
		empstat=int(line[66:68])
		labforce=int(line[68])
		inctot=int(line[79:87])
		hwtsupp=int(line[9:19])/10000
		famunit=int(line[61:63])
		ftype=int(line[87])

		try:
			hhincome=int(line[21:29])
		except:
			hhincome=-9999

		try:
			ftotval=int(line[69:79])
		except:
			ftotval=-9999

		lines.append([year,wtsupp,age,sex,empstat,labforce,ftotval,inctot,line[4:9],hwtsupp,famunit,ftype,hhincome])

	data=pd.DataFrame(lines,columns=['year','wtsupp','age','sex','empstat','labforce','ftotval','inctot','serial','hwtsupp','famunit','ftype','hhincome'])
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

	for year in range(1968,2016,1):
		temp=data[data['year']==year]
		temp_m=temp[temp['sex']==1]
		temp_f=temp[temp['sex']==2]

		# thanks to http://stackoverflow.com/a/35349142/3001940 for a weighted median algorithm
		temp_f=temp_f[(temp_f['inctot']<99999998) & (temp_f['inctot']!=-9999)].sort_values('inctot')
		cumsum=temp_f.wtsupp.cumsum()
		cutoff=temp_f.wtsupp.sum()/2
		median_female_income=temp_f.inctot[cumsum>=cutoff].iloc[0]*dollars_2016[year]

		temp_m=temp_m[(temp_m['inctot']<99999998) & (temp_m['inctot']!=-9999)].sort_values('inctot')
		cumsum=temp_m.wtsupp.cumsum()
		cutoff=temp_m.wtsupp.sum()/2
		median_male_income=temp_m.inctot[cumsum>=cutoff].iloc[0]*dollars_2016[year]

		# remove duplicate households here! Also use hwtsupp.
		temp2=temp.drop_duplicates(subset=['serial','year','famunit'])
		# temp2=temp
		temp2=temp2[temp2['hhincome']!=-9999].sort_values('hhincome')
		cumsum=temp2.hwtsupp.cumsum()
		cutoff=temp2.hwtsupp.sum()/2
		median_hh_income=temp2.hhincome[cumsum>=cutoff].iloc[0]*dollars_2016[year]

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



















