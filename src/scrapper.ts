import axios from 'axios';
import { load } from 'cheerio';
import { VrbneEvent, VrbneEventClass } from './models.js';

const URL = 'http://itdev.cz/SlalomCourse/OpeningTimes.aspx';
const TZ = 'Europe/Prague';

export async function fetchEvents(): Promise<VrbneEvent[]> {
  try {
    const response = await axios.get(URL, { timeout: 10000 });
    const html = response.data;
    const $ = load(html);

    const table = $('.rgMasterTable');
    if (table.length === 0) {
      return [];
    }

    const tbody = table.find('tbody').last();
    if (tbody.length === 0) {
      return [];
    }

    const rows = tbody.find('tr');
    const events: VrbneEvent[] = [];

    rows.each((_i: number, row: any) => {
      const rowEvents = parseRow(row, $);
      events.push(...rowEvents);
    });

    return events;
  } catch (error) {
    console.error('HTTP error fetching events:', error);
    return [];
  }
}

function parseRow(row: any, $: any): VrbneEvent[] {
  const events: VrbneEvent[] = [];

  try {
    const dateStr = getFirstContent(row, 'label', $);
    if (!dateStr) {
      return [];
    }

    const noteTd = $(row).find('td[align="left"]');
    const note = noteTd.length > 0 ? noteTd.first().text().trim() : '';

    const hours = getHours($(row).find('td[align="center"]'), $);

    const eventDate = parseDate(dateStr);

    for (const [timeFrom, timeTo] of hours) {
      const event = new VrbneEventClass(eventDate, timeFrom, timeTo, note, TZ);
      events.push(event);
    }
  } catch (error) {
    console.error('Error parsing row:', error);
  }

  return events;
}

function getHours($cells: any, $: any): Array<[string, string]> {
  const hoursText: string[] = [];
  $cells.each((_i: number, cell: any) => {
    const text = $(cell).text().trim();
    if (text) {
      hoursText.push(text);
    }
  });

  if (hoursText.length === 2) {
    return [[hoursText[0], hoursText[1]]];
  } else if (hoursText.length === 4) {
    return [
      [hoursText[0], hoursText[1]],
      [hoursText[2], hoursText[3]],
    ];
  }
  return [];
}

function parseDate(dayMonth: string): string {
  const year = new Date().getFullYear();
  const match = dayMonth.match(/([0-9]{1,2})\.([0-9]{1,2})\./);

  if (!match) {
    throw new Error(`Invalid date format: ${dayMonth}`);
  }

  const day = parseInt(match[1], 10);
  const month = parseInt(match[2], 10);

  return `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function getFirstContent(element: any, selector: string, $: any): string | null {
  const result = $(element).find(selector).first();
  if (result.length > 0) {
    return result.text().trim();
  }
  return null;
}
