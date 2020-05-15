#
# Copyright (C) Peeter Meris
#
# download the Eurojackpot numbers (and prizes) and compare your own numbers against them

import json
import requests
from dictor import dictor
from datetime import datetime
import os.path
from os import path



# URL: https://www.veikkaus.fi/api/draw-results/v1/games/EJACKPOT/draws/by-week/2020-W18
# fetch the numbers and save them to a json database (data_euro.json in current directory)
# current number system (5x 1 to 50; 2x 1 to 10) in use since 10.10.2014 
# 2014 week 41 -> 
def fetch():
    obj_list = {}
    obj_list['results'] = []
    for w in range(41, 54):
        print('Fetching 2014-W{w}'.format(w=w))
        url = 'https://www.veikkaus.fi/api/draw-results/v1/games/EJACKPOT/draws/by-week/2014-W{w}'.format(w=w)
        response = requests.get(url)        
        results = json.loads(response.text)
        
        # return code != 200
        if(not response):
            print(response)
            print(json.dumps(results, indent = 4, sort_keys=True))
        
        try:
            date = dictor(results, '0.drawTime')
            date_object = datetime.fromtimestamp(date / 1e3)
            #print(date_object)

            var1 = dictor(results, '0.results')
            #print(var1)
    
            var2 = dictor(results, '0.prizeTiers')
            #print(var2)
    
            obj_list['results'].append({
                'date': date_object.strftime("%d.%m.%Y"),
                'prize': var2,
                'numbers': var1
            })
        except TypeError:
            print("TypeError")
            
    for y in range(2015, 2021):
        for wn in range(1, 54):
            print('Fetching {Y}-W{w}'.format(Y=y, w=wn))
            url = 'https://www.veikkaus.fi/api/draw-results/v1/games/EJACKPOT/draws/by-week/{Y}-W{w}'.format(Y=y, w=wn)
            
            if wn < 10:
                url = 'https://www.veikkaus.fi/api/draw-results/v1/games/EJACKPOT/draws/by-week/{Y}-W0{w}'.format(Y=y, w=wn)
                
            response = requests.get(url) 
            results = json.loads(response.text)
            
            # return code != 200
            if not response:
                print(response)
                print(json.dumps(results, indent = 4, sort_keys=True))    
    
            try:
                date = dictor(results, '0.drawTime')
                date_object = datetime.fromtimestamp(date / 1e3)
                #print(date_object)

                var1 = dictor(results, '0.results')
                #print(var1)
    
                var2 = dictor(results, '0.prizeTiers')
                #print(var2)
    
                obj_list['results'].append({
                'date': date_object.strftime("%d.%m.%Y"),
                'prize': var2,
                'numbers': var1
                })
            except TypeError:
                print("TypeError")
                pass
            
    with open('data_euro.json', 'w') as outfile:
        json.dump(obj_list, outfile)
    
 


obj_list = []    
    
# read the numbers from the database  
def readJSON():
    print("Loading items from JSON database...")
    with open('data_euro.json') as json_file:
        data = json.load(json_file)
        for d in data['results']:
            date = d['date']
            #print('Date: ' + date)
            
            numbers = d['numbers']
            numbers_dict = numbers[0]
            #print(numbers_dict['primary'])
            #print(numbers_dict['secondary'])
            
            prize = d['prize']
            #for x in prize:
                #print(x)
                
            #print('')
            
            obj = {}
            obj['date'] = date
            obj['numbers'] = numbers_dict
            obj['prize'] = prize
            obj_list.append(obj)
    print('Items in database: {num}'.format(num=len(obj_list)))

    
    
    
# compare the given numbers to the numbers loaded from the database
def compareNumbers(pri, sec):
    pri_set = set(pri)
    sec_set = set(sec)
    
    pri_str = ' '.join(str(e) for e in pri_set)
    sec_str = ' '.join(str(e) for e in sec_set)
    
    for obj in obj_list:
        date = obj['date']
        numbers_dict = obj['numbers']
        num_pri = numbers_dict['primary']
        num_sec = numbers_dict['secondary']
        for i in range(0, len(num_pri)):
            num_pri[i] = int(num_pri[i])
        for n in range(0, len(num_sec)):
            num_sec[n] = int(num_sec[n])
        num_pri_set = set(num_pri)
        num_sec_set = set(num_sec)
        pri_len = len(pri_set & num_pri_set)
        sec_len = len(sec_set & num_sec_set)
        prizes = obj['prize']
        num_pri_str = ' '.join(str(e) for e in num_pri_set)
        num_sec_str = ' '.join(str(e) for e in num_sec_set)
        
        # >=2+1 or 1+2
        #if (pri_len > 1 and sec_len > 0) or (pri_len > 0 and sec_len > 1):
        #    print('Results: {p}+{s}'.format(p=pri_len, s=sec_len))
        #    print(date)
        
        # >=4+0
        if pri_len > 2:
            print('Results: {p}+{s}'.format(p=pri_len, s=sec_len))
            print('Date: ' + date)
            print('Your numbers: {p} + {s}'.format(p=pri_str, s=sec_str))
            print('Correct numbers: {p} + {s}'.format(p=num_pri_str, s=num_sec_str))
            prize = returnPrize(pri_len, sec_len, prizes)
            print('Prize: {:.2f}€'.format(prize))
            #for x in range(len(prizes)):
            #    print(prizes[x])
            print('')


# return the prize amount for the given numbers
def returnPrize(pri, sec, prizes):
    
    # prizes list:
    # 0: 5+2
    # 1: 5+1
    # 2: 5+0
    # 3: 4+2
    # 4: 4+1
    # 5: 4+0
    # 6: 3+2
    # 7: 2+2
    # 8: 3+1
    # 9: 3+0
    # 10: 1+2
    # 11: 2+1
    
    prize = {}
    amount = 0
    
    if pri == 0:
        return 0
    
    if pri == 5:
        if sec == 2:
            prize = prizes[0]
        elif sec == 1:
            prize = prizes[1]
        else:
            prize = prizes[2]
        
    if pri == 4:
        if sec == 2:
            prize = prizes[3]
        elif sec == 1:
            prize = prizes[4]
        else:
            prize = prizes[5]
            
    if pri == 3:
        if sec == 2:
            prize = prizes[6]
        elif sec == 1:
            prize = prizes[8]
        else:
            prize = prizes[9]
            
    if pri == 2:
        if sec == 2:
            prize = prizes[7]
        elif sec == 1:
            prize = prizes[11]
        else:
            amount = 0
            
    if pri == 1:
        if sec == 2:
            prize = prizes[10]
        else:
            amount = 0
    
    if(prize):
        amount = prize['shareAmount'] / 100.0
    
    return amount
    
        
    
# if the database doesn't exist, create it
if path.exists("data_euro.json") == False:
    fetch()

readJSON()

# primary numbers
pri = [1, 2, 3, 4, 5]
#secondary "extra" numbers
sec = [1, 2]
compareNumbers(pri, sec)



