from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH3F
import numpy as np


#from Class_Templatefiles import tempFile,tempHist


def  Rebin(hist,nmass,ndbsi):
    xbins = hist.GetNbinsX()
    ybins = hist.GetNbinsY()
    zbins = hist.GetNbinsZ()
    
    hname = hist.GetName()
    
    dbsiedg = []
    dbsie = np.arange(21,dtype='float64')/20 -1

    if ndbsi > 0 : 
        for i  in range(0,ndbsi): 
            if i < ( ndbsi-1)  : 
                cent = -1 + i*1./(ndbsi-1)
                dbsiedg.append(cent)
            else : 
                dbsiedg.append(0.)
                dbsiedg.append(1)
        dbsie = np.array(dbsiedg,dtype="float64")
        
    print dbsiedg
    medg = []
    medges = np.arange(22,dtype='float64')
    if nmass > 0 : 
        for i  in range(0,nmass): 
            if i < ( nmass-1)  : 
                cent = 0 + i*16./(nmass - 1)
                medg.append(cent)
            else : 
                medg.append(16.)
                medg.append(21)
        medges = np.array(medg,dtype='float64')

    dbkgedges = np.arange(21,dtype='float64') /20

    
    summ = 0
    temp_same  = TH3F("temp_same","",xbins,0,xbins,ybins,0,1,zbins,-1,1)
    for y in range (1,ybins+1):
        biny_c = hist.GetYaxis().GetBinCenter(y)
        for x in range (1,xbins+1):
            binx_c = hist.GetXaxis().GetBinCenter(x)            
            for z in range (1,zbins+1):
                binz_c = hist.GetZaxis().GetBinCenter(z)
                ibin  =  hist.FindBin(binx_c,biny_c,binz_c)
                cont  = hist.GetBinContent(ibin)  
                temp_same.SetBinContent(ibin,cont)
                summ = summ+ cont



    temp_rb  = TH3F("temp_rb","",len(medges)-1,medges,len(dbkgedges)-1,dbkgedges,len(dbsie)-1,dbsie)
    temp_rb.SetName(hname)

    for y in range (1,ybins+1):
        biny_c = temp_same.GetYaxis().GetBinCenter(y)
        for x in range (1,xbins+1):
            binx_c = temp_same.GetXaxis().GetBinCenter(x)
            for z in range (1,zbins+1):
                binz_c = temp_same.GetZaxis().GetBinCenter(z)
                ibin =  temp_same.FindBin(binx_c,biny_c,binz_c)
                cont  = temp_same.GetBinContent(ibin)
                temp_rb.Fill(binx_c,biny_c,binz_c, cont )






    print "integrals : ", hist.Integral(), summ,temp_same.Integral()  ,temp_rb.Integral()
    return temp_rb
