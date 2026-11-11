/* Geovyora editorial tools. All inputs remain in memory in the browser. */
(() => {
  'use strict';
  function estimateQuote({hours, rate, expenses, rights, fee}) {
    const values = [hours, rate, expenses, rights, fee];
    const limits = [100000, 1000000, 1000000, 1000000, 99];
    if (values.some((n,i) => typeof n !== 'number' || !Number.isFinite(n) || n < 0 || n > limits[i])) throw new RangeError('Invalid quote');
    const base = hours * rate + expenses + rights;
    const invoice = Math.max(0, Math.ceil((base / (1-fee/100)) * 100 - 1e-7) / 100);
    const deduction = invoice * fee/100;
    return {base, invoice, deduction, remaining: invoice-deduction};
  }
  function parseInstant(value) {
    const m = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?(Z|[+-]\d{2}:\d{2})$/.exec(value);
    if (!m) throw new RangeError('Explicit offset required');
    const [year,month,day,hour,minute,second] = m.slice(1,7).map(v => Number(v || 0));
    const leap = year%4===0 && (year%100!==0 || year%400===0);
    const days = [31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
    if (year<1 || month<1 || month>12 || day<1 || day>days[month-1] || hour>23 || minute>59 || second>59) throw new RangeError('Invalid date');
    if (m[7]!=='Z') {
      const parts=m[7].slice(1).split(':').map(Number);
      if (parts[0]>14 || parts[1]>59 || (parts[0]===14 && parts[1]!==0)) throw new RangeError('Invalid offset');
    }
    const date = new Date(value);
    if (!Number.isFinite(date.getTime())) throw new RangeError('Invalid instant');
    return date;
  }
  function formatInstant(value, zone, locale) {
    return new Intl.DateTimeFormat(locale, {timeZone:zone, year:'numeric', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit', hourCycle:'h23', timeZoneName:'longOffset'}).format(parseInstant(value));
  }
  const api = Object.freeze({estimateQuote,parseInstant,formatInstant});
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (typeof document === 'undefined') return;
  document.querySelectorAll('.editorial-tool').forEach(tool => {
    const form=tool.querySelector('form'), result=tool.querySelector('.tool-result'), error=tool.querySelector('.tool-error');
    function calculate() {
      try {
        if (!form.checkValidity()) throw new RangeError('Invalid input');
        if (tool.dataset.tool==='quote') {
          const values={};
          for (const key of ['hours','rate','expenses','rights','fee']) values[key]=form.elements[key].valueAsNumber;
          const quote=estimateQuote(values);
          const formatter=new Intl.NumberFormat(tool.dataset.locale, {style:'currency', currency:form.elements.currency.value});
          for (const [key,value] of Object.entries(quote)) tool.querySelector('[data-result="'+key+'"]').textContent=formatter.format(value);
        } else {
          const value=form.elements.instant.value.trim();
          parseInstant(value);
          tool.querySelectorAll('[data-zone]').forEach(cell => cell.textContent=formatInstant(value,cell.dataset.zone,tool.dataset.locale));
        }
        error.textContent='';result.hidden=false;
      } catch {
        result.hidden=true;error.textContent=tool.dataset.error;
      }
    }
    form.addEventListener('submit', event => {event.preventDefault();calculate();});
    form.addEventListener('input',()=>{result.hidden=true;error.textContent='';});
    form.addEventListener('reset',()=>{setTimeout(calculate,0);});
    form.querySelector('.tool-controls').disabled=false;
    calculate();
  });
})();
