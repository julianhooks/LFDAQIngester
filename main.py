import labjack as ljm
import questdb
import logging

def main() -> None:
    # Program needs to do a couple things
    # [TO-DO] Connect to QuestDB
    # [TO-DO] Pull active instruments (labjack port + calibration EQ + database stuff) from database
    # [TO-DO] Connect to Labjack
    # [TO-DO] Perform data ingestion:
    # - Get voltages of each active instrument
    # - Run calibration function on voltage
    # - Write (time,voltage,value) to each instrument table
    # - Repeat until close
    # [TO-DO] Exit cleanly on error (+ give me logs of what's going on) 

    return

if (__name__ == "__main__"):
    main()
