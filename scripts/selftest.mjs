// node scripts/selftest.mjs
import assert from 'node:assert/strict';
import { daysUntil, defaultFirstDay, passMath, slalomPath } from '../assets/js/site.js';

assert.equal(daysUntil(new Date(2026, 11, 13), new Date(2026, 10, 2)), 41);
assert.equal(daysUntil(new Date(2027, 2, 29), new Date(2027, 2, 27)), 2); // across DST change
assert.deepEqual(defaultFirstDay(new Date(2026, 10, 2)), new Date(2026, 11, 13));
assert.deepEqual(defaultFirstDay(new Date(2026, 11, 10)), new Date(2027, 11, 13));
assert.deepEqual(passMath(690, 65, 14), { even: 11, cost: 690 / 14, diff: 220, more: 0 });
assert.deepEqual(passMath(650, 65, 10), { even: 10, cost: 65, diff: 0, more: 0 });
assert.equal(passMath(690, 65, 5).more, 6);
assert.equal(passMath(0, 65, 5), null);
assert.equal(passMath(690, NaN, 5), null);
assert.equal(slalomPath(2), 'M50,0 C82,125 82,375 50,500 C18,625 18,875 50,1000');
console.log('selftest ok');
