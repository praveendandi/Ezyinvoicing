import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, EventEmitter, OnInit, ViewChild } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { forkJoin } from 'rxjs';
import { debounceTime, switchMap } from 'rxjs/operators';
import { ApiUrls, Doctypes } from 'src/app/shared/api-urls';

class RoleFilter {
  itemsPerPage = 20;
  currentPage = 1;
  totalCount = 100;
  search = '';
}
@Component({
  selector: 'app-roles',
  templateUrl: './roles.component.html',
  styleUrls: ['./roles.component.scss']
})
export class RolesComponent implements OnInit {
  @ViewChild('showUsers') showUsers: ElementRef;
  filters = new RoleFilter();
  onSearch = new EventEmitter();
  roleList = [];
  usersList = [];
  selectedRole;
  constructor(
    private http: HttpClient,
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private modal: NgbModal,
  ) { }

  ngOnInit(): void {
    this.onSearch.pipe(debounceTime(500)).subscribe((res) => this.updateRouterParams());

    this.getRolesCount();
  }
  updateRouterParams(): void {
    this.router.navigate(['home/roles'], {
      queryParams: this.filters
    });
  }

  getRolesCount(): void {
    this.http.get(`${ApiUrls.roles}`, {
      params: {
        fields: JSON.stringify(["count( `tabRole`.`name`) AS total_count"])
      }
    }).subscribe((res: any) => {
      this.filters.totalCount = res.data[0].total_count;
      this.getRolesData();
    });
  }

  getRolesData(): void {
    this.activatedRoute.queryParams.pipe(switchMap((params: RoleFilter) => {
      this.filters.totalCount = parseInt(params.totalCount as any, 0) || this.filters.totalCount;
      this.filters.search = params.search || this.filters.search;
      const queryParams: any = { filters: [] };

      if (this.filters.search) {
        queryParams.filters.push(['name', 'like', `%${this.filters.search}%`]);
      }
      queryParams.limit_page_length = this.filters.totalCount;
      queryParams.order_by = "`tabRole`.`creation` desc"
      queryParams.fields = JSON.stringify(["name", "role_name", "modified_by", "modified", "creation"]);
      queryParams.filters = JSON.stringify(queryParams.filters);
      
      const resultApi = this.http.get(`${ApiUrls.roles}`, { params: queryParams });
      return  resultApi;
    })).subscribe((res: any) => {
      if (res.data) {
        this.roleList = res.data;
        this.roleList = this.roleList.filter((each: any) => each?.name.includes('ezy'))
      }
    });
  }

  ShowUsers(item, i): void {
    this.usersList = []
    this.selectedRole = item
    this.modal.open(this.showUsers, {
      size: 'md',
      centered: true
    })

    const formData = new FormData();
    formData.append('doctype', Doctypes.user);
    formData.append('fields', JSON.stringify(["`tabUser`.`full_name`", "`tabUser`.`name`", "`tabUser`.`email`"]));
    formData.append('filters', JSON.stringify([["Has Role", "role", "=", `${item.name}`]]))
    this.http.post(ApiUrls.roleByUser, formData).subscribe((res: any) => {
      res.message.values.map((each: any) => {
        this.usersList.push(each[0])
      })
    })
  }
}
