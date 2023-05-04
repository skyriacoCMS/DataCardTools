
from ROOT import TCanvas, TFile, TProfile, TNtuple, TH1F, TH3F
#from Class_Templatefiles import tempFile,tempHist
import sys
import copy

def  Unrollflow(hist,category):

    
    xbins = hist.GetNbinsX()
    ybins = hist.GetNbinsY()
    
    is2d = False
    is3d = False
    fmname = category+"Mask.root"
    fmask = TFile(fmname)

    hmask = []
    hres_pos = []
    hres_neg = []
    for ikey,key in enumerate(fmask.GetListOfKeys()): 
        hres_pos.append(0) 
        hres_neg.append(0) 

        keyname = key.GetName()
        hm = fmask.Get(keyname)
        hmaski = copy.deepcopy(hm)
        hmask.append(hmaski)
    fmask.Close()    
    
    if "TH2" in str(type(hist)) :
        is2d = True 
        temp_pos = TH1F("temp_pos","",xbins*ybins,0,xbins*ybins)
        temp_neg = TH1F("temp_neg","dif",xbins*ybins,0,xbins*ybins)

    if "TH3" in str(type(hist)) :
        is3d = True 
        zbins = hist.GetNbinsZ()
        temp_pos = TH1F("temp_pos","",xbins*ybins*zbins,0,xbins*ybins*zbins)
        temp_neg = TH1F("temp_neg","dif",xbins*ybins*zbins,0,xbins*ybins*zbins)

        
    

    #Unroll Hists
    indk = 0
    has_negative = False 
    intt_in = hist.Integral()
    for y in range (1,ybins+1):
        for x in range (1,xbins+1):
            if is3d : 
             zbins = hist.GetNbinsZ()

             for z in range (1,zbins+1):
                binx_c = hist.GetXaxis().GetBinCenter(x)
                biny_c = hist.GetYaxis().GetBinCenter(y)
                binz_c = hist.GetZaxis().GetBinCenter(z)
                ibin =  hist.FindBin(binx_c,biny_c,binz_c)
                cont  = hist.GetBinContent(ibin)

                #put small values in empty background bins
                if cont == 0 : 
                    if "back" in hist.GetName():
                        nb = ybins*xbins*zbins
                        contt = 0.01*intt_in*1.0/nb
                        #if ("back_qqZZ" == hist.GetName()) : 
                        #   print ("found empty bin",contt)
                        hist.SetBinContent(ibin,contt)
                        #print (cont)
                if cont  < 0 :
                    has_negative = True
            else :
                binx_c = hist.GetXaxis().GetBinCenter(x)
                biny_c = hist.GetYaxis().GetBinCenter(y)
                ibin =  hist.FindBin(binx_c,biny_c)
                cont  = hist.GetBinContent(ibin)

                #put small values in empty background bins
                #if cont == 0 : 
                #    if "back" in hist.GetName():
                #        intt = hist.Integral()
                #        nb = ybins*xbins
                #        contt = 0.1*intt*1.0/nb
                #        #print ("found empty bin",contt)
                #        hist.SetBinContent(ibin,contt)
                #        #print (cont)
                if cont  < 0 :
                    has_negative = True
    length = 0
    lastindx3d = -1    
    for x in range (1,xbins+1):
        hmask_i  = hmask[x-1] 
        lastindx2d = -1 
        for y in range (1,ybins+1):
            if is3d : 
              zbins = hist.GetNbinsZ()  
              ressp = 0
              ressn = 0
              lastindx = -1
              for z in range (1,zbins+1):
                binx_c = hist.GetXaxis().GetBinCenter(x)
                biny_c = hist.GetYaxis().GetBinCenter(y)
                binz_c = hist.GetZaxis().GetBinCenter(z)
                ibin =  hist.FindBin(binx_c,biny_c,binz_c)
                cont  = hist.GetBinContent(ibin)
                ibinm = hmask_i.FindBin(biny_c,binz_c)
                mask = hmask_i.GetBinContent(ibinm)
                #print mask
                if mask  < 1 : 
                    if cont  < 0 :
                        ressn = ressn + cont
                    else :
                        ressp = ressp + cont

                    temp_neg.Fill(indk,-9999)
                    temp_pos.Fill(indk,-9999)
                    

                else :
                    length = length+1
                    if cont  < 0 :
                        temp_neg.Fill(indk,-1*(cont))
                    else :
                        temp_pos.Fill(indk,cont)
                    temp_neg.Fill(indk,-1*(ressn))
                    temp_pos.Fill(indk,ressp)
                    
                    ressp = 0
                    ressn = 0
                    lastindx = indk
                    if lastindx2d == -1 : 
                        lastindx2d = indk 
                    if lastindx3d == -1 : 
                        lastindx3d = indk 
                indk = indk +1
            
              #Add any residuals to the last nonempty bin
              if not lastindx == -1 :  
                  temp_neg.Fill(lastindx,-1*(ressn))
                  temp_pos.Fill(lastindx,(ressp))
              else :
                  if not lastindx2d == -1 : 
                      temp_neg.Fill(lastindx2d,-1*(ressn))
                      temp_pos.Fill(lastindx2d,(ressp))
                  else : 
                      temp_neg.Fill(lastindx3d,-1*(ressn))
                      temp_pos.Fill(lastindx3d,(ressp))

         
            else :
                #"Masking not implemented for 2D hists now"
                binx_c = hist.GetXaxis().GetBinCenter(x)
                biny_c = hist.GetYaxis().GetBinCenter(y)
                
                ibin =  hist.FindBin(binx_c,biny_c)
                cont  = hist.GetBinContent(ibin)
                if cont  < 0 :
                    temp_neg.Fill(indk,-1*cont)
                else :
                    temp_pos.Fill(indk,cont)
                indk = indk +1
                 
                
    temp_name = hist.GetName()
    
    tpname = temp_name
    tnname = temp_name

    '''  
    tnname = tnname.replace("0HPlus","0PH")
    tnname = tnname.replace("0Plus","0PM")
    tnname = tnname.replace("0Minus","0M")

    tpname = tpname.replace("0HPlus","0PH")
    tpname = tpname.replace("0Plus","0PM")
    tpname = tpname.replace("0Minus","0M")

    tnname = tnname.replace("background","bkg")
    tpname = tpname.replace("background","bkg")

    tpname = tnname.replace("qqZZ","qqzz")
    tpname = tpname.replace("ggZZ","ggzz")
    tpname = tpname.replace("ZX","zjets")

    tnname = tpname.replace("VBF","qqH")
    tpname = tpname.replace("VBF","qqH")
    '''
    

    
    if (has_negative or not ( "bkg" in tnname or "Data" in tnname  or "0PH" in tnname or "0PM" in tnname or "L1" in tnname or "0M" in tnname) ):
    

        if "up" in tpname or "dn" in tpname :
            tpnm = tpname.split("_")
            tpnm.insert(2,"positive")
            tpname= tpnm[0]
            for ist in range(1,len(tpnm)):
              tpname = tpname+"_"+tpnm[ist]  
              
        else :     
            tpname = tpname+"_positive"


        if "up" in tnname or "dn" in tnname :
            tnnm = tnname.split("_")
            tnnm.insert(2,"negative")
            tnname= tnnm[0]
            for ist in range(1,len(tnnm)):
              tnname = tnname+"_"+tnnm[ist]  
              
        else :     
            tnname = tnname+"_negative"



            
        temp_neg.SetName(tnname)
	temp_pos.SetName(tpname)
    else:
    
        tnname = tnname.replace("0Xff_","0Mff_")
        tpname = tpname.replace("0Xff_","0Mff_")

        #if ( not ( "0Mff" in tnname )  )  and ("ggH" in tnname or "ttH" in tnname): 

     #       print tpname
        
            #tnsplit =tnname.split("_") 
            #tpsplit =tpname.split("_")
            
            #tpname = tpsplit[0] + "_0PMff_"
            #tnname = tnsplit[0] + "_0PMff_"             
            #take care of syst by adding all the full ending 
            #for nitem in range(1,len(tpsplit)):
            #    tpname = tpname+"_"+tpsplit[nitem]
            #for nitem in range(1,len(tnsplit)):
            #    tnname = tnname+"_"+tnsplit[nitem]
            #tpname = tpname.replace("__","_")
            #tnname = tpname.replace("__","_")
                
        
        temp_neg.SetName(tnname)
        temp_pos.SetName(tpname)

    if "data" in  tnname or "Data" in tnname : 
        

        temp_neg.SetName("data_obs")
        temp_pos.SetName("data_obs")

    


    #length = length + 21


    temp_pos_arranged = TH1F("temp_pos","",length,0,length+1 ) 
    temp_neg_arranged = TH1F("temp_neg","",length,0,length+1 ) 
    iar = 0
    summ = 0

    for ibin in range(0,temp_pos.GetNbinsX()+2) : 
        
        cont = temp_pos.GetBinContent(ibin)

    
        
        if cont == -9999 : 
            continue
        else :            
            summ = summ + cont
            temp_pos_arranged.Fill(iar,cont)
            iar = iar + 1


    iar = 0 
    for ibin in range(0,temp_neg.GetNbinsX()+2) : 
        
        cont = temp_neg.GetBinContent(ibin)
        
        if cont == -9999 : 
            continue
        else : 
            temp_neg_arranged.Fill(iar,cont)
            iar = iar + 1
          

    temp_neg_arranged.SetName(temp_neg.GetName())
    temp_pos_arranged.SetName(temp_pos.GetName())

    return temp_neg_arranged,temp_pos_arranged

if __name__ == "__main__":

    fn = sys.argv[1]
    fin = TFile(fn)

    if "Un" in fn or "UN" in fn : 
        category = "Un"
    if "VH" in fn : 
        category = "VH"
    if "VBF" in fn : 
        category = "VBF"


    outname = fn.replace("../","")
    outname = outname.replace(".root","")    
    fout = TFile(outname+"Test.root","recreate")

    
    for key in fin.GetListOfKeys() : 
    
        kname  = key.GetName() 
        if "up" in kname or "dn" in kname : 
            continue
        htemp = fin.Get(kname)
        print kname,htemp.Integral()
        tneg,tpos = Unroll(htemp,category)

        print tpos.Integral(),tpos.GetName()
        print tneg.Integral(),tneg.GetName()

        fout.cd()
        tpos.Write()
    fout.Close()
