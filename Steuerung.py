
import time
import json
import customtkinter as ctk
from PIL import Image,ImageTk
from ChemTherm_library.tinkerforge_lib import *
from ChemTherm_library.Verdampfer_lib import *


def tk_loop():   
      
    if running_Json == 1:
        T_set, MFC_set,t_end,section = json_timing(config,section,t0)
        lable_timer.configure(text = str("{0:.2f}").format(t_end/60)+" min")
        for i in set_T:
            set_T[i].delete(0, tk.END)
            set_T[i].insert(0,str("{0:.2f}").format(T_set[i]))

        for i in set_MFC:
            set_MFC[i].delete(0, tk.END)
            set_MFC[i].insert(0,str(MFC_set[i]))
        getdata()         
        if (t_end < 0):
            Stop_Button_callback()  

    for tc_obj_name in tc_list:
        lable_T_ist[tc_obj_name].configure(text = str(tc_list[tc_obj_name].t)+" °C")
    for p_obj_name in patronen_list:   
        progressbar[p_obj_name].set(patronen_list[p_obj_name].pwroutput/100)

    MFC_1.get()
    value_MFC[0].configure(text = str(MFC_1.Voltage) + " mV") 
    pressure1.get()
    pressure2.get()
    value_pressure1.config(text = str(pressure1.Voltage) + " mV") 
    value_pressure2.config(text = str(pressure2.Voltage) + " mV") 

    Heater1.regeln()
    window.after(500, tk_loop)

def getdata():    

    if set_T[0].get() != '':
        Heater1.set_t_soll(float(set_T[0].get()))


    MFC_1.set(int(set_MFC[0].get()))

def Start_Button_callback():
    global section, running_json, t0
    running_json = 1
    section = 1
    t0 = time.time()
    Start_Button.configure(state = "disabled")

def Stop_Button_callback():
    global section, running_json,running_setFunction, t0
    running_json = 0
    running_setFunction = 0
    Start_Button.configure(state = "enabled")
    lable_timer.configure(text = str("{0:.2f}").format(0)+" min")

'''' 
====================================
SETUP 
====================================
'''
t0 = time.time()
section = 0
running_Json = 0
# Set Devices
HOST = "localhost"
PORT = 4223

ipcon = IPConnection() # Create IP connection
ipcon.connect(HOST, PORT) # Connect to brickd

''''
====================================
JSON
====================================
'''
json_name="Experiment1"

with open(json_name +'.json', 'r') as config_file:
    config = json.load(config_file)

''''
====================================
Set TkinterForge Elements
====================================
'''

tc_1 = tc(ipcon, "WQ8", typ='K') #A
tc_2 = tc(ipcon, "23iL", typ='K') #B
tc_3 = tc(ipcon, "23jK", typ='K') #C
tc_list = {'T1':tc_1,'T2':tc_2,'T3':tc_3}

OutHeat = BrickletIndustrialDigitalOut4V2("Tn6", ipcon)

Heater1 = regler(OutHeat,0,tc_1)
Heater1.config(0.000007, 0.015)
Heater1.start(0)
Heater_list = {'H1':Heater1}


pressureDual1 = TF_IndustrialDualAnalogIn(ipcon, "23UA")
pressureDual2 = TF_IndustrialDualAnalogIn(ipcon, "24xB")
pressure1 = pressure(pressureDual1,0)
pressure2 = pressure(pressureDual1,1)

MFC_WaterV = TF_IndustrialDualAnalogIn(ipcon, "23Ud")

MFC_1 = MFC(ipcon, "Zvg", MFC_WaterV,1)


''''
====================================
Set GUI
====================================
'''
window = ctk.CTk()
ctk.set_appearance_mode("light")
scrW = window.winfo_screenwidth()
scrH = window.winfo_screenheight()
window.geometry(str(scrW) + "x" + str(scrH))
window.title(config['EVAP']['Name'])
window.configure(bg= config['TKINTER']['background-color'])
window.attributes('-fullscreen',True)
#----------- Images ----------- 
bg_image = ctk.CTkImage(Image.open(config['Background']['name']))
close_img = ctk.CTkImage(Image.open(config['PATH']['images'] + 'close.png'),size=(80, 80))


#----------- Frames ----------
lf_MFC = ctk.CTkFrame(window, border_color=config['TKINTER']['background-color'], border_width=0, height=scrH, width=scrW)
MFC_Frame = ctk.CTkLabel(lf_MFC, font = ('Arial',16), text='MFC Steuerung')
MFC_Frame.grid(column=0, columnspan = 2, row=0, ipadx=5, ipady=5)
lf_MFC.place(x= 50,y= 800)

#----------- Labels -----------
label_background = ctk.CTkLabel(window,image=bg_image,text="")
x_offset = config['TKINTER']['x']
y_offset = config['TKINTER']['y']
label_background.place(x = x_offset,y = y_offset)
label_background.lower()


lf_pressure = ctk.CTkFrame(window, text='Druck')
lf_pressure.grid(column=3, row=2, padx=20, pady=20)
lf_pressure.place(x= 1050,y= 840)


Lable_pressure1= tk.Label(lf_pressure, text='Druck_1 ')
Lable_pressure1.grid(column=0, row=0, ipadx=5, ipady=5)
value_pressure1= tk.Label(lf_pressure, text='NaN mV')
value_pressure1.grid(column=1, row=0, ipadx=5, ipady=5)

Lable_pressure2= tk.Label(lf_pressure, text='Druck_2 ')
Lable_pressure2.grid(column=0, row=0, ipadx=5, ipady=5)
value_pressure2= tk.Label(lf_pressure, text='NaN mV')
value_pressure2.grid(column=1, row=0, ipadx=5, ipady=5)



lf_control = tk.LabelFrame(window, text='Steuerung')
lf_control.grid(column=0, row=1, padx=20, pady=20)


option = ['T1','T2','T3']
option_Heat = ['H1']
option_MFC = ['H1']

lable_T_ist ={}
progressbar ={}   
set_T ={}
for num, i in enumerate(option):
    lable_T_ist[i] = ctk.CTkLabel(window, font = ('Arial',16), text='0 °C')
    lable_T_ist[i].place(x = x_offset + config['T-Value']['x'][num],y = y_offset + config['T-Value']['y'][num])

for num, i in enumerate(option_Heat):
    progressbar[i] = ctk.CTkProgressBar(master=window, width = 80, progress_color = 'red')
    progressbar[i] .place(x = x_offset + config['T-Value']['x'][num]-8,y = y_offset + config['T-Value']['y'][num]+30)
    set_T[i] = tk.Entry(window, font = ('Arial',16), width = 6,bg='light blue' )
    set_T[i].place(x = x_offset + config['T-Set']['x'][i],y = y_offset + config['T-Set']['y'][i])

name_MFC={}; set_MFC={}; unit_MFC={}; value_MFC={}

for num, i in enumerate(option_Heat):
    name_MFC[i]= ctk.CTkLabel(lf_MFC, font = ('Arial',16), text=config['MFC']['name'][i])
    name_MFC[i].grid(column=0, row=i+1, ipadx=5, ipady=5)
    set_MFC[i] = tk.Entry(lf_MFC, font = ('Arial',16), width = 6 )
    set_MFC[i].grid(column=1, row=i+1, ipadx=5, ipady=5)
    unit_MFC[i]= ctk.CTkLabel(lf_MFC, font = ('Arial',16), text=' mV')
    unit_MFC[i].grid(column=2, row=i+1, ipadx=5, ipady=5)
    value_MFC[i]= ctk.CTkLabel(lf_MFC, font = ('Arial',16), text='0 mV')
    value_MFC[i].grid(column=3, row=i+1, ipadx=5, ipady=5)

lable_timer = ctk.CTkLabel(master = lf_control , font = ('Arial',16), text='0 min')
lable_timer.grid(column=1, row=2)
#----------- Buttons -----------
button1 = tk.Button(lf_control,text='Set Values', command=getdata, bg='brown', fg='white')
button1.grid(column=1, row=0, ipadx=8, ipady=8)
Stop_Button = ctk.CTkButton(master=lf_control, command=Stop_Button_callback,text="Messung stoppen", font = ('Arial',16),fg_color = 'blue')
Stop_Button.grid(column=2, row=0, padx=10, pady = 8)
Start_Button = ctk.CTkButton(master=lf_control, command=Start_Button_callback,text="JSON starten", font = ('Arial',16),fg_color = 'blue')
Start_Button.grid(column=2, row=1, padx=10, pady = 8)
Exit_Button = ctk.CTkButton(master=window,text="", command=window.destroy, fg_color= 'transparent',  hover_color='#F2F2F2', image= close_img)
Exit_Button.place(x=1700, y=50)


window.after(1000, tk_loop())
window.mainloop()

print("shutting down...")
Heater1.stop()
MFC_1.stop()

time.sleep(2)
ipcon.disconnect()
print("bye bye")