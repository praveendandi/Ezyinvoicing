import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { NgbActiveModal } from '@ng-bootstrap/ng-bootstrap';
import { ApiUrls, Doctypes } from '../../api-urls';
import { LocalStorageService, Storekeys } from '../../services/local-storage.service';

@Component({
  selector: 'app-upload-excel-file',
  templateUrl: './upload-excel-file.component.html',
  styleUrls: ['./upload-excel-file.component.scss']
})
export class UploadExcelFileComponent implements OnInit {

  filename: any
  fileToUpload: any
  loginDetails:any = {}
  companyDetails:any = {}
  dupThValues: any = []
  tableArrs: any = {
    thValues: [],
    gstr2XcelTableHeadings: [],
    gstr2XcelList: [],
    mappedArr: []
  }
  xcelModal = {
    uploadedFileData: false,
    mappedBtn: false,
    uploadedFilepath: '',
    showMappedBtnTh: false
  }
  constructor(
    private activeModal : NgbActiveModal,
    private http : HttpClient,
    private storageService : LocalStorageService
  ) { }

  ngOnInit(): void {
    this.loginDetails = JSON.parse(this.storageService.getRawValue(Storekeys.LOGIN)|| '')
    if(this.loginDetails?.company){
      this.getCompanyDetails();
    }
  }


  handleFileInput(e: any) {
    this.filename = e.target.files[0].name;
    this.fileToUpload = e.target.files[0];
  }

  uploadService() {
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      formData.append('doctype', Doctypes.gstr2a);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message?.file_url) {
          this.xcelModal.uploadedFilepath = res.message?.file_url;
          this.xcelModal.uploadedFileData = true
          this.http.post(`${ApiUrls.gstr2Excel}`, {
            data: {
              file_path: res.message?.file_url,
              company: this.loginDetails.company
            }
          }).subscribe((resXcel: any) => {
            if (resXcel.message.success) {
              this.xcelModal.mappedBtn = true;
              this.tableArrs.gstr2XcelList = resXcel.message.data;
              let headings = Object.keys(resXcel.message.data[0])
              headings.map((each: any, index: any) => {
                if (each) {
                  this.tableArrs.gstr2XcelTableHeadings.push({ "value": each, "id": index, "selected": false, mappedHead: '' });
                }
              })

              if (this.companyDetails?.mapping_fields !== "" && this.tableArrs.gstr2XcelTableHeadings.length > 0) {
                this.xcelModal.showMappedBtnTh = true
                let companyheadingList: any = JSON.parse(this.companyDetails?.mapping_fields)
                this.tableArrs.gstr2XcelTableHeadings.forEach((item: any) => {
                  companyheadingList.forEach((each: any) => {
                    if (item.value == Object.values(each)[0]) {
                      item.mappedHead = Object.values(each)[1]
                    }
                  })
                  return item;
                })

                this.tableArrs.thValues.forEach((item: any) => {
                  companyheadingList.forEach((each: any) => {
                    if (item.label == Object.values(each)[1]) {
                      item.selected = true
                    }
                  })
                  return item;
                })
                this.tableArrs.thValues = this.tableArrs.thValues.filter((res: any) => !res.selected)

              }
            }
          })
        } else {
          console.log(res)
        }
      })
    }
  }

  selectedITem(each: any, staticTh: any, id: any) {
    console.log(each, id, staticTh)
    each.selected = !each.selected;

    if (staticTh.mappedHead != '') {
      this.tableArrs.thValues.map((item: any) => {
        if (item.label == staticTh.mappedHead) {
          item.selected = false;
        }
        return item;
      })
      this.tableArrs.mappedArr.splice(this.tableArrs.mappedArr.findIndex((res: any) => res.mappedTh == staticTh.mappedHead), 1);
    }
    //  this.tableArrs.thValues = this.tableArrs.thValues.filter((res: any) => !res.selected)
    console.log("====== th  ", this.tableArrs.thValues)
    this.tableArrs.gstr2XcelTableHeadings = this.tableArrs.gstr2XcelTableHeadings.map((heading: any) => {
      if (heading.id === id) {
        heading.mappedHead = each.label
      }
      return heading
    })
    let obj: any = {}
    obj[each.fieldname] = staticTh.value;
    obj['mappedTh'] = each.label;
    this.tableArrs.mappedArr.push(obj)
    console.log("......mappedArr=====", this.tableArrs.mappedArr)
  }

  submitMappedData() {
    this.http.post(`${ApiUrls.gstr2AMapped}`, {
      data: { file_path: this.xcelModal.uploadedFilepath, company: this.loginDetails.company, mapping_fields: this.tableArrs.mappedArr }
    }).subscribe((res: any) => {
      if (res.message.success) {
        this.tableArrs = {
          gstr2XcelTableHeadings: [],
          gstr2XcelList: [],
          mappedArr: []
        }
        this.getCompanyDetails();
        // this.getGstr2ATheads();
        this.activeModal.close();
      }
    })
  }

  getCompanyDetails() {
    this.http.get(`${ApiUrls.resource}${Doctypes.company}/${this.loginDetails?.company}`).subscribe((res: any) => {
      if (res.data) {
        this.companyDetails = res.data;
        this.getGstr2ATheads();
      }
    })
  }
  getGstr2ATheads() {
    this.http.get(`${ApiUrls.gstr2ATheads}`).subscribe((res: any) => {
      if (res?.message?.fields) {
        this.tableArrs.thValues = res?.message?.fields;
        this.tableArrs.thValues.map((each: any) => {
          if (each) {
            each['selected'] = false;
          }
        })
      }
    })
  }
  resetbtn() {
    this.xcelModal.showMappedBtnTh = false;
    this.tableArrs.gstr2XcelTableHeadings.map((res: any) => res.mappedHead = "")
    this.tableArrs.thValues = this.tableArrs.thValues.map((res: any) => res.selected = false)
  }

  modalCancel(type: any) {
    this.tableArrs.gstr2XcelTableHeadings = []; this.tableArrs.gstr2XcelList = []; this.tableArrs.mappedArr = [];
    if (this.tableArrs.thValues.length > 0) {
      this.tableArrs.thValues.map((res: any) => {
        if (res?.selected) {
          res.selected = false
        }
      })
    }
    this.activeModal.close()
  }
  close(){
    this.activeModal.close()
  }

}
