from django.db import models

# Create your models here.

class travel:
    code : str
    Country : str
    continent : str
    advisory_score : float
    advisory_active : int
    source : str
    message : str
    risk : float
    trust : float


class news:
    author : str
    title : str
    description : str
    url	: str
    urlToImage : str
    publishedAt : str
    sourcename : str

class covid_gen_info:
    Country : str
    code : str
    NewConfirmed : int
    TotalConfirmed : int
    NewDeaths : int
    TotalDeaths : int
    NewRecovered : int
    TotalRecovered : int 

class global_gen_info:
    NewConfirmed : int
    TotalConfirmed : int
    NewDeaths : int
    TotalDeaths : int
    NewRecovered : int
    TotalRecovered : int 
