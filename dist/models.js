import { DateTime } from 'luxon';
export class VrbneEventClass {
    constructor(date, time_from, time_to, note = '', tz) {
        this.date = date;
        this.time_from = time_from;
        this.time_to = time_to;
        this.note = note;
        this.tz = tz;
    }
    getDateTime(timeStr) {
        const [h, m] = timeStr.split(':').map(Number);
        const [year, month, day] = this.date.split('-').map(Number);
        return DateTime.fromObject({ year, month, day, hour: h, minute: m }, { zone: this.tz });
    }
    getDatetimeFrom() {
        return this.getDateTime(this.time_from);
    }
    getDatetimeTo() {
        return this.getDateTime(this.time_to);
    }
}
//# sourceMappingURL=models.js.map