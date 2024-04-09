curr_date = df.index[0]
driver_available = 50

while(curr_date < last_date):
	next_date = curr_date +1
    
    if next_date does not exist in the dataset:
        just print the state? and does not much we can do.
        continue
	
	if(driver_available < math.abs(next_date.bal_lvl)):
		print("we only have '%d' available drivers now in PQ, it is not enough for tmr's deliveries, back up more drivers today!", driver_available)
		driver_available = next_date.bal_lvl
	
	if curr_date.bal_lvl == 0:
		print("Nothing to forecast")
	else if curr_date.bal_lvl > 0:
		# meaning that inbound > outbound, we have more available drivers in PQ
		driver_available += bal_lvl
		print("%d drivers will be awaiting for the deliveries.",driver_available)
        
		if next_date.bal_lvl < 0:
			# DISCUSS: Use available drivers to do tmr's delivery. (but how to decide the end date of the order?)
			if tailer_class == 'DRY':
				# we assume that 'DRY' trailers are always available
				next_date.outbound--; curr_date.inbound++; driver_available--;
			else: 
				#the order is "HEATER" etc., 
				if we have available trailer to do delivery:
					next_date.outbound--; driver_available--;
        else: #next_date.bal_lvl > 0
        
            # balance both days.
            # two cases: (4 cases)
            # curr_date.bal_lvl(20, -10) >> next_date.bal_lvl(2, 0):
            # curr_date.bal_lvl << next_date.bal_lvl:
            # print(forecast(" can you finish it one day earlier?"))
        
        # next_date.bal_lvl == 0
		
		# DISCUSS: we probably do not need more than 50 available drivers each day?
		if(driver_available > 50):
			driver_available = 50
            
	else(i.e., curr_date.bal_lvl < 0):
        driver_available -= curr_date.bal_lvl
        
        if next_date.bal_lvl == 0:
            continue #forecast
        else if next_date.bal_lvl > 0: # today we have more outgoing, tmr, more incoming.
            # forecast that, print(forecast(" can you finish it one day earlier?"))
            # assume
            driver_available += next_date.bal_lvl
        else
            # 4 cases like above?
            continue #forecast
	
	curr_date = next_date
# end of while loop	
	
This is a greedy algorithm, that we make sure every day(curr_date) has a best bal_lvl

# how to tell our algorithm is efficient:
# Jason: std , how far from 0?
# Qi:  histgram?
# outliers - mean square. 