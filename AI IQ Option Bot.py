import pandas as pd
import numpy as np
from itertools import count
from iqoptionapi.stable_api import IQ_Option
from sklearn.linear_model import LinearRegression
Iq=IQ_Option("email","password")
ch,fa=Iq.connect()
model=LinearRegression()
print('Start running...')
print('-------------------------------')
'''
-------------------------
>>> ปรับค่าต่าง ๆ ตรงนี้ <<<
-------------------------
'''
MODE="PRACTICE" #"REAL" & "PRACTICE"
XCurrency=["EURJPY"] #สกุลเงิน Ex."EURUSD","GBPUSD","EURJPY","EURUSD-OTC","GBPUSD-OTC","EURJPY-OTC"
Xmultiply=2 #ตัวคูณ martingal ต่อการทบ 1 ไม้
Xmartingale=7 #จำนวน martingale ติดกันสูงสุดที่รับได้
Xprofit=100 #จำนวนกำไรสูงสุดที่จะหยุด
Xloss=-100 #จำนวนขาดทุนที่จะหยุด
XDuration=1 #minute 1 or 5
XMoney=1 #จำนวนเงินที่ลงต่อไม้
Xsize=60 #หลักวินาที 15 วิเหมาะตอนไม่ผันผวนมาก
Xmaxdict=181 #จำนวนแท่ง
'''
>>> วิธีหยุดรันแบบ Manual <<<
 1. คลิกที่ Terminal ด้านล่าง
 2. กด Ctrl + C
 3. Done
'''
Iq.change_balance(MODE)
profit=0
gain=0
loss=0
martingale=0
MaxMartingale=0
maxprofit=0
maxloss=0
trigger=0
while profit < Xprofit:
    list_id=[]
    if profit <= Xloss or martingale > Xmartingale:
        break
    for x in XCurrency:
        Currency=x
        Duration=XDuration #minute 1 or 5
        Money=XMoney
        if MaxMartingale < martingale:
            MaxMartingale = martingale
        if martingale > 0:
            Money = Money*(Xmultiply**martingale) 
        size=Xsize
        maxdict=Xmaxdict
        Iq.start_candles_stream(Currency,size,maxdict)
        realtime = Iq.get_realtime_candles(Currency,size)  
        real_time = dict(reversed(list((dict(realtime).items()))))
        green=0
        red=0 
        count=0 
        Type=[]
        winorder=[]
        for i in real_time:
            count += 1  
            OpenA = realtime[i]['open']     
            CloseA = realtime[i]['close']  
            MinA = realtime[i]['min']
            MaxA = realtime[i]['max'] 
            VolumeA=realtime[i]['volume']
            if count == 1:              
                OpenB = OpenA
                MinB = MinA
                MaxB = MinB
                VolumeB = VolumeA
            if count != 1 and count < Xmaxdict+2:             
                Type.append([OpenA,MinA,MaxA,VolumeA])
                winorder.append(CloseA)
        dfx = pd.DataFrame(Type, columns =['Open','Min', 'Max','Volume'])
        WINORDER=np.array(winorder).reshape(-1,1)
        model.fit(dfx,WINORDER)
        CloseB=model.predict([[OpenB,MinB,MaxB,VolumeB]])
        if OpenB < CloseB:
            Order="put"
            print('Currency : ',str(Currency)) 
            print('I am put')
            print('-------------------------------') 
            _,id=(Iq.buy_digital_spot(Currency,Money,Order,Duration))
            list_id.append(id)
        elif OpenB > CloseB: #แก้ตรงนี้
            Order="call"
            print('Currency : ',str(Currency))
            print('I am call')
            print('-------------------------------')
            _,id=(Iq.buy_digital_spot(Currency,Money,Order,Duration))
            list_id.append(id)
        else:
            print('Currency : ',str(Currency))
            print("Waiting for trending..." )
            print('-------------------------------')
    if len(list_id) >= 1: 
        for id in list_id:
            if len(str(id)) < 30:
                while True:         
                    check,win=Iq.check_win_digital_v2(id)   
                    if check==True:     
                        break         
                if win<0:     
                    profit += win
                    loss += 1 
                    martingale += 1                                      
                else:     
                    profit += win
                    gain += 1  
                    martingale = 0      
    print('Gain : ',str(gain)) 
    print('Loss : ',str(loss))
    if martingale!=0:
        print('Martingale : ',str(martingale-1))
    else:
        print('Martingale : ',str(martingale))
    print('Max Martingale : ',str(MaxMartingale))
    if gain + loss == 0:
        print('Winrate : ',str(0)+' %')
        print('Profit : ',str(0)+' $')
    else:
        print('Winrate : ',str('%.2f'%(gain/(gain+loss)*100))+' %')
        print('Profit : ',str('%.2f'%profit)+' $')
    if maxprofit < profit:
        maxprofit = profit
    print('Max Profit : ',str('%.2f'%maxprofit)+' $')
    if maxloss > profit:
        maxloss = profit
    print('Max Loss : ',str('%.2f'%maxloss)+' $')
    print('-------------------------------')
