import tkinter as tk
import sys
sys.path.insert(0, 'C:/Users/barto/Desktop/Praca magisterska - program')
from load_csv import select_csv_directory, process_csv

def load_button():
    csv_label = tk.Label(main_window, text = "Progress ...")
    csv_label.place(x = 50, y = 35)
    [data_path, i, shape] = select_csv_directory()
    csv_label = tk.Label(main_window, text = "Załadowano {} plików CSV".format(i))
    csv_label.place(x = 10, y = 35)
    return data_path, shape

def process_button_cmd():
    czasy = process_csv(data_path, shape)

main_window = tk.Tk()
main_window.title("GBS DOBRZE JEST")
main_window.geometry("600x400")
#creating button and setting up button to load csv files
csv_load_button = tk.Button(main_window, text = 'Wybierz folder z plikami CSV', command = load_button)
csv_load_button.place(x = 5, y = 5)
#creating button and setting it up to process dataframe from csv files
process_button = tk.Button(main_window, text = 'Wybierz folder z plikami CSV', command = process_button_cmd)






main_window.mainloop()