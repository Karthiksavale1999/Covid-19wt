from django.shortcuts import render
from django.http import HttpResponse
from .models import covid_gen_info , global_gen_info , news ,travel
import numpy as np
import random
import pandas as pd
from pandas.io.json import json_normalize  
import requests
import warnings
import json
import mysql.connector
import sqlalchemy
warnings.filterwarnings("ignore")

global td , ts , tm , cnt 

# DATABASE UPDATTION AND CREATION 
def connec(df , name):
    df = df.astype(str)
    sqlEngine = sqlalchemy.create_engine('mysql+pymysql://user:root@127.0.0.1/database')
    dbConnection = sqlEngine.connect()
    df.to_sql(name=name,con=sqlEngine,index=False,if_exists='replace')
    print(" Data Base successfully created  :  ",name)
    dbConnection.close()
def trav():
    from firebase import firebase
    r = requests.get('https://www.travel-advisory.info/api')
    rates_json = json.loads(r.text)['data']
    df = json_normalize(rates_json['IN']) 
    for k in rates_json:
        td = json_normalize(rates_json[k]) 
        df = pd.concat([df , td])
    df = df.drop_duplicates() 
    df['message'] = 'Travel is usual' 
    df.loc[df['advisory.score'] >= 4 ,'message'] = 'Reconsider your journey'
    df.loc[df['advisory.score'] == 5 ,'message'] = 'Abort Travel Immediately' 
    df['risk'] = ( df['advisory.score'] / 5.0 )*100
    df['trust'] = ( df['advisory.sources_active'] / df['advisory.sources_active'].max() )*100
    df.index = range(df.shape[0])
    df = df.drop(['advisory.message' , 'advisory.updated'],axis=1)
    df.columns = ['code','country','continent','advisory_score','advisory_active','source','message','risk','trust']
    connec(df,'travel')
def con():
  r = requests.get('https://api.covid19api.com/summary')
  rates_json = json.loads(r.text)['Countries']
  df = json_normalize(rates_json) 
  df = df.drop(['Slug' ,'Date'], axis = 1)
  dfr = pd.read_csv('first\code.csv',names=['Country','scode','tcode','ncode'],encoding= 'unicode_escape')
  df = df.drop(['Country'],axis=1)
  df = df.join(dfr.set_index('scode'), on='CountryCode')
  connec(df,'country') 
def world_timeseries():
    r = requests.get('https://covidapi.info/api/v1/global/count')
    rates_json = json.loads(r.text)['result']
    df = pd.DataFrame(columns=['Date','confirmed','deaths','recovered'])
    for i in rates_json:
        df = df.append({'Date' : i , 'confirmed' : rates_json[i]['confirmed'],'deaths':rates_json[i]['deaths'],'recovered':rates_json[i]['recovered']} , ignore_index=True)
        df['dconfirmed']=0.0
        df['ddeaths']=0.0
        df['drecovered']=0.0
        for i in df.index:
            if i !=0 :
                df.iat[i,4] = df.iat[i,1] - df.iat[i-1,1]
                df.iat[i,5] = df.iat[i,2] - df.iat[i-1,2]
                df.iat[i,6] = df.iat[i,3] - df.iat[i-1,3]
            else:
                df.iat[i,4] = df.iat[i,1]
                df.iat[i,5] = df.iat[i,2]
                df.iat[i,6] = df.iat[i,3]
    connec(df,'worldtimeseries')
def w_news():
    r = requests.get('http://newsapi.org/v2/everything?domains=wsj.com&apiKey=ebd607ccdb1b4c2a95cfad734eb45466')
    rates_json = json.loads(r.text)['articles'] 
    df = json_normalize(rates_json)
    connec(df,'walstreet')
def t_news():
    r = requests.get('http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey=ebd607ccdb1b4c2a95cfad734eb45466')
    rates_json = json.loads(r.text)['articles'] 
    df = json_normalize(rates_json) 
    connec(df,'techcrunch')
def countrywise():
  r = requests.get('https://covidapi.info/api/v1/global/timeseries/2020-01-22/2020-05-23')
  rates_json = json.loads(r.text)['result']
  from datetime import date, timedelta
  start_date = date(2020, 1, 22)
  end_date = date(2020, 5, 22)
  delta = timedelta(days=1)
  col = []
  while start_date <= end_date:
      col.append(start_date.strftime("%Y-%m-%d"))
      start_date += delta
  col.insert(0,'Country')
  confirmed = pd.DataFrame(columns=col)
  deaths = pd.DataFrame(columns=col)
  recovered = pd.DataFrame(columns=col)
  for i in rates_json:
    conf = []
    det =[]
    recv = []
    for j in range(len(rates_json[i])):
      conf.append(rates_json[i][j]['confirmed'])
      det.append(rates_json[i][j]['deaths'])
      recv.append(rates_json[i][j]['recovered'])
    conf.insert(0,i)
    det.insert(0,i)
    recv.insert(0,i)
    wc = []
    wd = []
    wr = []
    wc.append(conf)
    wd.append(det)
    wr.append(recv)
    temp =pd.DataFrame(wc,columns = col)
    confirmed = confirmed.append(temp)
    tempd =pd.DataFrame(wd,columns = col)
    deaths = deaths.append(tempd)
    tempr =pd.DataFrame(wr,columns = col)
    recovered = recovered.append(tempr)
    confirmed.index = range(confirmed.shape[0])
    deaths.index = range(deaths.shape[0])
    recovered.index = range(recovered.shape[0])

  for i in range(len(confirmed.columns)):
    if(i > 1):
        confirmed.iloc[:,i] = confirmed.iloc[:,i].astype('int32') - confirmed.iloc[:,i-1].astype('int32')
        deaths.iloc[:,i] = deaths.iloc[:,i].astype('int32') - deaths.iloc[:,i-1].astype('int32')
        recovered.iloc[:,i] = recovered.iloc[:,i].astype('int32') - recovered.iloc[:,i-1].astype('int32')
  connec(confirmed,'confirmed')
  connec(deaths,'deaths')
  connec(recovered,'recovered')
def countrycodeconversion():
    df = pd.read_csv('first\code.csv',names=['Country','scode','tcode','ncode'],encoding= 'unicode_escape')
    connec(df,'code')
def state():
    import requests
    url = "https://corona-virus-world-and-india-data.p.rapidapi.com/api_india"
    headers = {
        'x-rapidapi-host': "corona-virus-world-and-india-data.p.rapidapi.com",
        'x-rapidapi-key': "35d1422d0cmshc1ac865a93e46a2p11eaaejsn1e4508ededf2"
        }
    response = requests.request("GET", url, headers=headers)
    rates_json = json.loads(response.text)
    dfs = pd.DataFrame(columns=['State','Confirmed' ,'Recovered','Deaths','active'])
    for j in rates_json['state_wise']:
        dfs = dfs.append({'State':j,
                    'Confirmed':rates_json['state_wise'][j]['confirmed'] ,
                    'Recovered':rates_json['state_wise'][j]['recovered'],
                    'Deaths':rates_json['state_wise'][j]['deaths'],
                    'active':rates_json['state_wise'][j]['active']
                    },ignore_index=True)
    f = open('templates\sc.json',) 
    data = json.load(f) 
    df = pd.DataFrame(columns=['State','code'])
    for i in range(len(data['codes'])): 
        df = df.append({'State':data['codes'][i]['name'],
                'code':data['codes'][i]['code']
                },ignore_index=True)
    dfs = dfs.join(df.set_index('State'), on='State',lsuffix='_c', rsuffix='_cd')
    dfs.dropna()
    dfs
    connec(dfs,'state')

def database_update():
    con()
    w_news()
    t_news()
    trav()
    world_timeseries()
    countrywise()
    countrycodeconversion()
    state()
def read(query):
    sqlEngine = sqlalchemy.create_engine('mysql+pymysql://user:root@127.0.0.1', pool_recycle=3600)
    dbConnection = sqlEngine.connect()
    frame = pd.read_sql(query, dbConnection)
    pd.set_option('display.expand_frame_repr', False)
    #print(frame)
    dbConnection.close()
    return frame


def getDataCountry():
  df = read('SELECT * FROM database.country order by TotalConfirmed desc limit 15;')
  instance_array = []
  for ind in df.index: 
    instance = covid_gen_info()
    instance.Country = df['Country'][ind]
    instance.code = df['CountryCode'][ind]
    instance.NewConfirmed = df['NewConfirmed'][ind]
    instance.TotalConfirmed = df['TotalConfirmed'][ind]
    instance.NewDeaths = df['NewDeaths'][ind]
    instance.TotalDeaths = df['TotalDeaths'][ind]
    instance.NewRecovered = df['NewRecovered'][ind]
    instance.TotalRecovered = df['TotalRecovered'][ind]
    instance_array.append(instance)
  return instance_array
def globalnews():
    r = requests.get('https://api.covid19api.com/summary')
    rates_json = json.loads(r.text)['Global']
    instance = global_gen_info()
    instance.NewConfirmed = rates_json['NewConfirmed']
    instance.TotalConfirmed = rates_json['TotalConfirmed']
    instance.NewDeaths = rates_json['NewDeaths']
    instance.TotalDeaths = rates_json['TotalDeaths']
    instance.NewRecovered = rates_json['NewRecovered']
    instance.TotalRecovered = rates_json['TotalRecovered']
    return  instance



def walstreetnews(): 
    instance = news()
    instance_array = []
    count = 0
    for ind in df.index: 
        if count == 6 :
            break
        instance = news()
        instance.author = df['author'][ind]
        instance.title = df['title'][ind]
        instance.description = df['description'][ind]
        instance.url = df['url'][ind]
        instance.urlToImage = df['urlToImage'][ind]
        instance.publishedAt = df['publishedAt'][ind]
        instance.sourcename = df['source.name'][ind]
        count = count + 1
        instance_array.append(instance)
    return instance_array
def techcrunch():
    
    instance = news()
    instance_array = []
    count = 0
    for ind in df.index: 
        if count == 6 :
            break
        instance = news()
        instance.author = df['author'][ind]
        instance.title = df['title'][ind]
        instance.description = df['description'][ind]
        instance.url = df['url'][ind]
        instance.urlToImage = df['urlToImage'][ind]
        instance.publishedAt = df['publishedAt'][ind]
        instance.sourcename = df['source.name'][ind]
        count = count + 1
        instance_array.append(instance)
    return instance_array



def Traveladvdanger():
    df = read('SELECT * FROM database.travel order by risk desc limit 4;')
    instance_array = []
    for ind in df.index: 
        instance = travel()
        instance.Country = df['country'][ind]
        instance.code = df['code'][ind]
        instance.continent = df['continent'][ind]
        instance.advisory_score = df['advisory_score'][ind]
        instance.advisory_source = df['advisory_active'][ind]
        instance.risk= df['risk'][ind]
        instance.trust = df['trust'][ind]
        instance.src = df['source'][ind]
        instance.msg = df['message'][ind]
        instance_array.append(instance) 
    return instance_array
def Traveladvmodr():
    df = read('SELECT * FROM database.travel where message = "Reconsider your journey" order by risk limit 4')
    instance_array = []
    for ind in df.index: 
        instance = travel()
        instance.Country = df['country'][ind]
        instance.code = df['code'][ind]
        instance.continent = df['continent'][ind]
        instance.advisory_score = df['advisory_score'][ind]
        instance.advisory_source = df['advisory_active'][ind]
        instance.risk= df['risk'][ind]
        instance.trust = df['trust'][ind]
        instance.src = df['source'][ind]
        instance.msg = df['message'][ind]
        instance_array.append(instance) 
    return instance_array
def Traveladvsafe():
    df = read('SELECT * FROM database.travel where message = "Travel is usual" order by trust desc limit 4')
    instance_array = []
    for ind in df.index: 
        instance = travel()
        instance.Country = df['country'][ind]
        instance.code = df['code'][ind]
        instance.continent = df['continent'][ind]
        instance.advisory_score = df['advisory_score'][ind]
        instance.advisory_source = df['advisory_active'][ind]
        instance.risk= df['risk'][ind]
        instance.trust = df['trust'][ind]
        instance.src = df['source'][ind]
        instance.msg = df['message'][ind]
        instance_array.append(instance)  
    return instance_array
def country():
    df = read('SELECT distinct country FROM database.travel order by country')
    return df['country'].tolist()



# HTML PATH TOUR
def country_request(country):
    qt = 'SELECT * FROM database.travel where country ="'+country+'" ;'
    df = read(qt)
    inst_arr=[]
    for ind in df.index: 
        instance = travel()
        instance.Country = df['country'][ind]
        instance.code = df['code'][ind]
        instance.continent = df['continent'][ind]
        instance.advisory_score = df['advisory_score'][ind]
        instance.advisory_source = df['advisory_active'][ind]
        instance.risk= df['risk'][ind]
        instance.trust = df['trust'][ind]
        instance.src = df['source'][ind]
        instance.msg = df['message'][ind]
        inst_arr.append(instance)
    return instance
def traveldet(request):
    country1 = request.GET['country']
    if(country1 == "Country"):
        return travelhome(request)
    return render(request,'travel.html',{'trav':Traveladvdanger() , 'trav1':Traveladvsafe() , 'trav2':Traveladvmodr() , 'res':country_request(country1) , 'lt':country() })
def travelhome(request):
    td = Traveladvdanger()
    ts = Traveladvsafe()
    tm = Traveladvmodr()
    cnt = country()

    return render(request,'travel.html',{'trav':td ,'trav1':ts , 'trav2': tm ,'lt':cnt  })
def info(request):
    return render(request,'covid19.html')
def prevent(request):
    return render(request,'info.html')
def home(request):
    #countrywise()
    #database_update()

    #print("Done")
    return render(request,'index.html',{'instArr':getDataCountry , 'glob':globalnews()})
    #return render(request,'news.html',{'news':walstreetnews() ,'newsit':techcrunch()})
    
    #return render(request,'covid19.html')
def localdash(request):
    return render(request,'logindash.html');
def login(request):
    return render(request,'login.html');




def dashboard(request):
    dates , confirmed , deaths , recovered ,  dconfirmed , ddeaths , drecovered= getBarData()
    seq , name ,  date = country_inc()
    context = {'date':dates , 
                'confirmed':confirmed , 
                'deaths':deaths,
                'recovered':recovered , 
                'dconfirmed':dconfirmed , 
                'ddeaths':ddeaths,
                'drecovered':drecovered,
                'sequence_dt':date,
                'sequence_data':seq,
                'sequence_name':name
                }
    return render(request,'Dashboard.html',context)
def cma(request):
    #print('reciever')
    countrycodeconversion()
    name1 = request.GET['name1']
    name2 = request.GET['name2']
    dataframec , dataframed , dataframer = country_series(name1 , name2 )
    
    selected_country , selected_dates , selected_list_c,selected_list_d,selected_list_r , selec_color = country_series_list(dataframec , dataframed , dataframer)
    context = {
        'Countries': coiuntries(),
        'name': selected_country,
        'dates': selected_dates ,
        'colosd': selec_color,
        'confirmed': selected_list_c,
        'deaths':selected_list_d,
        'recovered':selected_list_r,
        'dashtab':dashtab(name1 , name2)
    }

    return render(request,'comparitive_analytics.html',context)
def comparitive_analytics(request):
    name1 = 'ITA'
    name2 ='FRA'
    dataframec , dataframed , dataframer = country_series(name1 , name2 )
    
    selected_country , selected_dates , selected_list_c,selected_list_d,selected_list_r , selec_color = country_series_list(dataframec , dataframed , dataframer)
    context = {
        'Countries': coiuntries(),
        'name': selected_country,
        'dates': selected_dates ,
        'colosd': selec_color,
        'confirmed': selected_list_c,
        'deaths':selected_list_d,
        'recovered':selected_list_r,
        'dashtab':dashtab(name1 , name2)
    }

    return render(request,'comparitive_analytics.html',context)
def index(request):
    return render(request,'index1.html')
def india(request):
    mc , mr , md , bp= anind();
    country , col , ic , idt , ir , color =indiaseries();
    context = {
        'rcrdse':indidash(),
        'glob':cardind(),
        'max_con':mc,
        'max_rec':mr,
        'max_death':md,
        'Crtical_performance':bp,
        'ic':ic,
        'idt':idt,
        'ir':ir
    }
    return render(request,'india.html',context)

#  PLOT FUNCTIONS 
def indiaseries():
    df1 = read("SELECT * FROM database.confirmed where Country = 'IND';")
    df2 = read("SELECT * FROM database.deaths where Country = 'IND';")
    df3 = read("SELECT * FROM database.recovered where Country = 'IND';")
    return country_series_list(df1,df2,df3)
def anind():
    df1= read('SELECT State , Confirmed FROM database.state order by Confirmed desc limit 1;')
    df2 = read('Select State , Recovered/Confirmed *100 as r from database.state order by Recovered/Confirmed desc limit 1')
    df3 = read('Select State , Deaths/Confirmed * 100 as d from database.state order by Deaths/Confirmed desc limit 1')
    df4 = read('SELECT State , Recovered/Confirmed *100  as r , Deaths/Confirmed *100  as d FROM database.state where Confirmed >= 5000 order by r/d desc ;')
    return df1.to_json(orient='records') , df2.to_json(orient='records') , df3.to_json(orient='records') , df4.to_json(orient='records')
def cardind():
    df = read('SELECT sum(Confirmed) as c , sum(Deaths) as d , sum(Recovered) as r , sum(active) as a FROM database.state;')
    return df.to_json(orient='records')
def indidash():
    df = read('SELECT * FROM database.state limit 34;')
    return df.to_json(orient='records')
def dashtab(name1 , name2):
    df1 = read("SELECT * FROM database.country where tcode = '"+name1+"' ")
    df2 = read("SELECT * FROM database.country where tcode = '"+name2+"' ")
    df1 = df1.append(df2)
    return df1.to_json(orient='records')
def coiuntries():
    df = read('SELECT distinct Country FROM database.confirmed ')
    return df['Country'].tolist()
def country_series_list(df1 , df2 , df3):
    col = (df1.columns).tolist()
    col.pop(0) 
    country = df1['Country'].tolist()
    ct= []
    dt =[]
    rt =[]
    color =[]
    for i in df1.index:
        ct.append(df1.iloc[i,1:].tolist())
        dt.append(df2.iloc[i,1:].tolist())
        rt.append(df3.iloc[i,1:].tolist())
    for i in df1.index:
        r = lambda: random.randint(0,255)
        color.append('#%02X%02X%02X' % (r(),r(),r()))
    return country , col , ct , dt , rt , color
def country_series(name1 ,name2):
    tempc = read("SELECT * FROM database.confirmed where Country in ('"+name1+"' , '"+name2+"')") 
    tempd = read("SELECT * FROM database.deaths where Country in ('"+name1+"' , '"+name2+"')") 
    tempr = read("SELECT * FROM database.recovered where Country in ('"+name1+"' , '"+name2+"')") 
    return tempc  , tempd , tempr
def country_constant():
    temp = read("SELECT * FROM database.confirmed where Country in( 'USA', 'UKR' , 'ITA' , 'IND' , 'RUS' ,'FRA' , 'BEL' , 'CAN','IRN' )")
    return temp
def getBarData():
    df=read('SELECT * FROM database.worldtimeseries;')
    dates = df['Date'].tolist()
    confirmed = df['confirmed'].tolist()
    deaths = df['deaths'].tolist()
    recovered = df['recovered'].tolist()
    dconfirmed = df['dconfirmed'].tolist()
    ddeaths = df['ddeaths'].tolist()
    drecovered = df['drecovered'].tolist()
    return dates , confirmed , deaths , recovered , dconfirmed , ddeaths , drecovered
def Map_Confirmed():
    df = read('SELECT Country as name , CountryCode as id , TotalConfirmed as value ,NewConfirmed  FROM database.country order by Country')
    return df
def country_inc():
    df = read('SELECT * FROM database.confirmed limit 15;')
    date = df.columns[3:].tolist()
    final = []
    name = []
    #print(df)
    for i in df.index:
        listr= [] 
        name.append(df.iat[i,0])
        listr.append(df.iloc[i][3:].tolist())
        final.append(listr)
    return final , name , date