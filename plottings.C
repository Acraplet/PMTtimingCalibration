#include "TCanvas.h"
#include "TROOT.h"
#include <iostream>
#include "TGraphErrors.h"
#include "TF1.h"
#include "TLegend.h"
#include "TArrow.h"
#include "TTree.h"
#include "TLatex.h"
#include "TArrayD.h"
#include "TArray.h"
#include "TMath.h"
#include <vector>
#include <string>
// #include <std>



void plottings(){
  Double_t w = 600;
  Double_t h = 600;
//   std::unique_ptr<TFile> myFile( TFile::Open("example2.root", "RECREATE") );
//   std::unique_ptr<TH1> hist(myFile->Get<TH1>("mPMT"));
  TFile f("wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits.root", "r");
  TTree* ntuple = f.Get<TTree>("ntuple;1");
  TH1* p = f.Get<TH1>("mPMT");
  p->Draw("e1same");
  f.ls();
  ntuple->ls();
  auto c = new TCanvas("c", "canvas_1", w, h);
  c->SetWindowSize(w + (w - c->GetWw()), h + (h - c->GetWh()));
  c->SetGrid();
  c->Draw();

}

int main() {
//   velocities->ReadFile("example.root", "v");

//   myFile->WriteObject(hist, "MyHist");
  plottings();
  return 0;
}
