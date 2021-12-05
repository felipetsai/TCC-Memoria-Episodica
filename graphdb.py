# -*- coding: utf-8 -*-

from SPARQLWrapper import SPARQLWrapper, JSON
import json
import time

url = "http://192.168.81.129:7200/repositories/episodica_teste"

class Atimo:
    def __init__(self, number, classe, value, start, end, relation):
        self.number = number
        self.classe = classe
        self.value = value
        self.start = start
        self.end = end
        self.relation = relation

    def query(self):
        query = "PREFIX db1: <http://example.com/restaurantes/> \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:class \"" + self.classe +"\"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:value \"" + self.value +"\"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:start " + str(self.start) +"} }; \n"
        query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:end " + str(self.end) +"} }; \n"
        
        for r in self.relation:
            query += "INSERT DATA  { GRAPH db1: {  db1:at" + str(self.number) + " db1:related db1:at" + str(r) + "} }; \n"
        return query
        
    
def SendQuery(query):

    sparql = SPARQLWrapper(url)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    
    return results


def GetMostVisitedRestaurant():
    response = SendQuery("""
        PREFIX db1: <http://example.com/experimentos-iniciais>

        SELECT (SAMPLE(?restaurant) AS ?Restaurant) 
        (COUNT(?restaurant) AS ?Numberofvisits) 
        (SUM(IF(?emotion = "Positive", 1, IF(?emotion = "Negative", -1, 0))) AS ?EmotionSum)
        (MAX(?date) AS ?LastVisited)
        WHERE
            {
                ?p db1:class "person".
                ?p db1:value "Felipe".
                ?p db1:start ?date.
                ?e db1:class "emotion".
                ?e db1:value ?emotion.
                ?r db1:class "restaurant".
                ?r db1:value ?restaurant.
                ?p db1:related ?r.
                ?p db1:related ?e.
            }
        GROUP BY ?restaurant
        ORDER BY DESC(?Numberofvisits)
                """)["results"]["bindings"]
    
    # print(response)
    return response
    



def Main():
    
    restaurants = GetMostVisitedRestaurant()
    print(restaurants[1]["Restaurant"]["value"])
    # a = Atimo(1,"person","fefo",12,23,[2,3])
    # a.end = 234
    # print(a.query())
    
    # c = 1
    # listPeople = []
    # listEmotion = []
    # listRestaurant = []
    # while(c < 5):
    #     time.sleep(5)
    #     print("oi")
        
    #     c+=1
    ## Timer, simular tirar foto
    
    
    ## mandar foto pro opencv
    
    
    ## analisar pessoa e emocao, simular o restaurante
    
    ## pegar o resultado e inserir em query 
    
    
    
    
    
    
    ## Funcao diferente pra recomendar restaurante.
    
    ## criar funcoes diferentes para querys diferentes
    
    
    #GetMostVisitedRestaurant()
#     print(SendQuery("""
#            PREFIX db1: <http://example.com/experimentos-iniciais>

# SELECT (SAMPLE(?restaurant) AS ?Restaurant) 
# (COUNT(?restaurant) AS ?Numberofvisits) 
# WHERE
# 	  {
# 		?p db1:class "person".
# 		?p db1:value "Felipe".
# 		?r db1:class "restaurant".
# 		?r db1:value ?restaurant.
# 		?p db1:related ?r.
# 	  }
#       GROUP BY ?restaurant
#     """))
    
    
    
        # print(results)
    
    # for result in results["results"]["bindings"]:
    #     print(result["label"]["value"])
    
    # print('---------------------------')
    
    # for result in results["results"]["bindings"]:
    #    print('%s: %s' % (result["person"]["value"], result["restaurant"]["value"]))

Main()