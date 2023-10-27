import * as Moment from 'moment';
export class DateToFilter {
  filter: any;
  constructor(docType: string, filterBy: string, filterDate?: Date[], filterType?: string) {
    let checkType = filterType ? filterType : 'creation';
    // console.log("====",checkType,"===========",filterType)
    switch (filterBy) {
      case 'Today':
        if (filterType == 'invoice_date' || filterType == 'bill_generation_date' || filterType == 'date' ) {
          const todayDate = Moment(new Date()).format('YYYY-MM-DD').toString();
          this.filter = [`${checkType}`, 'like', `${todayDate}`];
        } else {
          const todayDate = Moment(new Date()).format('YYYY-MM-DD');
          this.filter = [`${checkType}`, 'like', `%${todayDate}%`];
        }
        break;
      case 'Yesterday':
        if (filterType == 'invoice_date'|| filterType == 'bill_generation_date' || filterType == 'date') {
          const yesterdayDate = Moment(new Date()).subtract(1, 'day').format('YYYY-MM-DD');
          this.filter = [`${checkType}`, 'like', `${yesterdayDate}`];
        } else {
          const yesterdayDate = Moment(new Date()).subtract(1, 'day').format('YYYY-MM-DD');
          this.filter = [`${checkType}`, 'like', `%${yesterdayDate}%`];
        }

        break;
      case 'This Week':
          const weekStart = Moment(new Date()).startOf('week').format('YYYY-MM-DD');
          const weekEnd = Moment(new Date()).endOf('week').format('YYYY-MM-DD');
          this.filter = [docType, `${checkType}`, 'Between', [weekStart, weekEnd]];

        break;
      case 'Last Week':
        const lastWeekStart = Moment(new Date()).subtract(1, 'week').startOf('week').format('YYYY-MM-DD');
        const lastWeekEnd = Moment(new Date()).subtract(1, 'week').endOf('week').format('YYYY-MM-DD');
        this.filter = [docType, `${checkType}`, 'Between', [lastWeekStart, lastWeekEnd]];
        break;
      case 'This Month':
        const monthStart = Moment(new Date()).startOf('month').format('YYYY-MM-DD');
        const monthEnd = Moment(new Date()).endOf('month').format('YYYY-MM-DD');
        this.filter = [docType, `${checkType}`, 'Between', [monthStart, monthEnd]];
        break;
      case 'Last Month':
        const lastMonthStart = Moment(new Date()).subtract(1, 'month').startOf('month').format('YYYY-MM-DD');
        const lastMonthEnd = Moment(new Date()).subtract(1, 'month').endOf('month').format('YYYY-MM-DD');
        this.filter = [docType, `${checkType}`, 'Between', [lastMonthStart, lastMonthEnd]];
        break;
      case 'This Year':
        const yearStart = Moment(new Date()).startOf('year').format('YYYY-MM-DD');
        const yearEnd = Moment(new Date()).endOf('year').format('YYYY-MM-DD');
        this.filter = [docType, `${checkType}`, 'Between', [yearStart, yearEnd]];
        break;
      case 'Custom':
        const [startDate, endDate] = filterDate;
        const from = Moment(startDate).format('YYYY-MM-DD');
        const to = Moment(endDate).format('YYYY-MM-DD');
        this.filter = [docType, `${checkType}`, 'Between', [from, to]];
        break;
    }
  }
}
