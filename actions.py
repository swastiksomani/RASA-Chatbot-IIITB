from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_sdk import Action
from rasa_sdk.events import SlotSet
import zomatopy
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'
    
    def run(self, dispatcher, tracker, domain):
        config={ "user_key":"f4924dc9ad672ee8c4f8c84743301af5"}
        zomato = zomatopy.initialize_app(config)
        
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        slot_price_range=tracker.get_slot('price_range')
        
        print(loc)
        print(cuisine)
        print(slot_price_range)


        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        cuisines_dict={'chinese':25,
         'american': 1,'mexican':73,
         'italian':55,'north indian':50,
         'south indian':85}
        results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 1000000) #Change value to larger number
        d = json.loads(results)
        print(d)
        response=""
        if d['results_found'] == 0:
                response= "No restaurants found matching your criteria"
        else:
            rest_recom_ls=[]
            for res in sorted(d['restaurants'], key=lambda x: x['restaurant']['user_rating']['aggregate_rating'], reverse=True): 
                if slot_price_range=='1':
                    print("1")
                    if res["restaurant"]["average_cost_for_two"]<300:
                        rest_recom_ls.append((res["restaurant"]["name"],
                                         res["restaurant"]["location"]["address"],
                                         res["restaurant"]["average_cost_for_two"],
                                         res["restaurant"]["user_rating"]["aggregate_rating"]
                                        ))
                if slot_price_range=='2':
                    print("2")
                    if res["restaurant"]["average_cost_for_two"]>=300 and res["restaurant"]["average_cost_for_two"]<700:
                        rest_recom_ls.append((res["restaurant"]["name"],
                                              res["restaurant"]["location"]["address"],
                                              res["restaurant"]["average_cost_for_two"],
                                              res["restaurant"]["user_rating"]["aggregate_rating"]
                                            ))
                if slot_price_range=='3':
                    print(3)
                    if res["restaurant"]["average_cost_for_two"]>700:
                        rest_recom_ls.append((res["restaurant"]["name"],
                                              res["restaurant"]["location"]["address"],
                                              res["restaurant"]["average_cost_for_two"],
                                              res["restaurant"]["user_rating"]["aggregate_rating"]
                                            ))
        
        restaurants_recom_ls=rest_recom_ls[:5]

        #print(restaurants_recom_ls)

        if len(restaurants_recom_ls)>0:
            for restaurant in restaurants_recom_ls:
                            response=response=response+ "Found "+ restaurant[0]+ " in "+ restaurant[1]+" with rating: "+ str(restaurant[3])+" and avg. price for two:"+ str(restaurant[2])+ "\n"
        else:
            #print("here")
            response= "No restaurants found matching your criteria"
        
            dispatcher.utter_message("-----"+response)
        return [SlotSet('email_content',response)]
    
class ActionSendEmail(Action):
    def name(self):
        return 'action_send_email'
	
    def run(self, dispatcher, tracker, domain):
        email_content=tracker.get_slot('email_content')
        email_content="Dear User,\n Based on you recent search, here are the restaurants that foodie recommends- \n"  + email_content + "\n Happy to help\n" + "Thanks! \n Foodie" 
        from_user = 'no.reply.foodie.restaurants@gmail.com'
        to_user = tracker.get_slot('user_email_id')
        password = 'Upgrad@1234'
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(from_user, password)
        subject = 'Foodie Found Restaurants'
        msg = MIMEMultipart()
        msg['From'] = from_user
        msg['TO'] = to_user
        msg['Subject'] = subject
        body = email_content
        msg.attach(MIMEText(body,'plain'))
        text = msg.as_string()
        server.sendmail(from_user,to_user,text)
        server.close()
        return
        


#Action class defination for Verificaiton of Location
class ActionCheckLocation(Action):
    def name(self):
        return 'action_check_location'
    def run(self, dispatcher, tracker, domain):
        user_loc=tracker.get_slot('location')
        
        cities_in_scope=['ahmedabad','bengaluru','bangalore', 'chennai','madras', 'delhi','new delhi', 'hyderabad',
		 'kolkata', 'culcatta' ,'mumbai','bombay', 'pune', 'agra', 'ajmer','aligarh', 'amravati','amaravati', 'amritsar',
		  'asansol', 'aurangabad', 'bareilly', 'belgaum', 'bhavnagar', 'bhiwandi', 'bhopal', 
		  'bhubaneswar', 'bikaner', 'bilaspur', 'bokaro', 'chandigarh', 'coimbatore', 
		  'cuttack', 'dehradun', 'dhanbad', 'bhilai', 'durgapur', 'erode', 'faridabad', 
		  'firozabad', 'ghaziabad', 'gorakhpur', 'gulbarga', 'guntur', 'gwalior', 'gurgaon', 
		  'guwahati', 'hamirpur', 'hubli–dharwad', 'indore', 'jabalpur', 'jaipur', 'jalandhar', 
		  'jammu', 'jamnagar', 'jamshedpur', 'jhansi', 'jodhpur', 'kakinada', 'kannur', 
		  'kanpur', 'kochi', 'kolhapur', 'kollam', 'kozhikode', 'kurnool', 'ludhiana', 
		  'lucknow', 'madurai', 'malappuram', 'mathura', 'goa', 'mangalore', 'meerut', 
		  'moradabad', 'mysore', 'nagpur', 'nanded', 'nashik', 'nellore', 'noida', 'patna', 
		  'pondicherry', 'purulia', 'prayagraj','allahabad' ,'raipur', 'rajkot', 'rajahmundry', 'ranchi', 
		  'rourkela', 'salem', 'sangli', 'shimla', 'siliguri', 'solapur', 'srinagar', 'surat', 
		  'thiruvananthapuram', 'thrissur', 'tiruchirappalli', 'tiruppur', 'ujjain', 'bijapur',
		   'vadodara', 'varanasi', 'vasai-virar', 'vijayawada','vijaywada', 'visakhapatnam', 'vellore', 
		   'warangal']
        
        if user_loc.lower() in [city.lower() for city in cities_in_scope]:
            print("true")
            return [SlotSet('location_scope',True)]
        else:
            print("false")
            return [SlotSet('location_scope',False)]
       
