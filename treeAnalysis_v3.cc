// #include <TTree.h>
#include "TTree.h"
#include "TFile.h"
#include "TRandom.h"
#include "TH1.h"
#include "TCanvas.h"
#include "TH1F.h"
#include "TTreeFormula.h"
// #include "gstyle.h"
#include <set>
#include <iostream>
#include <stdio.h>
 
Int_t Run, Event;
Float_t x,y,z;
 
TTree* CreateTree(const char* name) {
   // simple TTree
   TFile *f = new TFile(name, "read");
   TTree* T = (TTree*) f->Get("ntuple");
//    T->Print();
//    delete f;
   return T;
}

void VerifyCalibration(TTree* T) {
   Double_t smearingTime, calibration_mean;
   T->SetBranchAddress("smearingTime", &smearingTime);
   T->SetBranchAddress("calibration_mean", &calibration_mean);
   
   TH1F* h1 = new TH1F("h1", "Smearing offset", 100,  -1000, 1000);
   TH1F* h2 = new TH1F("h2", "Calibration value", 100, -1000, 1000);
   TH1F* h3 = new TH1F("h3", "Smearing offset - calibration value", 100, -4.5, -3.95);
   
   Int_t nentries = T->GetEntries();
   for (Long64_t i=0;i<nentries;i++) {
       T->GetEntry(i);
       h1->Fill(smearingTime);
       h2->Fill(calibration_mean);
       h3->Fill(smearingTime-calibration_mean);
   }
   TCanvas *c1 = new TCanvas("c1", "Canvas on which to display our histogram", 800, 400);
//    gStyle->SetOptTitle(1);
   c1->SetTitle("Smearing and calibration 1k photons");
//    TLatex *lat = new TLatex();
//    lat->DrawLatexNDC(0,0.95,"My Title");
   //can use the legend.DrawClone("same")
   //for the 
   c1->Divide(2,2);
   c1->cd(1);
   h1->Draw();
   h1->Draw("e0same");
   h1->SetLineColor(2);
   c1->cd(2);
   h2->Draw();
   h2->Draw("e0same");
   h2->SetLineColor(4);
   c1->cd(3);
//    c1[3].SetTitle("");
   h2->SetTitle("Comparision");
   h2->Draw();
   h1->Draw("same");
   h1->SetLineColor(2);
   h2->SetLineColor(4);


//    T->Draw("calibration_mean:smearingTime");


   c1->cd(4);
   h3->Draw("e0");
   h3->Draw("same");
   h3->Fit("gaus", "LEM");
//    gStyle->SetOptFit(1111);
   TF1 *fit = h3->GetFunction("gaus");
//    Double_t chi2 = fit->GetChisquare();

//    delete c1, h1, h2, h3;
}

void LookAtSinglePMT(TTree* T) {

  Double_t PMT_ID, smearedTime, calibration_mean;
//     T->SetBranchAddress("PMT_ID", &PMT_ID);
//     T->Branch("PMT_ID", &PMT_ID, "PMT_ID/F");
    T->SetBranchAddress("smearedTime", &smearedTime);
    T->SetBranchAddress("calibration_mean", &calibration_mean);


//     TBranch pmt_id = TBranch(T, "pmt_id", &PMT_ID, "PMT_ID");



    //This part creates a set with all unique values contained
    //within the PMT_ID branch to then perform the required selection
    TTreeFormula form("form","1",T);
    std::set<int> s;
    for(long long x = 0; x < T->GetEntries(); ++x) {
        T->LoadTree(x);
        s.insert(form.EvalInstance(0));
    }

    TBranch *bpmt = 0;
    T->SetBranchAddress("PMT_ID",&PMT_ID,&bpmt);
    for(long long x = 0; x < T->GetEntries(); ++x) {
      bpmt->GetEntry(x);
      s.insert( (int)PMT_ID );
    }
    std::cout << s.count(394) << ", " << s.size() << ".\n";

//     int n = 30;
    std::set<int>::iterator it = s.begin();
    std::advance(it, 1);
    int x = *it;


    std::cout << x;



//     std::cout << s << std::endl;
    
//     std::cout << pmt_id.GetListOfLeaves();
    //plan:
    // Run through the hit and place them
    //in sub-categories according to their 
    //PMT_ID value. Then with these sub-group
    //perform fitting with log-likelihood method
    //compare with python results
//     T->Scan("PMT_ID");
    TCanvas *c1 = new TCanvas("c1", "Canvas on which to display our histogram", 800, 400);

    TH1F* h1 = new TH1F("h1", "h1 title", 100,  -1000, 1000);

//     T->Draw("PMT_ID>>h1");
//     T->Draw("smearedTime","PMT_ID == 2458");
//     TBranch b1 = T->Branch("smearedTime","PMT_ID == 415");
//     for (Int_t i=0;i<200;i++) {
//       //need to work out how to make i shift... looking good otherwise
//       T->Draw(">>mylist","PMT_ID > " i, "entrylist");
//       TEntryList *list=(TEntryList*)gDirectory->Get("mylist");
//       T->SetEntryList(list);
//       T->Draw("smearedTime>>h1");
//       h1->Fit("gaus");
//
//     }


//     T->Draw(">>mylist","PMT_ID > 600", "entrylist");
//     TEntryList *list=(TEntryList*)gDirectory->Get("mylist");
//     T->SetEntryList(list);
//     T->Draw("smearedTime>>h1");
//     h1->Fit("gaus");


//     list->Print();



//     Int_t nentries = T->GetEntries();
//     TArrayD ListPMT_ID = TArrayD();
    
//     for (Long64_t i=0;i<nentries;i++) {
//        T->GetEntry(i);
//        //ListPMT_ID->GetEntries()
//        
//        for (Int_t j=0;j<25;j++) {
//            Double_t check = (Double_t) ListPMT_ID[j];
//            if (check == PMT_ID) {
//                std::cout << PMT_ID<<std::endl;
//                break;
//            }
//            ListPMT_ID.Set(ListPMT_ID.GetEntries()+1)
//            ListPMT_ID.AddAt(PMT_ID);
//        }
//        std::cout << PMT_ID <<std::endl;
       
//    }
    
}



void CompareTrees(TTree* T_ini, TTree* T) {
//    The two TTrees created above are compared.
//    The subset of entries in the small TTree must be identical
//    to the entries in the original TTree.
   
   Double_t Time, Time_ini;
   T->Print();
   T->SetBranchAddress("Time", &Time);
   
   T_ini->SetBranchAddress("Time", &Time_ini);
   

   TH1F* h1 = new TH1F("h1", "h1 title", 100,  940, 965);
   TH1F* h2 = new TH1F("h2", "h2 title", 100, 940, 965);
   
  //this works if we only want to see the data but 
   //for anylysis we need to properly fill the hist
//    T->Draw("Time>>h1");
//    T_ini->Draw("Time_ini>>h2");
   Int_t nentries = T->GetEntries();
   for (Long64_t i=0;i<nentries;i++) {
       T->GetEntry(i);
       h1->Fill(Time);
       T_ini->GetEntry(i);
       h2->Fill(Time_ini);
   }
    TCanvas *c1 = new TCanvas("c1", "Canvas on which to display our histogram", 800, 400);

   c1->cd(0);
   h1->Draw();
   h2->Draw("same");
//    h2->Fit("gaus");
//    delete c1, h1, h2;
}
 

int main() {
    const char* name_ini = "wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits.root";
    const char* name_1 = "wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits_cal300.root";
    
    TTree* calibrated = (TTree*) CreateTree(name_1);
    TTree* initial = (TTree*) CreateTree(name_ini);
//     TFile *f = new TFile(name_ini, "read");
//     TTree* calibrated = (TTree*) f->Get("ntuple");
    
//     TFile *f2 = new TFile(name_1, "read");
//     TTree* initial = (TTree*) f2->Get("ntuple");
    
//     calibrated->Print("Time");
//     initial->Print("Time");

    CompareTrees(initial, calibrated);
//     VerifyCalibration(calibrated);
//     LookAtSinglePMT(calibrated);
    return 0;
}
