// #include "TCanvas.h"
// #include "TROOT.h"
#include <iostream>
// #include "TGraphErrors.h"
// #include "TF1.h"
// #include "TLegend.h"
// #include "TArrow.h"
// #include "TLatex.h"
// #include "TArrayD.h"
// #include "TArray.h"
// #include "TMath.h"
#include <vector>
#include <string>
#include <memory>
// #include <std>



void plottings(){
  double w = 600;
  double h = 600;
  auto c = new TCanvas("c", "canvas_1", w, h);
  c->SetWindowSize(w + (w - c->GetWw()), h + (h - c->GetWh()));
}

int main() {
//   velocities->ReadFile("example.root", "v");
  TFile* myFile( TFile::Open("example2.root", "RECREATE") );
//   myFile->ls();
//   myFile->WriteObject(hist, "MyHist");
  plottings();
  return 0;
}
