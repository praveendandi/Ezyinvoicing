import { Component, OnInit, EventEmitter } from '@angular/core';
import { Router } from '@angular/router';
import { FileuploadProgressbarService } from './resuable/fileupload-progressbar/fileupload-progressbar.service';
import { SocketService } from 'src/app/shared/services/socket.service';
import { takeUntil } from 'rxjs/operators';

let MINUTES_UNITL_AUTO_LOGOUT = 30// in mins
const CHECK_INTERVAL = 5 // in ms
const STORE_KEY =  'lastAction';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  private destroyEvents: EventEmitter<boolean> = new EventEmitter();

  public getLastAction() {
    return parseInt(localStorage.getItem(STORE_KEY));
  }
 public setLastAction(lastAction: number) {
    localStorage.setItem(STORE_KEY, lastAction.toString());
  }

  title = 'Ezy-Invoice';
  isFileUploaderActive = true

  constructor(
    private router: Router,
    public fileuploadProgressbarService :FileuploadProgressbarService,
    private socketService: SocketService
  ){}

  ngOnInit(){
    this.isFileUploaderActive = false
    this.check();
    this.initListener();
    this.initInterval();
    localStorage.setItem(STORE_KEY,Date.now().toString());
    this.fileuploadProgressbarService.isFilesUploading.subscribe((res:any)=>{
      console.log(res)
      this.isFileUploaderActive = res
    })


  }

  initListener() {
    document.body.addEventListener('click', () => this.reset());
    document.body.addEventListener('mouseover',()=> this.reset());
    document.body.addEventListener('mouseout',() => this.reset());
    document.body.addEventListener('keydown',() => this.reset());
    document.body.addEventListener('keyup',() => this.reset());
    document.body.addEventListener('keypress',() => this.reset());
  }

  reset() {
    this.setLastAction(Date.now());
  }

  initInterval() {
    setInterval(() => {
      this.check();
    }, CHECK_INTERVAL);
  }

  check() {
    let company = JSON.parse(localStorage.getItem('company'))
    if(company){
      MINUTES_UNITL_AUTO_LOGOUT =  JSON.parse(localStorage.getItem('company')).minutes_until_auto_logout?JSON.parse(localStorage.getItem('company')).minutes_until_auto_logout:30
      const now = Date.now();
      const timeleft = this.getLastAction() + MINUTES_UNITL_AUTO_LOGOUT * 60 * 1000;
      const diff = timeleft - now;
      const isTimeout = diff < 0;

      if (isTimeout)  {
        localStorage.clear();
        this.router.navigate(['']);
      }
    }

  }

}
