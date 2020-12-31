import yahoo_fin.stock_info as si
import datetime as dt
import time

def fill_open(row):
    ticka = row['ticka']
    open_date = row['post_date']
    end_date = open_date+dt.timedelta(days=1)
    backup_count = 1
    while(True):
        try:
            if backup_count > 7:
                return -1
            price_info = si.get_data(ticka, start_date=open_date, end_date=end_date)
            return price_info['adjclose'][0]
        except KeyError:
            #print(f'KeyError, back a day {backup_count} {ticka}')
            open_date = open_date - dt.timedelta(days=1)
            backup_count += 1
        except AssertionError:
            #print(f'Ticka {ticka} is wrong, skipping')
            return -1
        except:
            #print("Likely JSON decode, try again and pray")
            backup_count += 1
            time.sleep(5)
            

def fill_close(row):
    close_date = row['expiry']
    if close_date > dt.datetime.today():
        return -1
    ticka = row['ticka']
    while close_date.weekday() != 4: # correct it back to friday for those fat fingered among us
        print(f'Date Adjustment from {close_date}')
        if close_date.weekday() <= 3 and close_date.weekday() >= 1:
            close_date = close_date + dt.timedelta(days=1)
        else:
            close_date = close_date - dt.timedelta(days=1)
    end_date = close_date+dt.timedelta(days=1)
    try:
        price_info = si.get_data(ticka, start_date=close_date, end_date=end_date)
        return price_info['adjclose'][0]
    except:
        #print(f'Ticka {ticka} is wrong, or expiry {close_date} has not occured yet')
        return -1

def convert_to_est(gmt_timestamp):
	return int(gmt_timestamp)-(60*60*5)