const assert = require('node:assert/strict');
const {estimateQuote,parseInstant,formatInstant} = require('./static/practical-tools.js');
const first=estimateQuote({hours:6,rate:25,expenses:35,rights:0,fee:15});
assert.equal(first.base,185);assert.equal(first.invoice,217.65);assert.ok(first.remaining>=185);
const second=estimateQuote({hours:8,rate:40,expenses:20,rights:100,fee:10});
assert.equal(second.base,440);assert.equal(second.invoice,488.89);assert.ok(second.remaining>=440);
assert.equal(estimateQuote({hours:1,rate:.29,expenses:0,rights:0,fee:0}).invoice,.29);
assert.equal(estimateQuote({hours:0,rate:0,expenses:0,rights:0,fee:99}).invoice,0);
for (const fee of [-1,100,Infinity,NaN]) assert.throws(()=>estimateQuote({hours:6,rate:25,expenses:35,rights:0,fee}));
assert.throws(()=>estimateQuote({hours:6,rate:-25,expenses:35,rights:0,fee:15}));
for (const invalid of ['2026-11-13T20:00:00','2026-02-30T20:00:00Z','2025-02-29T20:00:00Z','2026-11-13T24:00:00Z','2026-11-13T20:00:00+14:30','2026-11-13T20:00:00+03:99','<script>']) assert.throws(()=>parseInstant(invalid),invalid);
assert.equal(parseInstant('2026-11-13T20:00:00-03:00').toISOString(),'2026-11-13T23:00:00.000Z');
assert.equal(parseInstant('2024-02-29T20:00:00Z').toISOString(),'2024-02-29T20:00:00.000Z');
const instant='2026-11-13T20:00:00-03:00';
for (const locale of ['fr','en','pt-BR','es']) {
 assert.ok(formatInstant(instant,'America/Sao_Paulo',locale).includes('20:00'));
 assert.ok(formatInstant(instant,'America/Port-au-Prince',locale).includes('18:00'));
 assert.ok(formatInstant(instant,'Europe/Paris',locale).includes('00:00'));
}
assert.ok(formatInstant(instant,'Europe/Paris','fr').startsWith('14/11/2026'));
assert.ok(formatInstant('2026-07-13T20:00:00-03:00','America/New_York','fr').includes('19:00'));
assert.ok(formatInstant('2026-11-13T20:00:00-03:00','America/New_York','fr').includes('18:00'));
console.log('Quote examples, boundaries, calendar validation and seasonal time conversions: PASS');
