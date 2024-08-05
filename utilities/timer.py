import time

'''
timer.py

Times the execution time of a function.

Author: ILnaw
Version: 0.0.1
'''

def time_execution(callback, *args, **kwargs):
    
    start_time = time.time()
    result = callback(*args, **kwargs)
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time:.4f} seconds")
    return result