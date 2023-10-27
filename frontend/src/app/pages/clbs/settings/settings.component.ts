import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, OnInit } from '@angular/core';
import { NgForm } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { ToastrService } from 'ngx-toastr';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';
import { environment } from 'src/environments/environment';


class EventsFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  search = '';

}
class DocumentTypeFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 0;
  start = 0;
  search = '';
}
@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent implements OnInit {
  active=1
  companyDetails: any = {};
  bankDetails: any = {};
  clbsSettings: any = {}
  checkThreshold = true;
  filename;
  fileToUpload;
  fileError = false;
  fileTypes: any;
  sequenceOptions: any=[];
  options
  filters = new EventsFilter()
  onSearch = new EventEmitter()
  filters_doc_types = new DocumentTypeFilter()
  eventsList = [];
  eventInfo:any = {}
  documentTypeList = [];
  documentTypeInfo:any = {}
  loginUser: any;
  save_doc_type_seq = false;
  constructor(
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    private toaster: ToastrService,
    private modal: NgbModal
  ) { }

  ngOnInit(): void {
    this.loginUser = JSON.parse(localStorage.getItem('login'))
    this.companyDetails = JSON.parse(localStorage.getItem('company'));

    this.onSearch.pipe(debounceTime(500)).subscribe((res) => {
      if (res) {
        this.filters.start = 0;
        this.filters.totalCount = 0;
        this.updateRouterParams()
      }
    });
    this.activatedRoute.queryParams.subscribe((res: any) => {
      if (res) {
        this.filters.search = res.search;
      }
    })
    this.getEventsList();
    this.getDocumentList();

    this.getClbsSettings();
    this.get_bank_details();
    this.getDocumentTypeList()
  }

  updateRouterParams(): void {
    this.router.navigate(['clbs/clbs-settings'], {
      queryParams: this.filters
    });
  }

  get_bank_details() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.bankDetails}`, {
      params: {
        filters: JSON.stringify([['company', '=', this.companyDetails?.name]]),
        fields: JSON.stringify(['*'])
      }
    }).subscribe((res: any) => {
      if (res?.data.length) {
        this.bankDetails = res.data[0];
      }
    })
  }

  save_bank_details(bankDetailsForm:NgForm) {
    if(bankDetailsForm.valid){
      if(this.bankDetails?.name){
        this.http.put(`${ApiUrls.resource}/${Doctypes.bankDetails}/${this.bankDetails?.name}`, {
          data: this.bankDetails
        }).subscribe((res: any) => {
          if (res?.data) {
            this.toaster.success("Updated")
            this.bankDetails = res.data;
          }
        })
      }else{
        this.http.post(`${ApiUrls.resource}/${Doctypes.bankDetails}`, {
          data: {...bankDetailsForm.value,company:this.companyDetails.name}
        }).subscribe((res: any) => {
          if (res?.data) {
            this.toaster.success("Updated")
            this.bankDetails = res.data;
          }
        })
      }
    }else{
      this.toaster.error("Invalid Form")
    }


  }

  getClbsSettings() {
    this.http.get(`${ApiUrls.clbsSettings}`).subscribe((res: any) => {
      if (res?.data[0]) {
        this.http.get(`${ApiUrls.clbsSettings}/${res?.data[0]?.name}`).subscribe((each: any) => {
          if (each) {
            this.clbsSettings = each?.data;
            this.setSequenceValues()
          }
        })
      }
    })
  }

  save_qr_details(generalDetailsForm:NgForm) {
    if(generalDetailsForm.invalid){
      return;
      generalDetailsForm.touched;
    }
    if (this.checkThreshold) {
      if (this.clbsSettings?.name) {
        this.http.put(`${ApiUrls.clbsSettings}/${this.clbsSettings?.name}`, { data: this.clbsSettings }).subscribe((res: any) => {
          if (res?.data) {
            this.toaster.success("Updated")
            this.clbsSettings = res.data;
          }
        })
      } else {

        this.http.post(`${ApiUrls.clbsSettings}`, { data: {...generalDetailsForm.value,company:this.companyDetails.name} }).subscribe((res: any) => {
          if (res?.data) {
            this.toaster.success("Success")
            this.clbsSettings = res.data;
          }
        })
      }
    } else {

    }
  }

  onChangeThreshold(e) {
    if (e < 20) {
      this.checkThreshold = true;
    } else {
      this.checkThreshold = false;
    }
  }

  handleFileInput(files: File[], field_name) {
    this.filename = files[0].name;
    this.fileToUpload = files[0];
    if(files[0].type == 'text/plain'){
      this.fileError = false;
    if (this.fileToUpload) {
      const formData = new FormData();
      formData.append('file', this.fileToUpload, this.fileToUpload.name);
      formData.append('is_private', '1');
      formData.append('folder', 'Home');
      formData.append('doctype', this.clbsSettings.doctype);
      formData.append('fieldname', field_name);
      formData.append('docname', this.clbsSettings.company);
      this.http.post(ApiUrls.uploadFile, formData).subscribe((res: any) => {
        if (res.message.file_url) {
          if (field_name === 'document_sequence') {
            this.clbsSettings['document_sequence'] = res.message.file_url
            const formData = new FormData();
            formData.append('doc', JSON.stringify(this.clbsSettings));
            formData.append('action', 'Save')
            this.http.post(ApiUrls.fileSave, formData).subscribe((res: any) => {

              this.toaster.success('Document Saved');
              this.getClbsSettings();
            });
          }
        }
      })
    }
  }else{
    this.fileError = true;
  }
  }

  downloadFile(file){
    let url = environment.apiDomain + file
    window.open(url,'_blank');
  }

  getDocumentTypeList() {
    this.http.get(`${ApiUrls.resource}/${Doctypes.documentTypes}`, {
      params: {
        fields: JSON.stringify(['*']),
        limit_page_length: 'None'
      }
    }).subscribe((res: any) => {
      if (res?.data) {
        this.fileTypes = res?.data;
        console.log('====', this.fileTypes)
        let data ={
          name:'POS Checks',
          document_type : 'POS Checks',
          sequence_no:''
        }
        this.fileTypes.push(data)
        this.addSequenceOptions()
      }
    })
  }
  changeSequence(){
    // this.fileTypes.filter((res:any)=>{
    //   console.log(item)
    //   console.log(res)
    //  console.log(res?.sequence.indexOf(item.sequence_no))

    // })
    // for (const [key, value] of Object.entries()) {
    //   console.log(`${key}: ${value}`);
    // }
    // console.log(this.fileTypes?.sequence.indexOf(item.sequence_no))
  }
  addSequenceOptions(){
    this.fileTypes.filter((res:any)=>{
      res['sequence_no']=''
      res['sequence'] =Array.from({length: this.fileTypes.length}, (v, k) => k+3);
    })
    this.setSequenceValues()
  }
  saveSignatureDetails(form:NgForm){
    if(form.invalid){
      form.form.markAllAsTouched()
      return
    }
    this.save()
  }
  save(){

    let data ={
      summary:1,
      e_tax:2,
    }

    let objData = {};
    this.fileTypes.filter((res:any)=>{
      objData = {
        [res.document_type]: parseInt(res.sequence_no)
    };

    data = {...data,...objData}
    })
    this.clbsSettings.document_sequence = JSON.stringify(data)
    for (const [key, value] of Object.entries(data)) {
      for (const [key1, value1] of Object.entries(data)) {
        if(key != key1 && value == value1){
          this.toaster.error("Sequence should be unique")
          return;
        }

      }
    }
    if (this.checkThreshold) {
      if (this.clbsSettings?.name) {
        this.http.put(`${ApiUrls.clbsSettings}/${this.clbsSettings?.name}`, { data: this.clbsSettings }).subscribe((res: any) => {
          if (res?.data) {
            this.toaster.success("Updated")
            this.clbsSettings = res.data;
            console.log(this.clbsSettings)
            this.setSequenceValues()
          }
        })
      } else {

        this.http.post(`${ApiUrls.clbsSettings}`, { data: this.clbsSettings }).subscribe((res: any) => {
          if (res?.data) {
            this.toaster.success("Success")
            this.clbsSettings = res.data;
            console.log(this.clbsSettings)
            this.setSequenceValues()
          }
        })
      }
    } else {

    }
  }
  setSequenceValues(){
    if(this.clbsSettings?.document_sequence){
      let sequenceDat = JSON.parse(this.clbsSettings?.document_sequence)

      this.fileTypes.filter((res:any)=>{
        res['sequence_no'] = sequenceDat[res.document_type];
      })
    }

  }


  /**********Events */
  getEventsList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: EventsFilter) => {
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = (this.filters.currentPage - 1) * this.filters.itemsPerPage;
      queryParams.limit_page_length = this.filters.itemsPerPage;
      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters?.search}%`]);
      }
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.fields = JSON.stringify(['*']);
      queryParams.order_by = "`tabEvents`.`creation` desc";
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.events}`, {
        params: {
          fields: JSON.stringify(["count( `tabEvents`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.events}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters.currentPage == 1) {
        this.eventsList = [];
      }
      const [count, data] = res;
      this.filters.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.eventsList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters.currentPage !== 1) {
          this.eventsList = this.eventsList.concat(data.data)
        } else {
          this.eventsList = data.data;
        }

      }
    });
  }

  checkPagination(items: number): void {
    this.filters.itemsPerPage = items;
    this.filters.currentPage = 1
    this.updateRouterParams()
  }

  eventModalFunc(event, each){
    this.eventInfo = {...each};
    let modal = this.modal.open(event,{size:'md',centered:true})
  }

  eventFormAdd(form:NgForm,modal){
    this.http.post(`${ApiUrls.resource}/${Doctypes.events}`,{data:form.value}).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getEventsList()
      }
    })
  }

  eventFormEdit(form:NgForm,modal){
    this.http.put(`${ApiUrls.resource}/${Doctypes.events}/${this.eventInfo.name}`,form.value).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getEventsList()
      }
    })
  }
  /************Events end */

  /*********Document Types  */
  getDocumentList() {
    this.activatedRoute.queryParams.pipe(switchMap((params: DocumentTypeFilter) => {
      this.filters_doc_types.search = params.search || this.filters_doc_types.search;
      const queryParams: any = { filters: [] };
      queryParams.limit_start = (this.filters_doc_types.currentPage - 1) * this.filters_doc_types.itemsPerPage;
      queryParams.limit_page_length = this.filters_doc_types.itemsPerPage;
      if (this.filters_doc_types.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters_doc_types?.search}%`]);
      }
      queryParams.filters = JSON.stringify(queryParams.filters);
      queryParams.fields = JSON.stringify(['*']);
      // queryParams.order_by = "`tabDocument Types`.`sequence` asc";
      const countApi = this.http.get(`${ApiUrls.resource}/${Doctypes.documentTypes}`, {
        params: {
          fields: JSON.stringify(["count( `tabDocument Types`.`name`) AS total_count"]),
          filters: queryParams.filters
        }
      });
      const resultApi = this.http.get(`${ApiUrls.resource}/${Doctypes.documentTypes}`, { params: queryParams });
      return forkJoin([countApi, resultApi]);
    })).subscribe((res: any) => {
      if (this.filters_doc_types.currentPage == 1) {
        this.documentTypeList = [];
      }
      const [count, data] = res;
      this.filters_doc_types.totalCount = count.data[0].total_count;
      data.data = data.data.map((each: any, index) => {
        if (each) {
          each.index = this.documentTypeList.length + index + 1;
        }
        return each;
      })
      if (data.data) {
        if (this.filters_doc_types.currentPage !== 1) {
          this.documentTypeList = this.documentTypeList.concat(data.data)
        } else {
          this.documentTypeList = data.data;
        }

      }
    });
  }

  checkPaginationDocType(items: number): void {
    this.filters_doc_types.itemsPerPage = items;
    this.filters_doc_types.currentPage = 1
    this.updateRouterParamsDocType()
  }

  docTypeModalFunc(event, each){
    this.documentTypeInfo = {...each};
    let modal = this.modal.open(event,{size:'md',centered:true})
  }

  docTypeFormAdd(form:NgForm,modal){
    this.http.post(`${ApiUrls.resource}/${Doctypes.documentTypes}`,{data:form.value}).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getDocumentList()
      }
    })
  }

  docTypeFormEdit(form:NgForm,modal){
    this.http.put(`${ApiUrls.resource}/${Doctypes.documentTypes}/${this.documentTypeInfo.name}`,form.value).subscribe((res:any)=>{
      if(res?.data){
        modal.close();
        this.getDocumentList()
      }
    })
  }

  updateRouterParamsDocType(): void {
    this.router.navigate(['clbs/clbs-settings'], {
      queryParams: this.filters_doc_types
    });
  }
  /**************** Document Types Ends */
  // deleteDocType(item){
  //  console.log(item)
  //  this.http.put(`${ApiUrls.resource}/${Doctypes.documentTypes}/${item?.name}`, { doc_delete_status: item.doc_delete_status }).subscribe((res: any) => {
  //   if (res) {
  //     this.getDocumentList()
  //   }
  // })
  // }

  tabChange(){
   this.ngOnInit()
  }

  // /**************** Document Types Ends */
  StatusDocType(e, item){
    this.http.put(`${ApiUrls.resource}/${Doctypes.documentTypes}/${item?.name}`, { doc_delete_status: item.doc_delete_status}).subscribe((res: any) => {
     if (res) {
       this.getDocumentList()
     }
   })
   }

   onDrop(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.documentTypeList, event.previousIndex, event.currentIndex);
    this.documentTypeList.forEach((doc, idx) => {
      if(doc.is_editable == 0){
        this.save_doc_type_seq = true;
        doc.sequence = idx + 1;
      }

    });
  }

  saveSequence(){
    console.log(this.documentTypeList)
    this.http.post(ApiUrls.update_document_sequence,{data:{data:this.documentTypeList}}).subscribe((res:any)=>{
      if(res?.message?.success){
        this.toaster.success(res?.message?.message)
        this.getDocumentList()
        this.save_doc_type_seq = false;
      }else{
        this.toaster.error("Error")
      }

    })
  }
}
