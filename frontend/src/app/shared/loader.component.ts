
import { ChangeDetectionStrategy } from '@angular/compiler/src/compiler_facade_interface';
import { Component, OnInit, ViewChild, ElementRef, ChangeDetectorRef } from '@angular/core';
import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-loader',
  template: `
  <div  *ngIf="showLoading" class="content overlay">
    <div class="imgParent">
    <!-- <div class="loader-1 center"><span></span></div> -->
    <img class="imgGif" src="../assets/gif/ezyIvoiceWhite.gif">
    </div>

  </div>
  <ng-content></ng-content>
  `
  ,
  styles: [`
/* Loader 1 */
.loader-1 {
	height: 32px;
	width: 32px;
	-webkit-animation: loader-1-1 4.8s linear infinite;
	        animation: loader-1-1 4.8s linear infinite;
}
.imgParent{
  display: flex;
  justify-content: center;
  align-items : center;
}
.imgGif{
  width: 65px;
  height: 45px;
  text-align: center;
}
@-webkit-keyframes loader-1-1 {
	0%   { -webkit-transform: rotate(0deg); }
	100% { -webkit-transform: rotate(360deg); }
}
@keyframes loader-1-1 {
	0%   { transform: rotate(0deg); }
	100% { transform: rotate(360deg); }
}
.loader-1 span {
	display: block;
	position: absolute;
	top: 0; left: 0;
	bottom: 0; right: 0;
	margin: auto;
	height: 32px;
	width: 32px;
	clip: rect(0, 32px, 32px, 16px);
	-webkit-animation: loader-1-2 1.2s linear infinite;
	        animation: loader-1-2 1.2s linear infinite;
}
@-webkit-keyframes loader-1-2 {
	0%   { -webkit-transform: rotate(0deg); }
	100% { -webkit-transform: rotate(220deg); }
}
@keyframes loader-1-2 {
	0%   { transform: rotate(0deg); }
	100% { transform: rotate(220deg); }
}
.loader-1 span::after {
	content: "";
	position: absolute;
	top: 0; left: 0;
	bottom: 0; right: 0;
	margin: auto;
	height: 32px;
	width: 32px;
	clip: rect(0, 32px, 32px, 16px);
	border: 3px solid #FFF;
	border-radius: 50%;
	-webkit-animation: loader-1-3 1.2s cubic-bezier(0.770, 0.000, 0.175, 1.000) infinite;
	        animation: loader-1-3 1.2s cubic-bezier(0.770, 0.000, 0.175, 1.000) infinite;
}
@-webkit-keyframes loader-1-3 {
	0%   { -webkit-transform: rotate(-140deg); }
	50%  { -webkit-transform: rotate(-160deg); }
	100% { -webkit-transform: rotate(140deg); }
}
@keyframes loader-1-3 {
	0%   { transform: rotate(-140deg); }
	50%  { transform: rotate(-160deg); }
	100% { transform: rotate(140deg); }
}


  .overlay {
    text-align: center;
  height: 100%;
  width: 100%;
  position: fixed;
  z-index: 10000;
  top: 0;
  left: 0;
  background-color: rgba(0,0,0, 0.5);
  overflow-x: hidden;
  transition: 0.5s;
  display:flex;
  justify-content:center;
  align-items:center;
}
  `]
})
export class LoaderComponent implements OnInit {
  showLoading = false;
  constructor(
    private loaderService: LoaderService,
    private cdr:ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.loaderService.getLoaderStats().subscribe((res) => {
      this.showLoading = res;
      this.cdr.detectChanges();
      if (res) {
      }
    });

  }

}

@Injectable({
  providedIn: 'root'
})
export class LoaderService {
  private loader: BehaviorSubject<boolean> = new BehaviorSubject(false);
  constructor() { }
  showLoader() {
    this.loader.next(true);
  }
  hideLoader() {
    this.loader.next(false);
  }
  getLoaderStats() {
    return this.loader.asObservable();
  }
}

