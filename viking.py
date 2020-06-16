#
# Copyright (C) Peeter Meris
#
# download Viking Lottery numbers (and prizes) and compare your own numbers against them

import json
import requests
from dictor import dictor
from datetime import datetime
import os.path
from os import path

obj_list = []   
filename = 'data_viking_custom.json'

# URL: https://www.veikkaus.fi/api/draw-results/v1/games/VIKING/draws/by-week/2017-W21
# fetch the numbers and save them to a json database (data_euro.json in current directory)
# current number system (6x 1 to 48; 1x 1 to 8) in use since W21/2017  
## TODO: avoid duplicates (week 53 and week 1)
def fetch():
    obj_list = {}
    obj_list['results'] = []

    for w in range(21, 54):
        print('Fetching 2017-W{w}'.format(w=w))
        url = 'https://www.veikkaus.fi/api/draw-results/v1/games/VIKING/draws/by-week/2017-W{w}'.format(w=w)
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
    
            
    for y in range(2018, 2021):
        for wn in range(1, 54):
            print('Fetching {Y}-W{w}'.format(Y=y, w=wn))
            url = 'https://www.veikkaus.fi/api/draw-results/v1/games/VIKING/draws/by-week/{Y}-W{w}'.format(Y=y, w=wn)
            
            if wn < 10:
                url = 'https://www.veikkaus.fi/api/draw-results/v1/games/VIKING/draws/by-week/{Y}-W0{w}'.format(Y=y, w=wn)

            
                
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
            
    with open('data_viking.json', 'w') as outfile:
        json.dump(obj_list, outfile)
    
   
# read the numbers from the database  
def readJSON():
    print("Loading items from JSON database...")
    with open('data_viking.json') as json_file:
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
def compareNumbers(pri, sec, ter):
    pri_set = set(pri)
    sec_set = set(sec)
    ter_set = set(ter)
    
    pri_str = ' '.join(str(e) for e in pri)
    sec_str = ' '.join(str(e) for e in sec)
    ter_str = ' '.join(str(e) for e in ter)
    
    for obj in obj_list:
        date = obj['date']
        numbers_dict = obj['numbers']
        num_pri = numbers_dict['primary']
        num_sec = numbers_dict['secondary']
        num_ter = numbers_dict['tertiary']
        for i in range(0, len(num_pri)):
            num_pri[i] = int(num_pri[i])
        for n in range(0, len(num_sec)):
            num_sec[n] = int(num_sec[n])
        for n in range(0, len(num_ter)):
            num_ter[n] = int(num_ter[n])
        num_pri_set = set(num_pri)
        num_sec_set = set(num_sec)
        num_ter_set = set(num_ter)
        pri_len = len(pri_set & num_pri_set)
        sec_len = len(sec_set & num_sec_set)
        ter_len = len(ter_set & num_ter_set)
        prizes = obj['prize']
        num_pri_str = ' '.join(str(e) for e in num_pri)
        num_sec_str = ' '.join(str(e) for e in num_sec)
        num_ter_str = ' '.join(str(e) for e in num_ter)
        
        #if pri_len == 6 and sec_len == 1 and ter_len == 1:
        #    continue

        # >=3+0
        # TODO: check against shareCount, if 0: do nothing
        if pri_len > 3 and returnPrize(pri_len, sec_len, ter_len, prizes) > 0:
            print('Results: {p}+{s} P {q}'.format(p=pri_len, s=sec_len, q=ter_len))
            print('Date: ' + date)
            print('Your numbers: {p} + {s} P {q}'.format(p=pri_str, s=sec_str, q=ter_str))
            print('Correct numbers: {p} + {s} P {q}'.format(p=num_pri_str, s=num_sec_str, q=num_ter_str))
            prize = returnPrize(pri_len, sec_len, ter_len, prizes)
            print('Prize: {:.2f}€'.format(prize))
            #for x in range(len(prizes)):
            #    print(prizes[x])
            print('')

        #if ter_len > 0:


# return the prize amount for the given numbers
def returnPrize(pri, sec, ter, prizes):
    
    # prizes list:
    # 0: 6+1
    # 1: 6+0
    # 2: 5+1
    # 3: 5+0
    # 4: 4+1
    # 5: 4+0
    # 6: 3+1
    # 7: 3+0
    # 8: 6+0 + P
    # 9: 5+1 + P
    # 10: 5+0 + P
    # 11: 4+1 + P
    # 12: 4+0 + P
    # 13: 3+1 + P
    # 14: 3+0 + P
    # 15: P
    
    prize = {}
    amount = 0
    
    if ter == 0 and pri == 0:
        return 0

    # P 
    if ter == 1:
        if pri == 6:
            if sec == 0:
                prize = prizes[8]
            else:
                prize = prizes[0]
                
            
        if pri == 5:
            if sec == 1:
                prize = prizes[9]
            else:
                prize = prizes[10]
                
        if pri == 4:
            if sec == 1:
                prize = prizes[11]
            else:
                prize = prizes[12]
                
        if pri == 3:
            if sec == 1:
                prize = prizes[13]
            else:
                prize = prizes[14]

        if pri == 0:
                prize = prizes[15]

    # not P
    else:
        if pri == 6:
            if sec == 1:
                prize = prizes[0]
            else:
                prize = prizes[1]
            
        if pri == 5:
            if sec == 1:
                prize = prizes[2]
            else:
                prize = prizes[3]
                
        if pri == 4:
            if sec == 1:
                prize = prizes[4]
            else:
                prize = prizes[5]
                
        if pri == 3:
            if sec == 1:
                prize = prizes[6]
            else:
                prize = prizes[7]

                
    if(prize):
        amount = prize['shareAmount'] / 100.0
    
    return amount


# load numbers from our own custom JSON file
def loadNumbers():
    print("Loading custom numbers...")

    if path.exists(filename) == False:
        addCustomNumbers()


    with open(filename) as json_file: 
        data = json.load(json_file) 
        for d in data['numbers']:
            compareNumbers(d['primary'], d['secondary'], d['tertiary'])
            
    
# write to our own custom JSON file      
def writeNumbers(pri, sec, ter):
    data = {}
    data['numbers'] = []
    if path.exists(filename) == True:
        with open(filename) as json_file: 
            data = json.load(json_file) 
            temp = data['numbers']
            x = {
                "primary": pri,
                "secondary": sec,
                "tertiary": ter
            }
            temp.append(x)
    else:
        
        data['numbers'].append({
            "primary": pri,
            "secondary": sec,
            "tertiary": ter   
        })
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)


# run numbers from the database against other numbers in the db
def simulate():
    for n in range(0, len(obj_list)):
        obj = obj_list[n]
        numbers_dict = obj['numbers']
        num_pri = numbers_dict['primary']
        num_sec = [0]
        #num_sec = numbers_dict['secondary']
        num_ter = [0]
        #num_ter = numbers_dict['tertiary']
        for i in range(0, len(num_pri)):
            num_pri[i] = int(num_pri[i])
        for n in range(0, len(num_sec)):
            num_sec[n] = int(num_sec[n])
        for n in range(0, len(num_ter)):
            num_ter[n] = int(num_ter[n])
        compareNumbers(num_pri, num_sec, num_ter)


# add custom numbers to a JSON file
def addCustomNumbers():
    # primary numbers
    pri = [1, 2, 3, 4, 5, 6]
    #secondary "viking" number
    sec = [1]
    #tertiary "plus" number
    ter = [0]

    writeNumbers(pri, sec, ter)
    
     
    
# if the database doesn't exist, create it
if path.exists("data_viking.json") == False:
    fetch()

readJSON()
loadNumbers()

#simulate()





