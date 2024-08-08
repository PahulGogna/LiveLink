import logging
import azure.functions as func
import main

app = func.FunctionApp()

@app.schedule(schedule="00:15:00", arg_name="myTimer",
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')
    detail = main.main()
    logging.info(f'Python timer trigger function executed. {detail}')