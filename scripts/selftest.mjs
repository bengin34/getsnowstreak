// node scripts/selftest.mjs
import assert from 'node:assert/strict';
import { daysUntil, defaultFirstDay, passMath, slalomPath, stuntFrames } from '../assets/js/site.js';

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
{
  const r = stuntFrames([{ from: [0, 0], to: [100, 0], ms: 100 }, { from: [100, 0], to: [300, 0], ms: 300, h: 50, flip: -360 }], 4);
  assert.equal(r.duration, 400);
  assert.equal(r.frames.length, 9); // 5 + 4, shared joint frame not repeated
  assert.equal(r.frames.at(-1).offset, 1);
  assert.match(r.frames[6].transform, /translate\(200\.0px, -80\.0px\) rotate\(-180\.0deg\)/); // apex: 4*50*.25 + 30 above
  assert.deepEqual(r.landings, [{ t: 400, x: 300, y: 0 }]);
}
console.log('selftest ok');
