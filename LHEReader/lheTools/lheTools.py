import ROOT

class Event:
  def __init__(self,_hepeup):
    self.weight = _hepeup.XWGTUP
    self.N = _hepeup.NUP
    self.subprocessID = _hepeup.IDPRUP
    self.partonPdfWeights = _hepeup.XPDWUP
    self.pdfScale = _hepeup.SCALUP
    self.alphaQED = _hepeup.AQEDUP
    self.alphaQCP = _hepeup.AQCDUP
    self.nWeights = len(_hepeup.weights)
    self.weights = _hepeup.weights
    self.reweights_hel = None
    self.reweights_nohel = None

  def extractWeights(self,doAllWeights=False):
    w = {}
    w['nominal'] = self.weights[0][0]
    if doAllWeights:
      for iw in range(0,self.nWeights-1):
        name = "rw"+("%s"%(float(iw)/10000))[2:]
        if len(name) == 5: name += "0"
        elif len(name) == 4: name += "00"
        elif len(name) == 3: name += "000"
        elif len(name) == 2: name += "0000"
        w['%s'%name] = self.weights[iw+1][0]
    return w

  def reweight(self,_rwgtScheme,_genParticles,_alphas=0.137):
    partsRW, pdgIdsRW, helicitiesRW, statusRW = [], [], [], []
    for gp in _genParticles:
      if gp.pdgId == 25: #Incoming Higgs
        partsRW.append(gp.P4forRW)
        pdgIdsRW.append(gp.pdgId)
        helicitiesRW.append(gp.helicity)
        statusRW.append(-1)
      else:
        partsRW.append(gp.P4forRW)
        pdgIdsRW.append(gp.pdgId)
        helicitiesRW.append(gp.helicity)
        statusRW.append(1)
    weights_hel = _rwgtScheme.ComputeWeights(partsRW,pdgIdsRW,helicitiesRW,statusRW,_alphas,True,False)
    weights_nohel = _rwgtScheme.ComputeWeights(partsRW,pdgIdsRW,helicitiesRW,statusRW,_alphas,False,False)
    if weights_hel:
      self.reweights_hel = weights_hel
      self.reweights_nohel = weights_nohel
   
class Particle:
  # Constructor: takes particle
  def __init__(self,_hepeup,_ip):
    _p4 = ROOT.TLorentzVector()
    _p4.SetPxPyPzE(_hepeup.PUP[_ip][0],_hepeup.PUP[_ip][1],_hepeup.PUP[_ip][2],_hepeup.PUP[_ip][3])
    self.P4 = _p4
    self.pdgId = _hepeup.IDUP[_ip]
    self.status = _hepeup.ISTUP[_ip]
    self.helicity = _hepeup.SPINUP[_ip]
    self.mothers = _hepeup.MOTHUP[_ip]
    self.M1pdgId = _hepeup.IDUP[_hepeup.MOTHUP[_ip][0]-1] if _hepeup.MOTHUP[_ip][0]>=1 else -1
    self.M2pdgId = _hepeup.IDUP[_hepeup.MOTHUP[_ip][1]-1] if _hepeup.MOTHUP[_ip][1]>=1 else -1
    self.lifetime = _hepeup.VTIMUP[_ip]
    self.index = _ip
    self.P4forRW = [self.P4.E(),self.P4.Px(),self.P4.Py(),self.P4.Pz()]

