import { Injectable } from '@angular/core';
import { BehaviorSubject,Subject } from 'rxjs';
import Dynamsoft from 'dwt';
import { WebTwain } from 'dwt/dist/types/WebTwain';
import Swal from 'sweetalert2/dist/sweetalert2.js';
import { HttpClient } from '@angular/common/http';
import { ApiUrls, Doctypes } from '../api-urls';
import moment from 'moment';
import { ToastrService } from 'ngx-toastr';
import { environment } from 'src/environments/environment';

@Injectable({
    providedIn: 'root'
})

export class FiScannerService {

    scannerContainerId = new BehaviorSubject<any>(null);
    scannedFileUploadedRes = new BehaviorSubject<any>(null);
    scannerList = new BehaviorSubject<any>(null)
    public runningEnvironment = Dynamsoft.Lib.env;
    public bWASM: boolean = true;
    bufferSubject: Subject<string> = new Subject<string>();
    public bUseCameraViaDirectShow: boolean = false;
    public env=environment.production
    public bUseService = false;

    DWObject!: WebTwain;
    DWObjectEx: WebTwain = null;
    devices=[]

    containerId = "dwtcontrolContainer";
    // productKey = "t01529gIAAFxKlPfKOmjNkqDfvJtwI1s6PxKepHTnz/GswrqQ+Z7yPf8RKdXI6efd7fVKKHDBzHaxVAdS6+TFU7EzA6C5OtFtSGvDSAwWF7pXsqEFwxu4O5ABEIscgd/yBR7yPs0qBMAVkAJ4N36A85CfXnESMgKugBTgPGQASSfVflN7CmgdISkFXAEpwAgZwGxPY+36Avbilsk="
    productKey = "t01529gIAAKJkJ7NE09gGSCFgBPt9loCdjfWTUQw5J8LIA1LCRHboDI5iKHohQFdrJqlAdbgOdUyHwlRUQ6lL/EBrAhzNDHpzQy03jMDAhmh7p76JM/wGjwF0AvgmZzBe+QJPPapRBwc4A5qAMY0f4DrkZ1YchPSAM6AJuA7pQDDJ1r9JNgWtMySFgDOgCZghHailwMzwAu5jlhM=";
    public scanOptions:any = {
        IfShowUI: false,
        PixelType: "2",// "color"
        Resolution: 200,
        IfFeederEnabled: false,
        IfDuplexEnabled: false,
        IfDisableSourceAfterAcquire: true,
        IfGetImageInfo: true,
        IfGetExtImageInfo: true,
        IfShowFileDialog: false,
        extendedImageInfoQueryLevel: 0,
        IfAutomaticDeskew: true,

        continuousScan: {   //Only applicable to video scanning.
          visibility: true,   //Whether to display the continuous scan icon. The default value is true.
          enableContinuousScan: true,  //Whether to enable continuous scan. The default value is true.
        },
        funcConfirmExitContinuousScan: true,
        //funcConfirmExitContinuousScan is the callback funtion
        //Return true：Exit continuous scan mode without saving the captured image data. Return false: Stay on the original viewer
        funcConfirmExit: true,
        // moreSettings:{
        //   autoDeskew:true
        // }

      };

    constructor(
        private http: HttpClient,
        private toastr : ToastrService
    ){

    }

    setScannerContainerId(data:any){
        this.scannerContainerId.next(data);
    }

    getScannerContainerId(){
        return this.scannerContainerId.asObservable();
    }

    dynamSoftOnload(flag=false, id,date=null) {
        this.containerId = id;
        Dynamsoft.DWT.Containers = [{
          WebTwainId: 'dwtObject',
          ContainerId: id,
          Width: '470px',
          Height: '250px',
        }];
        console.log("Scanner service")

        Dynamsoft.DWT.OnWebTwainReady = () => {
          this.DWObject = Dynamsoft.DWT.GetWebTwain(id);
        }
        Dynamsoft.DWT.ProductKey = this.productKey;
        Dynamsoft.DWT.ResourcesPath = 'assets/dwt-resources';
        Dynamsoft.DWT.Load();

        if(flag){
          this.acquireImage('scan',null,date)
        }

     }


    //  mountDWT(UseService?: boolean): Promise<any> {
    //   this.DWObject = null;
    //   return new Promise((res, rej) => {
    //     let dwtInitialConfig: DWTInitialConfig = {
    //       WebTwainId: "dwtObject"
    //     };
    //     /**
    //      * [Why checkScript()?]
    //      * Dynamic Web TWAIN relies on a few extra scripts to work correct.
    //      * Therefore we must make sure these files are ready before creating a WebTwain instance.
    //      */
    //     let checkScript = () => {
    //       if (Dynamsoft.Lib.detect.scriptLoaded) {
    //         /*  Dynamsoft.DWT.OnWebTwainPreExecute = () => {
    //             // Show your own progress indicator
    //             console.log('An operation starts!');
    //           };
    //           Dynamsoft.DWT.OnWebTwainPostExecute = () => {
    //             // Hide the progress indicator
    //             console.log('An operation ends!');
    //           };
    //           */
    //         if (this.runningEnvironment.bMobile) {
    //           Dynamsoft.DWT.UseLocalService = true;
    //         } else {
    //           if (UseService !== undefined)
    //             Dynamsoft.DWT.UseLocalService = UseService;
    //           else {
    //             Dynamsoft.DWT.UseLocalService = this.bUseService;
    //           }
    //         }
    //         this.bWASM = this.runningEnvironment.bMobile || !Dynamsoft.DWT.UseLocalService;

    //         Dynamsoft.DWT.CreateDWTObjectEx(
    //           dwtInitialConfig,
    //           (DWObject) => {
    //             this.DWObject = DWObject;
    //             /*this.DWObject.IfShowProgressBar = false;
    //             this.DWObject.IfShowCancelDialogWhenImageTransfer = false;*/
    //             /**
    //              * The event OnBitmapChanged is used here for monitoring the image buffer.
    //              */
    //             this.DWObject.RegisterEvent("OnBitmapChanged", (changedIndexArray, operationType, changedIndex, imagesCount) => {
    //               switch (operationType) {
    //                 /** reserved space
    //                  * type: 1-Append(after index), 2-Insert(before index), 3-Remove, 4-Edit(Replace), 5-Index Change
    //                  */
    //                 case 1: break;
    //                 case 2: break;
    //                 case 3: break;
    //                 case 4: break;
    //                 case 5: break;
    //                 default: break;
    //               }
    //               this.bufferSubject.next("changed");
    //               if (this.DWObject.HowManyImagesInBuffer === 0)
    //                 this.bufferSubject.next("empty");
    //               else
    //                 this.bufferSubject.next("filled");
    //             });
    //             res(DWObject);
    //           },
    //           (errorString) => {
    //             rej(errorString);
    //           }
    //         );
    //       } else {
    //         setTimeout(() => checkScript(), 100);
    //       }
    //     };
    //     checkScript();
    //   });
    // }


      acquireImage(type, next,date) {

       let scannerList:any =[];
        return new Promise((res, rej) => {
          if (this.DWObject) {

            let sources:any =[]
            this.getDevices();
            sources = this.devices;

            console.log(sources)
            // if(sources?.length){

            //   // scannerList = sources.filter(ele => ele?.Manufacturer == "FUJITSU")
            //   // console.log(scannerList)
            // //  let  scannerIndex = sources.findIndex(ele => ele?.Manufacturer == "FUJITSU")

            //  this.scanOptions.SelectSourceByIndex = sources.findIndex(ele => ele?.Manufacturer == "FUJITSU")
            //  console.log(this.scanOptions.SelectSourceByIndex)
            // }else{
            //   this.toastr.error(" Scanner is not found")
            // }

            this.scanOptions.SelectSourceByIndex = sources?.length? sources.findIndex(ele => ele?.Manufacturer == "FUJITSU") : this.toastr.error("Supporting Scanner is not found")


            if(sources?.length){

              this.DWObject.AcquireImage(this.scanOptions, async () => {
                this.DWObject.SelectAllImages();
                let selectedIndices = this.DWObject.SelectedImagesIndices;
                if(selectedIndices){
                this.toastr.info("Scan Completed Processing the documents..")
                }
                selectedIndices.map( async (each:any,index)=>{
                  let arr = [each]
                  await this.uploadThroughAJAX(arr,4,date)
                })

                res(true);
              }, (errCode, errString) => {
                console.log(errString, errCode)
                Swal.fire({
                  title: "Connection Error",
                  text: "Please check the scanner connection",
                  type: 'warning',
                  showConfirmButton: true,
                  confirmButtonText: 'OK',
                  showCancelButton: true,
                  icon: "warning",
                  dangerMode: true,
                }).then((test:any)=>{
                  if(test.isConfirmed){
                    // this.dynamSoftOnload(true,this.containerId,date)
                  }
                })
                //
                rej(errString);
              });
            }




          }

        })

      }

      uploadThroughAJAX(indices, type, date) {
        this.DWObject.ConvertToBlob(
          indices,
          type,
          (result, _indices) => {
            // var url = ApiUrls.uploadFile;

           let data = new Date().toISOString().replace(/[\-\.\:ZT]/g,"");
           let dateFormat = moment(date).format('YYYY-MM-DD')
           let fileName = "pos-@"+dateFormat+"@"+data+"dwt.pdf"
          //  var fileName = "SampleFile" +  ".pdf";
            var formData = new FormData();
            formData.append('file', result, fileName);
            formData.append('is_private', '1');
            formData.append('folder', 'Home');
            // formData.append('doctype', Doctypes.posChecks);
            // this.makeRequest(url, formData, false);
            this.http.post(ApiUrls.uploadFile,formData).subscribe((res:any)=>{
              if(res){
                this.DWObject.RemoveImage(indices);
                this.scannedFileUploadedRes.next(res);

              }
            })
          },
          (errorCode, errorString) => {
            console.log(errorString);
          }
        );
      }

      getDevices(){
        return new Promise((res, rej) => {
          let _dwt = this.DWObject;

          if (this.DWObjectEx)
            _dwt = this.DWObjectEx;
          let count = this.DWObject?.SourceCount;
          let _scanners = <string[]>(this.DWObject.GetSourceNames(true));
          this.devices = _scanners
          if (count !== _scanners?.length) {
            rej('Possible wrong source count!');//not likely to happen
          }

          // if (this.bUseCameraViaDirectShow) {
          //   try {
          //     let _cameras = _dwt.Addon.Webcam.GetSourceList();
          //     for (let i = 0; i < _cameras.length; i++) {
          //       this.devices.push({ deviceId: Math.floor(Math.random() * 100000).toString(), name: (i + 1).toString() + "." + _cameras[i], label: _cameras[i], type: "camera" });
          //     }
          //     res(devices);
          //   } catch (e) {
          //     if(bfromCamera)
          //       rej(e);
          //     else {
          //       if(e.code == -2338)
          //         res(devices);
          //       else
          //         rej(e);
          //     }
          //   }

          // } else {
          //   _dwt.Addon.Camera.getSourceList()
          //     .then(_cameras => {
          //       for (let i = 0; i < _cameras.length; i++) {
          //         this.devices.push({ deviceId: _cameras[i].deviceId, name: (i + 1).toString() + "." + _cameras[i].label, label: _cameras[i].label, type: "camera" });
          //       }
          //       res(this.devices);
          //     }, err => {
          //       if(bfromCamera)
          //         rej(err);
          //       else {
          //         if(err.code == -2338)
          //           res(this.devices);
          //         else
          //           rej(err);
          //       }
          //     });
          // }
        });
      }

 }
