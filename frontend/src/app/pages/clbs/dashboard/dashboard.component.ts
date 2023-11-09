import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  // saleData = [
  //   { name: "Mobiles", value: 105000 },
  //   { name: "Laptop", value: 55000 },
  //   { name: "AC", value: 15000 },
  //   { name: "Headset", value: 150000 },
  //   { name: "Fridge", value: 20000 }
  // ];
  day='1'
  title = 'Population (in millions)';
  type = "ColumnChart";
  data221 = [
    ["Rooms", { v: 2, f: "12,345" }, "color: #214350", "6"],
    ["Food", { v: 6, f: "12,345" }, "color: #214350", "6"],
    ["Summary", { v: 3, f: "12,345" }, "color: #214350", "6"],
    ["Courtyard Rooms", { v: 8, f: "12,345" }, "color: #214350", "6"],
    ["Courtyard Food", { v: 9, f: "12,345" }, "color: #214350", "6"]
  ];
  columnNames221 = ["Year", "value", { role: "style" }, { role: "annotation" }];


   columnNames = ['Year', 'Asia','Europe'];
   options = {
    title: '',
    width: 450,
    height:290,
    isStacked: true,
    colors: ['#5cb85c', '#f0ad4e', '#d9534f', '#5bc0de'],
    legend: { position: 'none' },
    chart: { title: 'Chess opening moves',
             subtitle: 'popularity by percentage' },
    bars: 'horizontal', // Required for Material Bar Charts.
    axes: {
      x: {
        0: { side: 'top', label: 'Percentage'} // Top x-axis.
      }
    },
    bar: { groupWidth: "80%" }
  };

  constructor() { }

  ngOnInit(): void {
  }
  onSelect(event) {
    // const { row, column } = event[0];
    console.log(event);
    // const year = this.Bardata[row][0];
    // let selectedItem;
    // if (column === 1) {
    //   selectedItem = "current";
    // }
    // if (column === 2) {
    //   selectedItem = "target";
    // }
    // console.log("year", year, "SelectedItem", selectedItem, this.Bardata[row][column]);
  }
}
