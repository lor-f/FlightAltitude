import numpy as np
import sympy as sp
import matplotlib.pyplot as plt

def main():
    M = 8 # input mach number
    PDyn = 48000 # input dynamic pressure 
    GetAtmosphere(M,PDyn)
    PlotAltitudes()
    
def GetAtmosphere(M,PDyn):
    Ru = 8.3144598 # gas constant 
    g = 9.80665 # gravity acceleration 
    MM = 0.0289644 # molar mass of air
    R = 287 # air specific gas constant
    gamma = 1.4 # specific heat ratios
    Cp = 1006 # specific heat of air
    
    b = np.array([[0,1.225,288.15,-0.0065],
                 [11000, 0.36391, 216.65, 0],
                 [20000, 0.08803, 216.65, 0.001],
                 [32000, 0.01322, 228.65, 0.0028],
                 [47000, 0.00143, 270.65, 0],
                 [51000, 0.00086, 270.65, -0.0028]]) # atmosphere regions properties
    
    NRegion = np.size(b[:,1])
    for i in range(NRegion-1): # iterate thru regions
        
        h = sp.symbols("h",real=True) #sympy variable to solve
        
        hb = b[i,0] # region altitude 
        rhob = b[i,1] # region density
        Tb = b[i,2]  # region temp
        Lb = b[i,3] # region lapse rate
        
        # solving the barometric formula:
        if Lb != 0.0:
            rho = rhob*(Tb/(Tb + ((h - hb)*Lb)))**(1 + ((g*MM)/(Ru*Lb)))
        else:
            rho = rhob*sp.exp((-g*MM*(h - hb))/(Ru*Tb))
        
        T = Tb + (Lb*(h - hb)) 
        c = sp.sqrt(gamma*R*T)  
        EqN = sp.Eq(0.5*rho*((M*c)**2),PDyn) # governing equation
        H = sp.nsolve(EqN,h,10000) # solve it
        
        # find proper solution
        hFirst = b[i,0] 
        if i == NRegion-1:
            hNext = 1e6
        else:
            hNext = b[i + 1, 0]
        
        if H > hFirst and H < hNext:
            break
        
    TInf = T.subs(h,H)
    rhoInf = rho.subs(h,H)
    PInf = rhoInf*R*TInf # pressure
    UInf = c.subs(h,H)*M # air speed
    TStag = TInf + 0.5*(UInf**2/Cp) # stagnation temp
    return H

    # write output file
    with open('FlightData.txt', 'w') as f:
        f.write('For Mach ' + str(M) + ' and dynamic pressure ' + str(PDyn/1e03) + ' KPa: \n')
        f.write('------------------------------------------------------------------------------ \n')
        f.write('Flight altitude: ' + str(H/1e03) + ' km \n' )
        f.write('------------------------------------------------------------------------------ \n')
        f.write('     Air temperature: ' + str(TInf) + ' K \n' )
        f.write('     Air pressure: ' + str(PInf) + ' Pa \n' )
        f.write('     Air density: ' + str(rhoInf) + ' kg/m**3 \n' )
        f.write('     Airspeed: ' + str(UInf) + ' m/s \n' )
        f.write('     Stagnation temperature: ' + str(TStag) + ' K \n' )

# plotter 
def PlotAltitudes():
    MStart = 2
    MEnd = 10
    MRange = np.linspace(MStart,MEnd,30)
    PRange = np.array([24000,48000,72000,96000])
    j = 0
    n = 6
    colors = plt.cm.summer(np.linspace(0,1,n))
    for Pres in PRange:           
        He = np.zeros(np.size(MRange))
        i = 0
        for M in MRange:
            He[i] = GetAtmosphere(M,Pres)
            i = i + 1
        plt.figure(1)
        plt.plot(MRange,He/1e3,color = colors[j])
        j = j + 1
    plt.figure(1)
    plt.xlabel('Mach number [-]')
    plt.ylabel('Flight altitude [km]')
    plt.legend(['24','48','72','96'],title = 'Dynamic pressure [KPa]')
    plt.grid()
    plt.savefig('AltitudeVsMachVsPDyn.png',dpi = 800)

main()