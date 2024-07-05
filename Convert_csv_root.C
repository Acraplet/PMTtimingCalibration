#include "Riostream.h"
#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TSystem.h"

void Convert_csv_root() {

  TString dir = gSystem->UnixPathName(__FILE__);
  dir.ReplaceAll("UScsvToRoot.C","");
  dir.ReplaceAll("/./","/");

  TFile *f = new TFile("example2.root","RECREATE");
  TTree *tree = new TTree("ntuple","data from csv file");
  tree->ReadFile("example3.csv","index/I:photonID/F:mPMT/F:mPMT_pmt/F:PMT_QTot/F:PMT_x/F:PMT_y/F:PMT_z/F:Time/F:TOFTime/F:PMT_ID/F:smearingTime/F:smearedTime/F:calibration_std/F:calibration_mean/F",',');
  // ,photonID,mPMT,mPMT_pmt,PMT_QTot,PMT_x,PMT_y,PMT_z,Time,TOFTime,PMT_ID,smearingTime,smearedTime,calibration_std,calibration_mean

  f->Write();
}

int main() {
  Convert_csv_root();
  return 0;
}

