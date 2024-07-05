// #include "TVector.h"
#include "TFile.h"
#include "TTree.h"
#include "Math/Minimizer.h"
#include <iostream>
#include <string>
#include <utility>

// struct Hit
// {
//   double hitTime;
//   double hitSmearedTime;
//   double hit SmearingTime;
//   int hitPMT_ID;
// };




int main(int argc, char* argv[]){

  //Read the inputs
  std::string inputFilename(argv[1]);


  TFile oldFile(inputFilename.c_str(), "READ");
  TTree *tree = static_cast<TTree*>(oldFile.Get("ntuple"));

  //Set-up write-up branches
  double Time, smearedTime, smearingTime, calibration_mean, calibration_std;
  double PMT_ID, mPMT, mPMT_pmt;


  //this needs to be changed
  TBranch *Time_b = tree->Branch("Time", &Time, ("Time/D"));
  TBranch *smearingTime_b = tree->Branch(("smearingTime"), &smearingTime, ("smearingTime/D"));
  TBranch *calibration_mean_b = tree->Branch(("calibration_mean"), &calibration_mean, ("calibration_mean/D"));
  TBranch *calibration_std_b = tree->Branch(("calibration_std"), &calibration_mean, ("calibration_std/D"));
  TBranch *mPMT_b = tree->Branch(("mPMT"), &mPMT, ("mPMT/I"));
  TBranch *mPMT_pmt_b = tree->Branch(("mPMT_pmt"), &mPMT_pmt, ("mPMT_pmt/I"));



  tree->SetBranchAddress("smearedTime", &smearedTime);
  tree->SetBranchAddress("PMT_ID", &PMT_ID);


  std::vector<double> smearedTime_array;
  std::vector<int> PMT_ID_array;

  for (int i=0;i<tree->GetEntries();i++){
    tree->GetEntry(i);
    smearedTime_array.push_back(smearedTime);
    PMT_ID_array.push_back(PMT_ID);
  }


  std::vector<int> uniqueListPMT_ID  = PMT_ID_array;
  auto uniqueListPMT_ID2 = std::unique(PMT_ID_array.begin(), PMT_ID_array.end());
  // v now holds {1 2 1 3 4 5 4 x x x}, where 'x' is indeterminate
  PMT_ID_array.erase(last, PMT_ID_array.end());



  std::sort(uniqueListPMT_ID.begin(), uniqueListPMT_ID.end());

  std::cout << uniqueListPMT_ID[100000] << " " << PMT_ID_array[3] << std::endl;
  uniqueListPMT_ID_2 = std::unique(uniqueListPMT_ID.begin(), uniqueListPMT_ID.end());

  std::cout << uniqueListPMT_ID_2[100000] << " " << uniqueListPMT_ID.size() << std::endl;





//if we want to output a file
//   std::string outputFilename(argv[2]);
//   TFile newFile(outputFilename, "recreate");
//   std::cout << "Beginning cloning tree." << std::endl;
//   TTree *tree = oldTree->CloneTree();
//   std::cout << "Clone finished." << std::endl;
  return 0;
}
