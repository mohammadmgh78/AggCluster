# import random
# import math
# import pandas as pd
# import numpy as np
# import time
normal_customers_percentage = 0.7
impatient_customers_percentage = 0.15
technical_need_percentage = 0.15
num_of_specialists = 4
num_of_beginners = 36
num_of_technicals =  24
overwork_time = 8*60
shift_time_1 = 8*60
shift_time_2 = 16*60

def Exponential(lambd):
    r = random.random()
    return -(1 / lambd) * math.log(r)


def Uniform(a, b):
    r = random.random()
    return a + (b - a) * r



# starting state function, does sum initial work like definig variables and also initializes our variables.
def starting_state():

    # State variables
    state = dict()
    state['Special Customer Queue Length'] = 0 # To store length of special customers in the very first queue
    state['Normal Customer Queue Length'] = 0 # To store length of normal customers in the very first queue
    state['Technical Special Customer Queue Length'] = 0 # To store length of special customers in technical queue
    state['Technical Normal Customer Queue Length'] = 0 # To store length of normal customers in technical queue
    state['Specialist Server Status'] = 0  # 0: Free, 1:one Busy, 2: two busy
    state['Beginner Server Status'] = 0 # 0: Free, 1:one Busy, 2: two busy, 3: three busy
    state['Technical Server Status'] = 0 # 0: Free, 1:one Busy, 2: two busy

    # Data: will save everything
    data = dict()
    data['Special Customers'] = dict()  # To track each special customer, saving their arrival time, time service begins, etc.
    data['Normal Customers'] = dict() # To track each normal customer, saving their arrival time, time service begins, etc.
    data['Last Time Special Customer Queue Length Changed'] = 0
    data['Last Time Normal Customer Queue Length Changed'] = 0
    data['Last Time Technical Special Customer Queue Length Changed'] = 0
    data['Last Time Technical Normal Customer Queue Length Changed'] = 0
    # To check which customer has first arrived, we store them in a dictionary and for each line in a distinct dictionary
    data['Special Queue Customers'] = dict()
    data['Normal Queue Customers'] = dict()
    data['Technical Special Queue Customers'] = dict()
    data['Technical Normal Queue Customers'] = dict()

    # Cumulative Stats
    data['Cumulative Stats'] = dict()
    
    # Stores last time time each operator group serviced
    data['Cumulative Stats']['Specialist Servers Last Time'] = 0
    data['Cumulative Stats']['Beginner Servers Last Time'] = 0
    data['Cumulative Stats']['Technical Servers Last Time'] = 0
    
    
    # Stores busy time in order to calculate utilization
    data['Cumulative Stats']['Specialist Servers Busy Time'] = 0
    data['Cumulative Stats']['Beginner Servers Busy Time'] = 0
    data['Cumulative Stats']['Technical Servers Busy Time'] = 0
    
    #Stores OverWork of operators
    # yakhoda
    data['Cumulative Stats']['Specialist Servers Overworked'] = 0
    data['Cumulative Stats']['Beginner Servers Overworked'] = 0
    data['Cumulative Stats']['Technical Servers Overworked'] = 0    
    
    
    # Stores waiting times, each line and each customer distinctly
    data['Cumulative Stats']['Special Queue Waiting Time'] = 0
    data['Cumulative Stats']['Normal Queue Waiting Time'] = 0
    data['Cumulative Stats']['Technical Special Queue Waiting Time'] = 0
    data['Cumulative Stats']['Technical Normal Queue Waiting Time'] = 0
    # Stores area under queue length, each line and each customer distinctly
    data['Cumulative Stats']['Area Under Special Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Normal Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Technical Special Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Technical Normal Queue Length Curve'] = 0
    # stores immediate service tarters in each line. At the end we implement union on these sets to get general srvice starters.
    data['Special Service Starters'] = set()
    data['Special Service Starters Technical'] = set()
    # Stores customers who left the system and probably left us.
    data['Cumulative Stats']['Customer Churn'] = 0
    # Stores maximums legnths, each line and each kind distinctly
    data['Cumulative Stats']['Max Special Customer Queue Length'] = 0
    data['Cumulative Stats']['Max Normal Customer Queue Length'] = 0
    data['Cumulative Stats']['Max Technical Special Customer Queue Length'] = 0
    data['Cumulative Stats']['Max Technical Normal Customer Queue Length'] = 0
    data['Cumulative Stats']['Max Technical Normal Customer Queue Length'] = 0
    # Stores customers of each line and each kind distinctly
    data['Special Queue Customers All'] = set()
    data['Normal Queue Customers All'] = set()
    data['Technical Special Queue Customers All'] = set()
    data['Technical Normal Queue Customers All'] = set()
    data['Special Customers Waiting Time In System'] = 0
    data['Normal Customers Waiting Time In System'] = 0
    #Yakhoda

    # Stores maximums waiting times, each line and each kind distinctly
    data['Cumulative Stats']['Max Special Customer Queue Waiting Time'] = 0
    data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] = 0
    data['Cumulative Stats']['Max Technical Special Customer Queue Waiting Time'] = 0
    data['Cumulative Stats']['Max Technical Normal Customer Queue Waiting Time'] = 0


    # Starting FEL
    future_event_list = list()
    if Uniform(0, 1) > normal_customers_percentage:
        future_event_list.append(
            {'Event Type': 'Customer Call', 'Event Time': 0, 'Special Customer': 'S1', 'Normal Customer': 'C0',
             'Last Customer': 'S'})
    else:
        future_event_list.append(
            {'Event Type': 'Customer Call', 'Event Time': 0, 'Special Customer': 'S0', 'Normal Customer': 'C1',
             'Last Customer': 'C'})

    return state, future_event_list, data,

# we use this function to make our events with theirs specific features.
def fel_maker(future_event_list, event_type, state, data, clock, customer_special=None,
              customer_normal=None,
              last_customer=None):
    event_time = 0

    if event_type == 'Customer Call':
        if clock % 1440 < shift_time_1: 
            shift = 1
        elif clock % 1440 < shift_time_2:
            shift = 2
        else:
            shift = 3

        if shift == 1:
            event_time = clock + Exponential(1 / 0.15) 
        elif shift == 2:
            event_time = clock + Exponential(1 / 1.2)
        else:
            event_time = clock + Exponential(1 / 1) 
    elif event_type == 'Departure From Expert':
        event_time = clock + Exponential(1 / 3) 
    elif event_type == 'Departure From Beginner':
        event_time = clock + Exponential(1 / 7) 
    elif event_type == 'Departure From Technical':
        event_time = clock + Exponential(1/10) 
    elif event_type == 'Leaving Of Tired':
        max_queue_length = state['Special Customer Queue Length'] - 1
        event_time = clock + Uniform(0.5, 3) 

    # According to the information given, future event will be made above and will be added to fel as follows.
    new_event = {'Event Type': event_type, 'Event Time': event_time, 'Special Customer': customer_special,
                 'Normal Customer': customer_normal, 'Last Customer': last_customer}
    future_event_list.append(new_event)


def Customer_Call(future_event_list, state, clock, data, customer_special=None, customer_normal=None,
                  last_customer=None):
    # we make the next arrival here.
    if Uniform(0, 1) > normal_customers_percentage: #ASAP (Just Check if you can change this!)
        next_customer = 'S' + str(int(customer_special[1:]) + 1)
        fel_maker(future_event_list, 'Customer Call', state, data, clock,
                  customer_special=next_customer,
                  customer_normal=customer_normal, last_customer='S')

    else:
        next_customer = 'C' + str(int(customer_normal[1:]) + 1)
        fel_maker(future_event_list, 'Customer Call', state, data, clock,
                  customer_special=customer_special,
                  customer_normal=next_customer, last_customer='C')

    # This part is for the customer who has just arrived.
    if last_customer == 'S':
        # Our customer is special
        data['Special Customers'][customer_special] = dict()
        data['Special Customers'][customer_special]['Arrival Time'] = clock
        data['Special Queue Customers All'].add(customer_special)
        if state['Specialist Server Status'] < num_of_specialists: #ASAP_special
            state['Specialist Server Status'] += 1
            fel_maker(future_event_list, 'Departure From Expert', state, data, clock,
                      customer_special=customer_special, customer_normal=customer_normal, last_customer='S')
            data['Special Customers'][customer_special]['Time Service Begins'] = clock
            data['Special Service Starters'].add(customer_special)
        else:
            data['Cumulative Stats']['Area Under Special Queue Length Curve'] += state[
                                                                                     'Special Customer Queue Length'] * (
                                                                                         clock - data[
                                                                                     'Last Time Special Customer Queue Length Changed'])
            state['Special Customer Queue Length'] += 1
            if data['Cumulative Stats']['Max Special Customer Queue Length'] < state[
                'Special Customer Queue Length']:
                data['Cumulative Stats']['Max Special Customer Queue Length'] = state[
                    'Special Customer Queue Length']
            data['Special Queue Customers'][customer_special] = clock
            data['Special Queue Customers All'].add(customer_special)
            data['Last Time Special Customer Queue Length Changed'] = clock
            # will he get tired?
            if Uniform(0, 1) >= (1- impatient_customers_percentage):
                # he will get tired
                fel_maker(future_event_list, 'Leaving Of Tired', state, data, clock,
                          customer_special=customer_special, customer_normal=customer_normal, last_customer='S')

    elif last_customer == "C":
        data['Normal Customers'][customer_normal] = dict()
        data['Normal Customers'][customer_normal]['Arrival Time'] = clock
        data['Normal Queue Customers All'].add(customer_normal)
        if state['Beginner Server Status'] < num_of_beginners: #ASAP_beginner
            state['Beginner Server Status'] += 1
            fel_maker(future_event_list, 'Departure From Beginner', state, data, clock,
                      customer_special=customer_special, customer_normal=customer_normal, last_customer='C')
            data['Normal Customers'][customer_normal]['Time Service Begins'] = clock
        elif state['Specialist Server Status'] < num_of_specialists: #ASAP_special
            state['Specialist Server Status'] += 1
            fel_maker(future_event_list, 'Departure From Expert', state, data, clock,
                      customer_special=customer_special, customer_normal=customer_normal, last_customer='C')
            data['Normal Customers'][customer_normal]['Time Service Begins'] = clock
        else:
            data['Cumulative Stats']['Area Under Normal Queue Length Curve'] += state[
                                                                                    'Normal Customer Queue Length'] * (
                                                                                        clock - data[
                                                                                    'Last Time Normal Customer Queue Length Changed'])
            state['Normal Customer Queue Length'] += 1
            if data['Cumulative Stats']['Max Normal Customer Queue Length'] < state['Normal Customer Queue Length']:
                data['Cumulative Stats']['Max Normal Customer Queue Length'] = state['Normal Customer Queue Length']
            data['Normal Queue Customers'][customer_normal] = clock
            data['Normal Queue Customers All'].add(customer_normal)
            data['Last Time Normal Customer Queue Length Changed'] = clock
            # will he get tired?
            if Uniform(0, 1) >= (1- impatient_customers_percentage):
                # he will get tired
                fel_maker(future_event_list, 'Leaving Of Tired', state, data, clock,
                          customer_special=customer_special, customer_normal=customer_normal, last_customer='C')


def Departure_From_Expert(future_event_list, state, clock, data, customer_special=None,
                          customer_normal=None,
                          last_customer=None):
    # what is shift number?
    if (clock % 1440) // shift_time_1 == 0:
        shift = 0
    elif (clock % 1440) // shift_time_1 !=0 and (clock % 1440) // shift_time_2 ==0 :
        shift = 1
    else:
        shift = 2
    
    data['Cumulative Stats']['Specialist Servers Last Time'] = clock #yakhoda
    # was it a special or normal customer?
    if last_customer == 'S':
        data['Cumulative Stats']['Specialist Servers Busy Time'] += clock - data['Special Customers'][customer_special][
            'Time Service Begins']
        if clock > overwork_time: #yakhoda
            data['Cumulative Stats']['Specialist Servers Overworked'] += clock - data['Special Customers'][customer_special][
            'Time Service Begins']
        # data['Special Customers'].pop(customer_special, None)
        # will he use technical service?
        data['Special Customers Waiting Time In System'] += clock - data['Special Customers'][customer_special][
            'Arrival Time']
        if Uniform(0, 1) > (1-technical_need_percentage):
            # he will use technical service
            data['Special Customers'][customer_special]['Arrival Time Technical'] = clock
            data['Technical Special Queue Customers All'].add(customer_special)
            if state['Technical Server Status'] < num_of_technicals: #ASAP_technical
                # technical service begins immediately
                state['Technical Server Status'] += 1
                fel_maker(future_event_list, 'Departure From Technical', state, data, clock,
                          customer_special=customer_special, customer_normal=customer_normal, last_customer='S')
                data['Special Customers'][customer_special]['Time Service Begins Technical'] = clock
                data['Special Service Starters Technical'].add(customer_special)
            else:
                # gets in line in technical service
                data['Cumulative Stats']['Area Under Technical Special Queue Length Curve'] += state[
                                                                                                   'Technical Special Customer Queue Length'] * (
                                                                                                       clock - data[
                                                                                                   'Last Time Technical Special Customer Queue Length Changed'])
                state['Technical Special Customer Queue Length'] += 1
                if data['Cumulative Stats']['Max Technical Special Customer Queue Length'] < state[
                    'Technical Special Customer Queue Length']:
                    data['Cumulative Stats']['Max Technical Special Customer Queue Length'] = state[
                        'Technical Special Customer Queue Length']
                data['Technical Special Queue Customers'][customer_special] = clock
                data['Technical Special Queue Customers All'].add(customer_special)
                data['Last Time Technical Special Customer Queue Length Changed'] = clock
    else:
        # customer is normal
        data['Cumulative Stats']['Specialist Servers Busy Time'] += clock - data['Normal Customers'][customer_normal][
            'Time Service Begins']
        if clock > overwork_time: #yakhoda
            data['Cumulative Stats']['Specialist Servers Overworked'] += clock - data['Normal Customers'][customer_normal][
            'Time Service Begins']
        data['Normal Customers Waiting Time In System'] += clock - data['Normal Customers'][customer_normal][
            'Arrival Time']
        #Yakhoda
        data['Normal Customers'][customer_normal]['Time Service Ends'] = clock
        # will he use technical service?
        if Uniform(0, 1) > (1-technical_need_percentage):
            # he will use technical service
            data['Normal Customers'][customer_normal]['Arrival Time Technical'] = clock
            data['Technical Normal Queue Customers All'].add(customer_normal)
            if state['Technical Server Status'] < num_of_technicals: #ASAP_technical
                # technical service begins immediately
                state['Technical Server Status'] += 1
                fel_maker(future_event_list, 'Departure From Technical', state, data, clock,
                          customer_special=customer_special, customer_normal=customer_normal, last_customer='C')
                data['Normal Customers'][customer_normal]['Time Service Begins Technical'] = clock
            else:
                # gets in line in technical service
                data['Cumulative Stats']['Area Under Technical Normal Queue Length Curve'] += state[
                                                                                                  'Technical Normal Customer Queue Length'] * (
                                                                                                      clock - data[
                                                                                                  'Last Time Technical Normal Customer Queue Length Changed'])
                state['Technical Normal Customer Queue Length'] += 1
                if data['Cumulative Stats']['Max Technical Normal Customer Queue Length'] < state[
                    'Technical Normal Customer Queue Length']:
                    data['Cumulative Stats']['Max Technical Normal Customer Queue Length'] = state[
                        'Technical Normal Customer Queue Length']
                data['Technical Normal Queue Customers'][customer_normal] = clock
                data['Technical Normal Queue Customers All'].add(customer_normal)
                data['Last Time Technical Normal Customer Queue Length Changed'] = clock

    # Now after dealing with the customer woh left, wh go further checking the lines.
    if state['Special Customer Queue Length'] > 0:
        # who's the first in line?
        first_customer_in_queue = min(data['Special Queue Customers'], key=data['Special Queue Customers'].get)
        # this customer starts getting service
        data['Special Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        # Update queue waiting time
        data['Cumulative Stats']['Special Queue Waiting Time'] += \
            clock - data['Special Customers'][first_customer_in_queue]['Arrival Time']
        if data['Cumulative Stats']['Max Special Customer Queue Waiting Time'] < clock - \
                data['Special Customers'][first_customer_in_queue]['Arrival Time']:
            data['Cumulative Stats']['Max Special Customer Queue Waiting Time'] = clock - data['Special Customers'][
                first_customer_in_queue]['Arrival Time']
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Special Queue Length Curve'] += \
            state['Special Customer Queue Length'] * (clock - data['Last Time Special Customer Queue Length Changed'])
        state['Special Customer Queue Length'] -= 1
        # This customer no longer belongs to queue
        data['Special Queue Customers'].pop(first_customer_in_queue, None)
        # Queue length just changed. We should update it.
        data['Last Time Special Queue Length Changed'] = clock
        # Schedule its specific 'End of Service'.
        fel_maker(future_event_list, 'Departure From Expert', state, data, clock,
                  customer_special=first_customer_in_queue,
                  customer_normal=customer_normal, last_customer='S')

    elif state['Normal Customer Queue Length'] > 0:
        # who's the first in line?
        first_customer_in_queue = min(data['Normal Queue Customers'], key=data['Normal Queue Customers'].get)
        # this customer starts getting service
        data['Normal Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        # Update queue waiting time
        data['Cumulative Stats']['Normal Queue Waiting Time'] += \
            clock - data['Normal Customers'][first_customer_in_queue]['Arrival Time']
        if data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] < clock - \
                data['Normal Customers'][first_customer_in_queue]['Arrival Time']:
            data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] = clock - \
                                                                                 data['Normal Customers'][
                                                                                     first_customer_in_queue][
                                                                                     'Arrival Time']

        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Normal Queue Length Curve'] += \
            state['Normal Customer Queue Length'] * (clock - data['Last Time Normal Customer Queue Length Changed'])
        # Logic
        state['Normal Customer Queue Length'] -= 1
        # This customer no longer belongs to queue
        data['Normal Queue Customers'].pop(first_customer_in_queue, None)
        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Normal Queue Length Changed'] = clock
        # Schedule 'End of Service' for this customer
        fel_maker(future_event_list, 'Departure From Expert', state, data, clock,
                  customer_special=customer_special,
                  customer_normal=first_customer_in_queue, last_customer='C')

    else:
        # nothing to do
        state['Specialist Server Status'] -= 1


def Departure_From_Beginner(future_event_list, state, clock, data, customer_special=None,
                            customer_normal=None,
                            last_customer=None):
    # what is shift number
    if (clock % 1440) // shift_time_1 == 0:
        shift = 0
    elif (clock % 1440) // shift_time_1 !=0 and (clock % 1440) // shift_time_2 ==0 :
        shift = 1
    else:
        shift = 2

    data['Cumulative Stats']['Beginner Servers Last Time'] = clock
    data['Cumulative Stats']['Beginner Servers Busy Time'] += clock - data['Normal Customers'][customer_normal][
        'Time Service Begins']
    
    if clock > overwork_time: #yakhoda
        data['Cumulative Stats']['Beginner Servers Overworked'] += clock - data['Normal Customers'][customer_normal][
        'Time Service Begins']
    data['Normal Customers Waiting Time In System'] += clock - data['Normal Customers'][customer_normal][
            'Arrival Time']
    #Yakhoda
    data['Normal Customers'][customer_normal]['Time Service Ends'] = clock

    # will he use technical service?
    if Uniform(0, 1) > (1-technical_need_percentage):
        # he will use technical service
        data['Normal Customers'][customer_normal]['Arrival Time Technical'] = clock
        data['Technical Normal Queue Customers All'].add(customer_normal)
        if state['Technical Server Status'] < num_of_technicals:#ASAP_techincal
            # technical service begins immediately
            state['Technical Server Status'] += 1
            fel_maker(future_event_list, 'Departure From Technical', state, data, clock,
                      customer_special=customer_special, customer_normal=customer_normal, last_customer='C')
            data['Normal Customers'][customer_normal]['Time Service Begins Technical'] = clock
        else:
            # gets in line in technical service
            data['Cumulative Stats']['Area Under Technical Normal Queue Length Curve'] += state[
                                                                                              'Technical Normal Customer Queue Length'] * (
                                                                                                  clock - data[
                                                                                              'Last Time Technical Normal Customer Queue Length Changed'])
            state['Technical Normal Customer Queue Length'] += 1
            if data['Cumulative Stats']['Max Technical Normal Customer Queue Length'] < state[
                'Technical Normal Customer Queue Length']:
                data['Cumulative Stats']['Max Technical Normal Customer Queue Length'] = state[
                    'Technical Normal Customer Queue Length']
            data['Technical Normal Queue Customers'][customer_normal] = clock
            data['Technical Normal Queue Customers All'].add(customer_normal)
            data['Last Time Technical Normal Customer Queue Length Changed'] = clock

    # Now we go to check the lines and other stuff
    if state['Normal Customer Queue Length'] > 0:
        # who's the first in line?
        first_customer_in_queue = min(data['Normal Queue Customers'], key=data['Normal Queue Customers'].get)
        # this customer starts getting service
        data['Normal Customers'][first_customer_in_queue]['Time Service Begins'] = clock
        # Update queue waiting time
        data['Cumulative Stats']['Normal Queue Waiting Time'] += \
            clock - data['Normal Customers'][first_customer_in_queue]['Arrival Time']
        if data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] < clock - \
                data['Normal Customers'][first_customer_in_queue]['Arrival Time']:
            data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] = clock - \
                                                                                 data['Normal Customers'][
                                                                                     first_customer_in_queue][
                                                                                     'Arrival Time']
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Normal Queue Length Curve'] += \
            state['Normal Customer Queue Length'] * (clock - data['Last Time Normal Customer Queue Length Changed'])
        state['Normal Customer Queue Length'] -= 1
        # This customer no longer belongs to queue
        data['Normal Queue Customers'].pop(first_customer_in_queue, None)
        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Normal Queue Length Changed'] = clock
        # Schedule its specific 'End of Service' for this customer
        fel_maker(future_event_list, 'Departure From Beginner', state, data, clock,
                  customer_special=customer_special,
                  customer_normal=first_customer_in_queue, last_customer='C')

    else:
        state['Beginner Server Status'] -= 1


def Departure_From_Technical(future_event_list, state, clock, data, customer_special=None,
                             customer_normal=None,
                             last_customer=None):
    data['Cumulative Stats']['Technical Servers Last Time'] = clock
    if last_customer == 'S':
        data['Cumulative Stats']['Technical Servers Busy Time'] += clock - data['Special Customers'][customer_special][
            'Time Service Begins Technical']
        data['Special Customers Waiting Time In System'] += clock - data['Special Customers'][customer_special][
            'Arrival Time Technical']
        if clock > overwork_time: #yakhoda
            data['Cumulative Stats']['Technical Servers Overworked'] += clock - data['Special Customers'][customer_special][
            'Time Service Begins Technical']
    else:
        # customer is normal
        data['Cumulative Stats']['Technical Servers Busy Time'] += clock - data['Normal Customers'][customer_normal][
            'Time Service Begins Technical']
        
        data['Normal Customers Waiting Time In System'] += clock - data['Normal Customers'][customer_normal][
            'Arrival Time Technical']
        #Yakhoda
        if clock > overwork_time:#yakhoda
            data['Cumulative Stats']['Technical Servers Overworked'] += clock - data['Normal Customers'][customer_normal][
            'Time Service Begins Technical']
    # now we go check the line
    if state['Technical Special Customer Queue Length'] > 0:
        # who's the first in line?
        first_customer_in_queue = min(data['Technical Special Queue Customers'],
                                      key=data['Technical Special Queue Customers'].get)
        # this customer starts getting service
        data['Special Customers'][first_customer_in_queue]['Time Service Begins Technical'] = clock
        # Update queue waiting time
        data['Cumulative Stats']['Technical Special Queue Waiting Time'] += \
            clock - data['Special Customers'][first_customer_in_queue]['Arrival Time Technical']
        if data['Cumulative Stats']['Max Technical Special Customer Queue Waiting Time'] < clock - \
                data['Special Customers'][first_customer_in_queue]['Arrival Time Technical']:
            data['Cumulative Stats']['Max Technical Special Customer Queue Waiting Time'] = clock - \
                                                                                            data['Special Customers'][
                                                                                                first_customer_in_queue][
                                                                                                'Arrival Time Technical']
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Technical Special Queue Length Curve'] += \
            state['Technical Special Customer Queue Length'] * (
                    clock - data['Last Time Technical Special Customer Queue Length Changed'])
        # Logic
        state['Technical Special Customer Queue Length'] -= 1
        # This customer no longer belongs to queue
        data['Technical Special Queue Customers'].pop(first_customer_in_queue, None)
        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Technical Special Customer Queue Length Changed'] = clock
        # Schedule its specific 'End of Service' for this customer
        fel_maker(future_event_list, 'Departure From Technical', state, data, clock,
                  customer_special=first_customer_in_queue,
                  customer_normal=customer_normal, last_customer='S')

    elif state['Technical Normal Customer Queue Length'] > 0:
        # who's the first in line?
        first_customer_in_queue = min(data['Technical Normal Queue Customers'],
                                      key=data['Technical Normal Queue Customers'].get)
        # this customer starts getting service
        data['Normal Customers'][first_customer_in_queue]['Time Service Begins Technical'] = clock
        # Update queue waiting time
        data['Cumulative Stats']['Technical Normal Queue Waiting Time'] += \
            clock - data['Normal Customers'][first_customer_in_queue]['Arrival Time Technical']
        if data['Cumulative Stats']['Max Technical Normal Customer Queue Waiting Time'] < clock - \
                data['Normal Customers'][first_customer_in_queue]['Arrival Time Technical']:
            data['Cumulative Stats']['Max Technical Normal Customer Queue Waiting Time'] = clock - \
                                                                                           data['Normal Customers'][
                                                                                               first_customer_in_queue][
                                                                                               'Arrival Time Technical']
        # Queue length changes, so calculate the area under the current rectangle
        data['Cumulative Stats']['Area Under Technical Normal Queue Length Curve'] += \
            state['Technical Normal Customer Queue Length'] * (
                    clock - data['Last Time Technical Normal Customer Queue Length Changed'])
        # Logic
        state['Technical Normal Customer Queue Length'] -= 1
        # This customer no longer belongs to queue
        data['Technical Normal Queue Customers'].pop(first_customer_in_queue, None)
        # Queue length just changed. Update 'Last Time Queue Length Changed'
        data['Last Time Technical Normal Customer Queue Length Changed'] = clock
        # Schedule its 'End of Service' for this customer
        fel_maker(future_event_list, 'Departure From Technical', state, data, clock,
                  customer_special=customer_special,
                  customer_normal=first_customer_in_queue, last_customer='C')
    else:
        state['Technical Server Status'] -= 1


def Leaving_Of_Tired(future_event_list, state, clock, data, customer_special=None, customer_normal=None,
                     last_customer=None):
    if last_customer == 'S':
        data['Special Customers Waiting Time In System'] += clock - data['Special Customers'][
            customer_special]['Arrival Time']
        # customer is special
        # here we check if service for this customer has begun
        if 'Time Service Begins' in data['Special Customers'][customer_special].keys():
            # The Service has begun and we do nothing if so.
            True
        else:
            # this customer is one that leaves
            # Update queue waiting time
            data['Cumulative Stats']['Special Queue Waiting Time'] += \
                clock - data['Special Customers'][customer_special]['Arrival Time']
            if data['Cumulative Stats']['Max Special Customer Queue Waiting Time'] < clock - \
                    data['Special Customers'][customer_special]['Arrival Time']:
                data['Cumulative Stats']['Max Special Customer Queue Waiting Time'] = clock - data['Special Customers'][
                    customer_special]['Arrival Time']
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Special Queue Length Curve'] += \
                state['Special Customer Queue Length'] * (
                        clock - data['Last Time Special Customer Queue Length Changed'])
            # Logic
            state['Special Customer Queue Length'] -= 1
            # This customer no longer belongs to queue
            data['Special Queue Customers'].pop(customer_special, None)
            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Special Queue Length Changed'] = clock
            data['Cumulative Stats']['Customer Churn'] += 1
            data['Special Customers'][customer_special]['Leave Time'] = clock


    else:
        # customer is normal
        # here we check if service for this customer has begun
        if 'Time Service Begins' in data['Normal Customers'][customer_normal].keys():
            # The Service has begun and we do nothing if so.
            True
        else:
            # this customer is one that leaves
            # Update queue waiting time
            data['Cumulative Stats']['Normal Queue Waiting Time'] += \
                clock - data['Normal Customers'][customer_normal]['Arrival Time']
            if data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] < clock - \
                    data['Normal Customers'][customer_normal]['Arrival Time']:
                data['Cumulative Stats']['Max Normal Customer Queue Waiting Time'] = clock - \
                                                                                     data['Normal Customers'][
                                                                                         customer_normal][
                                                                                         'Arrival Time']
            # Queue length changes, so calculate the area under the current rectangle
            data['Cumulative Stats']['Area Under Normal Queue Length Curve'] += \
                state['Normal Customer Queue Length'] * (
                        clock - data['Last Time Normal Customer Queue Length Changed'])
            # Logic
            state['Normal Customer Queue Length'] -= 1
            # This customer no longer belongs to queue
            data['Normal Queue Customers'].pop(customer_normal, None)
            # Queue length just changed. Update 'Last Time Queue Length Changed'
            data['Last Time Normal Queue Length Changed'] = clock
            data['Cumulative Stats']['Customer Churn'] += 1
            data['Normal Customers'][customer_normal]['Leave Time'] = clock






def simulation(simulation_time):
    state, future_event_list, data = starting_state()
    clock = 0


    work_time = 8*60 #change1
    future_event_list.append(
        {'Event Type': 'End of Simulation', 'Event Time': simulation_time, 'Special Customer': None,
         'Normal Customer': None, 'Last Customer': None})
    

    while clock < simulation_time:


        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])

        current_event = sorted_fel[0]
        clock = current_event['Event Time']
        customer_special = current_event['Special Customer']
        customer_normal = current_event['Normal Customer']
        last_customer = current_event['Last Customer']
        if clock < simulation_time:
            if current_event['Event Type'] == 'Customer Call' and  clock<work_time:     #yakhoda
                Customer_Call(future_event_list, state, clock, data,
                              customer_special=customer_special,
                              customer_normal=customer_normal, last_customer=last_customer)
            elif current_event['Event Type'] == 'Departure From Expert':
                Departure_From_Expert(future_event_list, state, clock, data,
                                      customer_special=customer_special,
                                      customer_normal=customer_normal, last_customer=last_customer)
            elif current_event['Event Type'] == 'Departure From Beginner':
                Departure_From_Beginner(future_event_list, state, clock, data,
                                        customer_special=customer_special,
                                        customer_normal=customer_normal, last_customer=last_customer)
            elif current_event['Event Type'] == 'Departure From Technical':
                Departure_From_Technical(future_event_list, state, clock, data,
                                         customer_special=customer_special,
                                         customer_normal=customer_normal, last_customer=last_customer)
            elif current_event['Event Type'] == 'Leaving Of Tired':
                Leaving_Of_Tired(future_event_list, state, clock, data,
                                 customer_special=customer_special,
                                 customer_normal=customer_normal, last_customer=last_customer)
            future_event_list.remove(current_event)
        else:
            future_event_list.clear()
        if clock < warmup_point:
            for key in data['Cumulative Stats']:
                data['Cumulative Stats'][key] = 0
    print('Simulation Ended!')
    if data['Technical Special Queue Customers All'] == set():
        data['Technical Special Queue Customers All'] = {-1}
    if data['Technical Normal Queue Customers All'] == set():
        data['Technical Normal Queue Customers All'] = {-1}
    customer_churn = data['Cumulative Stats']['Customer Churn'] / (
                len(data['Special Queue Customers All']) + len(data['Normal Queue Customers All']))


    special_service_starters = (len(
        data['Special Service Starters'].intersection(data['Special Service Starters Technical']))) / (len(
        data['Special Queue Customers All']))
    max_special_customer_queue_length = data['Cumulative Stats']['Max Special Customer Queue Length']
    max_normal_customer_queue_length = data['Cumulative Stats']['Max Normal Customer Queue Length']


    max_special_customer_technical_queue_length = data['Cumulative Stats'][
        'Max Technical Special Customer Queue Length']
    max_normal_customer_technical_queue_length = data['Cumulative Stats']['Max Technical Normal Customer Queue Length']
    mean_special_customer_queue_length = data['Cumulative Stats'][
                                             'Area Under Special Queue Length Curve'] / (simulation_time - warmup_point)
    mean_normal_customer_queue_length = data['Cumulative Stats'][
                                            'Area Under Normal Queue Length Curve'] / (simulation_time - warmup_point)
    mean_special_customer_technical_queue_length = data['Cumulative Stats'][
                                                       'Area Under Technical Special Queue Length Curve'] / (simulation_time - warmup_point)
    mean_normal_customer_technical_queue_length = data['Cumulative Stats'][
                                                      'Area Under Technical Normal Queue Length Curve'] / (simulation_time - warmup_point)

    max_special_customer_queue_waiting_time = data['Cumulative Stats']['Max Special Customer Queue Waiting Time']
    max_normal_customer_queue_length_waiting_time = data['Cumulative Stats']['Max Normal Customer Queue Waiting Time']

    max_special_customer_technical_queue_waiting_time = data['Cumulative Stats'][
        'Max Technical Special Customer Queue Waiting Time']
    max_normal_customer_technical_queue_waiting_time = data['Cumulative Stats'][
        'Max Technical Normal Customer Queue Waiting Time']
    mean_special_customer_queue_waiting_time = data['Cumulative Stats']['Special Queue Waiting Time'] / len(
        data['Special Queue Customers All'])
    mean_normal_customer_queue_waiting_time = data['Cumulative Stats']['Normal Queue Waiting Time'] / len(
        data['Normal Queue Customers All'])

    mean_special_customer_technical_queue_waiting_time = data['Cumulative Stats'][
                                                             'Technical Special Queue Waiting Time'] / len(
        data['Technical Special Queue Customers All'])
    mean_normal_customer_technical_queue_waiting_time = data['Cumulative Stats'][
                                                            'Technical Normal Queue Waiting Time'] / len(
        data['Technical Normal Queue Customers All'])
    mean_special_customer_waiting_time_in_system = data['Special Customers Waiting Time In System'] / (
        len(data['Special Queue Customers All']))
    mean_normal_customer_waiting_time_in_system = data['Normal Customers Waiting Time In System'] / (
        len(data['Normal Queue Customers All']))

    specialist_servers_utilization = data['Cumulative Stats']['Specialist Servers Busy Time'] / (num_of_specialists * data['Cumulative Stats']['Specialist Servers Last Time']) # ASAP_specialist #yakhoda
    beginner_servers_utilization = data['Cumulative Stats']['Beginner Servers Busy Time'] / (num_of_beginners * data['Cumulative Stats']['Beginner Servers Last Time']) # ASAP_beginner  #yakhoda         
    technical_servers_utilization = data['Cumulative Stats']['Technical Servers Busy Time'] / (num_of_technicals * data['Cumulative Stats']['Technical Servers Last Time']) # ASAP_techinal #yakhoda

    
    specialist_servers_overwork = data['Cumulative Stats']['Specialist Servers Overworked'] /num_of_specialists
    beginner_servers_overwork = data['Cumulative Stats']['Beginner Servers Overworked'] / num_of_beginners
    technical_servers_overwork = data['Cumulative Stats']['Technical Servers Overworked'] / num_of_technicals

    

    return data




